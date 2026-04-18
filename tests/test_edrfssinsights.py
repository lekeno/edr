
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrfssinsights import EDRFSSInsights

class TestEDRFSSInsights(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.controllers.edrfssinsights.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.return_value.as_py_epoch.return_value = 1000.0
        self.mock_time.py_epoch_now.return_value = 1000.0

        self.i18n_patch = patch('edr.controllers.edrfssinsights._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        self.i18nc_patch = patch('edr.controllers.edrfssinsights._c', side_effect=lambda x: x.split('|')[1] if '|' in x else x)
        self.mock_i18nc = self.i18nc_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        self.i18n_patch.stop()
        self.i18nc_patch.stop()

    def test_process_nav_beacon(self):
        insights = EDRFSSInsights()
        event = {
            "event": "FSSSignalDiscovered",
            "timestamp": "2022-01-01T10:00:00Z",
            "SystemAddress": 12345,
            "SignalName": "$MULTIPLAYER_SCENARIO42_TITLE;",
            "SignalName_Localised": "Nav Beacon"
        }
        
        # First process sets system address
        insights.process(event)
        self.assertTrue(insights.noteworthy)
        self.assertEqual(insights.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"], 1)

    def test_process_uss_high_grade(self):
        insights = EDRFSSInsights()
        event = {
            "event": "FSSSignalDiscovered",
            "timestamp": "2022-01-01T10:00:00Z",
            "SystemAddress": 12345,
            "SignalName": "$USS;",
            "SignalName_Localised": "Unidentified Signal Source",
            "USSType": "$USS_Type_VeryValuableSalvage;",
            "USSType_Localised": "High Grade Emissions",
            "TimeRemaining": 300
        }
        
        insights.process(event)
        self.assertTrue(insights.noteworthy)
        self.assertTrue(insights.uss["available"])
        self.assertEqual(insights.uss["variants"]["$USS_Type_VeryValuableSalvage;"]["count"], 1)
        self.assertEqual(len(insights.uss["variants"]["$USS_Type_VeryValuableSalvage;"]["expiring"]), 1)

    def test_summarize(self):
        insights = EDRFSSInsights()
        insights.noteworthy = True
        insights.uss["available"] = True
        insights.uss["variants"]["$USS_Type_VeryValuableSalvage;"]["count"] = 1
        insights.uss["variants"]["$USS_Type_VeryValuableSalvage;"]["expiring"] = [1000.0 + 1200.0] # 20 mins left
        
        # Mock time now to be 1000.0
        self.mock_time.py_epoch_now.return_value = 1000.0
        
        summary = insights.summarize()
        # "USS: 1 High Grade(+++++)" or similar depending on ranking logic
        # Rank logic: duration / (40*60) * 5. 1200 / 2400 = 0.5 * 5 = 2.5 -> 3?
        self.assertTrue(any("High Grade" in s for s in summary))

    def test_fleet_carrier(self):
        insights = EDRFSSInsights()
        event = {
            "event": "FSSSignalDiscovered",
            "timestamp": "2022-01-01T10:00:00Z",
            "SystemAddress": 12345,
            "SignalName": "My Carrier XYZ-123",
            "SignalType": "FleetCarrier",
            "IsStation": True 
        }
        
        # IsStation property is used in __process_locations_fss
        # But wait, code says:
        # if not is_station: self.other_locations.add... return
        # So IsStation must be True for FC processing logic to trigger in __process_locations_fss?
        # Code:
        #         is_station = fss_event.get("IsStation", None)
        #         if not is_station:
        #             self.other_locations.add(location_name)
        #             return
        
        insights.process(event)
        self.assertIn("XYZ-123", insights.fleet_carriers)
        self.assertEqual(insights.fleet_carriers["XYZ-123"], "My Carrier")

    def test_reset_system_change(self):
        insights = EDRFSSInsights()
        insights.star_system["address"] = 12345
        insights.processed = 5
        
        event = {
            "event": "FSSSignalDiscovered",
            "timestamp": "2022-01-01T10:00:00Z",
            "SystemAddress": 67890, # Changed
            "SignalName": "$MULTIPLAYER_SCENARIO42_TITLE;"
        }
        
        insights.process(event)
        self.assertEqual(insights.star_system["address"], 67890)
        self.assertEqual(insights.processed, 1) # Reset and processed 1
        
    def test_update_system(self):
        insights = EDRFSSInsights()
        insights.star_system["address"] = 12345
        insights.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"] = 5
        
        insights.update_system(67890, "New System")
        self.assertEqual(insights.star_system["address"], 67890)
        self.assertEqual(insights.signals["$MULTIPLAYER_SCENARIO42_TITLE;"]["count"], 0)

if __name__ == '__main__':
    unittest.main()
