
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrfactions import EDRFaction, EDRFactions, EDRMaterialOutcomes

class TestEDRMaterialOutcomes(unittest.TestCase):
    def test_basic_probabilities(self):
        outcomes = EDRMaterialOutcomes()
        outcomes.chances_of("Iron", 1, 0.5)
        
        grade, likelihood = outcomes.grade_and_likelihood("Iron")
        self.assertEqual(grade, 1)
        self.assertEqual(likelihood, 0.5)

    def test_combine_probabilities(self):
        outcomes = EDRMaterialOutcomes()
        outcomes.chances_of("Iron", 1, 0.5)
        outcomes.chances_of("Iron", 1, 0.5)
        
        grade, likelihood = outcomes.grade_and_likelihood("Iron")
        # 1 - (1-0.5)*(1-0.5) = 1 - 0.25 = 0.75
        self.assertEqual(likelihood, 0.75)


class TestEDRFaction(unittest.TestCase):
    def test_init_from_ed(self):
        info = {
            "Name": "Test Faction",
            "Allegiance": "Federation",
            "Influence": 0.5,
            "FactionState": "Election",
            "Government": "Democracy",
            "ActiveStates": [{"State": "Boom"}],
            "PendingStates": [{"State": "CivilWar"}],
            "RecoveringStates": [{"State": "Outbreak"}]
        }
        faction = EDRFaction(info)
        self.assertEqual(faction.name, "Test Faction")
        self.assertEqual(faction.allegiance, "federation")
        self.assertEqual(faction.state, "election")
        self.assertIn("boom", faction.active_states)
        self.assertIn("civil war", faction.pending_states)
        self.assertIn("outbreak", faction.recovering_states)

    def test_simplified_state(self):
        self.assertEqual(EDRFaction._simplified_state("FactionState_CivilWar;"), "civil war")
        self.assertEqual(EDRFaction._simplified_state("$factionstate_Boom;"), "boom")

class TestEDRFactions(unittest.TestCase):
    def setUp(self):
        self.edsm_server = MagicMock()
        self.edr_config_patch = patch('edr.controllers.edrfactions.EDR_CONFIG')
        self.edr_config = self.edr_config_patch.start()
        self.edr_config.lru_max_size.return_value = 100
        self.edr_config.factions_max_age.return_value = 3600
        self.edr_config.edsm_factions_max_age.return_value = 3600
        
        # Patch LRUCache to avoid disk access
        self.lru_patch = patch('edr.controllers.edrfactions.LRUCache')
        self.MockLRU = self.lru_patch.start()
        self.MockLRU.load.return_value = MagicMock() 
        
        self.factions_manager = EDRFactions(self.edsm_server)
        self.factions_manager.factions_cache = MagicMock()
        self.factions_manager.controlling_factions_cache = MagicMock()
        self.factions_manager.edsm_factions_cache = MagicMock()

    def tearDown(self):
        self.edr_config_patch.stop()
        self.lru_patch.stop()

    def test_process_jump_event(self):
        entry = {
            "event": "FSDJump",
            "StarSystem": "Test System",
            "Factions": [
                {"Name": "Faction A", "Influence": 0.1, "Allegiance": "Empire"},
                {"Name": "Faction B", "Influence": 0.9, "Allegiance": "Independent"}
            ]
        }
        
        # Mock cache to return empty dict initially
        self.factions_manager.factions_cache.get.return_value = {}
        
        self.factions_manager.process_jump_event(entry)
        
        # Verification
        self.factions_manager.factions_cache.set.assert_called()
        args, _ = self.factions_manager.factions_cache.set.call_args
        system_name = args[0]
        factions_dict = args[1]
        
        self.assertEqual(system_name, "test system")
        self.assertIn("faction a", factions_dict)
        self.assertIn("faction b", factions_dict)
        self.assertEqual(factions_dict["faction a"].influence, 0.1)

    def test_process_station_settlement_event(self):
        # This tests the potential bug in __process_station_settlement_event regarding self.state
        entry = {
            "event": "Docked",
            "timestamp": "2023-01-01T12:00:00Z",
            "StationFaction": {"Name": "Faction A", "FactionState": "Boom"},
            "StationAllegiance": "Federation",
            "StationGovernment": "$government_Democracy;"
        }
        
        # Setup existing faction in cache
        faction_a = EDRFaction({"Name": "Faction A", "Influence": 0.5})
        self.factions_manager.factions_cache.get.return_value = {"faction a": faction_a}
        
        # Ensure EDSM lookups fail so it uses local cache
        self.factions_manager.edsm_factions_cache.has_key.return_value = False
        self.factions_manager.edsm_factions_cache.get.return_value = None
        
        self.factions_manager.process_docking_event(entry, "Test System")
        
        # Should now have updated state
        self.assertEqual(faction_a.state, "Boom")
        self.assertIn("Boom", faction_a.active_states)

if __name__ == '__main__':
    unittest.main()
