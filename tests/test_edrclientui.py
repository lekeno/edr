
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import sys

# Mocking dependencies for EDRClientUI
import sys
from unittest.mock import MagicMock, patch

class TestEDRClientUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We need to mock these for the duration of the tests in this file
        cls.mock_edri18n = MagicMock()
        cls.mock_edri18n._.side_effect = lambda x: x
        cls.mock_edri18n.ugettext.side_effect = lambda x: x

        # Create a mock class for EDRTogglingPanel
        cls.mock_toggling_panel_class = MagicMock()

        cls.mocks = {
            'myNotebook': MagicMock(),
            'ttkHyperlinkLabel': MagicMock(),
            'edrtogglingpanel': MagicMock(),
            'edri18n': cls.mock_edri18n
        }
        # Ensure the mock module has the mock class
        cls.mocks['edrtogglingpanel'].EDRTogglingPanel = cls.mock_toggling_panel_class

        cls.patcher = patch.dict('sys.modules', cls.mocks)
        cls.patcher.start()

        # Import or reload EDRClientUI only after mocking its dependencies
        import edrclientui
        import importlib
        importlib.reload(edrclientui)
        cls.EDRClientUI = edrclientui.EDRClientUI

    @classmethod
    def tearDownClass(cls):
        # Clean up sys.modules to avoid pollution for other test files
        cls.patcher.stop()

    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_parent = MagicMock()
        self.ui = self.EDRClientUI(self.mock_client, self.mock_parent)

    def test_init_creates_toggling_panel(self):
        self.assertIsNotNone(self.ui.ui)
        self.ui.ui.notify.assert_called()

    def test_proxied_methods(self):
        self.ui.refresh_theme()
        self.ui.ui.refresh_theme.assert_called_once()
        
        self.ui.clear()
        self.ui.ui.clear.assert_called_once()

    @patch('edrclientui.notebook')
    def test_prefs_ui(self, mock_notebook):
        mock_frame = MagicMock()
        mock_notebook.Frame.return_value = mock_frame
        
        frame = self.ui.prefs_ui(self.mock_parent)
        self.assertEqual(frame, mock_frame)
        mock_notebook.Frame.assert_any_call(self.mock_parent)

if __name__ == '__main__':
    unittest.main()
