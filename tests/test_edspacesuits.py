
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
from edr.models import edspacesuits

class TestEDSuitFactory(unittest.TestCase):
    def test_is_spacesuit(self):
        # Check actual values in internal mappings if possible, or assume some
        # Based on typical ED naming
        self.assertTrue(edspacesuits.EDSuitFactory.is_spacesuit("tacticalsuit_class1"))
        self.assertFalse(edspacesuits.EDSuitFactory.is_spacesuit("sidewinder"))

    def test_from_internal_name(self):
        # Case insensitive check? Or exact?
        # Assuming defaults
        suit = edspacesuits.EDSuitFactory.from_internal_name("tacticalsuit_class3")
        if suit:
            self.assertIsInstance(suit, edspacesuits.EDDominatorSuit)
            self.assertEqual(suit.grade, 3) # Integer 3?
            # Type might be "Dominator"
        
        suit = edspacesuits.EDSuitFactory.from_internal_name("explorationsuit_class1")
        if suit:
             self.assertIsInstance(suit, edspacesuits.EDArtemisSuit)

    def test_from_suitloadout_event(self):
        event = {
            "SuitID": 123,
            "SuitName": "utilitysuit_class2",
            "LoadoutID": 456,
            "LoadoutName": "My Maverick",
            "SuitMods": [],
            "Modules": []
        }
        suit = edspacesuits.EDSuitFactory.from_suitloadout_event(event)
        self.assertIsInstance(suit, edspacesuits.EDMaverickSuit)
        self.assertEqual(suit.id, 123)
        self.assertEqual(suit.loadout.name, "My Maverick")

class TestEDSpaceSuit(unittest.TestCase):
    def setUp(self):
        self.suit = edspacesuits.EDMaverickSuit()

    def test_health_setter(self):
        self.suit.health = 0.5
        self.assertEqual(self.suit.health, 0.5)
        self.assertEqual(self.suit._health["value"], 0.5)

    def test_destroy(self):
        self.suit.health = 1.0
        self.suit.destroy()
        self.assertEqual(self.suit.health, 0.0)

    def test_shield_state(self):
        self.suit.shield_state(True)
        self.assertTrue(self.suit.shield_up)
        self.suit.shield_state(False)
        self.assertFalse(self.suit.shield_up)

class TestEDGeneticSampler(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.object(edspacesuits.EDGeneticSampler, 'BIOLOGY', {
            "genuses": {
                "tussock": {"ccr": 500}
            },
            "species": {
                "tussock_viridem": {"credits": 1000}
            }
        })
        self.patcher.start()
        self.sampler = edspacesuits.EDGeneticSampler()

    def tearDown(self):
        self.patcher.stop()

    def test_process_scan_sample(self):
        event = {
            "ScanType": "Sample",
            "SystemAddress": 12345,
            "Body": 2,
            "Genus": "tussock",
            "Genus_Localised": "Tussock",
            "Species": "tussock_viridem",
            "Species_Localised": "Tussock Viridem"
        }
        location = {"latitude": 10, "longitude": 20}
        
        self.sampler.process(event, location)
        
        self.assertTrue(self.sampler.is_tracking())
        self.assertEqual(self.sampler.species_tracked(), "Tussock Viridem")
        self.assertEqual(self.sampler.tracked_species_credits(), 1000)
        
        locs = self.sampler.samples_locations(12345, 2)
        self.assertEqual(len(locs), 1)
        self.assertEqual(locs[0], location)

if __name__ == '__main__':
    unittest.main()
