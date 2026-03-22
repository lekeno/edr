import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import sys

from edr.controllers.edrsystems import EDRSystems

class TestEDRSystems(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        self.edsm_server = MagicMock()
        self.factions = MagicMock()
        
        # Mock LRUCache to avoid disk I/O and isolate logic
        with patch('edr.controllers.edrsystems.LRUCache.load') as mock_load:
            # Create separate mocks for different caches to track calls individually
            self.mock_systems_cache = MagicMock()
            self.mock_fcs_cache = MagicMock()
            self.mock_fc_presence_cache = MagicMock()
            self.mock_fc_reports_cache = MagicMock()
            self.mock_fc_materials_cache = MagicMock()
            self.mock_edsm_systems_cache = MagicMock()
            self.mock_edsm_stations_cache = MagicMock()
            self.mock_edsm_bodies_cache = MagicMock()
            self.mock_edsm_system_values_cache = MagicMock()
            
            # Configure load to return appropriate mocks based on some call order or just return a generic mock that we configure later
            # Simpler approach: let load return a new MagicMock each time, and we capture them from the instance after init
            
            self.edr_systems = EDRSystems(self.server, self.edsm_server, self.factions)
            
            # Replace the instance caches with our specific mocks for easier assertions
            self.edr_systems.systems_cache = self.mock_systems_cache
            self.edr_systems.fcs_cache = self.mock_fcs_cache
            self.edr_systems.fc_presence_cache = self.mock_fc_presence_cache
            self.edr_systems.fc_reports_cache = self.mock_fc_reports_cache
            self.edr_systems.fc_materials_cache = self.mock_fc_materials_cache
            self.edr_systems.edsm_systems_cache = self.mock_edsm_systems_cache
            
            # Update manager caches
            self.edr_systems.station_manager.edsm_stations_cache = self.mock_edsm_stations_cache
            self.edr_systems.body_manager.edsm_bodies_cache = self.mock_edsm_bodies_cache
            self.edr_systems.body_manager.materials_cache = MagicMock() # or add a mock for it
            self.edr_systems.intel.traffic_cache = MagicMock()
            self.edr_systems.intel.crimes_cache = MagicMock()
            self.edr_systems.intel.sitreps_cache = MagicMock()
            self.edr_systems.intel.notams_cache = MagicMock()

    def test_system_id_cache_hit(self):
        star_system = "Sol"
        self.mock_systems_cache.has_key.return_value = True
        self.mock_systems_cache.is_stale.return_value = False
        self.mock_systems_cache.peek.return_value = {"1": {"name": "Sol"}}
        
        sid = self.edr_systems.system_id(star_system)
        
        self.assertEqual(sid, "1")
        self.server.system.assert_not_called()

    def test_system_id_cache_miss_server_hit(self):
        star_system = "Sol"
        self.mock_systems_cache.has_key.return_value = False
        self.server.system.return_value = {"1": {"name": "Sol"}}
        
        sid = self.edr_systems.system_id(star_system)
        
        self.assertEqual(sid, "1")
        self.server.system.assert_called_with(star_system, False, None)
        self.mock_systems_cache.set.assert_called_with("sol", {"1": {"name": "Sol"}})

    def test_system_id_negative_cache(self):
        star_system = "Unknown"
        self.mock_systems_cache.has_key.return_value = False
        self.server.system.return_value = None
        
        sid = self.edr_systems.system_id(star_system)
        
        self.assertIsNone(sid)
        self.mock_systems_cache.set.assert_called_with("unknown", None)

    def test_fc_id_cache_hit(self):
        callsign = "ABC-123"
        self.mock_fcs_cache.has_key.return_value = True
        self.mock_fcs_cache.is_stale.return_value = False
        self.mock_fcs_cache.peek.return_value = {"1": {"callsign": "ABC-123"}}
        
        fcid = self.edr_systems.fc_id(callsign, "Carrier", "Sol")
        
        self.assertEqual(fcid, "1")
        self.server.fc.assert_not_called()

    def test_fc_id_cache_miss(self):
        callsign = "ABC-123"
        self.mock_fcs_cache.has_key.return_value = False
        self.server.fc.return_value = {"1": {"callsign": "ABC-123"}}
        
        fcid = self.edr_systems.fc_id(callsign, "Carrier", "Sol")
        
        self.assertEqual(fcid, "1")
        self.server.fc.assert_called_with(callsign, "Carrier", "Sol", False)

    def test_stations_in_system_cache_hit(self):
        system = "Sol"
        stations = [{"name": "Galileo"}]
        self.mock_edsm_stations_cache.get.return_value = stations
        self.mock_edsm_stations_cache.has_key.return_value = True
        
        result = self.edr_systems.stations_in_system(system)
        
        self.assertEqual(result, stations)
        self.edsm_server.stations_in_system.assert_not_called()

    def test_stations_in_system_cache_miss(self):
        system = "Sol"
        stations = [{"name": "Galileo"}]
        self.mock_edsm_stations_cache.get.return_value = None
        self.mock_edsm_stations_cache.has_key.return_value = False
        self.edsm_server.stations_in_system.return_value = stations
        
        result = self.edr_systems.stations_in_system(system)
        
        self.assertEqual(result, stations)
        self.mock_edsm_stations_cache.set.assert_called_with("sol", stations)

    def test_distance(self):
        # EDRSystems.distance relies on self.system(name) which uses edsm_systems_cache
        # So we must mock edsm_systems_cache NOT systems_cache for system details
        self.mock_edsm_systems_cache.get.side_effect = [
            [{"name": "Sol", "coords": {"x": 0, "y": 0, "z": 0}}],
            [{"name": "Barnard's Star", "coords": {"x": 1, "y": 0, "z": 0}}]
        ]
        self.mock_edsm_systems_cache.has_key.return_value = True
        
        dist = self.edr_systems.distance("Sol", "Barnard's Star")
        
        self.assertEqual(dist, 1.0)

    def test_distance_with_coords(self):
        # Setup
        # distance_with_coords calls self.system(source_system) -> edsm_systems_cache
        self.mock_edsm_systems_cache.has_key.return_value = True
        self.mock_edsm_systems_cache.get.return_value = [{"name": "Sol", "coords": {"x": 0, "y": 0, "z": 0}}]
        
        dest_coords = {"x": 0, "y": 0, "z": 10}
        
        dist = self.edr_systems.distance_with_coords("Sol", dest_coords)
        self.assertEqual(dist, 10.0)

    def test_fuzzy_stations(self):
        system = "Sol"
        stations = [{"name": "Galileo"}, {"name": "Daedalus"}, {"name": "M. Gorbachev"}]
        self.mock_edsm_stations_cache.get.return_value = stations
        self.mock_edsm_stations_cache.has_key.return_value = True
        
        result = self.edr_systems.fuzzy_stations(system, "Galileo")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Galileo")
        
        result = self.edr_systems.fuzzy_stations(system, "ae")
        # "ae" matches in "Daedalus" only (case insensitive)
        self.assertEqual(len(result), 1) 
        self.assertEqual(result[0]["name"], "Daedalus")

    @patch('edr.controllers.edrsystems.edrconfig.EDR_CONFIG')
    def test_persist(self, mock_config):
        self.edr_systems.persist()
        
        self.mock_systems_cache.save.assert_called()
        self.mock_fcs_cache.save.assert_called()
        self.mock_edsm_systems_cache.save.assert_called()

    def test_update_fc_presence_novel(self):
        fc_report = {"starSystem": "Sol", "fcCount": 5}
        
        self.mock_systems_cache.has_key.return_value = True
        self.mock_systems_cache.is_stale.return_value = False
        self.mock_systems_cache.peek.return_value = {"1": {"name": "Sol"}}

        self.mock_fc_reports_cache.has_key.return_value = True
        self.mock_fc_reports_cache.is_stale.return_value = False
        self.mock_fc_reports_cache.get.return_value = {"fcCount": 4} # Different count
        
        self.server.report_fcs.return_value = True
        
        result = self.edr_systems.update_fc_presence(fc_report)
        
        self.assertTrue(result)
        self.mock_fc_reports_cache.set.assert_called_with("1", fc_report)
        self.mock_fc_presence_cache.evict.assert_called_with("1")

    def test_update_fc_presence_not_novel(self):
        fc_report = {"starSystem": "Sol", "fcCount": 5}
        
        self.mock_systems_cache.has_key.return_value = True
        self.mock_systems_cache.is_stale.return_value = False
        self.mock_systems_cache.peek.return_value = {"1": {"name": "Sol"}}

        self.mock_fc_reports_cache.has_key.return_value = True
        self.mock_fc_reports_cache.is_stale.return_value = False
        self.mock_fc_reports_cache.get.return_value = {"fcCount": 5} # Same count
        
        result = self.edr_systems.update_fc_presence(fc_report)
        
        self.assertFalse(result)
        self.server.report_fcs.assert_not_called()
        
    def test_describe_system_basic(self):
         # Setup
        self.mock_edsm_systems_cache.get.return_value = [{
            "name": "Sol",
            "primaryStar": {"type": "G", "isScoopable": True},
            "information": {
                "government": "Democracy",
                "allegiance": "Federation",
                "population": 10000000000,
                "security": "High",
                "economy": "Refinery",
                "factionState": "Boom"
            }
        }]
        # Need to ensure edsm_systems_cache.get is called by system()
        self.mock_edsm_systems_cache.has_key.return_value = True

        # Ensure system values cache miss so it hits the server mock
        self.mock_edsm_system_values_cache.get.return_value = None
        
        # Mock edsm_server.system_value to return a dict with integers, avoiding TypeError
        self.edsm_server.system_value.return_value = {"estimatedValue": 1000, "estimatedValueMapped": 2000, "valuableBodies": []}
        
        # Ensure we don't iterate over a MagicMock for bodies, which would cause totalHonkValue to become a Mock
        self.mock_edsm_bodies_cache.get.return_value = []
        self.mock_edsm_bodies_cache.has_key.return_value = True
        
        # Since we invoke real module code, we rely on however it is imported.
        # But wait, describe_system builds strings. 
        # In `edrsystems.py`, `from edr.core.edri18n import _, _c, _edr`.
        # If not mocked, `_` likely returns the string itself if language is English default.
        
        description = self.edr_systems.describe_system("Sol")

        # The description is a list of strings.
        # Check if contents are present.
        # "Gvt: Democracy" might be "Gvt: Democracy  " because of formatting.
        
        found_gvt = any("Gvt: Democracy" in line for line in description)
        found_alg = any("Alg: Federation" in line for line in description)
        
        self.assertTrue(found_gvt, f"Description was: {description}")
        self.assertTrue(found_alg, f"Description was: {description}")

if __name__ == '__main__':
    unittest.main()
