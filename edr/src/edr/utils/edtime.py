import datetime
import calendar
import time
import math
import email.utils

from .comparable import ComparableMixin
from edr.core.edri18n import _, _c


class EDTime(ComparableMixin):
    """
    Time utility class for Elite Dangerous, handling conversions between
    Python epochs, JavaScript epochs, datetime objects, and in-game time.
    """

    @staticmethod
    def js_epoch_now():
        """
        Returns current time in milliseconds (JS epoch).

        Returns:
            int: The current time in milliseconds since epoch.
        """
        return 1000 * calendar.timegm(time.gmtime())

    @staticmethod
    def py_epoch_now():
        """
        Returns current time in seconds (Python epoch).

        Returns:
            int: The current time in seconds since epoch.
        """
        return calendar.timegm(time.gmtime())

    @staticmethod
    def ms_epoch_now():
        """
        Returns current high-precision time in milliseconds.

        Returns:
            int: The current time in milliseconds.
        """
        return int(round(time.time() * 1000))

    @staticmethod
    def immersive_delta():
        """
        Returns the year difference between IRL and Elite Dangerous.

        Returns:
            int: The year difference (1286).
        """
        return 1286  # Elite Dangerous is set 1286 years in the future

    @staticmethod
    def t_minus(js_epoch_then, short=False):
        """
        Formats time elapsed since a JS epoch timestamp.

        Args:
            js_epoch_then (int): The past timestamp in JS epoch (ms).
            short (bool): Whether to use short notation. Defaults to False.

        Returns:
            str: Locally formatted t-minus string (e.g. "T-2H").
        """
        return EDTime.t_minus_py(int(js_epoch_then // 1000), short)

    @staticmethod
    def t_minus_py(py_epoch_then, short=False):
        """
        Formats time elapsed since a Python epoch timestamp.

        Args:
            py_epoch_then (int): The past timestamp in Python epoch (s).
            short (bool): Whether to use short notation. Defaults to False.

        Returns:
            str: Locally formatted t-minus string.
        """
        ago = EDTime.py_epoch_now() - py_epoch_then
        if short:
            # Translators: this is to show how long ago an event took place, keep it ultra-short, e.g. -{} would show something like -3H
            return _c("short notation for t-minus|-{}").format(EDTime.pretty_print_timespan(ago, short=True))
        # Translators: this is to show how long ago an event took place, keep it short, e.g. T-{} would show something like T-3H
        return "T-{}".format(EDTime.pretty_print_timespan(ago))

    @staticmethod
    def t_plus_py(py_epoch_later, short=False):
        """
        Formats time remaining until a future Python epoch timestamp.

        Args:
            py_epoch_later (int): The future timestamp in Python epoch (s).
            short (bool): Whether to use short notation. Defaults to False.

        Returns:
            str: Locally formatted t-plus string.
        """
        ahead = int(py_epoch_later - EDTime.py_epoch_now())
        if short:
            # Translators: this is to show how long ahead an event will take place, keep it ultra-short, e.g. +{} would show something like +3H
            return _c("short notation for t-plus|+{}").format(EDTime.pretty_print_timespan(ahead, short=True))
        # Translators: this is to show how long ahead an event will take place, keep it short, e.g. T+{} would show something like T+3H
        return "T+{}".format(EDTime.pretty_print_timespan(ahead))

    @staticmethod
    def eta_transfer(distance):
        """
        Calculates ETA timestamp for a transfer over a given distance.

        Args:
            distance (float): Distance in light years.

        Returns:
            int: The estimated arrival timestamp (Python epoch).
        """
        return EDTime.py_epoch_now() + EDTime.transfer_time(distance)

    @staticmethod
    def transfer_time(distance):
        """
        Calculates transfer duration in seconds for a given distance.

        Args:
            distance (float): Distance in light years.

        Returns:
            int: Duration in seconds.
        """
        return int(math.ceil(distance * 9.75 + 300))

    @staticmethod
    def pretty_print_timespan(timespan, short=False, verbose=False):
        """
        Formats a time duration into a human-readable string (e.g., '2d:4h').

        Args:
            timespan (int): Duration in seconds.
            short (bool): Use abbreviated units (d/h/m/s). Defaults to False.
            verbose (bool): Use full unit names (days/hours...). Defaults to False.

        Returns:
            str: Formatted duration string.
        """
        if timespan < 0:
            return "-" + EDTime.pretty_print_timespan(abs(timespan), short, verbose)
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
            suffix = (_c("suffix| days") if days > 1 else _c("suffix| day")) if verbose else _c("short suffix|d")
            readable = _("{nb_days}{suffix}").format(nb_days=days, suffix=suffix)
            if hours > 0 and not short:
                suffix = (_c("suffix| hours") if hours > 1 else _c("suffix| hour")) if verbose else _c("short suffix|h")
                readable += _(":{nb_hours}{suffix}").format(nb_hours=hours, suffix=suffix)
        elif hours > 0:
            suffix = (_c("suffix| hours") if hours > 1 else _c("suffix| hour")) if verbose else _c("short suffix|h")
            readable = _("{nb_hours}{suffix}").format(nb_hours=hours, suffix=suffix)
            if minutes > 0 and not short:
                suffix = (_c("suffix| minutes") if minutes > 1 else _c("suffix| minute")) if verbose else _c("short suffix|m")
                readable += _(":{nb_minutes}{suffix}").format(nb_minutes=minutes, suffix=suffix)
        elif minutes > 0:
            suffix = (_c("suffix| minutes") if minutes > 1 else _c("suffix| minute")) if verbose else _c("short suffix|m")
            readable = _("{nb_minutes}{suffix}").format(nb_minutes=minutes, suffix=suffix)
            if seconds > 0 and not short:
                suffix = (_c("suffix| seconds") if seconds > 1 else _c("suffix| second")) if verbose else _c("short suffix|s")
                readable += _(":{nb_seconds}{suffix}").format(nb_seconds=seconds, suffix=suffix)
        else:
            suffix = (_c("suffix| seconds") if seconds > 1 else _c("suffix| second")) if verbose else _c("short suffix|s")
            readable = _("{nb_seconds}{suffix}").format(nb_seconds=seconds, suffix=suffix)

        return readable

    def __immersive(self):
        d = self._datetime
        try:
            return d.replace(year=d.year + EDTime.immersive_delta())
        except ValueError:
            return d + (datetime.date(d.year + EDTime.immersive_delta(), 1, 1) - datetime.date(d.year, 1, 1))

    def __init__(self):
        """
        Initializes with current UTC time.
        """
        self._datetime = datetime.datetime.now(datetime.timezone.utc)

    def from_datetime(self, datetimestamp):
        """
        Sets time from a datetime object.

        Args:
            datetimestamp (datetime): The datetime to invoke.
        """
        self._datetime = datetimestamp

    def from_js_epoch(self, js_epoch):
        """
        Sets time from a JavaScript epoch (milliseconds).

        Args:
            js_epoch (int): Timestamp in milliseconds.
        """
        self._datetime = datetime.datetime.fromtimestamp(js_epoch // 1000, datetime.timezone.utc)

    def from_py_epoch(self, py_epoch):
        """
        Sets time from a Python epoch (seconds).

        Args:
            py_epoch (int): Timestamp in seconds.
        """
        self._datetime = datetime.datetime.fromtimestamp(py_epoch, datetime.timezone.utc)

    def from_journal_timestamp(self, journal_timestamp):
        """
        Sets time from an ED Journal timestamp string.

        Args:
            journal_timestamp (str): Timestamp string (e.g. '2022-01-01T12:00:00Z').
        """
        self._datetime = datetime.datetime.strptime(journal_timestamp, '%Y-%m-%dT%H:%M:%S%z')

    def from_http_header(self, date_str):
        """
        Sets time from an HTTP header date string.

        Args:
            date_str (str): Date string or timestamp.
        """
        if date_str.isdigit():
            self._datetime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=int(date_str))
        else:
            self._datetime = email.utils.parsedate_to_datetime(date_str)

    def from_edsm_timestamp(self, edsm_timestamp):
        """
        Sets time from an EDSM timestamp string.

        Args:
            edsm_timestamp (str): Timestamp string without Z (e.g. '2022-01-01 12:00:00').
        """
        self._datetime = datetime.datetime.strptime(edsm_timestamp + "Z", '%Y-%m-%d %H:%M:%S%z')

    def as_js_epoch(self):
        """
        Gets time as JavaScript epoch (milliseconds).

        Returns:
            int: Timestamp in milliseconds.
        """
        return self.as_py_epoch() * 1000  # JavaScript expects milliseconds while Python uses seconds for Epoch

    def as_py_epoch(self):
        """
        Gets time as Python epoch (seconds).

        Returns:
            int: Timestamp in seconds.
        """
        return int(self._datetime.timestamp())

    def as_datetime(self):
        """
        Gets the internal datetime object.

        Returns:
            datetime: The internal datetime object.
        """
        return self._datetime

    def as_journal_timestamp(self):
        """
        Gets time as ED Journal timestamp string.

        Returns:
            str: Formatted string 'YYYY-MM-DDTHH:MM:SSZ'.
        """
        return self._datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    def as_timestamp(self):
        """
        Gets time as simple timestamp string.

        Returns:
            str: Formatted string 'YYYY-MM-DDTHH:MM:SS'.
        """
        return self._datetime.strftime('%Y-%m-%dT%H:%M:%S')

    def as_local_timestamp(self):
        """
        Gets time as local timestamp string.

        Returns:
            str: Formatted string 'YYYY-MM-DD HH:MM:SS'.
        """
        return self._datetime.astimezone().strftime('%Y-%m-%d %H:%M:%S')

    def as_date(self):
        """
        Gets date part string (UTC).

        Returns:
            str: 'YYYY-MM-DD'.
        """
        return self._datetime.strftime('%Y-%m-%d')

    def as_local_date(self):
        """
        Gets date part string (Local).

        Returns:
            str: 'YYYY-MM-DD'.
        """
        return self._datetime.astimezone().strftime('%Y-%m-%d')

    def as_immersive_date(self):
        """
        Gets date adjusted for Elite Dangerous time (+1286 years).

        Returns:
            str: 'YYYY-MM-DD'.
        """
        immersive_datetime = self.__immersive()
        return immersive_datetime.strftime(_('%Y-%m-%d'))

    def as_hhmmss(self):
        """
        Gets time as HH:MM:SS string.

        Returns:
            str: 'HH:MM:SS'.
        """
        return self._datetime.strftime('%H:%M:%S')

    def __lt__(self, other):
        """
        Compares two EDTime objects.

        Args:
            other (EDTime): The other time object.

        Returns:
            bool: True if self is earlier than other.
        """
        if isinstance(other, EDTime):
            return self._datetime < other._datetime
        return NotImplemented

    def is_in_the_past(self):
        """
        Checks if the time is in the past relative to now.

        Returns:
            bool: True if in the past.
        """
        return self < EDTime()

    def elapsed_threshold(self, journal_timestamp, threshold_timedelta_seconds):
        """
        Checks if a given journal timestamp is older than this object by a threshold.

        Careful: this method compares journal string vs internal (self).

        Args:
            journal_timestamp (str): The timestamp to compare.
            threshold_timedelta_seconds (int): Threshold in seconds.

        Returns:
            bool: True if elapsed >= threshold.
        """
        edt = EDTime()
        edt.from_journal_timestamp(journal_timestamp)

        if edt < self:
            return False

        return (edt._datetime - self._datetime).total_seconds() >= threshold_timedelta_seconds

    def older_than(self, threshold_timedelta_seconds):
        """
        Checks if this time object is older than now by a threshold.

        Args:
            threshold_timedelta_seconds (int): Threshold in seconds.

        Returns:
            bool: True if age >= threshold.
        """
        now = EDTime()

        if now < self:
            return False

        return (now._datetime - self._datetime).total_seconds() >= threshold_timedelta_seconds

    def __str__(self):
        """String representation (journal format)."""
        return str(self.as_journal_timestamp())

    def advance(self, seconds):
        """
        Advances the internal time by seconds.

        Args:
            seconds (int): Seconds to add.
        """
        self._datetime += datetime.timedelta(seconds=seconds)

    def rewind(self, seconds):
        """
        Rewinds the internal time by seconds.

        Args:
            seconds (int): Seconds to subtract.
        """
        self._datetime -= datetime.timedelta(seconds=seconds)

    __repr__ = __str__
