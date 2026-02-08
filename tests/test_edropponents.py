import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import datetime

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edropponents import EDROpponents # EDR_INTERNAL

class TestEDROpponents(unittest.TestCase):
    def setUp(self):
        self.config_patch = patch('edrconfig.EDR_CONFIG')
        self.mock_config = self.config_patch.start()
        self.addCleanup(self.config_patch.stop)
        
        self.mock_config.lru_max_size.return_value = 100
        self.mock_config.opponents_max_age.return_value = 3600
        self.mock_config.opponents_max_recents.return_value = 10
        self.mock_config.opponents_recent_threshold.return_value = 600
        self.mock_config.reports_check_interval.return_value = 300
        self.mock_config.intel_bounty_threshold.return_value = 50000

        self.lru_patch = patch('edropponents.lrucache.LRUCache')
        self.mock_lru = self.lru_patch.start()
        self.addCleanup(self.lru_patch.stop)
        
        # Mock load to return a fresh mock instead of None
        self.mock_cache_instance = MagicMock()
        self.mock_lru.load.return_value = self.mock_cache_instance
        # Mock class instantiation to return same instance
        self.mock_lru.return_value = self.mock_cache_instance 

        self.mock_server = MagicMock()
        self.mock_callback = MagicMock()

        # Patch pickle and open inside edr.edropponents to avoid global side effects
        self.pickle_patch = patch('edropponents.pickle')
        self.mock_pickle = self.pickle_patch.start()
        self.addCleanup(self.pickle_patch.stop)
        self.mock_pickle.load.return_value = []
        
        self.open_patch = patch('edropponents.open', create=True)
        self.mock_open = self.open_patch.start()
        self.addCleanup(self.open_patch.stop)
        self.mock_open.return_value.__enter__.return_value = MagicMock()

        self.opponents = EDROpponents(self.mock_server, EDROpponents.OUTLAWS, self.mock_callback)

    def tearDown(self):
        pass

    def test_init(self):
        self.mock_lru.load.assert_called_once()
        self.assertEqual(self.opponents.kind, EDROpponents.OUTLAWS)

    def test_where_cached_valid(self):
        # Setup cache hit
        report = {"timestamp": 1000, "cmdr": "BadGuy", "starSystem": "Anarchy", "place": None, "ship": "FDL", "bounty": 1000}
        self.mock_cache_instance.get.return_value = report
        # Configure sightings.last_updated to be recent
        self.mock_cache_instance.last_updated = datetime.datetime.now()
        
        result = self.opponents.where("BadGuy")
        
        self.mock_cache_instance.get.assert_called_with("badguy")
        self.mock_server.where.assert_not_called()
        self.assertIsNotNone(result)

    def test_where_server_fetch(self):
        # Setup cache miss
        self.mock_cache_instance.get.return_value = None
        self.mock_cache_instance.last_updated = datetime.datetime.now()
        
        server_report = {"timestamp": 2000, "cmdr": "BadGuy", "starSystem": "Anarchy", "place": None, "ship": "FDL", "bounty": 1000}
        self.mock_server.where.return_value = server_report
        
        result = self.opponents.where("BadGuy")
        
        self.mock_server.where.assert_called_with("BadGuy", None)
        self.mock_cache_instance.set.assert_called_with("badguy", server_report)
        self.assertIsNotNone(result)

    def test_where_server_fetch_fail(self):
        self.mock_cache_instance.get.return_value = None
        self.mock_cache_instance.last_updated = datetime.datetime.now()
        self.mock_server.where.return_value = None
        
        result = self.opponents.where("Ghost")
        
        self.assertIsNone(result)

    def test_pledged_to(self):
        # For OUTLAWS, pledged_to does nothing
        self.opponents.pledged_to("Empire", 100)
        self.assertIsNone(self.opponents.powerplay)
        
        # For ENEMIES
        enemies = EDROpponents(self.mock_server, EDROpponents.ENEMIES, self.mock_callback)
        enemies.pledged_to("Empire", 100)
        self.assertEqual(enemies.powerplay, "Empire")
        
    def test_pledged_to_change_resets_cache(self):
        enemies = EDROpponents(self.mock_server, EDROpponents.ENEMIES, self.mock_callback)
        enemies.pledged_to("Empire", 100)
        
        # Reset cache check
        self.mock_lru.reset_mock()
        enemies.pledged_to("Federation", 100)
        
        # Should re-init cache (create new LRUCache)
        self.mock_lru.assert_called()
        self.assertEqual(enemies.powerplay, "Federation")

if __name__ == '__main__':
    unittest.main()
