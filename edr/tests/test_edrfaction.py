import config_tests
from unittest import TestCase, main
from edrfactions import EDRFaction

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
        
