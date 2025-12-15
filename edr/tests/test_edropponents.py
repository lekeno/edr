import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import datetime

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edr.edropponents import EDROpponents

class TestEDROpponents(unittest.TestCase):
    def setUp(self):
        self.config_patch = patch('edrconfig.EDRConfig')
        self.mock_config = self.config_patch.start()
        
        # Patch edentities.EDRConfig because it is imported via 'from edrconfig import'
        self.edentities_config_patch = patch('edentities.EDRConfig')
        self.mock_edentities_config = self.edentities_config_patch.start()
        self.mock_edentities_config.return_value = self.mock_config.return_value

        self.mock_config.return_value.lru_max_size.return_value = 100
        self.mock_config.return_value.opponents_max_age.return_value = 3600
        self.mock_config.return_value.opponents_max_recents.return_value = 10
        self.mock_config.return_value.opponents_recent_threshold.return_value = 600
        self.mock_config.return_value.reports_check_interval.return_value = 300
        self.mock_config.return_value.intel_bounty_threshold.return_value = 50000

        self.lru_patch = patch('edr.edropponents.lrucache.LRUCache')
        self.mock_lru = self.lru_patch.start()
        # Mock load to return a fresh mock instead of None
        self.mock_cache_instance = MagicMock()
        self.mock_lru.load.return_value = self.mock_cache_instance
        # Mock class instantiation to return same instance
        self.mock_lru.return_value = self.mock_cache_instance 

        self.mock_server = MagicMock()
        self.mock_callback = MagicMock()

        # Suppress pickle loading
        self.pickle_patch = patch('edr.edropponents.pickle')
        self.mock_pickle = self.pickle_patch.start()
        self.mock_pickle.load.return_value = []
        
        # Suppress file open
        self.open_patch = patch('builtins.open', mock_open())
        self.mock_open = self.open_patch.start()

        self.opponents = EDROpponents(self.mock_server, EDROpponents.OUTLAWS, self.mock_callback)

    def tearDown(self):
        self.edentities_config_patch.stop()
        self.config_patch.stop()
        self.lru_patch.stop()
        self.pickle_patch.stop()
        self.open_patch.stop()

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
