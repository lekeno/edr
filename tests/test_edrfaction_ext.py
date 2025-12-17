import config_tests
from unittest import TestCase, main
from edrfactions import EDRFaction
import edtime
import edrfactions

class TestEDRFactionExt(TestCase):
    def test_update_from_ed(self):
        sample = { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        faction = EDRFaction(sample)

        update_info = {
            "FactionState": "Boom",
            "Influence": 0.05,
            "Allegiance": "Federation",
            "ActiveStates": [ { "State": "Boom" } ],
            "timestamp": edtime.EDTime().as_journal_timestamp()
        }

        faction.updateFromED(update_info)
        self.assertEqual(faction.state, "boom")
        self.assertEqual(faction.influence, 0.05)
        self.assertEqual(faction.allegiance, "federation")
        self.assertEqual(faction.active_states, set(['boom']))

    def test_update_from_edsm(self):
        sample = { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000, "timestamp": "2020-01-01T00:00:00Z" }
        faction = EDRFaction(sample)

        update_info = {
            "state": "Boom",
            "influence": 0.05,
            "allegiance": "Federation",
            "activeStates": [ { "state": "Boom" } ],
            "lastUpdate": edtime.EDTime.py_epoch_now()
        }

        faction.updateFromEDSM(update_info)
        self.assertEqual(faction.state, "boom")
        self.assertEqual(faction.influence, 0.05)
        self.assertEqual(faction.allegiance, "federation")
        self.assertEqual(faction.active_states, set(['boom']))

    def test_chance_of_rare_mats(self):
        sample = { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        faction = EDRFaction(sample)
        self.assertFalse(faction.chance_of_rare_mats())

        faction.active_states = set(['investment'])
        self.assertFalse(faction.chance_of_rare_mats())

        faction.active_states = set(['outbreak', 'war', 'boom', 'civil unrest', 'civil war', 'famine', 'election', 'none'])
        self.assertTrue(faction.chance_of_rare_mats())

        faction.active_states = set(['outbreak'])
        faction.allegiance = 'empire'
        self.assertTrue(faction.chance_of_rare_mats())

        faction.active_states = set(['none'])
        faction.allegiance = 'federation'
        self.assertTrue(faction.chance_of_rare_mats())

        faction.active_states = set(['election'])
        faction.allegiance = 'empire'
        self.assertTrue(faction.chance_of_rare_mats())

class MockEDSMServer(object):
    def factions_in_system(self, system_name):
        return {
            "name": system_name,
            "factions": [
                {
                    "name": "Phekda Society",
                    "state": "None",
                    "allegiance": "Independent",
                    "influence": 0.041,
                    "activeStates": [],
                    "lastUpdate": edtime.EDTime.py_epoch_now()
                }
            ]
        }

class TestEDRFactions(TestCase):
    def test_process(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        factions_data = [
            { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        ]
        factions.process(factions_data, "Phekda")
        phekda_factions = factions.factions_cache.get("phekda")
        self.assertIsNotNone(phekda_factions)
        self.assertIn("phekda society", phekda_factions)

    def test_get_all(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        phekda_factions = factions.get_all("Phekda")
        self.assertIsNotNone(phekda_factions)
        self.assertIn("phekda society", phekda_factions)

    def test_process_jump_event(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        jump_event = {
            "event": "FSDJump",
            "StarSystem": "Phekda",
            "Factions": [
                { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
            ]
        }
        factions.process_jump_event(jump_event)
        phekda_factions = factions.factions_cache.get("phekda")
        self.assertIsNotNone(phekda_factions)
        self.assertIn("phekda society", phekda_factions)

    def test_process_fc_jump_event(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        jump_event = {
            "event": "CarrierJump",
            "StarSystem": "Phekda",
            "Factions": [
                { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
            ]
        }
        factions.process_fc_jump_event(jump_event)
        phekda_factions = factions.factions_cache.get("phekda")
        self.assertIsNotNone(phekda_factions)
        self.assertIn("phekda society", phekda_factions)

    def test_process_location_event(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        location_event = {
            "event": "Location",
            "StarSystem": "Phekda",
            "Factions": [
                { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
            ]
        }
        factions.process_location_event(location_event)
        phekda_factions = factions.factions_cache.get("phekda")
        self.assertIsNotNone(phekda_factions)
        self.assertIn("phekda society", phekda_factions)

    def test_get(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        factions_data = [
            { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        ]
        factions.process(factions_data, "Phekda")
        faction = factions.get("Phekda Society", "Phekda")
        self.assertIsNotNone(faction)
        self.assertEqual(faction.name, "Phekda Society")

    def test_get_controlling_faction_allegiance(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        factions_data = [
            { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        ]
        factions.process(factions_data, "Phekda")
        self.assertIsNone(factions.getControllingFactionAllegiance("Phekda"))

    def test_get_controlling_faction_state(self):
        edsm_server = MockEDSMServer()
        factions = edrfactions.EDRFactions(edsm_server)
        factions_data = [
            { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        ]
        factions.process(factions_data, "Phekda")
        state, last_updated = factions.getControllingFactionState("Phekda")
        self.assertIsNone(state)
        self.assertIsNone(last_updated)


if __name__ == '__main__':
    main()
