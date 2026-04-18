import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src and root to path safely
current_dir = os.path.dirname(os.path.abspath(__file__))
edr_path = os.path.abspath(os.path.join(current_dir, '..', 'edr'))
src_path = os.path.join(edr_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if edr_path not in sys.path:
    sys.path.insert(0, edr_path)

class TestLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock dependencies that are imported during 'import load'
        cls.patches = []
        for mod in ['ingamemsg', 'myNotebook', 'EDMCOverlay', 'ttkHyperlinkLabel', 'tkinter', 'tkinter.ttk', 'config']:
            p = patch.dict('sys.modules', {mod: MagicMock()})
            p.start()
            cls.patches.append(p)
            
        # Also mock EDRClient and EDREventDispatcher to avoid full initialization
        p_client = patch('edr.controllers.edrclient.EDRClient', MagicMock())
        p_client.start()
        cls.patches.append(p_client)
        p_dispatcher = patch('edr.controllers.edreventdispatcher.EDREventDispatcher', MagicMock())
        p_dispatcher.start()
        cls.patches.append(p_dispatcher)

    @classmethod
    def tearDownClass(cls):
        for p in reversed(cls.patches):
            p.stop()

    def test_plugin_start(self):
        import load
        with patch('load.EDR_CLIENT') as mock_client:
            load.plugin_start()
            mock_client.apply_config.assert_called()
            mock_client.login.assert_called()

    def test_plugin_stop(self):
        import load
        with patch('load.EDR_CLIENT') as mock_client:
            mock_client.autoupdate_pending = False
            load.plugin_stop()
            mock_client.shutdown.assert_called_with(everything=True)

    def test_journal_entry(self):
        import load
        with patch('load.EDR_EVENT_DISPATCHER') as mock_dispatcher:
            load.journal_entry("cmdr", False, "system", "station", {"event": "Test"}, {"state": "Test"})
            mock_dispatcher.journal_entry.assert_called_with("cmdr", False, "system", "station", {"event": "Test"}, {"state": "Test"})

if __name__ == '__main__':
    unittest.main()
