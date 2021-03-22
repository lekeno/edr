from collections import deque
from edtime import EDTime

class EDRHitPPoints(object):
    def __init__(self, history_length, history_max_span, trend_span_s):
        self.history = deque(maxlen=history_length)
        self.history_max_span_ms = history_max_span * 1000
        self.trend_span_ms = trend_span_s * 1000

    def update(self, ppoints):
        previous_value = self.history[-1]["value"] if len(self.history) >= 2 else None
        if previous_value is not None and previous_value == ppoints:
            # remove redundant data point
            self.history.pop()
        now = EDTime.ms_epoch_now()
        self.history.append({"timestamp": now, "value": ppoints})

    def last_value(self):
        if self.empty():
            return None
        return self.history[-1]["value"]

    def previous_value(self):
        if self.len() < 2:
            return None
        return self.history[-2]["value"]

    def last(self):
        if self.empty():
            return None
        return self.history[-1]

    def previous(self):
        if self.len() < 2:
            return None
        return self.history[-2]

    def empty(self):
        return len(self.history) == 0

    def len(self):
        return len(self.history)

    def meaningful(self):
        if self.len() < 2:
            return False
        return self.last_value() != None and self.previous_value() != None

    def trend(self):
        if len(self.history) <= 2:
            return 0
        sum_delta_value = 0
        sum_delta_time = 0
        previous = self.history[-1]
        delta_time = self.history[-1]["timestamp"]
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
        
