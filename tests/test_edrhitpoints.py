import unittest
from unittest.mock import Mock, patch
from edr.models.edrhitppoints import EDRHitPPoints

class TestEDRHitPPoints(unittest.TestCase):
    def setUp(self):

        self.edtime_patch = patch('edr.models.edrhitppoints.EDTime')
        self.mock_edtime = self.edtime_patch.start()
        # Default time
        self.mock_edtime.ms_epoch_now.return_value = 10000

        # Max length 10, max span 10s (10000ms), trend span 1s (1000ms)
        self.hp = EDRHitPPoints(10, 10, 1)

    def tearDown(self):
        self.edtime_patch.stop()

    def test_update_consistency(self):
        self.assertTrue(self.hp.empty())
        
        self.hp.update(100)
        self.assertEqual(self.hp.len(), 1)
        self.assertEqual(self.hp.last_value(), 100)
        
        self.mock_edtime.ms_epoch_now.return_value = 11000
        self.hp.update(100)
        self.assertEqual(self.hp.len(), 2)
        self.assertEqual(self.hp.last()["timestamp"], 11000)

        # distinct value
        self.mock_edtime.ms_epoch_now.return_value = 12000
        self.hp.update(90)
        self.mock_edtime.ms_epoch_now.return_value = 12000
        self.hp.update(90)
        self.assertEqual(self.hp.len(), 3)

    def test_redundant_values(self):
        self.hp.update(100)
        self.mock_edtime.ms_epoch_now.return_value = 11000
        self.hp.update(100)
        self.assertEqual(self.hp.len(), 2)
        
        # Third redundant value should replace the second one (timestamp update)
        self.mock_edtime.ms_epoch_now.return_value = 12000
        self.hp.update(100)
        self.assertEqual(self.hp.len(), 2)
        self.assertEqual(self.hp.last()["timestamp"], 12000)
        self.assertEqual(self.hp.history[0]["timestamp"], 10000)

    def test_trend_stable(self):
        self.hp.update(100)
        self.mock_edtime.ms_epoch_now.return_value = 11000
        self.hp.update(100)
        
        # Trend requires length > 2? or >=2?
        # Code: if len <= 2: return 0. (Actually code says <= 2 which means need 3 points? let's verify)
        # Line 50: if len(self.history) <= 2: return 0
        # So we need 3 points.
        
        self.mock_edtime.ms_epoch_now.return_value = 12000
        self.hp.update(100)
        
        self.assertEqual(self.hp.trend(), 0)

    def test_trend_decreasing(self):
        # 1. 100% at T=0
        self.mock_edtime.ms_epoch_now.return_value = 10000
        self.hp.update(100)
        
        # 2. 90% at T=1000ms (1s)
        self.mock_edtime.ms_epoch_now.return_value = 11000
        self.hp.update(90)
        
        # 3. 80% at T=2000ms (2s)
        self.mock_edtime.ms_epoch_now.return_value = 12000
        self.hp.update(80)
        
        # Delta total: (90-100) + (80-90) = -10 + -10 = -20
        # Time total: 1000 + 1000 = 2000
        # Avg = -20 / 2000 = -0.01 per ms = -10% per sec
        # Trend to 0: current (80) / (-0.01) / 1000 
        # 80 / -10 = -8 seconds to destruction
        
        trend = self.hp.trend()
        self.assertAlmostEqual(trend, -8.0)

    def test_trend_increasing(self):
        # 1. 50%
        self.mock_edtime.ms_epoch_now.return_value = 10000
        self.hp.update(50)
        
        # 2. 60%
        self.mock_edtime.ms_epoch_now.return_value = 11000
        self.hp.update(60)
        
        # 3. 70%
        self.mock_edtime.ms_epoch_now.return_value = 12000
        self.hp.update(70)
        
        # Avg = (10+10)/2000 = 0.01 per ms = +10% per sec
        # Trend to 100: (100-70) / 0.01 / 1000 = 30 / 10 = 3 seconds to recover
        
        trend = self.hp.trend()
        self.assertAlmostEqual(trend, 3.0)

    def test_meaningful(self):
        self.hp.update(100)
        self.assertFalse(self.hp.meaningful()) # Only 1 point
        
        self.mock_edtime.ms_epoch_now.return_value = 11000
        self.hp.update(90)
        self.assertTrue(self.hp.meaningful()) # 2 points
