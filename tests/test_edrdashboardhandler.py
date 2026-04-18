import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path safely
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '..', 'edr', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

class TestEDRDashboardHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patches = []
        for mod in ['ingamemsg', 'myNotebook', 'EDMCOverlay', 'ttkHyperlinkLabel', 'tkinter', 'tkinter.ttk', 'config']:
            p = patch.dict('sys.modules', {mod: MagicMock()})
            p.start()
            cls.patches.append(p)
        
        # Mock edmc_data
        cls.mock_edmc_data = MagicMock()
        cls.edmc_patch = patch.dict('sys.modules', {'edmc_data': cls.mock_edmc_data})
        cls.edmc_patch.start()
        cls.mock_edmc_data.FlagsFsdJump = 0x1
        cls.mock_edmc_data.FlagsDocked = 0x2
        cls.mock_edmc_data.Flags2OnFoot = 0x2
        cls.mock_edmc_data.FlagsInMainShip = 0x20

    @classmethod
    def tearDownClass(cls):
        cls.edmc_patch.stop()
        for p in reversed(cls.patches):
            p.stop()

    def setUp(self):
        from edr.controllers.edrdashboardhandler import EDRDashboardHandler
        self.mock_client = MagicMock()
        self.mock_player = MagicMock()
        self.mock_client.player = self.mock_player
        self.handler = EDRDashboardHandler(self.mock_client)

    def test_dashboard_entry_gui_focus(self):
        entry = {"GuiFocus": 1}
        self.handler.dashboard_entry("cmdr", False, entry)
        self.assertTrue(self.handler.ed_player.in_game)

    def test_dashboard_entry_flags(self):
        entry = {
            "GuiFocus": 1,
            "Flags": self.mock_edmc_data.FlagsDocked,
            "Flags2": 0
        }
        self.mock_player.is_docked = False
        self.handler.dashboard_entry("cmdr", False, entry)
        self.mock_player.docked.assert_called_with(True)

if __name__ == '__main__':
    unittest.main()
