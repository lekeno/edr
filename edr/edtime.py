import datetime
import calendar
import time
import comparable
import math
from edri18n import _, _c

class EDTime(comparable.ComparableMixin):
    @staticmethod
    def js_epoch_now():
        return 1000 * calendar.timegm(time.gmtime())

    @staticmethod
    def py_epoch_now():
        return calendar.timegm(time.gmtime())

    @staticmethod
    def ms_epoch_now():
        return int(round(time.time() * 1000))

    @staticmethod
    def immersive_delta():
        return 1286 # Elite Dangerous is set 1286 years in the future

    @staticmethod
    def t_minus(js_epoch_then, short=False):
        return EDTime.t_minus_py(int(js_epoch_then // 1000))

    @staticmethod
    def t_minus_py(py_epoch_then, short=False):
        ago = EDTime.py_epoch_now() - py_epoch_then
        if short:
            # Translators: this is to show how long ago an event took place, keep it ultra-short, e.g. -{} would show something like -3H
            return _c(u"short notation for t-minus|-{}").format(EDTime.pretty_print_timespan(ago, short=True))
        # Translators: this is to show how long ago an event took place, keep it short, e.g. T-{} would show something like T-3H
        return u"T-{}".format(EDTime.pretty_print_timespan(ago))
    
    @staticmethod
    def t_plus_py(py_epoch_later, short=False):
        ahead = int(py_epoch_later - EDTime.py_epoch_now())
        if short:
            # Translators: this is to show how long ahead an event will take place, keep it ultra-short, e.g. +{} would show something like +3H
            return _c(u"short notation for t-plus|+{}").format(EDTime.pretty_print_timespan(ahead, short=True))
        # Translators: this is to show how long ahead an event will take place, keep it short, e.g. T+{} would show something like T+3H
        return u"T+{}".format(EDTime.pretty_print_timespan(ahead))

    @staticmethod
    def eta_transfer(distance):
        return EDTime.py_epoch_now() + EDTime.transfer_time(distance)

    
    @staticmethod
    def transfer_time(distance):
        return int(math.ceil(distance * 9.75 + 300))
    
    @staticmethod
    def pretty_print_timespan(timespan, short=False, verbose=False):
        if timespan < 0:
            return u"0"
        remaining = timespan
        days = remaining // 86400
        remaining -= days * 86400

        hours = (remaining // 3600) % 24
        remaining -= hours * 3600

        minutes = (remaining // 60) % 60
        remaining -= minutes * 60

        seconds = (remaining % 60)

        readable = ""
        if days > 0:
            suffix = (_c(u"suffix| days") if days > 1 else _c(u"suffix| day")) if verbose else _c(u"short suffix|d")            
            readable = _(u"{nb_days}{suffix}").format(nb_days=days, suffix=suffix)
            if hours > 0 and not short:
                suffix = (_c(u"suffix| hours") if hours > 1 else _c(u"suffix| hour")) if verbose else _c(u"short suffix|h")
                readable += _(u":{nb_hours}{suffix}").format(nb_hours=hours, suffix=suffix)
        elif hours > 0:
            suffix = (_c(u"suffix| hours") if hours > 1 else _c(u"suffix| hour")) if verbose else _c(u"short suffix|h")
            readable = _(u"{nb_hours}{suffix}").format(nb_hours=hours, suffix=suffix)
            if minutes > 0 and not short:
                suffix = (_c(u"suffix| minutes") if minutes > 1 else _c(u"suffix| minute")) if verbose else _c(u"short suffix|m")
                readable += _(u":{nb_minutes}{suffix}").format(nb_minutes=minutes, suffix=suffix)
        elif minutes > 0:
            suffix = (_c(u"suffix| minutes") if minutes > 1 else _c(u"suffix| minute")) if verbose else _c(u"short suffix|m")
            readable = _(u"{nb_minutes}{suffix}").format(nb_minutes=minutes, suffix=suffix)
            if seconds > 0 and not short:
                suffix = (_c(u"suffix| seconds") if seconds > 1 else _c(u"suffix| second")) if verbose else _c(u"short suffix|s")
                readable += _(u":{nb_seconds}{suffix}").format(nb_seconds=seconds, suffix=suffix)
        else:
            suffix = (_c(u"suffix| seconds") if seconds > 1 else _c(u"suffix| second")) if verbose else _c(u"short suffix|s")
            readable = _(u"{nb_seconds}{suffix}").format(nb_seconds=seconds, suffix=suffix)

        return readable

    def __immmersive(self):
        d = self._datetime
        try:
            return d.replace(year = d.year + EDTime.immersive_delta())
        except ValueError:
            return d + (datetime.date(d.year + EDTime.immersive_delta(), 1, 1) - datetime.date(d.year, 1, 1))

    def __init__(self):
        self._datetime = datetime.datetime.now()

    def from_datetime(self, datetimestamp):
        self._datetime = datetimestamp

    def from_js_epoch(self, js_epoch):
        self._datetime = datetime.datetime.fromtimestamp(js_epoch // 1000, datetime.timezone.utc)

    def from_journal_timestamp(self, journal_timestamp):
        self._datetime = datetime.datetime.strptime(journal_timestamp, '%Y-%m-%dT%H:%M:%SZ')

    def from_edsm_timestamp(self, edsm_timestamp):
        self._datetime = datetime.datetime.strptime(edsm_timestamp, '%Y-%m-%d %H:%M:%S')
    
    def as_js_epoch(self):
        return self.as_py_epoch() * 1000 # JavaScript expects milliseconds while Python uses seconds for Epoch
        
    def as_py_epoch(self):
        return int(self._datetime.timestamp())

    def as_datetime(self):
        return self._datetime

    def as_journal_timestamp(self):
        return self._datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    def as_date(self):
        return self._datetime.strftime('%Y-%m-%d')
        
    def as_immersive_date(self):
        immersive_datetime = self.__immmersive()
        return immersive_datetime.strftime(_('%Y-%m-%d'))

    def as_hhmmss(self):
        return self._datetime.strftime('%H:%M:%S')

    def __lt__(self, other):
        if isinstance(other, EDTime):
            return self._datetime < other._datetime
        else:
            return NotImplemented

    def is_in_the_past(self):
        return self < EDTime()

    def elapsed_threshold(self, journal_timestamp, threshold_timedelta_seconds):
        edt= EDTime()
        edt.from_journal_timestamp(journal_timestamp)

        if edt < self:
            return False

        return (edt._datetime - self._datetime).total_seconds() >= threshold_timedelta_seconds

    def older_than(self, threshold_timedelta_seconds):
        now= EDTime()
        
        if now < self:
            return False

        return (now._datetime - self._datetime).total_seconds() >= threshold_timedelta_seconds

    def __str__(self):
        return str(self.as_journal_timestamp())

    def advance(self, seconds):
        self._datetime += datetime.timedelta(seconds=seconds)

    def rewind(self, seconds):
        self._datetime -= datetime.timedelta(seconds=seconds)

    __repr__ = __str__ 