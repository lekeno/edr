
import unittest
from unittest.mock import MagicMock, patch
import json
import os
from edr.utils.RESTFirebase import RESTFirebaseAuth, AuthState

class TestRESTFirebaseAuth(unittest.TestCase):
    def setUp(self):
        self.auth = RESTFirebaseAuth("1.0.0")
        self.auth.api_key = "dummy_key"

    @patch('edr.utils.RESTFirebase.os.path.exists')
    @patch('edr.utils.RESTFirebase.open')
    def test_init_clears_legacy(self, mock_open, mock_exists):
        mock_exists.side_effect = lambda p: p.endswith('.p') # Legacy pickle exists
        with patch('edr.utils.RESTFirebase.os.remove') as mock_remove:
            RESTFirebaseAuth("1.0.0")
            mock_remove.assert_called()

    @patch('edr.utils.RESTFirebase.requests.post')
    def test_login_success(self, mock_post):
        # Response for __login (Identity Toolkit)
        login_response = MagicMock()
        login_response.status_code = 200
        login_response.content = json.dumps({
            "refreshToken": "refresh_token_1",
            "idToken": "id_token_1",
            "expiresIn": "3600",
            "localId": "uid"
        }).encode('utf-8')

        # Response for __refresh_fb_token (Secure Token)
        refresh_response = MagicMock()
        refresh_response.status_code = 200
        refresh_response.content = json.dumps({
            "refresh_token": "refresh_token_2",
            "id_token": "id_token_2",
            "expires_in": "3600",
            "user_id": "uid"
        }).encode('utf-8')

        mock_post.side_effect = [login_response, refresh_response]

        # Ensure clean state so __login actually triggers a POST request
        self.auth.refresh_token = None
        self.auth.auth = None

        with patch('edr.utils.RESTFirebase.RESTFirebaseAuth._RESTFirebaseAuth__clear_cache_file'):
             status = self.auth.authenticate()
             self.assertEqual(status, AuthState.SUCCESS)
             self.assertEqual(self.auth.id_token(), "id_token_2")
             self.assertEqual(self.auth.uid(), "uid")

    @patch('edr.utils.RESTFirebase.requests.post')
    def test_login_fail(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "INVALID_PASSWORD"}}
        mock_post.return_value = mock_response

        self.auth.email = "test@example.com"
        self.auth.password = "wrong"
        
        status = self.auth.authenticate()
        self.assertEqual(status, AuthState.INVALID_CREDENTIALS)

    @patch('edr.utils.RESTFirebase.requests.post')
    def test_refresh_token(self, mock_post):
        self.auth.refresh_token = "old_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({
            "refresh_token": "new_token",
            "id_token": "new_id",
            "expires_in": "3600",
            "user_id": "uid"
        }).encode('utf-8')
        mock_post.return_value = mock_response
        
        success = self.auth._RESTFirebaseAuth__refresh_fb_token()
        self.assertTrue(success)
        self.assertEqual(self.auth.refresh_token, "new_token")

if __name__ == '__main__':
    unittest.main()
