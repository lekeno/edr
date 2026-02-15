
from unittest import TestCase, main
from edr.controllers.edrfactions import EDRFaction

class TestEDRFaction(TestCase):
    def test_constructor(self):
        sample = { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        faction = EDRFaction(sample)
        self.assertEqual(faction.name, "Phekda Society")
        self.assertEqual(faction.state, "none")
        self.assertEqual(faction.allegiance, "independent")
        self.assertAlmostEqual(faction.influence, 0.041000)
        self.assertEqual(faction.active_states, set(['none']))
        self.assertFalse(faction.chance_of_rare_mats())

    def test_updateFromED(self):
        sample = { "Name":"Phekda Society", "FactionState":"None", "Government":"Anarchy", "Influence":0.041000, "Allegiance":"Independent", "MyReputation":0.000000 }
        faction = EDRFaction(sample)
        
        update = { "Name":"Phekda Society", "FactionState":"Boom", "ActiveStates":[{"State":"Boom"}], "Influence":0.05, "Allegiance":"Alliance" }
        faction.updateFromED(update)

        self.assertEqual(faction.state, "boom")
        self.assertAlmostEqual(faction.influence, 0.05)
        self.assertEqual(faction.allegiance, "alliance")
        self.assertEqual(faction.active_states, set(["boom"]))

    def test_chance_of_rare_mats(self):
        # Imperial Shielding: Empire + None/Election/Outbreak
        imp_none = { "Name":"Imp", "FactionState":"None", "Government":"Patronage", "Influence":0.1, "Allegiance":"Empire" }
        self.assertTrue(EDRFaction(imp_none).chance_of_rare_mats())

        imp_election = { "Name":"Imp", "FactionState":"Election", "Government":"Patronage", "Influence":0.1, "Allegiance":"Empire" }
        self.assertTrue(EDRFaction(imp_election).chance_of_rare_mats())

        # Core Dynamics Composites: Federation + None/Election
        fed_none = { "Name":"Fed", "FactionState":"None", "Government":"Democracy", "Influence":0.1, "Allegiance":"Federation" }
        self.assertTrue(EDRFaction(fed_none).chance_of_rare_mats())

        # Improvised Components: Independent/Alliance + Civil Unrest
        ind_unrest = { "Name":"Ind", "FactionState":"CivilUnrest", "Government":"Dictatorship", "Influence":0.1, "Allegiance":"Independent" }
        self.assertTrue(EDRFaction(ind_unrest).chance_of_rare_mats())

        # Boring faction
        boring = { "Name":"Boring", "FactionState":"None", "Government":"Democracy", "Influence":0.1, "Allegiance":"Independent" }
        self.assertFalse(EDRFaction(boring).chance_of_rare_mats())

    def test_active_states(self):
        sample = { "Name":"MultiState", "FactionState":"Boom", "ActiveStates":[{"State":"War"}, {"State":"Election"}], "Influence":0.1, "Allegiance":"Independent" }
        faction = EDRFaction(sample)
        # Main state is included in active states
        expected_states = set(["boom", "war", "election"])
        self.assertEqual(faction.active_states, expected_states)

if __name__ == '__main__':
    main()
