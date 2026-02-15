import unittest
from unittest.mock import Mock, patch
import sys
import os



from edr.controllers.edrfssinsights import EDRFSSInsights
from edr.utils.edtime import EDTime

class TestEDRFSSInsights(unittest.TestCase):
    def setUp(self):
        self.fss = EDRFSSInsights()

    def test_initial_state(self):
        self.assertEqual(self.fss.processed, 0)
        self.assertFalse(self.fss.noteworthy)
        self.assertEqual(len(self.fss.signals_seen), 0)

    def test_process_fss_signal(self):
        event = {
            "timestamp": "2023-10-27T10:00:00Z",
            "event": "FSSSignalDiscovered",
            "SystemAddress": 12345,
            "SignalName": "$MULTIPLAYER_SCENARIO42_TITLE;",
            "SignalName_Localised": "Nav Beacon"
        }
        
        # First call updates system
        self.fss.process(event)
        self.assertEqual(self.fss.star_system["address"], 12345)
        self.assertEqual(self.fss.processed, 1)
        self.assertTrue(self.fss.noteworthy)
        self.assertEqual(self.fss.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"], 1)

    @patch('edr.controllers.edrfssinsights.EDTime')
    def test_process_uss(self, mock_edtime):
        # Mock current time to be "before" expiration
        # Event is 2023...
        mock_edtime.return_value = MagicMock()
        # We need to mock the CLASS method py_epoch_now on the Mock object that replaces the class?
        # Actually simplest is to patch 'edrfssinsights.EDTime.py_epoch_now'
        
        pass

    def test_process_uss_logic(self):
        # Splitting logic to avoid patching issues in existing method if I mess up
        pass

    @patch('edr.controllers.edrfssinsights.EDTime.py_epoch_now')
    def test_process_uss(self, mock_now):
        # 2023-10-27T10:00:00Z is approx 1698400800
        mock_now.return_value = 1698400800
        
        event = {
            "timestamp": "2023-10-27T10:00:00Z",
            "event": "FSSSignalDiscovered",
            "SystemAddress": 12345,
            "SignalName": "$USS;",
            "SignalName_Localised": "Unidentified Signal Source",
            "USSType": "$USS_Type_ValuableSalvage;",
            "TimeRemaining": 1200
        }
        
        self.fss.process(event)
        self.assertTrue(self.fss.uss["available"])
        self.assertEqual(self.fss.uss["variants"]["$USS_Type_ValuableSalvage;"]["count"], 1)

    def test_summarize(self):
        self.fss.noteworthy = True
        self.fss.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"] = 2
        
        summary = self.fss.summarize()
        self.assertTrue(any("Nav Beacon: 2" in s for s in summary))

    def test_fleet_carrier(self):
        event = {
            "timestamp": "2023-10-27T10:00:00Z",
            "event": "FSSSignalDiscovered",
            "SystemAddress": 12345,
            "SignalName": "My Carrier X12-345",
            "SignalType": "FleetCarrier",
            "IsStation": True
        }
        
        self.fss.process(event)
        self.assertIn("X12-345", self.fss.fleet_carriers)
        self.assertEqual(self.fss.fleet_carriers["X12-345"], "My Carrier")

    def test_reset(self):
        self.fss.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"] = 5
        self.fss.reset()
        self.assertEqual(self.fss.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"], 0)


if __name__ == '__main__':
    unittest.main()
