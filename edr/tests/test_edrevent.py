import config_tests
from unittest import TestCase, main
import calendar, time
from edrevent import EDREvent

class TestEDREvent(TestCase):
    def test_is_upcoming(self):
        event = EDREvent()
        self.assertFalse(event.is_upcoming())

        event = EDREvent()
        now = calendar.timegm(time.gmtime()) * 1000
        aday = 60*60*24*1000
        tomorrow = now + aday
        event.start = tomorrow
        event.heads_up = 1
        self.assertTrue(event.is_upcoming())

        event = EDREvent()
        aweek = 7 * aday
        next_week = now + aweek
        event.start = next_week
        event.heads_up = 1
        self.assertFalse(event.is_upcoming())
        event.heads_up = 7
        self.assertTrue(event.is_upcoming())

if __name__ == '__main__':
    main()