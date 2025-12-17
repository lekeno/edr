import unittest
from unittest.mock import Mock, patch, mock_open
import json
from edmodulesinforeader import EDModulesInfoReader # EDR_INTERNAL

class TestEDModulesInfoReader(unittest.TestCase):
    @patch('edr.edmodulesinforeader.config')
    def test_process_valid(self, mock_config):
        mock_config.get_str.return_value = "/tmp/journal"
        mock_data = json.dumps({"timestamp": "2023-01-01T12:00:00Z", "event": "ModulesInfo", "Modules": []})
        
        with patch('edr.edmodulesinforeader.open', mock_open(read_data=mock_data)):
            reader = EDModulesInfoReader()
            result = reader.process()
            self.assertEqual(result.get("event"), "ModulesInfo")
            self.assertEqual(result.get("Modules"), [])

    @patch('edr.edmodulesinforeader.config')
    def test_process_empty(self, mock_config):
        mock_config.get_str.return_value = "/tmp/journal"
        
        with patch('edr.edmodulesinforeader.open', mock_open(read_data="")):
            reader = EDModulesInfoReader()
            result = reader.process()
            self.assertIsNone(result)

    @patch('edr.edmodulesinforeader.config')
    def test_process_invalid_json(self, mock_config):
        mock_config.get_str.return_value = "/tmp/journal"
        
        with patch('edr.edmodulesinforeader.open', mock_open(read_data="{invalid_json")):
            with patch('edr.edmodulesinforeader.EDR_LOG') as mock_log:
                reader = EDModulesInfoReader()
                result = reader.process()
                self.assertIsNone(result)
                mock_log.exception.assert_called_with("Couldn't process modulesinfo")

if __name__ == '__main__':
    unittest.main()
