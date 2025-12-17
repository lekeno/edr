
from edr.edrlog import EDR_LOG
import random
from edtime import EDTime



class Backoff(object):

    def __init__(self, name, base=10, cap=7200):
        self.backoff_until = 0 
        self.attempts = 0
        self.base = base
        self.cap = cap
        self.name = name

    def throttle(self):
        self.attempts += 1
        delay = min(self.cap, self.base * 2 ** self.attempts) + random.randint(0, 60)
        self.backoff_until = EDTime.py_epoch_now() + delay
        EDR_LOG.debug("Exponential backoff for {} API calls: attempts={}, until={}".format(self.name, self.attempts, EDTime.t_plus_py(self.backoff_until)))

    def until(self, expire_at):
        self.attempts += 1
        self.backoff_until = expire_at
        EDR_LOG.debug("Backoff for {} API calls: attempts={}, until={}".format(self.name, self.attempts, EDTime.t_plus_py(self.backoff_until)))

    def throttled(self):
        should = EDTime.py_epoch_now() < self.backoff_until
        if should:
            EDR_LOG.debug("Exponential backoff still active for {} API calls: attempts={}, until={}".format(self.name, self.attempts, EDTime.t_plus_py(self.backoff_until)))
        return should
    
    def reset(self):
        if self.attempts > 0:
            EDR_LOG.debug("Clearing exponential backoff for {} API calls, attempts={}".format(self.name, self.attempts))
        self.attempts = 0
        self.backoff_until = 0
