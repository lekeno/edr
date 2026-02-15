import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# sys.path injection removed
from edr.controllers.edrfactions import EDRFactions, EDRFaction, EDRMaterialOutcomes
from edr.utils.edtime import EDTime

class TestEDRMaterialOutcomes(unittest.TestCase):
    def test_combine_probabilities(self):
        outcomes = EDRMaterialOutcomes()
        # Chance 1: 50% chance, grade 1
        outcomes.chances_of("Iron", 1, 0.5)
        self.assertAlmostEqual(outcomes.outcomes["iron"]["likelihood"], 0.5)
        self.assertEqual(outcomes.outcomes["iron"]["grade"], 1)

        # Chance 2: another 50% chance, grade 1
        # Combined likelihood: 1 - (1-0.5)*(1-0.5) = 1 - 0.25 = 0.75
        outcomes.chances_of("Iron", 1, 0.5)
        self.assertAlmostEqual(outcomes.outcomes["iron"]["likelihood"], 0.75) 
        
        # Chance 3: High grade input
        # Grade logic: weighted average based on contribution to new probability mass?
        # The code refactored says:
        # grade = current_grade * (current_likelihood / base) + grade * (likelihood / base)
        # outcome["grade"] updates.
        
    def test_merge(self):
        o1 = EDRMaterialOutcomes()
        o1.chances_of("Iron", 1, 0.5)
        
        o2 = EDRMaterialOutcomes()
        o2.chances_of("Nickel", 2, 0.3)
        
        o1.merge(o2)
        self.assertIn("iron", o1.outcomes)
        self.assertIn("nickel", o1.outcomes)
        self.assertEqual(o1.outcomes["nickel"]["grade"], 2)


class TestEDRFaction(unittest.TestCase):
    def test_init_parsing(self):
        info = {
            "Name": "Faction A",
            "Allegiance": "Federation",
            "Government": "Democracy",
            "Influence": 0.1,
            "FactionState": "Boom",
            "ActiveStates": [{"State": "Boom"}, {"State": "CivilLiberty"}],
            "PendingStates": [{"State": "Expansion"}]
        }
        faction = EDRFaction(info)
        self.assertEqual(faction.name, "Faction A")
        self.assertEqual(faction.allegiance, "federation")
        self.assertEqual(faction.state, "boom")
        self.assertIn("boom", faction.active_states)
        self.assertIn("civil liberty", faction.active_states)
        self.assertIn("expansion", faction.pending_states)

    def test_chance_of_rare_mats(self):
        # Federation + Election = Proprietary Composites chance
        info = {
            "Name": "Fed Faction",
            "Allegiance": "Federation",
            "ActiveStates": [{"State": "Election"}]
        }
        faction = EDRFaction(info)
        self.assertTrue(faction.chance_of_rare_mats())
        
        # Independent + None = No rare mats usually (except managing "none" state logic?)
        info_none = {
            "Name": "Indy Faction",
            "Allegiance": "Independent",
            "ActiveStates": [{"State": "None"}]
        }
        faction_none = EDRFaction(info_none)
        # Independent 'None' is not in relevant states check
        self.assertFalse(faction_none.chance_of_rare_mats())

    def test_hge_yield_imperial_shielding(self):
        # Empire + None/Election/Outbreak = Imperial Shielding
        info = {
            "Name": "Imp Faction",
            "Allegiance": "Empire",
            "FactionState": "None", # Primary state
            "ActiveStates": [{"State": "None"}]
        }
        faction = EDRFaction(info)
        inventory = MagicMock()
        inventory.oneliner.side_effect = lambda x: x
        
        # Empire None -> Imperial Shielding
        yields = faction.hge_yield("High", 10000000, "none", inventory)
        # Note: EDRMaterialOutcomes uses lower case keys. oneliner returns as is from key.
        self.assertIn("imperial shielding", yields)

    def test_update_from_edsm(self):
        info = {
            "Name": "Test Faction",
            "Allegiance": "Federation",
            "Influence": 0.1
        }
        faction = EDRFaction(info)
        
        edsm_info = {
            "name": "Test Faction",
            "allegiance": "Alliance", # Changed
            "influence": 0.5, # Changed
            "state": "Boom",
            "activeStates": [{"state": "Boom"}],
            "lastUpdate": EDTime.py_epoch_now() + 100 # Future update
        }
        
        faction.updateFromEDSM(edsm_info)
        self.assertEqual(faction.allegiance, "alliance")
        self.assertEqual(faction.influence, 0.5)
        self.assertEqual(faction.state, "boom")

class TestEDRFactions(unittest.TestCase):
    def setUp(self):
        self.edsm_server = MagicMock()
        with patch('edr.controllers.edrfactions.LRUCache') as MockLRU:
             self.factions = EDRFactions(self.edsm_server)
             # Mock the internal caches
             self.factions.factions_cache = MagicMock()
             self.factions.factions_cache.get.return_value = None
             self.factions.controlling_factions_cache = MagicMock()
             self.factions.edsm_factions_cache = MagicMock()
             self.factions.edsm_factions_cache.get.return_value = None
             self.factions.edsm_factions_cache.has_key.return_value = False

    def test_process_jump_event(self):
        entry = {
            "event": "FSDJump",
            "StarSystem": "Sol",
            "Factions": [
                {"Name": "Mother Gaia", "Allegiance": "Independent", "Influence": 0.1}
            ]
        }
        
        # Mock get returning empty first, then set being called
        self.factions.factions_cache.get.return_value = {}
        
        self.factions.process_jump_event(entry)
        
        # Verify set was called with updated info
        args, _ = self.factions.factions_cache.set.call_args
        system, factions_map = args
        self.assertEqual(system, "sol")
        self.assertIn("mother gaia", factions_map)
        self.assertEqual(factions_map["mother gaia"].allegiance, "independent")

    def test_summarize_yields(self):
        # Mocking complex interaction with caches
        faction_a = EDRFaction({"Name": "F_A", "Allegiance": "Empire", "Influence": 0.5, "ActiveStates": [{"State": "None"}]})
        
        factions_map = {"f_a": faction_a}
        self.factions.factions_cache.get.return_value = factions_map
        self.factions.edsm_factions_cache.get.return_value = None # No EDSM backup needed for now
        self.factions.edsm_server.factions_in_system.return_value = None
        
        inventory = MagicMock()
        inventory.oneliner.side_effect = lambda x: x
        
        yields = self.factions.summarize_yields("Sol", "High", 10000000, inventory)
        # Empire None -> Imperial Shielding
        # Chance = Influence (0.5) * StateChance (1/1) = 0.5
        # Output string format: "{:.0f}%: {}".format(50, "Imperial Shielding")
        self.assertTrue(any("50%: Imperial Shielding" in y for y in yields))

if __name__ == '__main__':
    unittest.main()
