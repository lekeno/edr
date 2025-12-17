import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import errno
import zipfile
from edr.edrautoupdater import EDRAutoUpdater

class TestEDRAutoUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = EDRAutoUpdater()

    @patch('requests.get')
    def test_download_latest_fail_no_release(self, mock_get):
        # Mock GitHub API returning not OK or no assets
        mock_get.return_value.status_code = 404
        self.assertFalse(self.updater.download_latest())

    @patch('requests.get')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_download_latest_success(self, mock_exists, mock_makedirs, mock_get):
        # Mock exists to avoid directory creation
        mock_exists.return_value = True
        
        # Mock GitHub API
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.content = b'{"assets": [{"browser_download_url": "http://example.com/latest.zip"}]}'
        
        # Mock File Download
        mock_file_response = Mock()
        mock_file_response.status_code = 200
        mock_file_response.iter_content.return_value = [b'chunk1', b'chunk2']
        
        mock_get.side_effect = [mock_api_response, mock_file_response]
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.assertTrue(self.updater.download_latest())
            mock_file.assert_called_with(self.updater.output, 'wb')
            # Should have written chunks
            handle = mock_file()
            handle.write.assert_any_call(b'chunk1')
            handle.write.assert_any_call(b'chunk2')

    @patch('zipfile.ZipFile')
    def test_extract_latest(self, mock_zipfile):
        mock_zip = Mock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        self.updater.extract_latest()
        mock_zip.extractall.assert_called_with(EDRAutoUpdater.EDR_PATH)

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('os.path.getctime')
    @patch('os.unlink')
    def test_clean_old_backups(self, mock_unlink, mock_getctime, mock_join, mock_listdir):
        # Mock file system with 7 backups
        files = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7']
        mock_listdir.return_value = files
        # Setup join and ctime to simulate order
        mock_join.side_effect = lambda d, f: f"/path/{f}"
        mock_getctime.side_effect = lambda f: int(f[-1]) # Use last char as time
        
        self.updater.clean_old_backups()
        
        # Should keep 5 newest (b3-b7), remove 2 oldest (b1, b2)
        # Note: clean_old_backups logic matches exact implementation
        # The logic sorts by ctime, then iterates 0 to nbfiles - max_backups
        # So it removes oldest files.
        self.assertEqual(mock_unlink.call_count, 2)

    @patch('zipfile.ZipFile')
    @patch('os.walk')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_make_backup(self, mock_exists, mock_makedirs, mock_walk, mock_zipfile):
        mock_exists.return_value = True
        mock_walk.return_value = [('/root', [], ['file1.py'])]
        
        mock_zip = Mock()
        mock_zipfile.return_value = mock_zip
        
        self.updater.make_backup()
        
        mock_zip.write.assert_called()
        mock_zip.close.assert_called()

if __name__ == '__main__':
    unittest.main()
