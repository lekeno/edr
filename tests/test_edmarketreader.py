import unittest
from unittest.mock import Mock, patch, mock_open
import json
from edr.edmarketreader import EDMarketReader

class TestEDMarketReader(unittest.TestCase):
    @patch('edr.edmarketreader.config')
    def test_process_valid(self, mock_config):
        mock_config.get_str.return_value = "/tmp/journal"
        mock_data = json.dumps({"timestamp": "2023-01-01T12:00:00Z", "event": "Market", "Items": []})
        
        with patch('edr.edmarketreader.open', mock_open(read_data=mock_data)):
            reader = EDMarketReader()
            result = reader.process()
            self.assertEqual(result.get("event"), "Market")
            self.assertEqual(result.get("Items"), [])

    @patch('edr.edmarketreader.config')
    def test_process_empty(self, mock_config):
        mock_config.get_str.return_value = "/tmp/journal"
        
        with patch('edr.edmarketreader.open', mock_open(read_data="")):
            reader = EDMarketReader()
            result = reader.process()
            self.assertIsNone(result)

    @patch('edr.edmarketreader.config')
    def test_process_invalid_json(self, mock_config):
        mock_config.get_str.return_value = "/tmp/journal"
        
        with patch('edr.edmarketreader.open', mock_open(read_data="{invalid_json")):
            with patch('edr.edmarketreader.EDR_LOG') as mock_log:
                reader = EDMarketReader()
                result = reader.process()
                self.assertIsNone(result)
                mock_log.exception.assert_called_with("Couldn't process market")

if __name__ == '__main__':
    unittest.main()
