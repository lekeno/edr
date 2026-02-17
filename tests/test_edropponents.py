
import unittest
from unittest.mock import MagicMock, patch, mock_open
import datetime
import time
from edr.controllers.edropponents import EDROpponents

class TestEDROpponents(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        self.server.nodify.return_value = "power_node"
        self.callback = MagicMock()
        
        self.config_patch = patch('edr.controllers.edropponents.edrconfig.EDR_CONFIG')
        self.mock_config = self.config_patch.start()
        self.mock_config.lru_max_size.return_value = 100
        self.mock_config.opponents_max_age.return_value = 3600
        self.mock_config.opponents_max_recents.return_value = 10
        self.mock_config.opponents_recent_threshold.return_value = 600
        self.mock_config.reports_check_interval.return_value = 60
        
        self.lru_patch = patch('edr.controllers.edropponents.lrucache.LRUCache')
        self.mock_lru = self.lru_patch.start()
        self.mock_lru.load.return_value = MagicMock()
        
        self.pickle_patch = patch('edr.controllers.edropponents.pickle')
        self.mock_pickle = self.pickle_patch.start()
        from collections import deque
        self.mock_pickle.load.return_value = deque()
        
        self.open_patch = patch('edr.controllers.edropponents.open', mock_open(), create=True)
        self.mock_open = self.open_patch.start()
        
        self.i18n_patch = patch('edr.controllers.edropponents._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()

    def tearDown(self):
        self.config_patch.stop()
        self.lru_patch.stop()
        self.pickle_patch.stop()
        self.open_patch.stop()
        self.i18n_patch.stop()

    def test_init_outlaws(self):
        opponents = EDROpponents(self.server, EDROpponents.OUTLAWS, self.callback)
        self.assertEqual(opponents.kind, EDROpponents.OUTLAWS)
        self.mock_lru.load.assert_called_once()

    def test_where_cached(self):
        opponents = EDROpponents(self.server, EDROpponents.OUTLAWS, self.callback)
        # Setup cache hit
        opponents.sightings.get.return_value = {
            "timestamp": 1234567890,
            "cmdr": "BadGuy",
            "starSystem": "Anarchy System",
            "place": "Haz RES",
            "ship": "FDL",
            "bounty": 10000
        }
        opponents.sightings.last_updated = datetime.datetime.now()
        
        report = opponents.where("BadGuy")
        self.assertIsNotNone(report)
        self.assertEqual(report["timestamp"], 1234567890)
        self.server.where.assert_not_called()

    def test_where_server(self):
        opponents = EDROpponents(self.server, EDROpponents.OUTLAWS, self.callback)
        opponents.sightings.get.return_value = None
        opponents.sightings.last_updated = datetime.datetime.now()
        
        server_report = {
            "timestamp": 1234567890,
            "cmdr": "BadGuy",
            "starSystem": "Anarchy System",
            "place": "Haz RES",
            "ship": "FDL",
            "bounty": 10000
        }
        self.server.where.return_value = server_report
        
        report = opponents.where("BadGuy")
        self.assertIsNotNone(report)
        self.server.where.assert_called_once()
        opponents.sightings.set.assert_called_once()

    def test_pledged_to_enemies(self):
        opponents = EDROpponents(self.server, EDROpponents.ENEMIES, self.callback)
        opponents.pledged_to("Aisling Duval", 100)
        self.assertEqual(opponents.powerplay, "Aisling Duval")
        
        # Changing pledge should reset cache
        opponents.sightings = MagicMock() 
        opponents.sightings.last_updated = datetime.datetime.now()
        
        opponents.pledged_to("Felicia Winters", 100)
        self.assertEqual(opponents.powerplay, "Felicia Winters")
        
    def test_recent_sightings(self):
        opponents = EDROpponents(self.server, EDROpponents.OUTLAWS, self.callback)
        now = time.mktime(datetime.datetime.now().timetuple()) * 1000
        opponents.recents = [{
            "timestamp": now - 10000, # 10s ago
            "cmdr": "BadGuy",
            "starSystem": "Anarchy",
            "place": "Nav Beacon",
            "ship": "Eagle",
            "bounty": 500
        }]
        
        # Test assumes not stale
        opponents.sightings.last_updated = datetime.datetime.now()
        
        summary = opponents.recent_sightings()
        self.assertIsNotNone(summary)
        self.assertEqual(len(summary), 1)
        self.assertIn("BadGuy", summary[0])

    def test_update_opponents_if_stale(self):
        opponents = EDROpponents(self.server, EDROpponents.OUTLAWS, self.callback)
        opponents.sightings.last_updated = datetime.datetime.now() - datetime.timedelta(seconds=120) # Stale
        opponents.sightings.get.return_value = None
        self.mock_config.reports_check_interval.return_value = 60
        
        self.server.recent_outlaws.return_value = [{
            "timestamp": 123, "cmdr": "FreshGuy"
        }]
        
        # Accessing private method via name mangling or just triggering where/recent_sightings
        # using recent_sightings triggers __update_opponents_if_stale
        
        opponents.recent_sightings()
        self.server.recent_outlaws.assert_called_once()

if __name__ == '__main__':
    unittest.main()
