import config_tests
from unittest import TestCase, main
from unittest.mock import MagicMock, patch
from edr.backoff import Backoff

class TestBackoff(TestCase):
    def test_init(self):
        b = Backoff("Test")
        self.assertEqual(b.name, "Test")
        self.assertEqual(b.base, 10)
        self.assertEqual(b.cap, 7200)
        self.assertEqual(b.attempts, 0)
        self.assertEqual(b.backoff_until, 0)

    @patch('backoff.EDTime')
    @patch('backoff.random.randint')
    def test_throttle(self, mock_randint, mock_edtime):
        mock_randint.return_value = 5 # Fixed jitter
        mock_edtime.py_epoch_now.return_value = 1000
        
        b = Backoff("Test", base=2, cap=100)
        
        # 1st attempt
        b.throttle()
        self.assertEqual(b.attempts, 1)
        # delay = min(100, 2 * 2^1) + 5 = 4 + 5 = 9
        # until = 1000 + 9
        self.assertEqual(b.backoff_until, 1009)
        
        # 2nd attempt
        b.throttle()
        self.assertEqual(b.attempts, 2)
        # delay = min(100, 2 * 2^2) + 5 = 8 + 5 = 13
        # until = 1000 + 13
        self.assertEqual(b.backoff_until, 1013)
        
        # Check capping behavior
        # Force high attempts to exceed cap
        b.attempts = 5 
        b.throttle()
        self.assertEqual(b.attempts, 6)
        # delay = min(100, 2 * 2^6) + 5 = 100 + 5 = 105
        # until = 1000 + 105
        self.assertEqual(b.backoff_until, 1105)

    @patch('backoff.EDR_LOG')
    @patch('backoff.EDTime')
    def test_until(self, mock_edtime, mock_log):
        b = Backoff("Test")
        b.until(5000)
        self.assertEqual(b.attempts, 1)
        self.assertEqual(b.backoff_until, 5000)

    @patch('backoff.EDTime')
    def test_throttled(self, mock_edtime):
        b = Backoff("Test")
        b.backoff_until = 2000
        
        mock_edtime.py_epoch_now.return_value = 1000
        self.assertTrue(b.throttled())
        
        mock_edtime.py_epoch_now.return_value = 3000
        self.assertFalse(b.throttled())

    @patch('backoff.EDR_LOG')
    def test_reset(self, mock_log):
        b = Backoff("Test")
        b.attempts = 5
        b.backoff_until = 9999
        
        b.reset()
        self.assertEqual(b.attempts, 0)
        self.assertEqual(b.backoff_until, 0)

if __name__ == '__main__':
    main()
