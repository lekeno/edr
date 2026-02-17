
import unittest
from unittest.mock import MagicMock, patch, call
import requests
from edr.controllers.edsmserver import EDSMServer

class TestEDSMServer(unittest.TestCase):
    def setUp(self):
        self.config_patch = patch('edr.controllers.edsmserver.EDR_CONFIG')
        self.mock_config = self.config_patch.start()
        self.mock_config.edsm_api_key.return_value = 'test_key'
        self.mock_config.edsm_server.return_value = 'http://test.edsm.net'
        
        self.log_patch = patch('edr.controllers.edsmserver.EDR_LOG')
        self.mock_log = self.log_patch.start()
        
        self.backoff_patch = patch('edr.controllers.edsmserver.Backoff')
        self.mock_backoff = self.backoff_patch.start()
        
        self.http_cache_patch = patch('edr.controllers.edsmserver.EDRHttpCache')
        self.mock_http_cache = self.http_cache_patch.start()
        
        self.session_patch = patch('edr.controllers.edsmserver.requests.Session')
        self.mock_session_cls = self.session_patch.start()
        self.mock_session = self.mock_session_cls.return_value
        
        # Patch the class level SESSION, or instance's session usage?
        # EDSMServer.SESSION is set at class level.
        # So I should patch EDSMServer.SESSION or requests.Session before it's used?
        # EDSMServer.SESSION = requests.Session() happens at import time.
        # So I need to patch the object on the class.
        
        self.server = EDSMServer()
        # Mock the class-level SESSION with my mock
        EDSMServer.SESSION = self.mock_session

    def tearDown(self):
        self.config_patch.stop()
        self.log_patch.stop()
        self.backoff_patch.stop()
        self.http_cache_patch.stop()
        self.session_patch.stop()

    def test_system_success(self):
        self.server.http_cache.get.return_value = None
        self.server.backoff.throttled.return_value = False
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Sol", "id": 1}
        mock_response.headers = {}
        self.mock_session.get.return_value = mock_response
        
        result = self.server.system("Sol")
        self.assertEqual(result, {"name": "Sol", "id": 1})
        self.mock_session.get.assert_called_with(
            'http://test.edsm.net/api-v1/systems', 
            params={'systemName': 'Sol', 'showCoordinates': 1, 'showInformation': 1, 'showId': 1, 'showPermit': 1, 'showPrimaryStar': 1},
            timeout=5
        )

    def test_system_cached(self):
        self.server.http_cache.get.return_value = {"name": "Sol", "cached": True}
        
        result = self.server.system("Sol")
        self.assertEqual(result, {"name": "Sol", "cached": True})
        self.mock_session.get.assert_not_called()

    def test_system_not_found(self):
        self.server.http_cache.get.return_value = None
        self.server.backoff.throttled.return_value = False
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        self.mock_session.get.return_value = mock_response
        
        result = self.server.system("Unknown")
        self.assertIsNone(result)

    def test_throttled(self):
        self.server.http_cache.get.return_value = None
        self.server.backoff.throttled.return_value = True
        
        result = self.server.system("Sol")
        self.assertIsNone(result)
        self.mock_session.get.assert_not_called()

    def test_systems_within_radius_fail(self):
        self.server.http_cache.get.return_value = None
        self.server.backoff.throttled.return_value = False
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = "Not a list"
        mock_response.headers = {}
        self.mock_session.get.return_value = mock_response
        
        result = self.server.systems_within_radius("Sol", 10)
        self.assertIsNone(result)

    def test_systems_within_radius_success(self):
        self.server.http_cache.get.return_value = None
        self.server.backoff.throttled.return_value = False
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"name": "Sol", "distance": 0}, {"name": "Alpha", "distance": 5}]
        mock_response.headers = {}
        self.mock_session.get.return_value = mock_response
        
        result = self.server.systems_within_radius("Sol", 10)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "Sol")

if __name__ == '__main__':
    unittest.main()
