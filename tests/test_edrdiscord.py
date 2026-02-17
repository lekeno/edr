
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import json
import requests
from edr.controllers.edrdiscord import (
    EDRDiscordMessage, 
    EDRDiscordEmbed, 
    EDRDiscordWebhook, 
    EDRDiscordIntegration,
    EDRDiscordSimpleMessage
)

class TestEDRDiscordMessage(unittest.TestCase):
    def test_validity(self):
        msg = EDRDiscordMessage()
        self.assertFalse(msg.valid()) # Empty message invalid
        
        msg.content = "Hello"
        self.assertTrue(msg.valid())
        
        msg.content = ""
        embed = EDRDiscordEmbed()
        msg.add_embed(embed)
        self.assertFalse(msg.valid()) # Content required even with embed

    def test_json_structure(self):
        msg = EDRDiscordMessage()
        msg.content = "Test"
        json_output = msg.json()
        self.assertEqual(json_output["content"], "Test")
        self.assertEqual(json_output["username"], "EDR")

class TestEDRDiscordWebhook(unittest.TestCase):
    def setUp(self):
        self.webhook_url = "http://fake.url"
        self.webhook = EDRDiscordWebhook(self.webhook_url)

    @patch('edr.controllers.edrdiscord.EDRDiscordWebhook.SESSION')
    def test_send_success(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_session.post.return_value = mock_response
        
        msg = EDRDiscordMessage()
        msg.content = "Test"
        
        success = self.webhook.send(msg)
        self.assertTrue(success)
        mock_session.post.assert_called_once()

    @patch('edr.controllers.edrdiscord.EDRDiscordWebhook.SESSION')
    def test_backoff_throttling(self, mock_session):
        # Simulate 429 Too Many Requests
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_session.post.return_value = mock_response
        
        msg = EDRDiscordMessage()
        msg.content = "Test"
        
        success = self.webhook.send(msg)
        self.assertFalse(success)
        
        # Next call should be throttled locally without hitting session
        mock_session.reset_mock()
        success = self.webhook.send(msg)
        self.assertFalse(success)
        mock_session.post.assert_not_called()

class TestEDRDiscordIntegration(unittest.TestCase):
    def setUp(self):
        self.edrcmdrs = MagicMock()
        self.edrcmdrs.player.name = "TestCmdr"
        self.edrcmdrs.player.location.pretty_print.return_value = "Sol"
        self.edrcmdrs.player.star_system = "Sol"
        
        # Configure mocked profile karma
        self.mock_profile = MagicMock()
        self.mock_profile.karma = 0
        self.mock_profile.readable_karma.return_value = "Neutral"
        self.edrcmdrs.cmdr.return_value = self.mock_profile

        self.edr_config_patch = patch('edr.controllers.edrdiscord.EDR_CONFIG')
        self.edr_config = self.edr_config_patch.start()
        self.edr_config.lru_max_size.return_value = 100
        self.edr_config.blips_max_age.return_value = 3600
        self.edr_config.cognitive_novelty_threshold.return_value = 3600
        
        self.user_config_patch = patch('edr.controllers.edrdiscord.EDRUserConfig')
        self.MockUserConfig = self.user_config_patch.start()
        # Mock webhook URLs to return valid strings so Webhooks are initialized
        self.MockUserConfig.return_value.discord_webhook_for_comms.return_value = "http://fake.url"
        self.MockUserConfig.return_value.discord_webhook_for_fc.return_value = "http://fake.url"
        
        # Patch `open` to avoid reading user_discord_players.json
        self.open_patch = patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{}')
        self.mock_open = self.open_patch.start()
        
        self.integration = EDRDiscordIntegration(self.edrcmdrs)
        
        # Mock the internal webhooks to avoid real calls
        for key in self.integration.incoming:
            self.integration.incoming[key] = MagicMock()
        for key in self.integration.outgoing:
            self.integration.outgoing[key] = MagicMock()

    def tearDown(self):
        self.edr_config_patch.stop()
        self.user_config_patch.stop()
        self.open_patch.stop()

    def test_process_incoming_text(self):
        entry = {
            "event": "ReceiveText",
            "From": "TestFriend",
            "Message": "Hello",
            "Channel": "friend",
            "timestamp": "2023-01-01T12:00:00Z"
        }
        
        # Incoming "friend" channel is not in default self.incoming map usually,
        # but let's check what channels ARE supported.
        # self.incoming keys: afk, squadron, squadleaders, starsystem, local, wing, crew, chat, voicechat, player.
        
        # But wait, logic:
        # if channel is None and "From" in entry...
        # Here "Channel" is "friend".
        # It falls through to: if not (channel in self.incoming ...): return False.
        # So "friend" channel fails unless configured?
        # Let's change channel to "squadron" which is supported.
        
        entry = {
            "event": "ReceiveText",
            "From": "TestFriend",
            "Message": "Hello",
            "Channel": "squadron",
            "timestamp": "2023-01-01T12:00:00Z"
        }
        
        self.integration.process(entry)
        
        self.integration.incoming["squadron"].send.assert_called()

    def test_process_outgoing_text(self):
        entry = {
            "event": "SendText",
            "To": "local",
            "Message": "Hello System",
            "timestamp": "2023-01-01T12:00:00Z"
        }
        
        self.integration.process(entry)
        self.integration.outgoing["local"].send.assert_called()

if __name__ == '__main__':
    unittest.main()
