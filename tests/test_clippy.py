import unittest
from unittest.mock import patch, MagicMock
import sys
# We need to import clippy after patching if we want to test platform specific import logic, 
# but usually we just test the functions it exports.
from edr.utils import clippy

class TestClippy(unittest.TestCase):
    
    @patch('edr.utils.clippy.ctypes')
    @patch('edr.utils.clippy.user32')
    @patch('edr.utils.clippy.kernel32')
    def test_win_set_clipboard(self, mock_kernel, mock_user, mock_ctypes):
        # Simulate Windows environment behavior mostly for logic coverage
        # This prevents actual clipboard access
        
        # Setup mocks
        mock_user.OpenClipboard.return_value = True
        mock_kernel.GlobalLock.return_value = 12345 # Fake address
        mock_user.SetClipboardData.return_value = True
        
        # Test
        success = clippy._win_set_clipboard("Test Content")
        
        # Verify calls
        mock_user.OpenClipboard.assert_called()
        mock_user.EmptyClipboard.assert_called()
        mock_kernel.GlobalAlloc.assert_called()
        mock_kernel.GlobalLock.assert_called()
        mock_kernel.GlobalUnlock.assert_called()
        mock_user.SetClipboardData.assert_called()
        mock_user.CloseClipboard.assert_called()
        self.assertTrue(success)

    @patch('edr.utils.clippy.ctypes')
    @patch('edr.utils.clippy.user32')
    @patch('edr.utils.clippy.kernel32')
    def test_win_get_clipboard(self, mock_kernel, mock_user, mock_ctypes):
         # Setup mocks
        mock_user.OpenClipboard.return_value = True
        mock_user.GetClipboardData.return_value = 999
        mock_kernel.GlobalLock.return_value = 12345
        
        # Mock ctypes.c_wchar_p(p_contents).value
        # When called with 12345, return an object with a value attribute
        mock_c_wchar_p = MagicMock()
        mock_c_wchar_p.value = "Windows Content"
        mock_ctypes.c_wchar_p.return_value = mock_c_wchar_p
        
        result = clippy._win_get_clipboard()
        self.assertEqual(result, "Windows Content")
        mock_user.OpenClipboard.assert_called()
        mock_user.CloseClipboard.assert_called()

    @patch('edr.utils.clippy.user32')
    def test_win_get_clipboard_fail_open(self, mock_user):
        mock_user.OpenClipboard.return_value = False
        result = clippy._win_get_clipboard()
        self.assertIsNone(result)

    @patch('edr.utils.clippy.subprocess')
    @patch('edr.utils.clippy.platform')
    def test_unix_clipboard(self, mock_platform, mock_subprocess):
        # Test generic unix path (xclip)
        mock_platform.system.return_value = 'Linux'
        
        # Set
        clippy._unix_set_clipboard("Linux Test")
        mock_subprocess.run.assert_called_with(['xclip', '-selection', 'clipboard'], input="Linux Test", check=True, text=True)
        
        # Get
        mock_subprocess.run.return_value.stdout = "Linux Paste"
        result = clippy._unix_get_clipboard()
        self.assertEqual(result, "Linux Paste")
        
        # Test Mac path (pbcopy/pbpaste)
        mock_platform.system.return_value = 'Darwin'
        
        # Set
        clippy._unix_set_clipboard("Mac Test")
        mock_subprocess.run.assert_called_with(['pbcopy'], input="Mac Test", check=True, text=True)

if __name__ == '__main__':
    unittest.main()