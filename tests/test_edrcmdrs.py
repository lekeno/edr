import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os

from edrcmdrs import EDRCmdrs # EDR_INTERNAL

class TestEDRCmdrs(unittest.TestCase):
    def setUp(self):
        self.edr_server = MagicMock()
        
        # Patch dependencies
        self.edr_config_patch = patch('edr.edrcmdrs.EDR_CONFIG')
        self.edr_config = self.edr_config_patch.start()
        self.edr_config.return_value.lru_max_size.return_value = 100
        self.edr_config.return_value.cmdrs_max_age.return_value = 3600
        self.edr_config.return_value.inara_max_age.return_value = 3600
        self.edr_config.return_value.sqdrdex_max_age.return_value = 3600
        self.edr_config.return_value.edr_heartbeat.return_value = 60
        self.edr_config.return_value.noteworthy_pledge_threshold.return_value = 600

        # Distinct mocks for caches to allow separate assertion checks
        self.mock_cmdrs_cache = MagicMock()
        self.mock_inara_cache = MagicMock()
        self.mock_sqdrdex_cache = MagicMock()

        self.lru_cache_patch = patch('edr.edrcmdrs.LRUCache')
        self.lru_cache_cls = self.lru_cache_patch.start()
        # Return different mocks sequentially
        self.lru_cache_cls.load.side_effect = [
            self.mock_cmdrs_cache,
            self.mock_inara_cache,
            self.mock_sqdrdex_cache
        ]

        self.ed_player_one_patch = patch('edr.edrcmdrs.EDPlayerOne')
        self.ed_player_one_cls = self.ed_player_one_patch.start()
        self.ed_player_one_cls.return_value = MagicMock()
        self.ed_player_one_cls.return_value.name = "CmdrTest"

        # Initialize EDRCmdrs
        self.cmdrs = EDRCmdrs(self.edr_server)

    def tearDown(self):
        self.edr_config_patch.stop()
        self.lru_cache_patch.stop()
        self.ed_player_one_patch.stop()

    def test_init(self):
        self.assertIsNotNone(self.cmdrs.cmdrs_cache)
        self.assertIsNotNone(self.cmdrs.inara_cache)
        self.assertIsNotNone(self.cmdrs.sqdrdex_cache)
        self.assertEqual(self.cmdrs.player.name, "CmdrTest")

    def test_persist(self):
        self.cmdrs.persist()
        self.mock_cmdrs_cache.save.assert_called_once()
        self.mock_inara_cache.save.assert_called_once()
        self.mock_sqdrdex_cache.save.assert_called_once()

    def test_cmdr_cached(self):
        # Setup cache hit
        mock_profile = MagicMock()
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False
        
        profile = self.cmdrs.cmdr("TestCmdr")
        
        self.assertEqual(profile, mock_profile)
        self.edr_server.cmdr.assert_not_called()

    def test_cmdr_server_fetch(self):
        # Setup cache miss
        self.mock_cmdrs_cache.peek.return_value = None
        mock_profile = MagicMock()
        mock_profile.cid = "12345"
        self.edr_server.cmdr.return_value = mock_profile
        self.edr_server.cmdrdex.return_value = None # No dex entry

        profile = self.cmdrs.cmdr("TestCmdr", check_inara_server=False)
        
        self.assertEqual(profile, mock_profile)
        self.edr_server.cmdr.assert_called_with("TestCmdr", True)
        self.mock_cmdrs_cache.set.assert_called()

    def test_tag_cmdr(self):
        # Needs a profile to tag
        mock_profile = MagicMock()
        mock_profile.cid = "12345"
        mock_profile.tag.return_value = True
        mock_profile.dex_dict.return_value = {"tags": ["outlaw"]}
        
        # Mock __edr_cmdr internally or mock server response
        self.mock_cmdrs_cache.peek.return_value = None
        self.edr_server.cmdr.return_value = mock_profile
        self.edr_server.cmdrdex.return_value = None
        self.edr_server.update_cmdrdex.return_value = True

        success = self.cmdrs.tag_cmdr("TestCmdr", "outlaw")
        
        self.assertTrue(success)
        mock_profile.tag.assert_called_with("outlaw")
        self.edr_server.update_cmdrdex.assert_called_with("12345", {"tags": ["outlaw"]})

    def test_untag_cmdr(self):
        mock_profile = MagicMock()
        mock_profile.cid = "12345"
        mock_profile.untag.return_value = True
        mock_profile.dex_dict.return_value = {"tags": []}

        self.mock_cmdrs_cache.peek.return_value = None
        self.edr_server.cmdr.return_value = mock_profile
        self.edr_server.cmdrdex.return_value = None
        self.edr_server.update_cmdrdex.return_value = True

        success = self.cmdrs.untag_cmdr("TestCmdr", "outlaw")
        
        self.assertTrue(success)
        mock_profile.untag.assert_called_with("outlaw")
        self.edr_server.update_cmdrdex.assert_called_with("12345", {"tags": []})

    def test_is_friend(self):
        mock_profile = MagicMock()
        mock_profile.is_friend.return_value = True
        
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False

        self.assertTrue(self.cmdrs.is_friend("FriendCmdr"))

if __name__ == '__main__':
    unittest.main()
