
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edentities import EDRCrew, EDRPowerplay, EDPilot, EDFineOrBounty
from edr.utils.edtime import EDTime

class TestEDRCrew(unittest.TestCase):
    def test_crew_management(self):
        crew = EDRCrew("Captain")
        self.assertTrue(crew.is_captain("Captain"))
        
        self.assertTrue(crew.add("CrewMember1"))
        self.assertFalse(crew.add("CrewMember1")) # Already present
        self.assertIn("CrewMember1", crew.all_members())
        
        self.assertTrue(crew.remove("CrewMember1"))
        self.assertFalse(crew.remove("CrewMember1")) # Already removed
        
        crew.disband()
        self.assertEqual(len(crew.all_members()), 0)
        self.assertIsNone(crew.captain)

class TestEDRPowerplay(unittest.TestCase):
    def test_powerplay_affiliation(self):
        # Aisling Duval (Empire) vs Zachary Hudson (Federation) -> Enemy
        pp_aisling = EDRPowerplay("aisling_duval", 0)
        self.assertTrue(pp_aisling.is_enemy("zachary_hudson"))
        
        # Aisling Duval (Empire) vs A. Lavigny-Duval (Empire) -> Not Enemy
        self.assertFalse(pp_aisling.is_enemy("a_lavigny-duval"))
        
        # Independent vs Unknown
        pp_independent = EDRPowerplay("archon_delaine", 0) # treated as None affiliation in map
        self.assertTrue(pp_independent.is_enemy("zachary_hudson"))

    def test_pretty_print(self):
        pp = EDRPowerplay("aisling_duval", 0)
        self.assertEqual(pp.pretty_print(), "Aisling")
        
        pp_unknown = EDRPowerplay("UnknownPower", 0)
        self.assertEqual(pp_unknown.pretty_print(), "UnknownPower")

class TestEDFineOrBounty(unittest.TestCase):
    def setUp(self):
        self.mock_config_patch = patch('edr.models.edentities.EDR_CONFIG')
        self.mock_config = self.mock_config_patch.start()
        self.mock_config.intel_bounty_threshold.return_value = 10000

    def tearDown(self):
        self.mock_config_patch.stop()

    def test_is_significant(self):
        bounty = EDFineOrBounty(5000)
        self.assertFalse(bounty.is_significant())
        
        bounty = EDFineOrBounty(15000)
        self.assertTrue(bounty.is_significant())

    def test_addition(self):
        bounty = EDFineOrBounty(1000)
        bounty += 500
        self.assertEqual(bounty.value, 1500)

class TestEDPilot(unittest.TestCase):
    @patch('edr.models.edentities.EDVehicleFactory')
    def test_pilot_initialization(self, mock_factory):
        pilot = EDPilot("Cmdr Name", 5)
        self.assertEqual(pilot.name, "Cmdr Name")
        self.assertEqual(pilot.rank, 5)
        self.assertFalse(pilot.in_normal_space()) # Default location is empty/unknown

    @patch('edr.models.edentities.EDVehicleFactory')
    def test_pilot_location(self, mock_factory):
        pilot = EDPilot("Cmdr Name", 5)
        pilot.star_system = "Sol"
        self.assertEqual(pilot.star_system, "Sol")
        
        pilot.place = "Earth"
        self.assertEqual(pilot.place, "Earth")

    def test_killed(self):
        pilot = EDPilot("Cmdr Test", 1)
        pilot.wanted = True
        pilot.bounties = {"Faction": 1000}
        
        pilot.killed()
        
        self.assertTrue(pilot.destroyed)
        self.assertFalse(pilot.wanted)
        self.assertEqual(len(pilot.bounties), 0)

if __name__ == '__main__':
    unittest.main()
