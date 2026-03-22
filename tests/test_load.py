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
sys.modules['config'] = MagicMock()

# Add the 'edr' directory to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr')))

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
        load.plugin_start('some_dir')
        
        # Verify
        # We need to check the global EDR_CLIENT in load, not the patched one which was overwritten
        load.EDR_CLIENT.apply_config.assert_called()
        load.EDR_CLIENT.login.assert_called()

    @patch('load.EDR_CLIENT')
    def test_plugin_stop(self, mock_client):
        # Setup
        mock_client.autoupdate_pending = False
        
        # Test
        load.plugin_stop()
        
        # Verify
        mock_client.shutdown.assert_called_with(everything=True)

    @patch('load.EDR_CLIENT')
    def test_prerequisites(self, mock_client):
        # Setup
        mock_client.mandatory_update = False
        mock_client.is_logged_in.return_value = True
        
        # Test Success
        self.assertTrue(load.prerequisites(mock_client, False, False))
        
        # Test Failures
        mock_client.mandatory_update = True
        self.assertFalse(load.prerequisites(mock_client, False, False))
        
        mock_client.mandatory_update = False
        mock_client.is_logged_in.return_value = False
        self.assertFalse(load.prerequisites(mock_client, False, False))

if __name__ == '__main__':
    unittest.main()
