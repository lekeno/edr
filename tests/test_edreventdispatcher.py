import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path safely
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '..', 'edr', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

class TestEDREventDispatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Specific mocks for this test to avoid full import issues
        cls.patches = []
        for mod in ['ingamemsg', 'myNotebook', 'EDMCOverlay', 'ttkHyperlinkLabel', 'tkinter', 'tkinter.ttk', 'config']:
            p = patch.dict('sys.modules', {mod: MagicMock()})
            p.start()
            cls.patches.append(p)

    @classmethod
    def tearDownClass(cls):
        for p in reversed(cls.patches):
            p.stop()

    def setUp(self):
        from edr.controllers.edreventdispatcher import EDREventDispatcher
        self.mock_client = MagicMock()
        # Mock the handlers within the dispatcher
        with patch('edr.controllers.edreventdispatcher.EDRJournalHandler', MagicMock()):
            with patch('edr.controllers.edreventdispatcher.EDRDashboardHandler', MagicMock()):
                self.dispatcher = EDREventDispatcher(self.mock_client)
        self.dispatcher.in_legacy_mode = False

    def test_prerequisites_success(self):
        self.mock_client.mandatory_update = False
        self.mock_client.is_logged_in.return_value = True
        self.assertTrue(self.dispatcher.prerequisites(False))

    def test_journal_entry(self):
        self.mock_client.mandatory_update = False
        self.mock_client.is_logged_in.return_value = True
        
        entry = {"event": "FSDJump", "GameVersion": "4.0.0.0", "timestamp": "2023-01-01T00:00:00Z"}
        state = {"Friends": [], "GameVersion": "4.0.0.0"}
        
        with patch.object(self.dispatcher, 'is_legacy', return_value=False):
            self.dispatcher.journal_entry("cmdr", False, "system", "station", entry, state)
            self.mock_client.player_name.assert_called_with("cmdr")
            self.dispatcher.journal_handler.journal_entry.assert_called_with(entry, state)

if __name__ == '__main__':
    unittest.main()
