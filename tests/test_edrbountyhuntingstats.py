
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrbountyhuntingstats import EDRBountyHuntingStats

class TestEDRBountyHuntingStats(unittest.TestCase):
    def setUp(self):
        self.config_patch = patch('edr.controllers.edrbountyhuntingstats.EDR_CONFIG')
        self.mock_config = self.config_patch.start()
        self.mock_config.lru_max_size.return_value = 100
        self.mock_config.blips_max_age.return_value = 600

        self.time_patch = patch('edr.controllers.edrbountyhuntingstats.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.py_epoch_now.return_value = 1000.0

    def tearDown(self):
        self.config_patch.stop()
        self.time_patch.stop()

    def test_init(self):
        stats = EDRBountyHuntingStats()
        self.assertEqual(stats.max, 0)
        self.assertEqual(stats.min, float('inf'))
        self.assertEqual(stats.sum_scanned, 0)
        self.assertEqual(stats.scanned_nb, 0)
        self.assertEqual(stats.awarded_nb, 0)

    def test_reset(self):
        stats = EDRBountyHuntingStats()
        stats.sum_scanned = 1000
        stats.scanned_nb = 5
        
        stats.reset()
        self.assertEqual(stats.sum_scanned, 0)
        self.assertEqual(stats.scanned_nb, 0)
        self.assertEqual(stats.min, float('inf'))

    def test_scanned_valid(self):
        stats = EDRBountyHuntingStats()
        entry = {
            "event": "ShipTargeted",
            "ScanStage": 3,
            "PilotName": "BadGuy",
            "PilotName_Localised": "Bad Guy",
            "LegalStatus": "Wanted",
            "Bounty": 50000
        }
        
        # First scan
        stats.scanned(entry)
        self.assertEqual(stats.scanned_nb, 1)
        self.assertEqual(stats.sum_scanned, 50000)
        self.assertEqual(stats.max, 50000)
        self.assertEqual(stats.min, 50000)
        self.assertEqual(len(stats.scans), 1)
        
        # Second scan, higher bounty
        entry2 = entry.copy()
        entry2["Bounty"] = 100000
        entry2["PilotName"] = "WorseGuy"
        
        stats.scanned(entry2)
        self.assertEqual(stats.scanned_nb, 2)
        self.assertEqual(stats.sum_scanned, 150000)
        self.assertEqual(stats.max, 100000)
        self.assertEqual(stats.min, 50000)

    def test_scanned_invalid(self):
        stats = EDRBountyHuntingStats()
        
        # Wrong event
        stats.scanned({"event": "OtherEvent"})
        self.assertEqual(stats.scanned_nb, 0)
        
        # Low scan stage
        stats.scanned({"event": "ShipTargeted", "ScanStage": 1})
        self.assertEqual(stats.scanned_nb, 0)
        
        # No pilot name
        stats.scanned({"event": "ShipTargeted", "ScanStage": 3})
        self.assertEqual(stats.scanned_nb, 0)
        
        # Zero bounty
        stats.scanned({
            "event": "ShipTargeted", 
            "ScanStage": 3, 
            "PilotName": "BrokeGuy", 
            "LegalStatus": "Wanted",
            "Bounty": 0
        })
        self.assertEqual(stats.scanned_nb, 0)

    def test_scanned_duplicate(self):
        stats = EDRBountyHuntingStats()
        entry = {
            "event": "ShipTargeted",
            "ScanStage": 3,
            "PilotName": "BadGuy",
            "LegalStatus": "Wanted",
            "Bounty": 50000
        }
        
        stats.scanned(entry)
        self.assertEqual(stats.scanned_nb, 1)
        
        # Same pilot, same bounty = duplicate
        stats.scanned(entry)
        self.assertEqual(stats.scanned_nb, 1)
        
        # Same pilot, different bounty = update?
        # Code logic: 
        # last_scan = self.scans_cache.get(raw_pilot_name)
        # return (entry["LegalStatus"] == last_scan["LegalStatus"]) and (entry.get("Bounty", 0) == last_scan.get("Bounty",0))
        
        entry_diff = entry.copy()
        entry_diff["Bounty"] = 60000
        stats.scanned(entry_diff)
        self.assertEqual(stats.scanned_nb, 2)

    def test_awarded(self):
        stats = EDRBountyHuntingStats()
        entry = {
            "event": "Bounty",
            "Rewards": [
                {"Faction": "Fed", "Reward": 10000},
                {"Faction": "Emp", "Reward": 20000}
            ]
        }
        
        stats.awarded(entry)
        self.assertEqual(stats.awarded_nb, 1)
        self.assertEqual(stats.sum_awarded, 30000)
        self.assertEqual(len(stats.awarded_bounties), 1)

    def test_credits_per_hour(self):
        stats = EDRBountyHuntingStats()
        
        # Start at 1000
        # Award at 4600 (1 hour later)
        self.mock_time.py_epoch_now.return_value = 4600.0
        
        entry = {
            "event": "Bounty",
            "Rewards": [{"Reward": 1000000}]
        }
        stats.awarded(entry)
        
        cph = stats.credits_per_hour()
        self.assertEqual(cph, 1000000.0)
        
    def test_averages(self):
        stats = EDRBountyHuntingStats()
        stats.sum_scanned = 100000
        stats.scanned_nb = 2
        stats.sum_awarded = 50000
        stats.awarded_nb = 1
        
        self.assertEqual(stats.bounty_average(), 50000.0)
        # NOTE: reward_average uses self.scanned_nb as divisor in the code?
        # return (self.sum_awarded / self.awarded_nb) if self.scanned_nb else 0.0
        # Wait, if scanned_nb != 0, it divides by awarded_nb. 
        # But if scanned_nb is 0, it returns 0.
        
        self.assertEqual(stats.reward_average(), 50000.0)
        
        stats.scanned_nb = 0
        self.assertEqual(stats.reward_average(), 0.0)

if __name__ == '__main__':
    unittest.main()
