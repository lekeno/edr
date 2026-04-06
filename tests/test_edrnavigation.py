import sys
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from edr.controllers.edrnavigation import EDRNavigationManager

class MockEDRClient:
    def __init__(self):
        self.player = MagicMock()
        self.edrsystems = MagicMock()
        self.edrboi = MagicMock()
        self.edrresourcefinder = MagicMock()
        self.gesture_triggers = True
        
    def _EDRClient__notify(self, header, details, clear_before=False, sfx=True):
        self.last_notify = (header, details)


class TestEDRNavigationManager(unittest.TestCase):
    def setUp(self):
        self.client = MockEDRClient()
        self.manager = EDRNavigationManager(self.client)

    def test_hyperspace_jump(self):
        self.client.player.routenav.update.return_value = {"route_updated": False, "journey_updated": False}
        self.manager.hyperspace_jump("LHS 3447")
        self.client.player.to_hyper_space.assert_called_once()
        self.client.edrsystems.system_coords.assert_called_with("LHS 3447")

    def test_system_guidance_found(self):
        self.client.edrsystems.describe_system.return_value = ["Details"]
        result = self.manager.system_guidance("Sol")
        self.assertTrue(result)
        self.assertEqual(self.client.last_notify[0], "Sol")

    def test_system_guidance_not_found(self):
        self.client.edrsystems.describe_system.return_value = []
        result = self.manager.system_guidance("UnknownSys")
        self.assertFalse(result)
        self.assertEqual(self.client.last_notify[0], "EDR System Search")

if __name__ == '__main__':
    unittest.main()
