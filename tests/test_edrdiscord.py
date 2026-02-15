import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# sys.path injection removed
from edr.controllers.edrdiscord import EDRDiscordWebhook, EDRDiscordMessage, EDRDiscordIntegration, EDRDiscordSimpleMessage, EDRDiscordEmbed, EDRDiscordField

class TestEDRDiscordWebhook(unittest.TestCase):
    def setUp(self):
        self.webhook_url = "https://discord.com/api/webhooks/12345/abcde"
        self.webhook = EDRDiscordWebhook(self.webhook_url)

    @patch('edr.controllers.edrdiscord.requests.Session')
    def test_send_text_success(self, mock_session):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_session.return_value.post.return_value = mock_response
        
        # We need to mock the SESSION class attribute, not just requests.Session
        with patch.object(EDRDiscordWebhook, 'SESSION', mock_session.return_value):
            success = self.webhook.send_text("Hello World")
            self.assertTrue(success)
            mock_session.return_value.post.assert_called_once()
    
    @patch('edr.controllers.edrdiscord.requests.Session')
    def test_send_text_throttled(self, mock_session):
        self.webhook.backoff.throttle()
        success = self.webhook.send_text("Hello World")
        self.assertFalse(success)
        mock_session.return_value.post.assert_not_called()

    @patch('edr.controllers.edrdiscord.requests.Session')
    def test_send_complex_message(self, mock_session):
        mock_response = Mock()
        mock_response.status_code = 204
        
        with patch.object(EDRDiscordWebhook, 'SESSION', mock_session.return_value):
            mock_session.return_value.post.return_value = mock_response
            
            msg = EDRDiscordMessage()
            msg.content = "Complex Message"
            success = self.webhook.send(msg)
            
            self.assertTrue(success)
            mock_session.return_value.post.assert_called_once()


class TestEDRDiscordMessage(unittest.TestCase):
    def test_basic_message(self):
        msg = EDRDiscordMessage()
        msg.content = "Hello"
        self.assertTrue(msg.valid())
        json_output = msg.json()
        self.assertEqual(json_output["content"], "Hello")
        self.assertEqual(json_output["username"], "EDR")

    def test_invalid_message(self):
        msg = EDRDiscordMessage()
        self.assertFalse(msg.valid())

    def test_message_with_embed(self):
        msg = EDRDiscordMessage()
        msg.content = "Embed Text"
        
        embed = EDRDiscordEmbed()
        embed.title = "Title"
        embed.description = "Desc"
        msg.add_embed(embed)
        
        self.assertTrue(msg.valid())
        json_output = msg.json()
        self.assertEqual(len(json_output["embeds"]), 1)
        self.assertEqual(json_output["embeds"][0]["title"], "Title")


class TestEDRDiscordIntegration(unittest.TestCase):
    def setUp(self):
        self.edrcmdrs = Mock()
        self.edrcmdrs.player.name = "CmdrTest"
        self.edrcmdrs.player.location.pretty_print.return_value = "Sol"
        self.edrcmdrs.player.star_system = "Sol"
        # Fix karma comparison error
        self.edrcmdrs.cmdr.return_value.karma = 0
        
        self.integration = EDRDiscordIntegration(self.edrcmdrs)
        # Mock configs to avoid file I/O and external dependencies
        self.integration.channels_players_cfg = {} 

    @patch('edr.controllers.edrdiscord.EDRDiscordWebhook.send')
    def test_process_incoming_direct(self, mock_send):
        entry = {
            "event": "ReceiveText",
            "Channel": "player",
            "From": "CmdrSender",
            "Message": "Hello",
            "timestamp": "2023-10-27T10:00:00Z"
        }
        
        # Ensure the webhook exists for 'player'
        self.integration.incoming['player'] = Mock()
        self.integration.incoming['player'].send.return_value = True
        
        # Ensure AFK detector says False
        self.integration.afk_detector = Mock()
        self.integration.afk_detector.is_afk.return_value = False

        result = self.integration.process(entry)
        self.assertTrue(result)
        self.integration.incoming['player'].send.assert_called_once()

    @patch('edr.controllers.edrdiscord.EDRDiscordWebhook.send')
    def test_process_outgoing_broadcast(self, mock_send):
        entry = {
            "event": "SendText",
            "To": "local",
            "Message": "!discord Hello All",
            "timestamp": "2023-10-27T10:00:00Z"
        }
        
        self.integration.outgoing['broadcast'] = Mock()
        self.integration.outgoing['broadcast'].send.return_value = True
        
        result = self.integration.process(entry)
        self.assertTrue(result)
        self.integration.outgoing['broadcast'].send.assert_called_once()


if __name__ == '__main__':
    unittest.main()
