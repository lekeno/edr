
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
import tempfile
import shutil
import zipfile
from edr.core.edrautoupdater import EDRAutoUpdater

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

    @patch('edr.core.edrautoupdater.requests')
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

    def test_extract_latest_migration(self):
        # Setup: Simulate old flat install
        # Create dummy flat files that should be removed
        obsolete_files = ['edrclient.py', 'edrutils.py', '__init__.py']
        
        for f in obsolete_files:
            with open(os.path.join(self.edr_path, f), 'w') as fh:
                fh.write("old code")
        
        # Verify they exist
        for f in obsolete_files:
            self.assertTrue(os.path.exists(os.path.join(self.edr_path, f)))

        # Create a mock update zip with the NEW structure
        updater = EDRAutoUpdater()
        updater.EDR_PATH = self.edr_path
        updater.updates = self.updater_target_dir
        updater.output = os.path.join(self.updater_target_dir, 'latest.zip')
        
        with zipfile.ZipFile(updater.output, 'w') as zf:
            zf.writestr('edr/__init__.py', '')
            zf.writestr('edr/edrclient.py', 'new code')

        # Run extraction
        self.assertTrue(updater.extract_latest())

        # Verify obsolete files are gone
        for f in obsolete_files:
            self.assertFalse(os.path.exists(os.path.join(self.edr_path, f)), f"File {f} should have been deleted")

        # Verify new files exist
        self.assertTrue(os.path.exists(os.path.join(self.edr_path, 'edr', '__init__.py')))
        self.assertTrue(os.path.exists(os.path.join(self.edr_path, 'edr', 'edrclient.py')))

if __name__ == '__main__':
    unittest.main()
