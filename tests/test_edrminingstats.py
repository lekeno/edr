
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
from edr.controllers.edrminingstats import EDRMiningStats, EDRMineralStats

class TestEDRMineralStats(unittest.TestCase):
    def test_prospected(self):
        stats = EDRMineralStats("Painite", "painite", "Pa")
        stats.prospected(50.0, 1000)
        
        self.assertEqual(stats.max, 50.0)
        self.assertEqual(stats.sum, 0.5)
        self.assertEqual(len(stats.prospectements), 1)
        
        stats.prospected(60.0, 1010)
        self.assertEqual(stats.max, 60.0)
        self.assertEqual(stats.sum, 1.1)

    def test_yield_average(self):
        stats = EDRMineralStats("Painite", "painite", "Pa")
        stats.sum = 1.0 # 100% total
        
        # If we prospected 2 asteroids
        avg = stats.yield_average(2)
        # (1.0 / 2) * 100 = 50.0%
        self.assertEqual(avg, 50.0)

class TestEDRMiningStats(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.controllers.edrminingstats.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.py_epoch_now.return_value = 1000.0
        
        self.i18n_patch = patch('edr.controllers.edrminingstats._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        # Mock the JSON load specifically
        # EDRMiningStats loads the JSON at class level effectively when module is imported or class is defined.
        # But wait, it's defined:
        # MINERALS_LUT = json.loads(open(...).read())
        # Since the class is already imported/defined when I import it in the test file, 
        # mocking open NOW won't change the class attribute if it was already executed.
        # However, the class attribute is used in __init__.
        # I can mock MINERALS_LUT directly on the class or instance if needed.
        # Or I can rely on the fact that if the import worked in the production code, the file exists.
        # But for unit/CI env, it might not. 
        # The imports are at top level in test file `from edr.controllers.edrminingstats ...`
        # So it executed already.
        # If I want to control it, I should have patched before import or patch the attribute after.
        pass

    def tearDown(self):
        self.time_patch.stop()
        self.i18n_patch.stop()

    def test_init(self):
        stats = EDRMiningStats()
        self.assertIsNotNone(stats.lmh)
        self.assertIsNotNone(stats.stats)

    def test_prospected_event(self):
        stats = EDRMiningStats()
        # Mock the LUT to ensure we have "painite"
        if "painite" not in stats.mineral_types_lut:
             stats.mineral_types_lut["painite"] = "Painite"
             # Code logic lowercases name to use as key, so we must use lowercase here
             stats.stats["painite"] = EDRMineralStats("Painite", "painite", "Pa")
             stats.of_interest["names"].add("painite")
             stats.of_interest["types"].add("painite")

        entry = {
            "event": "ProspectedAsteroid",
            "timestamp": "2022-01-01T12:00:00Z",
            "Content": "$AsteroidMaterialContent_High;",
            "Materials": [
                {"Name": "Painite", "Proportion": 45.0},
                {"Name": "Rock", "Proportion": 55.0}
            ],
            "Remaining": 100.0
        }
        
        # Configure the mock from setUp
        # timestamp parsing uses EDTime().from_journal_timestamp(...) and then .as_py_epoch()
        # We need EDTime() to return a mock that has as_py_epoch returning a float
        self.mock_time.return_value.as_py_epoch.return_value = 2000.0
        self.mock_time.py_epoch_now.return_value = 2000.0
        
        stats.prospected(entry)

        self.assertEqual(stats.prospected_nb, 1)
        self.assertEqual(stats.lmh["H"], 1)
        self.assertEqual(stats.stats["painite"].max, 45.0)

    def test_refined_event(self):
        stats = EDRMiningStats()
        # Ensure setup
        stats.of_interest["types"].add("painite")
        stats.mineral_types_lut["painite"] = "painite"
        stats.stats["painite"] = EDRMineralStats("Painite", "painite", "Pa")

        entry = {
            "event": "MiningRefined",
            "timestamp": "2022-01-01T12:30:00Z",
            "Type": "painite"
        }
        
        self.mock_time.return_value.as_py_epoch.return_value = 3800.0
        self.mock_time.py_epoch_now.return_value = 3800.0
        
        stats.refined(entry)

        self.assertEqual(stats.refined_nb, 1)
        self.assertEqual(stats.stats["painite"].refined_nb, 1)

    def test_item_per_hour(self):
        stats = EDRMiningStats()
        stats.start = 1000.0
        self.mock_time.py_epoch_now.return_value = 4600.0 # 1 hour later
        
        stats.refined_nb = 10
        iph = stats.item_per_hour()
        self.assertEqual(iph, 10.0)

    def test_depleted(self):
        stats = EDRMiningStats()
        entry = {
            "event": "ProspectedAsteroid",
            "Remaining": 0.0
        }
        stats.prospected(entry)
        self.assertTrue(stats.depleted)

if __name__ == '__main__':
    unittest.main()
