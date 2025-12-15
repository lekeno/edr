import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os
import json

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edr.edrdiscord import EDRDiscordIntegration

class TestEDRDiscord(unittest.TestCase):
    def setUp(self):
        self.edr_config_patch = patch('edr.edrdiscord.EDRConfig')
        self.edr_config_cls = self.edr_config_patch.start()
        self.edr_config_cls.return_value.discord_webhook.return_value = "http://webhook.url"
        # Mock other config methods used in init
        self.edr_config_cls.return_value.cognitive_novelty_threshold.return_value = 100
        self.edr_config_cls.return_value.lru_max_size.return_value = 100
        self.edr_config_cls.return_value.blips_max_age.return_value = 100

        self.user_config_patch = patch('edr.edrdiscord.EDRUserConfig')
        self.user_config_cls = self.user_config_patch.start()
        self.user_config_cls.return_value.discord_webhook_for_comms.return_value = "http://webhook.url"
        self.user_config_cls.return_value.discord_webhook_for_fc.return_value = "http://webhook.url"

        self.session_patch = patch('edr.edrdiscord.EDRDiscordWebhook.SESSION')
        self.mock_session = self.session_patch.start()
        self.mock_session.post.return_value.status_code = 204

        self.afk_patch = patch('edr.edrdiscord.EDRAfkDetector')
        self.mock_afk = self.afk_patch.start()
        self.mock_afk.return_value.is_afk.return_value = False

        self.lru_patch = patch('edr.edrdiscord.LRUCache')
        self.mock_lru = self.lru_patch.start()
        # Ensure instances of LRUCache return None on get() to simulate cache miss
        self.mock_lru.return_value.get.return_value = None
        
        # Mock open for config file reading
        self.mock_open = mock_open(read_data='{}')
        self.file_patch = patch('builtins.open', self.mock_open)
        self.file_patch.start()
        
        self.mock_edrcmdrs = MagicMock()
        self.mock_edrcmdrs.player.name = "CmdrTest"
        # Fix: Configure profile to have serializable attributes and int karma
        mock_profile = MagicMock()
        mock_profile.url = "http://url"
        mock_profile.avatar_url = "http://avatar"
        mock_profile.karma = 0
        mock_profile.readable_karma.return_value = "Neutral"
        self.mock_edrcmdrs.cmdr.return_value = mock_profile
        
        self.discord = EDRDiscordIntegration(self.mock_edrcmdrs)

    def tearDown(self):
        self.edr_config_patch.stop()
        self.user_config_patch.stop()
        self.session_patch.stop()
        self.afk_patch.stop()
        self.lru_patch.stop()
        self.file_patch.stop()

    def test_init(self):
        self.assertIsNotNone(self.discord)

    def test_process_incoming(self):
        # Process incoming messages
        entry = {
            "event": "ReceiveText",
            "Channel": "player",
            "From": "FriendCmdr",
            "Message": "Hello",
            "timestamp": "2023-10-27T10:00:00Z"
        }
        
        # Ensure 'player' webhook is mocked (it is in setUp)
        # Mock checking novelty
        with patch.object(self.discord, '_EDRDiscordIntegration__novel_enough_comms', return_value=True):
            success = self.discord.process(entry)
            self.assertTrue(success)
            self.mock_session.post.assert_called()

    def test_process_outgoing(self):
        entry = {
            "event": "SendText",
            "To": "FriendCmdr",
            "Message": "Hello back",
            "timestamp": "2023-10-27T10:01:00Z"
        }
         # Ensure 'player' webhook is mocked
        with patch.object(self.discord, '_EDRDiscordIntegration__novel_enough_outgoing_comms', return_value=True):
            success = self.discord.process(entry)
            self.assertTrue(success)
            self.mock_session.post.assert_called()

    def test_fc_jump_scheduled(self):
        flight_plan = {
            "owner": "OwnerCmdr",
            "name": "CarrierName",
            "callsign": "AAA-111",
            "from": "Sol",
            "to": "Colonia",
            "body": "Colonia 4",
            "at": 1234567890,
            "lockdown": 1234567890,
            "access": "all",
            "allow_notorious": True
        }
        success = self.discord.fc_jump_scheduled(flight_plan)
        self.assertTrue(success)
        self.mock_session.post.assert_called()

    def test_fc_market_update(self):
        market_data = {
            "owner": "OwnerCmdr",
            "name": "CarrierName",
            "callsign": "AAA-111",
            "summary": "Market Info",
            "location": {"system": "Sol", "body": "Earth"},
            "access": "all",
            "allow_notorious": True,
            "sales": [],
            "purchases": ["Tritium"]
        }
        success = self.discord.fc_market_update(market_data)
        self.assertTrue(success)
        self.mock_session.post.assert_called()
