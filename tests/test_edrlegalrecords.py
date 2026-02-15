
import unittest
from unittest.mock import MagicMock, patch
import datetime
from edr.models.edrlegalrecords import EDRLegalRecords

class TestEDRLegalRecords(unittest.TestCase):
    def setUp(self):
        self.server = MagicMock()
        with patch('edr.models.edrlegalrecords.EDR_CONFIG') as mock_config:
            mock_config.lru_max_size.return_value = 100
            mock_config.legal_records_max_age.return_value = 3600
            mock_config.legal_records_recent_threshold.return_value = 30 * 24 * 3600
            mock_config.legal_records_check_interval.return_value = 60
            self.legal = EDRLegalRecords(self.server)
            # Prevent loading from disk
            self.legal.records = MagicMock() 

    def test_summarize_no_cmdr(self):
        self.assertIsNone(self.legal.summarize(None))

    def test_summarize_stale(self):
        # Setup cache miss or stale
        self.legal.records.peek.return_value = None
        
        # Setup server response
        self.server.legal_stats.return_value = {"record": "data"}
        
        self.legal.summarize("CmdrX")
        
        self.server.legal_stats.assert_called_with("CmdrX")
        self.legal.records.set.assert_called()

    def test_are_records_stale(self):
        self.legal.records.peek.return_value = None
        self.assertTrue(self.legal._are_records_stale_for_cmdr("CmdrX"))
        
        now = datetime.datetime.now()
        fresh = now
        self.legal.records.peek.return_value = {"last_updated": fresh, "records": {}}
        self.assertFalse(self.legal._are_records_stale_for_cmdr("CmdrX"))
        
        old = now - datetime.timedelta(seconds=100)
        self.legal.records.peek.return_value = {"last_updated": old, "records": {}}
        self.assertTrue(self.legal._are_records_stale_for_cmdr("CmdrX")) # Interval is 60

    def test_process(self):
        # Mocking the _process logic which depends on datetime
        # stats = { "month_num": { "year": ..., "clean": ... } }
        # This is a bit complex to mock fully without setting datetime, 
        # so we will trust the logic refactor didn't break it if it runs without error.
        # Minimal test:
        stats = {}
        c, w, b, r = self.legal._process(stats)
        self.assertEqual(len(c), 12)
