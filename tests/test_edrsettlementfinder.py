
import unittest
from unittest.mock import MagicMock, patch
from edrsettlementfinder import EDRSettlementFinder

class TestEDRSettlementFinder(unittest.TestCase):
    def setUp(self):
        self.checker = MagicMock()
        self.edr_systems = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRSettlementFinder("Sol", self.checker, self.edr_systems, self.callback)
        # Mock translation
        self.patcher = patch('edrsettlementfinder._', side_effect=lambda x: x)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 50)

    def test_search_prime_candidate(self):
        self.edr_systems.system.return_value = [{"name": "Sol", "requirePermit": False}]
        self.checker.check_system.return_value = True
        self.edr_systems.are_settlements_stale.return_value = False
        
        settlement = {"name": "Outpost", "distanceToArrival": 100}
        self.edr_systems.stations_in_system.return_value = [settlement]
        self.checker.check_settlement.return_value = True
        self.checker.is_ambiguous.return_value = False # High confidence
        
        self.edr_systems.closest_settlement.return_value = settlement
        
        result = self.finder.nearby()
        self.assertEqual(result, settlement)

    def test_search_alt_candidate_ambiguous(self):
        # Current system fails
        self.edr_systems.system.return_value = None
        
        # Neighbor system
        self.edr_systems.systems_within_radius.return_value = [{"name": "Neighbor"}]
        self.checker.check_system.return_value = True
        
        settlement = {"name": "Outpost", "distanceToArrival": 100}
        self.edr_systems.stations_in_system.return_value = [settlement]
        self.checker.check_settlement.return_value = True
        self.checker.is_ambiguous.return_value = True # Ambiguous -> Alt with Low Confidence check
        
        self.edr_systems.closest_settlement.return_value = settlement
        
        result = self.finder.nearby()
        self.assertEqual(result, settlement)
        self.assertIn("[Confidence: LOW]", settlement['comment'])

    def test_faction_state_filtering(self):
        self.finder.ignore_states(['War'])
        
        settlement_war = {"name": "WarZone", "controllingFaction": {"name": "Warmongers"}, "distanceToArrival": 100}
        settlement_peace = {"name": "PeaceTime", "controllingFaction": {"name": "Peacemakers"}, "distanceToArrival": 200}
        
        # Mock faction lookup
        war_faction = MagicMock()
        war_faction.state = 'War'
        peace_faction = MagicMock()
        peace_faction.state = 'None'
        
        self.edr_systems.faction_in_system.side_effect = lambda name, sys: war_faction if name == "Warmongers" else peace_faction
        self.checker.check_settlement.return_value = True
        
        result = self.finder.closest_matching_settlement([settlement_war, settlement_peace], "Sol")
        self.assertEqual(result, settlement_peace) # Should skip war settlement

if __name__ == '__main__':
    unittest.main()
