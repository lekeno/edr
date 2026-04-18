
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import json
import edr.controllers.edrserver
from edr.controllers.edrserver import EDRServer
from edr.utils.edtime import EDTime

class TestEDRServer(unittest.TestCase):
    def setUp(self):
        self.mock_config = patch('edr.controllers.edrserver.EDR_CONFIG').start()
        self.mock_config.edr_version.return_value = "1.0.0"
        self.mock_config.edr_api_key.return_value = "dummy_api_key"
        self.mock_config.edr_server.return_value = "http://dummy_server"
        self.mock_config.edr_server_functions.return_value = "http://dummy_functions"
        self.mock_config.inara_api_key.return_value = "dummy_inara_key"

        self.mock_auth_cls = patch('edr.controllers.edrserver.RESTFirebaseAuth').start()
        self.mock_auth = MagicMock()
        self.mock_auth_cls.return_value = self.mock_auth
        
        self.mock_http_cache_cls = patch('edr.controllers.edrserver.EDRHttpCache').start()
        self.mock_http_cache = MagicMock()
        self.mock_http_cache_cls.return_value = self.mock_http_cache

        # Mock Session at class level
        self.mock_session_patch = patch('edr.controllers.edrserver.EDRServer.SESSION')
        self.mock_session = self.mock_session_patch.start()
        
        # Ensure prepared request has a valid URL string to avoid urllib parse errors
        self.mock_prepped = MagicMock()
        self.mock_prepped.url = "http://dummy_url"
        self.mock_session.prepare_request.return_value = self.mock_prepped

        self.server = EDRServer()


    def tearDown(self):
        patch.stopall()

    def test_login(self):
        self.mock_auth.authenticate.return_value = True
        result = self.server.login("user@example.com", "password")
        self.assertTrue(result)
        self.assertEqual(self.mock_auth.email, "user@example.com")

    def test_is_authenticated(self):
        self.mock_auth.is_valid_auth_token.return_value = True
        self.assertTrue(self.server.is_authenticated())

    def test_system_success(self):
        # Mock auth token
        self.mock_auth.id_token.return_value = "dummy_token"
        self.mock_auth.is_valid_auth_token.return_value = True
        
        # Mock GET response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"-dummy_id": {"name": "Sol", "coords": {"x":0, "y":0, "z":0}}}'
        mock_response.json.return_value = {"-dummy_id": {"name": "Sol", "coords": {"x":0, "y":0, "z":0}}}
        mock_response.headers = {"Cache-Control": "max-age=60", "ETag": "dummy_etag"}
        
        self.mock_session.send.return_value = mock_response
        self.mock_http_cache.get.return_value = None # Cache miss

        result = self.server.system("Sol", may_create=False)
        
        self.assertIsNotNone(result)
        self.assertIn("-dummy_id", result)
        self.assertEqual(result["-dummy_id"]["name"], "Sol")

    def test_system_not_found_no_create(self):
        self.mock_auth.id_token.return_value = "dummy_token"
        
        # Mock GET response empty dict
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_response.headers = {}
        
        self.mock_session.send.return_value = mock_response
        self.mock_http_cache.get.return_value = None

        result = self.server.system("UnknownSys", may_create=False)
        self.assertIsNone(result)

    def test_fc_success(self):
        self.mock_auth.id_token.return_value = "dummy_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"-fc_id": {"callsign": "ABC-123", "name": "Carrier"}}'
        mock_response.json.return_value = {"-fc_id": {"callsign": "ABC-123", "name": "Carrier"}}
        mock_response.headers = {}
        
        self.mock_session.send.return_value = mock_response
        self.mock_http_cache.get.return_value = None

        result = self.server.fc("ABC-123", "Carrier", "Sol", may_create=False)
        
        self.assertIsNotNone(result)
        self.assertIn("-fc_id", result)

    def test_server_version(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"version": "1.0.0"}'
        mock_response.json.return_value = {"version": "1.0.0"}
        mock_response.headers = {}
        
        self.mock_session.send.return_value = mock_response
        self.mock_http_cache.get.return_value = None
        
        result = self.server.server_version()
        self.assertEqual(result["version"], "1.0.0")

if __name__ == '__main__':
    unittest.main()
