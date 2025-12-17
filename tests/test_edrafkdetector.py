import unittest
from unittest.mock import patch, MagicMock
from edr.edrafkdetector import EDRAfkDetector
import edr.edtime

class TestEDRAfkDetector(unittest.TestCase):
    def setUp(self):
        self.detector = EDRAfkDetector()

    def test_init(self):
        self.assertIsNone(self.detector.last_active_event)
        self.assertTrue(self.detector.is_afk())

    def test_process_passive_event(self):
        # Passive event should not update last_active_event
        event = {"event": "Music", "timestamp": "2023-01-01T12:00:00Z"}
        self.detector.process(event)
        self.assertIsNone(self.detector.last_active_event)

    def test_process_active_event(self):
        # Active event SHOULD update last_active_event
        event = {"event": "SupercruiseEntry", "timestamp": "2023-01-01T12:00:00Z"}
        self.detector.process(event)
        self.assertEqual(self.detector.last_active_event, event)

    def test_is_afk_logic(self):
        # Setup active event
        event_timestamp = "2023-01-01T12:00:00Z"
        event = {"event": "SupercruiseEntry", "timestamp": event_timestamp}
        self.detector.process(event)
        
        # Mock EDTime to convert timestamp string to epoch
        # The code does: last_active.from_journal_timestamp(self.last_active_event["timestamp"])
        # then: now - last_active.as_py_epoch() > 300
        
        # We need to control EDTime behavior entirely or just mock py_epoch_now
        
        # Let's say event was at T=1000
        with patch('edr.edtime.EDTime') as MockEDTime:
            # Instance mock
            mock_time_instance = MockEDTime.return_value
            mock_time_instance.as_py_epoch.return_value = 1000
            
            # Static method mock
            with patch('edr.edtime.EDTime.py_epoch_now') as mock_now:
                # Case 1: Not AFK (elapsed < 300)
                mock_now.return_value = 1100 # 100 seconds elapsed
                self.assertFalse(self.detector.is_afk())
                
                # Case 2: AFK (elapsed > 300)
                mock_now.return_value = 1400 # 400 seconds elapsed
                self.assertTrue(self.detector.is_afk())

if __name__ == '__main__':
    unittest.main()
