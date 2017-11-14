import datetime
import time
import calendar
import comparable

class EDTime(object, comparable.ComparableMixin):
    @staticmethod
    def immersive_delta():
        return 11644473600 # immersive time set 369 years in the future

    def __init__(self):
        self._datetime = datetime.datetime.now()

    def from_datetime(self, datetimestamp):
        self._datetime = datetimestamp

    def from_journal_timestamp(self, journal_timestamp):
        self._datetime = datetime.datetime.strptime(journal_timestamp, '%Y-%m-%dT%H:%M:%SZ')

    def from_immersive_epoch(self, epoch):
        self._datetime = datetime.datetime.utcfromtimestamp(epoch - EDTime.immersive_delta())
    
    def as_js_epoch(self):
        return int(calendar.timegm(self._datetime.timetuple()) * 1000) # JavaScript expects milliseconds while Python uses seconds for Epoch

    def as_py_epoch(self):
        return int(calendar.timegm(self._datetime.timetuple()))

    def as_datetime(self):
        return self._datetime

    def as_journal_timestamp(self):
        return self._datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        
    def as_immersive_epoch(self):
        epoch = self.as_py_epoch()
        return epoch + EDTime.immersive_delta()

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