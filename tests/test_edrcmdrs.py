
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edrcmdrs import EDRCmdrs
from edr.controllers.edrserver import CommsJammedError

class TestEDRCmdrs(unittest.TestCase):
    def setUp(self):
        # Mock Config
        self.config_patch = patch('edr.models.edrcmdrs.EDR_CONFIG')
        self.mock_config = self.config_patch.start()
        self.mock_config.lru_max_size.return_value = 100
        self.mock_config.cmdrs_max_age.return_value = 600
        self.mock_config.inara_max_age.return_value = 600
        self.mock_config.sqdrdex_max_age.return_value = 600
        self.mock_config.edr_heartbeat.return_value = 60

        # Mock LRUCache
        self.lru_patch = patch('edr.models.edrcmdrs.LRUCache')
        self.mock_lru = self.lru_patch.start()
        # LRUCache.load returns a mock cache generic
        self.mock_cmdrs_cache = MagicMock()
        self.mock_inara_cache = MagicMock()
        self.mock_sqdrdex_cache = MagicMock()
        self.mock_lru.load.side_effect = [
            self.mock_cmdrs_cache, 
            self.mock_inara_cache, 
            self.mock_sqdrdex_cache
        ]

        # Mock PlayerOne - careful as it is instantiated in __init__
        self.player_patch = patch('edr.models.edrcmdrs.EDPlayerOne')
        self.mock_player_cls = self.player_patch.start()
        self.mock_player = self.mock_player_cls.return_value
        self.mock_player.name = "CmdrMe"

        # Mock EDRServer
        self.mock_server = MagicMock()
        
        # Mock Time
        self.time_patch = patch('edr.models.edrcmdrs.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.js_epoch_now.return_value = 1000

        # Mock Log
        self.log_patch = patch('edr.models.edrcmdrs.EDR_LOG')
        self.mock_log = self.log_patch.start()

    def tearDown(self):
        self.config_patch.stop()
        self.lru_patch.stop()
        self.player_patch.stop()
        self.time_patch.stop()
        self.log_patch.stop()

    def test_init(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        self.assertEqual(edrcmdrs.player, self.mock_player)
        self.assertEqual(self.mock_lru.load.call_count, 3)

    def test_cmdr_cached_fresh(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        # Setup Cache Hit
        mock_profile = MagicMock()
        mock_profile.name = "CmdrTests"
        self.mock_cmdrs_cache.has_key.return_value = True
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False
        
        profile = edrcmdrs.cmdr("CmdrTests")
        self.assertEqual(profile, mock_profile)
        self.mock_server.cmdr.assert_not_called()

    def test_cmdr_server_fetch(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        # Cache Miss
        self.mock_cmdrs_cache.has_key.return_value = False
        
        # Server Hit
        mock_profile = MagicMock()
        mock_profile.cid = "123"
        mock_profile.name = "CmdrNew"
        self.mock_server.cmdr.return_value = mock_profile
        self.mock_server.cmdrdex.return_value = None # No dex entry
        
        profile = edrcmdrs.cmdr("CmdrNew")
        self.assertEqual(profile, mock_profile)
        self.mock_cmdrs_cache.set.assert_called()

    def test_cmdr_server_fail_fallback(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        # Cache Hit but Stale
        mock_profile_old = MagicMock()
        self.mock_cmdrs_cache.has_key.return_value = True
        self.mock_cmdrs_cache.peek.return_value = mock_profile_old
        self.mock_cmdrs_cache.is_stale.return_value = True
        
        # Server Fail
        self.mock_server.cmdr.side_effect = CommsJammedError("Jammed")
        
        profile = edrcmdrs.cmdr("CmdrStale")
        # Should return old profile
        self.assertEqual(profile, mock_profile_old)
        self.mock_cmdrs_cache.refresh.assert_called()

    def test_tag_cmdr(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        # Mock finding the cmdr
        mock_profile = MagicMock()
        mock_profile.tag.return_value = True
        mock_profile.dex_dict.return_value = {"tag": "outlaw"}
        
        # We need to mock __edr_cmdr internally or mock the cache/server flow
        # easier to mock the cache since __edr_cmdr uses it
        self.mock_cmdrs_cache.has_key.return_value = True
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False
        
        self.mock_server.update_cmdrdex.return_value = True
        
        result = edrcmdrs.tag_cmdr("CmdrGanker", "outlaw")
        self.assertTrue(result)
        mock_profile.tag.assert_called_with("outlaw")
        self.mock_server.update_cmdrdex.assert_called()
        self.mock_cmdrs_cache.__delitem__.assert_called() # Evict

    def test_memo_cmdr(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        mock_profile = MagicMock()
        mock_profile.memo.return_value = True
        
        self.mock_cmdrs_cache.has_key.return_value = True
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False
        
        self.mock_server.update_cmdrdex.return_value = True
        
        result = edrcmdrs.memo_cmdr("CmdrNote", "Watch out")
        self.assertTrue(result)
        mock_profile.memo.assert_called_with("Watch out")
        self.mock_server.update_cmdrdex.assert_called()

    def test_clear_memo(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        mock_profile = MagicMock()
        mock_profile.remove_memo.return_value = True
        
        self.mock_cmdrs_cache.has_key.return_value = True
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False
        
        self.mock_server.update_cmdrdex.return_value = True
        
        result = edrcmdrs.clear_memo_cmdr("CmdrNoNote")
        self.assertTrue(result)
        mock_profile.remove_memo.assert_called()

    def test_contracts(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        self.mock_server.contracts.return_value = [{"id": 1}]
        
        contracts = edrcmdrs.contracts()
        self.assertEqual(len(contracts), 1)

    def test_place_contract(self):
        edrcmdrs = EDRCmdrs(self.mock_server)
        
        mock_profile = MagicMock()
        mock_profile.cid = "100"
        
        self.mock_cmdrs_cache.has_key.return_value = True
        self.mock_cmdrs_cache.peek.return_value = mock_profile
        self.mock_cmdrs_cache.is_stale.return_value = False
        
        self.mock_server.place_contract.return_value = True
        
        result = edrcmdrs.place_contract("CmdrWanted", 100000)
        self.assertTrue(result)
        self.mock_server.place_contract.assert_called_with("100", {"cname": "cmdrwanted", "reward": 100000})

if __name__ == '__main__':
    unittest.main()
