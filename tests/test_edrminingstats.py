import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edr.edrminingstats import EDRMiningStats, EDRMineralStats

class TestEDRMiningStats(unittest.TestCase):
    def setUp(self):
        self.edtime_patch = patch('edr.edrminingstats.EDTime')
        self.mock_edtime = self.edtime_patch.start()
        self.mock_edtime.py_epoch_now.return_value = 1000

        self.mining_data = {
            "painite": {"name": "painite", "type": "painite", "symbol": "P"},
            "platinum": {"name": "platinum", "type": "platinum", "symbol": "Pt"}
        }
        
        self.lut_patch = patch.dict(EDRMiningStats.MINERALS_LUT, self.mining_data, clear=True)
        self.lut_patch.start()
        
        self.mining_stats = EDRMiningStats()

    def tearDown(self):
        self.lut_patch.stop()
        self.edtime_patch.stop()

    def test_init_reset(self):
        self.assertEqual(self.mining_stats.prospected_nb, 0)
        self.assertEqual(self.mining_stats.refined_nb, 0)
        self.assertFalse(self.mining_stats.depleted)
        self.assertEqual(len(self.mining_stats.stats), 2)
        self.mining_stats.prospected_nb = 10
        self.mining_stats.reset()
        self.assertEqual(self.mining_stats.prospected_nb, 0)

    def test_prospected_low_content(self):
        entry = {
            "timestamp": "2023-01-01T12:00:00Z",
            "event": "ProspectedAsteroid",
            "Content": "$AsteroidMaterialContent_Low;",
            "Materials": [
                {"Name": "Painite", "Proportion": 20.0},
                {"Name": "Other", "Proportion": 10.0}
            ],
            "Remaining": 100
        }
        
        # Setup timestamp mock for internal call
        mock_timestamp = MagicMock()
        mock_timestamp.as_py_epoch.return_value = 1000
        self.mock_edtime.return_value = mock_timestamp

        self.mining_stats.prospected(entry)
        
        self.assertEqual(self.mining_stats.prospected_nb, 1)
        self.assertEqual(self.mining_stats.lmh["L"], 1)
        self.assertEqual(self.mining_stats.stats["painite"].distribution["bins"][5], 1) # 20% index
        self.assertEqual(self.mining_stats.last["raw"], "L")

    def test_prospected_depleted(self):
        entry = {
             "event": "ProspectedAsteroid",
             "Remaining": 0
        }
        self.mining_stats.prospected(entry)
        self.assertTrue(self.mining_stats.depleted)

    def test_refined(self):
        entry = {
            "timestamp": "2023-01-01T12:05:00Z",
            "event": "MiningRefined",
            "Type": "painite"
        }
        mock_timestamp = MagicMock()
        mock_timestamp.as_py_epoch.return_value = 1300 # 5 mins later
        self.mock_edtime.return_value = mock_timestamp

        self.mining_stats.refined(entry)
        
        self.assertEqual(self.mining_stats.refined_nb, 1)
        self.assertEqual(self.mining_stats.stats["painite"].refined_nb, 1)

    def test_refined_ignored(self):
        entry = {
            "timestamp": "2023-01-01T12:05:00Z",
            "event": "MiningRefined",
            "Type": "gold" # Not in our mock data
        }
        mock_timestamp = MagicMock()
        mock_timestamp.as_py_epoch.return_value = 1300
        self.mock_edtime.return_value = mock_timestamp

        self.mining_stats.refined(entry)
        self.assertEqual(self.mining_stats.refined_nb, 0)

    def test_yield_average(self):
        # 1. Prospect 100% Painite
        entry1 = {
             "timestamp": "2023-01-01T12:00:00Z", "event": "ProspectedAsteroid",
             "Content": "$AsteroidMaterialContent_High;",
             "Materials": [{"Name": "Painite", "Proportion": 50.0}],
             "Remaining": 100
        }
        
        mock_timestamp = MagicMock()
        mock_timestamp.as_py_epoch.return_value = 1000
        self.mock_edtime.return_value = mock_timestamp

        self.mining_stats.prospected(entry1)
        
        # 2. Prospect 0% Painite (implied by absence, or just another rock)
        entry2 = {
             "timestamp": "2023-01-01T12:01:00Z", "event": "ProspectedAsteroid",
             "Content": "$AsteroidMaterialContent_Low;",
             "Materials": [{"Name": "Platinum", "Proportion": 20.0}],
             "Remaining": 100
        }
        self.mining_stats.prospected(entry2)

        # Average yield for Painite: (50 + 0) / 2 = 25.0
        
        self.assertEqual(self.mining_stats.stats["painite"].yield_average(2), 25.0)

    def test_item_per_hour(self):
        # Start at 1000
        self.mining_stats.start = 1000
        self.mock_edtime.py_epoch_now.return_value = 4600 # 3600 seconds later (1 hour)
        
        self.mining_stats.refined_nb = 10
        iph = self.mining_stats.item_per_hour()
        self.assertAlmostEqual(iph, 10.0)

if __name__ == '__main__':
    unittest.main()
