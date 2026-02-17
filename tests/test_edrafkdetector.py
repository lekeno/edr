import unittest
from unittest.mock import patch, MagicMock
from edr.controllers.edrafkdetector import EDRAfkDetector
from edr.utils.edtime import EDTime

class TestEDRAfkDetector(unittest.TestCase):
    def setUp(self):
        self.detector = EDRAfkDetector()

    def test_init(self):
        self.assertIsNone(self.detector.last_active_event)
        self.assertTrue(self.detector.is_afk())

    def test_process_passive_event(self):
        # Passive event should not update last_active_event
        # Iterate through all defined passive events
        for event_type in EDRAfkDetector.PASSIVE_EVENTS:
            event = {"event": event_type, "timestamp": "2023-01-01T12:00:00Z"}
            self.detector.process(event)
            self.assertIsNone(self.detector.last_active_event, f"Event {event_type} should be passive")

    def test_process_unknown_event(self):
        # Unknown event should be treated as active
        event = {"event": "UnknownEvent", "timestamp": "2023-01-01T12:00:00Z"}
        self.detector.process(event)
        self.assertEqual(self.detector.last_active_event, event)

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
        with patch('edr.controllers.edrafkdetector.EDTime') as MockEDTime:
            # Instance mock
            mock_time_instance = MockEDTime.return_value
            mock_time_instance.as_py_epoch.return_value = 1000
            
            # Case 1: Not AFK (elapsed < 300)
            MockEDTime.py_epoch_now.return_value = 1100 # 100 seconds elapsed
            self.assertFalse(self.detector.is_afk())
            
            # Case 2: AFK (elapsed >= 300)
            MockEDTime.py_epoch_now.return_value = 1400 # 400 seconds elapsed
            self.assertTrue(self.detector.is_afk())

if __name__ == '__main__':
    unittest.main()
