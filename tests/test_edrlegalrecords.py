

from unittest import TestCase, main
from unittest.mock import MagicMock, patch
import datetime

from edr.edrlegalrecords import EDRLegalRecords

class TestEDRLegalRecords(TestCase):
    def setUp(self):
        self.config_patcher = patch('edr.edrlegalrecords.EDR_CONFIG')
        self.MockEDRConfig = self.config_patcher.start()
        
        # Setup config mock return values
        self.mock_config_instance = self.MockEDRConfig.return_value
        self.mock_config_instance.lru_max_size.return_value = 100
        self.mock_config_instance.legal_records_max_age.return_value = 3600
        self.mock_config_instance.legal_records_recent_threshold.return_value = 7
        self.mock_config_instance.legal_records_check_interval.return_value = 60

        self.lru_patcher = patch('edr.edrlegalrecords.LRUCache')
        self.MockLRUCache = self.lru_patcher.start()
        self.mock_lru_load = self.MockLRUCache.load
        self.mock_records_cache = MagicMock()
        self.mock_lru_load.return_value = self.mock_records_cache
        
        self.log_patcher = patch('edr.edrlegalrecords.EDR_LOG')
        self.mock_log = self.log_patcher.start()

        self.time_patcher = patch('edr.edrlegalrecords.EDTime')
        self.mock_edtime = self.time_patcher.start()

        self.addCleanup(self.config_patcher.stop)
        self.addCleanup(self.lru_patcher.stop)
        self.addCleanup(self.log_patcher.stop)
        self.addCleanup(self.time_patcher.stop)
        
        self.server = MagicMock()
        self.legal_records = EDRLegalRecords(self.server)

    def test_init(self):
        self.mock_lru_load.assert_called_once()
        self.assertEqual(self.legal_records.timespan, 7)
        self.assertEqual(self.legal_records.records_check_interval, 60)

    def test_summarize_no_id(self):
        self.assertIsNone(self.legal_records.summarize(None))

    def test_summarize_no_records_ever(self):
        # Mock cache miss and server returning nothing
        self.mock_records_cache.peek.return_value = None
        self.mock_records_cache.get.side_effect = [None, {"records": None}, {"records": None}] # peek returns entry, get returns entry
        # Actually peek returns values. Logic uses peek.
        # Check implementation:
        # record_entry = self.records.peek(cmdr_id)
        # if not records: ...
        
        # Checking update logic:
        # __update_records_if_stale calls peek -> None -> update
        # update calls server -> None -> set cache
        
        self.server.legal_stats.return_value = None
        
        # summarize calls __update_records_if_stale
        # __update calls __are_records_stale_for_cmdr -> peek -> None -> True
        # __update calls server -> None -> records.set
        
        # then summarize calls peek -> returns whatever records.set put in? 
        # No, peek returns value from mock. We need to update mock behavior if set is called? 
        # Or simpler: set mock to return None first, then return something else?
        # But here we want no records ever. So always None.
        
        self.mock_records_cache.peek.return_value = None
        
        self.assertIsNone(self.legal_records.summarize("cmdr1"))
        self.server.legal_stats.assert_called_with("cmdr1")

    @patch('edr.edrlegalrecords.datetime')
    def test_process_logic_empty(self, mock_datetime):
        # Inject data into cache
        records = {
            "0": {"clean": 10, "wanted": 5, "year": 2025, "max": {"value": 100}, "last": {"value": 50, "timestamp": 123, "starSystem": "Sol"}},
        }
        
        # Mock peek to return this structure directly
        record_entry = {"last_updated": datetime.datetime(2025, 1, 1), "records": records}
        self.mock_records_cache.peek.return_value = record_entry
        
        # Mocks for process interactions
        mock_datetime.datetime.now.return_value.month = 1
        mock_datetime.datetime.now.return_value.year = 2025
        mock_datetime.datetime.now.return_value.day = 1
        
        # Configure subtraction to return a mock with total_seconds
        mock_delta = MagicMock()
        mock_delta.total_seconds.return_value = 1000.0
        mock_datetime.datetime.now.return_value.__sub__.return_value = mock_delta
        
        # Mock EDTime
        self.mock_edtime.pretty_print_timespan.return_value = "7 days"
        self.mock_edtime.t_minus.return_value = "1 hour"
        
        summary = self.legal_records.summarize("cmdr1")
        
        self.assertIsNotNone(summary)
        self.assertIn("overview", summary)
        self.assertIn("clean", summary)
        self.assertIn("wanted", summary)
        
        # Check overview string formatting
        self.assertIn("clean:10", summary["overview"])
        self.assertIn("wanted:5", summary["overview"])

if __name__ == '__main__':
    main()
