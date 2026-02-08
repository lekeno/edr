import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the 'edr' directory to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr')))

from unittest.mock import MagicMock
sys.modules['ingamemsg'] = MagicMock()
sys.modules['edrclient'] = MagicMock() # Also mock edrclient to avoid complex init
# But load.py needs EDRClient class... 
# Actually if I mock edrclient module, load.py will get a Mock object when it does 'from edrclient import EDRClient'.
# That might be enough since load.py does EDR_CLIENT = EDRClient() which would be Mock()() -> Mock.

import load

class TestLoad(unittest.TestCase):
    @patch('load.EDR_CLIENT')
    def test_plugin_start(self, mock_client):
        # Setup
        # mock_client is the Mock object replacing load.EDR_CLIENT
        
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

    @patch('load.EDR_CLIENT')
    def test_prerequisites(self, mock_client):
        # Setup
        mock_client.mandatory_update = False
        mock_client.is_logged_in.return_value = True
        
        # Test Success - verify passing the mock_client works
        self.assertTrue(load.prerequisites(mock_client, False, False))
        
        # Test Failures
        mock_client.mandatory_update = True
        self.assertFalse(load.prerequisites(mock_client, False, False))
        
        mock_client.mandatory_update = False
        mock_client.is_logged_in.return_value = False
        self.assertFalse(load.prerequisites(mock_client, False, False))

if __name__ == '__main__':
    unittest.main()
