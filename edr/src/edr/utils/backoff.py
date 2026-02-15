import random

from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL
from .edtime import EDTime  # EDR_INTERNAL


class Backoff:
    """
    Implements an exponential backoff strategy for API calls.
    """

    def __init__(self, name, base=10, cap=7200):
        """
        Initialize the backoff strategy.

        Args:
            name (str): Name of the service/API being throttled (for logging).
            base (int): Base delay in seconds.
            cap (int): Maximum delay in seconds.
        """
        self.backoff_until = 0
        self.attempts = 0
        self.base = base
        self.cap = cap
        self.name = name

    def throttle(self):
        """Increment attempts and calculate the next backoff time.

        Delay is calculated as min(cap, base * 2^attempts) + jitter (0-60s).
        """
        self.attempts += 1
        delay = min(self.cap, self.base * 2**self.attempts) + random.randint(0, 60)
        self.backoff_until = EDTime.py_epoch_now() + delay
        EDR_LOG.debug(f"Exponential backoff for {self.name} API calls: attempts={self.attempts}, until={EDTime.t_plus_py(self.backoff_until)}")

    def until(self, expire_at):
        """Force a backoff until a specific timestamp.

        Args:
            expire_at (int): The timestamp (Python epoch) to backoff until.
        """
        self.attempts += 1
        self.backoff_until = expire_at
        EDR_LOG.debug(f"Backoff for {self.name} API calls: attempts={self.attempts}, until={EDTime.t_plus_py(self.backoff_until)}")

    def throttled(self):
        """Check if the backoff is currently active.

        Returns:
            bool: True if currently throttled, False otherwise.
        """
        should = EDTime.py_epoch_now() < self.backoff_until
        if should:
            EDR_LOG.debug(f"Exponential backoff still active for {self.name} API calls: attempts={self.attempts}, until={EDTime.t_plus_py(self.backoff_until)}")
        return should

    def reset(self):
        """Reset the backoff state."""
        if self.attempts > 0:
            EDR_LOG.debug(f"Clearing exponential backoff for {self.name} API calls, attempts={self.attempts}")
        self.attempts = 0
        self.backoff_until = 0
