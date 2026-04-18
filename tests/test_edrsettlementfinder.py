
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrsettlementfinder import EDRSettlementFinder

class TestEDRSettlementFinder(unittest.TestCase):
    def setUp(self):
        self.edr_systems = MagicMock()
        self.checker = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRSettlementFinder("Sol", self.checker, self.edr_systems, self.callback)
        
        self.i18n_patch = patch('edr.controllers.edrsettlementfinder._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        self.log_patch = patch('edr.controllers.edrsettlementfinder.EDR_LOG')
        self.mock_log = self.log_patch.start()

    def tearDown(self):
        self.i18n_patch.stop()
        self.log_patch.stop()

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 50)
        self.assertEqual(self.finder.sc_distance, 1500)

    def test_nearby_prime_found(self):
        system = {"name": "Sol", "requirePermit": False}
        settlement = {"name": "Galileo", "distanceToArrival": 100}
        
        self.edr_systems.system.return_value = [system]
        self.edr_systems.are_settlements_stale.return_value = False
        self.edr_systems.stations_in_system.return_value = [settlement]
        self.edr_systems.closest_settlement.return_value = settlement
        
        self.checker.check_system.return_value = True
        self.checker.check_settlement.return_value = True
        self.checker.is_ambiguous.return_value = False
        
        result = self.finder.nearby()
        self.assertEqual(result, settlement)

    def test_nearby_alt_found(self):
        # Setup: Prime candidate not found (e.g. too far), but alt found (ambiguous or far)
        # Here we test "too far" which should put into alt?
        # Code: if check_sc_distance and not ambiguous -> prime. else -> alt.
        
        system = {"name": "Sol"}
        settlement = {"name": "Far Out", "distanceToArrival": 10000}
        
        self.edr_systems.system.return_value = [system]
        self.edr_systems.stations_in_system.return_value = [settlement]
        self.edr_systems.closest_settlement.side_effect = lambda sys, cand: sys['settlement']
        
        self.checker.check_system.return_value = True
        self.checker.check_settlement.return_value = True
        self.checker.is_ambiguous.return_value = False
        
        result = self.finder.nearby()
        self.assertEqual(result, settlement)
        # Since it's far (10000 > 1500), it goes to alt.
        # Since prime is None, it returns alt.

    def test_closest_matching_settlement_state_filtering(self):
        s1 = {"name": "S1", "distanceToArrival": 100, "controllingFaction": {"name": "Faction1"}}
        s2 = {"name": "S2", "distanceToArrival": 200, "controllingFaction": {"name": "Faction2"}}
        
        self.checker.check_settlement.return_value = True
        
        f1 = MagicMock()
        f1.state = "War"
        f2 = MagicMock()
        f2.state = "Boom"
        
        self.edr_systems.faction_in_system.side_effect = lambda f, s: f1 if f == "Faction1" else f2
        
        # Test ignore states
        self.finder.ignore_states(["War"])
        result = self.finder.closest_matching_settlement([s1, s2], "Sol")
        self.assertEqual(result, s2)
        
        # Test require states
        self.finder.ignore_states([])
        self.finder.require_states(["War"])
        result = self.finder.closest_matching_settlement([s1, s2], "Sol")
        self.assertEqual(result, s1)

    def test_closest_matching_settlement_distance(self):
        s1 = {"name": "S1", "distanceToArrival": 500}
        s2 = {"name": "S2", "distanceToArrival": 100}
        
        self.checker.check_settlement.return_value = True
        self.edr_systems.faction_in_system.return_value = None # No faction info, ignores state check
        
        result = self.finder.closest_matching_settlement([s1, s2], "Sol")
        self.assertEqual(result, s2)

    def test_ambiguous_settlement(self):
        system = {"name": "Sol"}
        settlement = {"name": "Ambiguous", "distanceToArrival": 100}
        
        self.edr_systems.system.return_value = [system]
        self.edr_systems.stations_in_system.return_value = [settlement]
        self.edr_systems.closest_settlement.return_value = settlement
        
        self.checker.check_system.return_value = True
        self.checker.check_settlement.return_value = True
        self.checker.is_ambiguous.return_value = True
        
        result = self.finder.nearby()
        self.assertEqual(result, settlement)
        self.assertIn("comment", result)
        self.assertIn("[Confidence: LOW]", result["comment"])

if __name__ == '__main__':
    unittest.main()
