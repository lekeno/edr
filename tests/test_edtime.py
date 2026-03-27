
from unittest import TestCase, main
from edr.utils.edtime import EDTime
import calendar, time, math

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
        self.assertEqual(result, u"-12d")

    def test_pretty_print_negative_timespan(self):
        timespan = -60*60*24*7
        result = EDTime.pretty_print_timespan(timespan)
        self.assertEqual(result, u"-7d")

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

    def test_epochs(self):
        # Python Epoch (seconds)
        now_py = 1600000000
        edt = EDTime()
        edt.from_py_epoch(now_py)
        self.assertEqual(edt.as_py_epoch(), now_py)
        self.assertEqual(edt.as_js_epoch(), now_py * 1000)
        
        # JS Epoch (multiseconds)
        now_js = 1600000000000
        edt = EDTime()
        edt.from_js_epoch(now_js)
        self.assertEqual(edt.as_py_epoch(), now_js // 1000)
        self.assertEqual(edt.as_js_epoch(), now_js)

    def test_future_times(self):
        distance = 100
        expected_duration = int(math.ceil(distance * 9.75 + 300))
        calculated_duration = EDTime.transfer_time(distance)
        self.assertEqual(calculated_duration, expected_duration)
        
        now = EDTime.py_epoch_now()
        eta = EDTime.eta_transfer(distance)
        # Allow small delta for execution time
        self.assertTrue(abs(eta - (now + expected_duration)) <= 1)
        
        future_py = now + 3600 # 1 hour later
        t_plus = EDTime.t_plus_py(future_py)
        self.assertEqual(t_plus, "T+1h")
        t_plus_short = EDTime.t_plus_py(future_py, short=True)
        self.assertEqual(t_plus_short, "+1h")

    def test_thresholds(self):
        # 1. older_than
        edt = EDTime()
        self.assertFalse(edt.older_than(10))
        
        # Rewind 11 seconds
        edt.rewind(11)
        self.assertTrue(edt.older_than(10))
        self.assertFalse(edt.older_than(20))
        
        # 2. is_in_the_past
        edt = EDTime()
        self.assertTrue(edt.is_in_the_past()) # Technically created a few micros ago
        
        future_edt = EDTime()
        future_edt.advance(100)
        self.assertFalse(future_edt.is_in_the_past())

    def test_time_travel(self):
        edt = EDTime()
        start_epoch = edt.as_py_epoch()
        
        edt.advance(60)
        self.assertEqual(edt.as_py_epoch(), start_epoch + 60)
        
        edt.rewind(30)
        self.assertEqual(edt.as_py_epoch(), start_epoch + 30)

if __name__ == '__main__':
    main()