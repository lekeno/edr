from collections import deque
from edr.utils.edtime import EDTime


class EDRHitPPoints:
    """
    Tracks and analyzes hit points or percentage values over time to determine trends.
    """

    def __init__(self, history_length, history_max_span, trend_span_s):
        """Initialize the hit points tracker.

        Args:
            history_length (int): Maximum number of data points to keep.
            history_max_span (int): (Unused) Intended max span for history in seconds.
            trend_span_s (int): Time span in seconds over which to calculate trends.
        """
        self.history = deque(maxlen=history_length)
        self.history_max_span_ms = history_max_span * 1000
        self.trend_span_ms = trend_span_s * 1000

    def update(self, ppoints):
        """Update the tracker with a new percentage value.

        Removes redundant consecutive values to save space.

        Args:
            ppoints (float): The percentage points value (e.g., hull or shield %).
        """
        previous_value = self.history[-1]["value"] if len(self.history) >= 2 else None
        if previous_value is not None and previous_value == ppoints:
            # remove redundant data point
            self.history.pop()
        now = EDTime.ms_epoch_now()
        self.history.append({"timestamp": now, "value": ppoints})

    def last_value(self):
        """Return the most recent value.

        Returns:
            float: The most recent value, or None if empty.
        """
        if self.empty():
            return None
        return self.history[-1]["value"]

    def previous_value(self):
        """Return the second most recent value.

        Returns:
            float: The previous value, or None if less than 2 points.
        """
        if self.len() < 2:
            return None
        return self.history[-2]["value"]

    def last(self):
        """Return the most recent data point.

        Returns:
            dict: The most recent data point (dict), or None if empty.
        """
        if self.empty():
            return None
        return self.history[-1]

    def previous(self):
        """Return the second most recent data point.

        Returns:
            dict: The previous data point (dict), or None if less than 2 points.
        """
        if self.len() < 2:
            return None
        return self.history[-2]

    def empty(self):
        """Check if history is empty.

        Returns:
            bool: True if empty, False otherwise.
        """
        return len(self.history) == 0

    def len(self):
        """Return the number of data points in history.

        Returns:
            int: Number of data points.
        """
        return len(self.history)

    def meaningful(self):
        """Check if there is enough data to be meaningful.

        Meaningful data requires at least 2 points and non-None values.

        Returns:
            bool: True if meaningful, False otherwise.
        """
        if self.len() < 2:
            return False
        return self.last_value() is not None and self.previous_value() is not None

    def trend(self):
        """Calculate the trend (rate of change) in percentage points per second.

        Positive value indicates increasing, negative indicates decreasing.
        Also calculates estimated time to 0% or 100% based on the trend.

        Returns:
            float: Estimated seconds to reach 0% or 100%, or 0 if stable/undefined.
        """
        if len(self.history) <= 2:
            return 0
        sum_delta_value = 0
        sum_delta_time = 0
        previous = self.history[-1]

        span = 0
        checked = 0
        for i in reversed(self.history):
            delta_value = previous["value"] - i["value"]
            delta_time = previous["timestamp"] - i["timestamp"]
            span = self.history[-1]["timestamp"] - i["timestamp"]
            previous = i
            if delta_time == 0:
                continue
            if span >= self.trend_span_ms and checked >= 2:
                break
            sum_delta_value += delta_value
            sum_delta_time += delta_time
            checked += 1

        if sum_delta_time == 0:
            return 0

        trend_to100_or_0 = 0
        avg = sum_delta_value / sum_delta_time
        if avg > 0:
            trend_to100_or_0 = (100.0 - self.history[-1]["value"]) / avg / 1000 if (self.history[-1]["value"] and self.history[-1]["value"] < 100) else 0
        elif avg < 0 and span:
            trend_to100_or_0 = self.history[-1]["value"] / avg / 1000 if (self.history[-1]["value"] and self.history[-1]["value"] > 0) else 0
        return trend_to100_or_0
        
