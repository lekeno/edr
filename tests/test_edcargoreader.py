import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os
import json
from edcargoreader import EDCargoReader # EDR_INTERNAL

class TestEDCargoReader(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # Patch the config object imported in edcargoreader
        self.config_patcher = patch('edcargoreader.config')
        self.mock_config = self.config_patcher.start()
        # Setup mock behavior
        self.mock_config.get_str.side_effect = lambda key: self.test_dir if key == 'journaldir' else None
        self.mock_config.default_journal_dir = self.test_dir
        
        self.log_patcher = patch('edcargoreader.EDR_LOG')
        self.mock_log = self.log_patcher.start()
        
        self.addCleanup(self.config_patcher.stop)
        self.addCleanup(self.log_patcher.stop)

    def test_init(self):
        reader = EDCargoReader()
        self.assertEqual(reader.journal_location, self.test_dir)

    def test_process_success(self):
        cargo_data = {
            "timestamp": "2025-01-01T00:00:00Z",
            "event": "Cargo",
            "Inventory": [
                {"Name": "Gold", "Count": 10},
            ]
        }
        with open(os.path.join(self.test_dir, 'Cargo.json'), 'w') as f:
            json.dump(cargo_data, f)
            
        reader = EDCargoReader()
        result = reader.process()
        self.assertEqual(result, cargo_data)

    def test_process_empty_file(self):
        # Create empty file
        with open(os.path.join(self.test_dir, 'Cargo.json'), 'w') as f:
            pass 
            
        reader = EDCargoReader()
        result = reader.process()
        self.assertIsNone(result)
        # Should not log exception for empty file (polling handling)
        self.assertFalse(self.mock_log.exception.called)

    def test_process_missing_file(self):
        # File doesn't exist
        reader = EDCargoReader()
        result = reader.process()
        self.assertIsNone(result)
        # Should log exception because open() raises FileNotFoundError
        self.assertTrue(self.mock_log.exception.called)
        self.mock_log.exception.assert_called_with("Couldn't process cargo")

    def test_process_invalid_json(self):
        with open(os.path.join(self.test_dir, 'Cargo.json'), 'w') as f:
            f.write("Invalid JSON")
            
        reader = EDCargoReader()
        result = reader.process()
        self.assertIsNone(result)
        # Should log exception because json.loads raises JSONDecodeError
        self.assertTrue(self.mock_log.exception.called)

if __name__ == '__main__':
    unittest.main()
