
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
import tempfile
import shutil
from edrautoupdater import EDRAutoUpdater

class TestEDRAutoUpdater(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.updater_target_dir = os.path.join(self.temp_dir, 'edr', 'updates')
        self.backup_target_dir = os.path.join(self.temp_dir, 'edr', 'backup')
        self.edr_path = os.path.join(self.temp_dir, 'edr')
        os.makedirs(self.updater_target_dir)
        os.makedirs(self.backup_target_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('edrautoupdater.requests')
    def test_download_latest_success(self, mock_requests):
        updater = EDRAutoUpdater()
        updater.updates = self.updater_target_dir
        updater.output = os.path.join(self.updater_target_dir, 'latest.zip')
        
        # Mock release URL response
        mock_release_response = MagicMock()
        mock_release_response.status_code = 200
        mock_release_response.json.return_value = {
            "assets": [{"browser_download_url": "http://example.com/latest.zip"}]
        }
        
        # Mock file download response
        mock_file_response = MagicMock()
        mock_file_response.status_code = 200
        mock_file_response.iter_content.return_value = [b"zipdata"]
        
        mock_requests.get.side_effect = [mock_release_response, mock_file_response]
        mock_requests.codes.ok = 200

        self.assertTrue(updater.download_latest())
        self.assertTrue(os.path.exists(updater.output))

    def test_clean_old_backups(self):
        # Create dummy backups
        EDRAutoUpdater.BACKUP = self.backup_target_dir
        for i in range(7):
            with open(os.path.join(self.backup_target_dir, f'backup{i}.zip'), 'w') as f:
                f.write('dummy')
        
        updater = EDRAutoUpdater()
        updater.clean_old_backups()
        
        files = os.listdir(self.backup_target_dir)
        self.assertEqual(len(files), 5)

if __name__ == '__main__':
    unittest.main()
