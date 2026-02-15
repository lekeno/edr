
import unittest
from unittest.mock import MagicMock, patch
import configparser
from edr.core.edrconfig import EDRConfig, EDRUserConfig

class TestEDRConfig(unittest.TestCase):
    def setUp(self):
        self.config = EDRConfig()
        # Mock the underlying configparser
        self.config.config = MagicMock(spec=configparser.ConfigParser)

    def test_edr_version(self):
        self.config.config.get.return_value = "1.0.0"
        self.assertEqual(self.config.edr_version(), "1.0.0")
        self.config.config.get.assert_called_with('general', 'version')

    def test_edr_api_key(self):
        self.config.config.get.return_value = "secret"
        self.assertEqual(self.config.edr_api_key(), "secret")
        self.config.config.get.assert_called_with('edr', 'edr_api_key')
        
    def test_integers(self):
        self.config.config.get.return_value = "100"
        self.assertEqual(self.config.edr_heartbeat(), 100)

class TestEDRUserConfig(unittest.TestCase):
    def setUp(self):
        self.user_config = EDRUserConfig()
        self.user_config.config = MagicMock()

    def test_discord_webhook(self):
        self.user_config.config.get.return_value = "http://webhook"
        self.assertEqual(self.user_config.discord_webhook_for_comms("general"), "http://webhook")
        self.user_config.config.get.assert_called_with('discord_incoming', 'general_webhook')

    def test_discord_webhook_missing(self):
        self.user_config.config.get.side_effect = configparser.NoOptionError("opt", "sec")
        self.assertIsNone(self.user_config.discord_webhook_for_comms("general"))
