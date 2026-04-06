import sys
import os
import unittest
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

from edr.controllers.edrsearch import EDRSearchManager

class MockEDRClient:
    def __init__(self):
        self.player = MagicMock()
        self.player.star_system = "Sol"
        self.edrsystems = MagicMock()
        self.edrresourcefinder = MagicMock()
        self.edrfssinsights = MagicMock()
        self.edrfactions = MagicMock()
        self.status = ""
        self.audio_feedback = False
        self.SFX = MagicMock()
        self.feature_ads = {"parking": {"advertised": False}}
        self.register_fss_signals = MagicMock()
        self.describe_station = MagicMock(return_value=["Station details"])
        self.server = MagicMock()
        
    def _EDRClient__notify(self, header, details, clear_before=False, sfx=True):
        self.last_notify = (header, details)
        
    def notify_with_details(self, header, details):
        self.last_notify = (header, details)


class TestEDRSearchManager(unittest.TestCase):
    def setUp(self):
        self.client = MockEDRClient()
        self.manager = EDRSearchManager(self.client)

    def test_interstellar_factors_near_success(self):
        self.client.edrsystems.in_bubble.return_value = True
        self.manager.interstellar_factors_near("Sol")
        self.client.edrsystems.search_interstellar_factors.assert_called_once()
        self.assertEqual(self.client.status, "I.Factors: searching...")

    def test_interstellar_factors_near_unknown_system(self):
        self.client.edrsystems.in_bubble.return_value = True
        self.client.edrsystems.search_interstellar_factors.side_effect = ValueError("Unknown system")
        self.manager.interstellar_factors_near("UnknownSys")
        self.assertEqual(self.client.status, "I.Factors: failed")

    def test_search_resource(self):
        self.client.edrsystems.in_bubble.return_value = True
        self.client.edrresourcefinder.canonical_name.return_value = "Iron"
        self.client.edrresourcefinder.resource_near.return_value = True
        self.manager.search_resource("iron", "Sol")
        self.assertEqual(self.client.status, "Iron: searching...")

    def test_parking_system_near(self):
        self.client.edrsystems.in_bubble.return_value = True
        self.manager.parking_system_near("Sol")
        self.client.edrsystems.search_parking_system.assert_called_once()
        self.assertTrue(self.client.feature_ads["parking"]["advertised"])

if __name__ == '__main__':
    unittest.main()
