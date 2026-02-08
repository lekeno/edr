import unittest
from unittest.mock import MagicMock, patch
from edrserver import EDRServer  # EDR_INTERNAL
from edrconfig import EDRConfig # EDR_INTERNAL

class TestEDRServer(unittest.TestCase):
    def setUp(self):
        self.server = EDRServer()

    def test_nodify(self):
        self.assertEqual(EDRServer.nodify("Simple Name"), "simple_name")
        self.assertEqual(EDRServer.nodify("ALL CAPS"), "all_caps")
        self.assertEqual(EDRServer.nodify("Mixed 123"), "mixed_123")
        self.assertEqual(EDRServer.nodify("  Spaces  "), "__spaces__") # Should it trim? Logic says replace only.

    @patch('edrserver.EDR_CONFIG')
    def test_initialization(self, mock_config):
        mock_config.edr_version.return_value = "1.0.0"
        mock_config.edr_api_key.return_value = "fake_key"
        
        server = EDRServer()
        self.assertEqual(server.version, "1.0.0")
        self.assertEqual(server.EDR_API_KEY, "fake_key")

    @patch('edrserver.RESTFirebaseAuth')
    def test_login(self, mock_auth_cls):
        mock_auth_instance = mock_auth_cls.return_value
        mock_auth_instance.authenticate.return_value = {"status": "success"}
        
        server = EDRServer()
        result = server.login("user@example.com", "password")
        
        self.assertEqual(result, {"status": "success"})
        self.assertEqual(server.REST_firebase.email, "user@example.com")
        self.assertEqual(server.REST_firebase.password, "password")

    def test_set_player_name(self):
        self.server.set_player_name("Cmdr Test")
        self.assertEqual(self.server.player_name, "Cmdr Test")

    def test_set_game_mode(self):
        self.server.set_game_mode("Open")
        self.assertEqual(self.server.game_mode, "Open")
        self.assertIsNone(self.server.private_group)
        
        self.server.set_game_mode("Group", "Mobius")
        self.assertEqual(self.server.game_mode, "Group")
        self.assertEqual(self.server.private_group, "Mobius")

if __name__ == '__main__':
    unittest.main()
