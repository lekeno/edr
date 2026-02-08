import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the 'edr' directory to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr')))

from edrsystems import EDRSystems

class TestEDRSystems(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        self.edsm_server = MagicMock()
        self.factions = MagicMock()
        self.edr_systems = EDRSystems(self.server, self.edsm_server, self.factions)

    def test_system_id_cache_miss_server_hit(self):
        # Setup
        star_system = "Sol"
        self.server.system.return_value = {"1": {"name": "Sol"}}
        
        # Test
        sid = self.edr_systems.system_id(star_system)
        
        # Verify
        self.server.system.assert_called_with(star_system, False, None)
        self.assertEqual(sid, "1")

    def test_system_id_cache_hit(self):
        # Setup
        star_system = "Sol"
        self.edr_systems.systems_cache.set("sol", {"1": {"name": "Sol"}})
        
        # Test
        sid = self.edr_systems.system_id(star_system)
        
        # Verify
        self.server.system.assert_not_called()
        self.assertEqual(sid, "1")

    def test_distance(self):
        # Setup
        self.edr_systems.systems_cache.set("sol", [{"coords": {"x": 0, "y": 0, "z": 0}}])
        self.edr_systems.systems_cache.set("barnard's star", [{"coords": {"x": 1, "y": 0, "z": 0}}])
        
        # Test
        dist = self.edr_systems.distance("Sol", "Barnard's Star")
        
        # Verify
        self.assertEqual(dist, 1.0)

    def test_describe_system(self):
        # Setup
        system_data = [{
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
        self.edr_systems.edsm_systems_cache.set("sol", system_data)
        self.edsm_server.system_value.return_value = {"estimatedValue": 1000, "estimatedValueMapped": 2000, "valuableBodies": []}
        
        # Test
        description = self.edr_systems.describe_system("Sol")
        
        # Verify
        self.assertTrue(any("Gvt: Democracy" in line for line in description))
        self.assertTrue(any("Alg: Federation" in line for line in description))
        self.assertTrue(any("Star: G [Fuel]" in line for line in description))

if __name__ == '__main__':
    unittest.main()
