import unittest
from unittest.mock import patch, MagicMock
from edrbountyhuntingstats import EDRBountyHuntingStats # EDR_INTERNAL
from edtime import EDTime # EDR_INTERNAL

class TestEDRBountyHuntingStats(unittest.TestCase):
    def setUp(self):
        # We need to mock EDTime to control "now"
        self.mock_time = MagicMock()
        self.mock_time.py_epoch_now.return_value = 1000
        
        # Patch EDTime in edrbountyhuntingstats module namespace if possible, 
        # but class usage might require patching where it is imported.
        # inspecting edrbountyhuntingstats.py: `from edr.edtime import EDTime`
        # so we patch `edrbountyhuntingstats.EDTime`
        
        self.patcher = patch('edrbountyhuntingstats.EDTime', self.mock_time)
        self.patcher.start()
        
        # Also need to mock EDRConfig to avoid file reads in __init__
        self.edr_config_patch = patch('edrbountyhuntingstats.EDR_CONFIG')
        self.mock_config = self.edr_config_patch.start()
        # Setup expected config return values
        self.mock_config.lru_max_size.return_value = 100
        self.mock_config.blips_max_age.return_value = 3600

        self.stats = EDRBountyHuntingStats()

    def tearDown(self):
        self.patcher.stop()
        self.edr_config_patch.stop()

    def test_init_reset(self):
        self.assertEqual(self.stats.max, 0)
        self.assertEqual(self.stats.min, float('inf'))
        self.assertEqual(self.stats.sum_scanned, 0)
        self.assertEqual(self.stats.scanned_nb, 0)

    def test_scanned(self):
        # Setup a scan event
        event = {
            "event": "ShipTargeted",
            "ScanStage": 3,
            "PilotName": "Pirate Lord",
            "PilotName_Localised": "Pirate Lord",
            "Bounty": 50000,
            "LegalStatus": "Wanted"
        }
        
        self.stats.scanned(event)
        
        self.assertEqual(self.stats.scanned_nb, 1)
        self.assertEqual(self.stats.sum_scanned, 50000)
        self.assertEqual(self.stats.max, 50000)
        self.assertEqual(self.stats.min, 50000)
        self.assertEqual(self.stats.bounty_average(), 50000)
        
        # Scan another one
        event2 = {
            "event": "ShipTargeted",
            "ScanStage": 3,
            "PilotName": "Minion",
            "PilotName_Localised": "Minion",
            "Bounty": 10000,
            "LegalStatus": "Wanted"
        }
        self.stats.scanned(event2)
        
        self.assertEqual(self.stats.scanned_nb, 2)
        self.assertEqual(self.stats.sum_scanned, 60000)
        self.assertEqual(self.stats.max, 50000)
        self.assertEqual(self.stats.min, 10000)
        self.assertEqual(self.stats.bounty_average(), 30000)

    def test_awarded(self):
        # Scan first (normally awarded comes after scan, but logic separates them partially)
        # But stats.efficiency needs time elapsed.
        self.mock_time.py_epoch_now.return_value = 2000 # 1000s elapsed
        
        event = {
            "event": "Bounty",
            "Rewards": [{"Reward": 50000}],
            "TotalReward": 50000
        }
        self.stats.awarded(event)
        
        self.assertEqual(self.stats.awarded_nb, 1)
        self.assertEqual(self.stats.sum_awarded, 50000)
        
        # Credits per hour: 50000 / (1000/3600) = 50000 / 0.2777 = 180000
        self.assertAlmostEqual(self.stats.credits_per_hour(), 180000.0)

if __name__ == '__main__':
    unittest.main()
