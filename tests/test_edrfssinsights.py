import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edrfssinsights import EDRFSSInsights # EDR_INTERNAL

class TestEDRFSSInsights(unittest.TestCase):
    def setUp(self):
        self.edtime_patch = patch('edr.edrfssinsights.EDTime')
        self.mock_edtime = self.edtime_patch.start()
        self.mock_edtime.py_epoch_now.return_value = 1000

        self.fss = EDRFSSInsights()

    def tearDown(self):
        self.edtime_patch.stop()

    def test_init(self):
        self.assertFalse(self.fss.noteworthy)
        self.assertEqual(self.fss.processed, 0)
        self.assertEqual(self.fss.signals_seen, [])

    def test_process_ignored_event(self):
        event = {"event": "FSSDiscoveryScan", "timestamp": "2023-10-27T10:00:00Z"}
        self.assertFalse(self.fss.process(event))

    def test_process_uss(self):
        # Initial state
        self.assertFalse(self.fss.uss["available"])
        
        event = {
            "event": "FSSSignalDiscovered",
            "SignalName": "$USS;",
            "SignalName_Localised": "Unidentified Signal Source",
            "USSType": "$USS_Type_Salvage;",
            "USSType_Localised": "Degraded Emissions",
            "TimeRemaining": 1200, # 20 mins
            "timestamp": "2023-10-27T10:00:00Z",
            "SystemAddress": 123456
        }
        
        # Configure EDTime instance returned by EDTime() in process
        mock_event_time = MagicMock()
        mock_event_time.as_py_epoch.return_value = 1000
        self.mock_edtime.return_value = mock_event_time

        self.fss.update_system(123456, "TestSystem")
        
        processed = self.fss.process(event)
        self.assertTrue(processed)
        self.assertTrue(self.fss.uss["available"])
        self.assertEqual(self.fss.uss["variants"]["$USS_Type_Salvage;"]["count"], 1)
        self.assertTrue(self.fss.noteworthy)

    def test_process_station(self):
        event = {
            "event": "FSSSignalDiscovered",
            "SignalName": "Jameson Memorial",
            "IsStation": True,
            "timestamp": "2023-10-27T10:00:00Z",
            "SystemAddress": 123456
        }
        self.fss.update_system(123456, "Shinrarta Dezhra")
        
        processed = self.fss.process(event)
        self.assertTrue(processed)
        self.assertIn("Jameson Memorial", self.fss.stations)
        self.assertTrue(self.fss.noteworthy)

    def test_process_fleet_carrier(self):
        event = {
            "event": "FSSSignalDiscovered",
            "SignalName": "Carrier Name HGN-22X",
            "IsStation": True,
            "SignalType": "FleetCarrier",
            "timestamp": "2023-10-27T10:00:00Z",
            "SystemAddress": 123456
        }
        self.fss.update_system(123456, "TestSystem")
        
        processed = self.fss.process(event)
        self.assertTrue(processed)
        self.assertIn("HGN-22X", self.fss.fleet_carriers)
        # Regex captures trailing space
        self.assertEqual(self.fss.fleet_carriers["HGN-22X"], "Carrier Name ")

    def test_process_combat_zone(self):
        event = {
            "event": "FSSSignalDiscovered",
            "SignalName": "$Warzone_PointRace_High;",
            "SignalName_Localised": "Conflict Zone [High Intensity]",
            "timestamp": "2023-10-27T10:00:00Z",
            "SystemAddress": 123456
        }
        self.fss.update_system(123456, "TestSystem")
        
        processed = self.fss.process(event)
        self.assertTrue(processed)
        self.assertTrue(self.fss.combat_zones["available"])
        self.assertEqual(self.fss.combat_zones["variants"]["$Warzone_PointRace_High;"]["count"], 1)

    def test_summarize(self):
        # Setup state directly or via process
        self.fss.noteworthy = True
        self.fss.combat_zones["available"] = True
        self.fss.combat_zones["variants"]["$Warzone_PointRace_High;"]["count"] = 2
        
        summary = self.fss.summarize()
        # Expect list of strings
        # "CZ: 2 High" (localized/short name)
        # Checking for presence of "CZ" and "2"
        self.assertTrue(any("CZ" in s for s in summary))
        self.assertTrue(any("2" in s for s in summary))

    def test_update_system_resets(self):
        self.fss.update_system(123456, "System A")
        self.fss.process({
            "event": "FSSSignalDiscovered",
            "SignalName": "Station A",
            "IsStation": True,
            "timestamp": "2023-10-27T10:00:00Z",
            "SystemAddress": 123456
        })
        self.assertEqual(len(self.fss.stations), 1)
        
        # Update to different system
        self.fss.update_system(654321, "System B")
        self.assertEqual(len(self.fss.stations), 0)
        self.assertEqual(self.fss.star_system["name"], "System B")

    def test_process_different_system_resets(self):
        self.fss.update_system(123456, "System A")
        self.fss.process({
            "event": "FSSSignalDiscovered",
            "SignalName": "Station A",
            "IsStation": True,
            "timestamp": "2023-10-27T10:00:00Z",
            "SystemAddress": 123456
        })
        
        # Process event from different system address
        self.fss.process({
            "event": "FSSSignalDiscovered",
            "SignalName": "Station B",
            "IsStation": True,
            "timestamp": "2023-10-27T10:05:00Z",
            "SystemAddress": 654321
        })
        
        # Should have reset, so only Station B is there
        self.assertEqual(len(self.fss.stations), 1)
        self.assertIn("Station B", self.fss.stations)
        self.assertNotIn("Station A", self.fss.stations)
