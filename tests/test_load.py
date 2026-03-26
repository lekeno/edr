import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Setup mocks BEFORE importing load
# This prevents the real EDRClient from initializing and causing dependency issues
edr_client_mock = MagicMock()
sys.modules['edr.controllers.edrclient'] = MagicMock()
sys.modules['edr.controllers.edrclient'].EDRClient = edr_client_mock

sys.modules['ingamemsg'] = MagicMock()
sys.modules['myNotebook'] = MagicMock()
sys.modules['EDMCOverlay'] = MagicMock()
sys.modules['ttkHyperlinkLabel'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

# Mock config properly so gettext doesn't crash during EDRClient initialization
config_mock = MagicMock()
config_mock.get_str.return_value = 'en'
sys.modules['config'] = config_mock

# Add the 'edr' directory to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr', 'src')))

sys.modules['edr.controllers.edrevents'] = MagicMock()

try:
    import load
except ImportError:
    # If load fails to import due to other missing modules, we might need to mock them too
    # But with EDRClient mocked, it should be fine
    pass

class TestLoad(unittest.TestCase):
    def setUp(self):
        # Ensure imports are reloaded or mocks are fresh if needed
        pass

    @patch('load.EDR_CLIENT')
    def test_plugin_start(self, mock_client):
        # Setup
        # mock_client is the Mock object replacing load.EDR_CLIENT
        # Note: If import load ran successfully, load.EDR_CLIENT is already an instance of our mock EDRClient
        
        # Test
        load.plugin_start()
        
        # Verify
        mock_client.apply_config.assert_called()
        mock_client.login.assert_called()

    @patch('load.EDR_CLIENT')
    def test_plugin_stop(self, mock_client):
        # Setup
        mock_client.autoupdate_pending = False
        
        # Test
        load.plugin_stop()
        
        # Verify
        mock_client.shutdown.assert_called_with(everything=True)

    @patch('load.EDR_EVENTS')
    def test_journal_entry_delegation(self, mock_events):
        # Setup
        cmdr = "TestCmdr"
        entry = {"event": "FSDJump", "StarSystem": "Sol"}
        state = {"Friends": []}
        
        # Test
        load.journal_entry(cmdr, False, "Sol", None, entry, state)
        
        # Verify delegation
        mock_events.journal_entry.assert_called_with(cmdr, False, "Sol", None, entry, state)

    @patch('load.EDR_EVENTS')
    def test_dashboard_entry_delegation(self, mock_events):
        # Setup
        cmdr = "TestCmdr"
        entry = {"Flags": 0}
        
        # Test
        load.dashboard_entry(cmdr, False, entry)
        
        # Verify delegation
        mock_events.dashboard_entry.assert_called_with(cmdr, False, entry)

if __name__ == '__main__':
    unittest.main()
