
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from edr.controllers.edsmserver import EDSMServer
import json
import requests

class TestEDSMServer(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.config_patcher = patch('edr.controllers.edsmserver.EDR_CONFIG')
        self.mock_config = self.config_patcher.start()
        self.mock_config.edsm_api_key.return_value = "TEST_API_KEY"
        self.mock_config.edsm_server.return_value = "https://www.edsm.net"
        
        self.cache_patcher = patch('edr.controllers.edsmserver.EDRHttpCache')
        self.mock_cache = self.cache_patcher.start()
        
        self.backoff_patcher = patch('edr.controllers.edsmserver.Backoff')
        self.mock_backoff = self.backoff_patcher.start()
        
        # Patch the SESSION on the CLASS
        self.session_patcher = patch('edr.controllers.edsmserver.EDSMServer.SESSION')
        self.mock_session = self.session_patcher.start()
        
        self.server = EDSMServer()
        self.server.http_cache = MagicMock()
        self.server.backoff = MagicMock()
        self.server.backoff.throttled.return_value = False

    def tearDown(self):
        self.config_patcher.stop()
        self.cache_patcher.stop()
        self.backoff_patcher.stop()
        self.session_patcher.stop()

    def test_get_system_success(self):
        system_name = "Sol"
        expected_data = {"name": "Sol", "id": 1}
        
        # Mock requests session response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_response.headers = {"Cache-Control": "max-age=60"}
        
        self.mock_session.get.return_value = mock_response
        
        # Ensure cache miss
        self.server.http_cache.get.return_value = None

        result = self.server.system(system_name)
        self.assertEqual(result, expected_data)

    def test_systems_within_radius(self):
        system_name = "Sol"
        radius = 10
        expected_data = [{"name": "Alpha Centauri", "distance": 4.3}, {"name": "Barnard's Star", "distance": 5.9}]
        
        self.server.http_cache.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_response.headers = {"Cache-Control": "max-age=60"}
        
        self.mock_session.get.return_value = mock_response

        result = self.server.systems_within_radius(system_name, radius)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Alpha Centauri")

    def test_get_cached(self):
        self.server.http_cache.get.return_value = {"cached": "data"}
        result = self.server.system("Sol")
        self.assertEqual(result, {"cached": "data"})
        # Should not call session get
        self.mock_session.get.assert_not_called()

    def test_backoff_active(self):
        self.server.backoff.throttled.return_value = True
        self.server.http_cache.get.return_value = None # Important: Cache miss!
        result = self.server.system("Sol")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
