from edentities import EDLocation
from edtime import EDTime

class EDREvent(object):
    def __init__(self, event_dict = None):
        if event_dict:
            self.from_dict(event_dict)
        else:
            self.name = None
            self.description = None
            self._start = None
            self._end = None
            self.heads_up = None
            self.mode = None
            self.location = None
            self.more = None

    def from_dict(self, event_dict):
        #TODO try except?
        self.name = event_dict.get("name", None)
        self.description = event_dict.get("description", None)
        self._start = EDTime.from_js_epoch(event_dict.get("start", None))
        self._end = EDTime.from_js_epoch(event_dict.get("end", None))
        self.heads_up = event_dict.get("headsUp", None)
        self.mode = event_dict.get("mode", None)
        self.location = EDLocation()
        self.location.star_system = event_dict.get("starSystem", None)
        self.location.place = event_dict.get("place", None) 
        self.more = event_dict.get("more", None)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, js_epoch_start):
        edt = EDTime.from_js_epoch(js_epoch_start)
        self._start = edt

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, js_epoch_end):
        self._end = EDTime.from_js_epoch(js_epoch_end)

    def is_upcoming(self):
        if self._start and self.heads_up:
            return self._start.is_upcoming(self.heads_up)
        return False

    def is_on_going(self):
        if self._start and self._end:
            return self._start.is_past() and self._end.is_future()
        return False

    def is_over(self):
        if self._end:
            return self._end.is_past()
        return False

    def summarize(self):
        if not self.__is_valid():
            return None
        summary = None
        if self.is_future():
            summary = u"".format(self.name)

    def one_liner(self):
        if not self.__is_valid():
            return None
        summary = u"{} {}".format(self._start.t_notation(short=True), self.name)
        summary += u" in {}".format(self.location)
        #TODO
        return summary

    def __is_valid(self):
        fields = self.name and self._start and self._end and self.heads_up and self.mode
        rules = self._start <= self._end and self.heads_up >= 0
        return fields and rules


