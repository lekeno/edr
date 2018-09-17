import config_tests
from unittest import TestCase, main
from edtime import EDTime
import calendar, time

class TestEDTime(TestCase):
    def test_pretty_print_timespan(self):
        timespan = 60*60*24*7
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"7d")

        timespan = 60*60*3
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"3h")

        timespan = 60*34
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"34m")

        timespan = 12
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"12s")

        timespan = 0
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"0s")

        timespan = -60*60*24*12
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"0")

    def test_pretty_print_timespan_short_diff(self):
        timespan = 60*60*24*7 + 60*60*5
        result = EDTime.pretty_print_timespan(timespan, short=False)
        self.assertEqual(result, u"7d:5h")
        result = EDTime.pretty_print_timespan(timespan, short=True)
        self.assertEqual(result, u"7d")

        timespan = 60*60*24*7 + 60*60*5 + 60*23 + 12
        result = EDTime.pretty_print_timespan(timespan, short=False)
        self.assertEqual(result, u"7d:5h")
        result = EDTime.pretty_print_timespan(timespan, short=True)
        self.assertEqual(result, u"7d")

        timespan = 60*60*5
        result = EDTime.pretty_print_timespan(timespan, short=False)
        self.assertEqual(result, u"5h")
        result = EDTime.pretty_print_timespan(timespan, short=True)
        self.assertEqual(result, u"5h")

        timespan = 60*60*5 + 60*12 + 23
        result = EDTime.pretty_print_timespan(timespan, short=False)
        self.assertEqual(result, u"5h:12m")
        result = EDTime.pretty_print_timespan(timespan, short=True)
        self.assertEqual(result, u"5h")

    def test_t_minus(self):
        nowish_ms = 1000 * calendar.timegm(time.gmtime())
        ago_ms = nowish_ms - 1000*60*60*24*7
        result = EDTime.t_minus(ago_ms)
        self.assertEqual(result, u"T-7d")

        ago_ms = nowish_ms - 1000*60*60*(24*7 + 5)
        result = EDTime.t_minus(ago_ms)
        self.assertEqual(result, u"T-7d:5h")
        result = EDTime.t_minus(ago_ms, short=True)
        self.assertEqual(result, u"-7d")
        
    def test_immersive_delta(self):
        actual_year = 2018
        elite_year = 3304
        self.assertEqual(actual_year + EDTime.immersive_delta(), elite_year)

    def test_js_epoch_now(self):
        epoch_nowish = calendar.timegm(time.gmtime())
        self.assertTrue(int(EDTime.js_epoch_now() / 1000) - epoch_nowish <= 1)

if __name__ == '__main__':
    main()