import datetime
import time
import calendar
import comparable

class EDTime(object, comparable.ComparableMixin):
    @staticmethod
    def immersive_delta():
        return 1286 # Elite Dangerous is set 1286 years in the future

    def __immmersive(self):
        d = self._datetime
        try:
            return d.replace(year = d.year + EDTime.immersive_delta())
        except ValueError:
            return d + (date(d.year + EDTime.immersive_delta(), 1, 1) - date(d.year, 1, 1))

    def __init__(self):
        self._datetime = datetime.datetime.now()

    def from_datetime(self, datetimestamp):
        self._datetime = datetimestamp

    def from_js_epoch(self, js_epoch):
        self._datetime = datetime.datetime.fromtimestamp(js_epoch / 1000)

    def from_journal_timestamp(self, journal_timestamp):
        self._datetime = datetime.datetime.strptime(journal_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    
    def as_js_epoch(self):
        return int(calendar.timegm(self._datetime.timetuple()) * 1000) # JavaScript expects milliseconds while Python uses seconds for Epoch

    def as_py_epoch(self):
        return int(calendar.timegm(self._datetime.timetuple()))

    def as_datetime(self):
        return self._datetime

    def as_journal_timestamp(self):
        return self._datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        
    def as_immersive_date(self):
        immersive_datetime = self.__immmersive()
        return immersive_datetime.strftime('%Y-%m-%d')


    def __lt__(self, other):
        if isinstance(other, EDTime):
            return self._datetime < other._datetime
        else:
            return NotImplemented

    def elapsed_threshold(self, journal_timestamp, threshold_timedelta):
        edt= EDTime()
        edt.from_journal_timestamp(journal_timestamp)

        if edt < self:
            return False

        return (edt._datetime - self._datetime) >= threshold_timedelta

    def __str__(self):
        return str(self.as_journal_timestamp())

    __repr__ = __str__ 