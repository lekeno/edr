
import unittest
from unittest.mock import MagicMock, patch, call
import tkinter as tk
import sys

class TestEDRClientUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clean up any potential pollution
        sys.modules.pop('edr.ui.edrclientui', None)
        sys.modules.pop('edr.ui.edrtogglingpanel', None)
        sys.modules.pop('edr.ui', None)

        # We need to mock these for the duration of the tests in this file
        cls.mock_edri18n = MagicMock()
        cls.mock_edri18n._.side_effect = lambda x: x
        cls.mock_edri18n.ugettext.side_effect = lambda x: x

        # Create a mock class for EDRTogglingPanel
        cls.mock_toggling_panel_class = MagicMock()
        cls.mock_toggling_panel_instance = MagicMock()
        cls.mock_toggling_panel_class.return_value = cls.mock_toggling_panel_instance

        cls.mocks = {
            'myNotebook': MagicMock(),
            'ttkHyperlinkLabel': MagicMock(),
            'edr.ui.edrtogglingpanel': MagicMock(),
            'edr.core.edri18n': cls.mock_edri18n
        }
        # Ensure the mock module has the mock class
        cls.mocks['edr.ui.edrtogglingpanel'].EDRTogglingPanel = cls.mock_toggling_panel_class

        cls.patcher = patch.dict('sys.modules', cls.mocks)
        cls.patcher.start()

        # Import EDRClientUI only after mocking its dependencies
        sys.modules.pop('edr.ui.edrclientui', None)
        from edr.ui import edrclientui
        cls.EDRClientUI = edrclientui.EDRClientUI

    @classmethod
    def tearDownClass(cls):
        # Clean up sys.modules to avoid pollution for other test files
        cls.patcher.stop()

    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_parent = MagicMock()
        # Reset the mock instance for each test
        TestEDRClientUI.mock_toggling_panel_class.return_value = MagicMock()
        self.ui = self.EDRClientUI(self.mock_client, self.mock_parent)

    def test_init_creates_toggling_panel(self):
        self.assertIsNotNone(self.ui.ui)
        self.ui.ui.notify.assert_called()

    def test_app_ui(self):
        self.assertEqual(self.ui.app_ui(), self.ui.ui)

    def test_proxied_methods(self):
        self.ui.refresh_theme()
        self.ui.ui.refresh_theme.assert_called_once()
        
        self.ui.clear()
        self.ui.ui.clear.assert_called_once()

    def test_entry_methods(self):
        self.ui.enable_entry()
        self.ui.ui.enable_entry.assert_called_once()

        self.ui.disable_entry()
        self.ui.ui.disable_entry.assert_called_once()

    def test_notification_methods(self):
        self.ui.notify("Header", "Body")
        self.ui.ui.notify.assert_called_with("Header", "Body")

        self.ui.help("Help Header", "Help Body")
        self.ui.ui.help.assert_called_with("Help Header", "Help Body")
        
        self.ui.intel("Intel Header", "Intel Body")
        self.ui.ui.intel.assert_called_with("Intel Header", "Intel Body")

        self.ui.sitrep("Sitrep Header", "Sitrep Body")
        self.ui.ui.sitrep.assert_called_with("Sitrep Header", "Sitrep Body")

        self.ui.warning("Warning Header", "Warning Body")
        self.ui.ui.warning.assert_called_with("Warning Header", "Warning Body")

    def test_link_methods(self):
        self.ui.nolink()
        self.ui.ui.nolink.assert_called_once()

        self.ui.link("http://example.com")
        self.ui.ui.link.assert_called_with("http://example.com")

    @patch('edr.ui.edrclientui.notebook')
    @patch('edr.ui.edrclientui.ttkHyperlinkLabel')
    def test_prefs_ui_construction(self, mock_hyperlink, mock_notebook):
        mock_frame = MagicMock()
        mock_notebook.Frame.return_value = mock_frame
        
        # Setup mocks for UI components
        mock_notebook.Label.return_value = MagicMock()
        mock_notebook.EntryMenu.return_value = MagicMock()
        mock_notebook.Checkbutton.return_value = MagicMock()
        mock_notebook.OptionMenu.return_value = MagicMock()
        
        frame = self.ui.prefs_ui(self.mock_parent)
        self.assertEqual(frame, mock_frame)
        mock_notebook.Frame.assert_any_call(self.mock_parent)
        
        # Verify components creation
        self.assertTrue(mock_notebook.Label.called)
        self.assertTrue(mock_hyperlink.HyperlinkLabel.called)

    @patch('edr.ui.edrclientui.notebook')
    @patch('edr.ui.edrclientui.ttkHyperlinkLabel')
    def test_toggle_fc_links(self, mock_hyperlink, mock_notebook):
        # We need to access the private method __toggle_fc_links.
        # It's mangled to _EDRClientUI__toggle_fc_links
        
        # First call prefs_ui to setup the links (which are instance attributes like self._private_fc_link)
        mock_frame = MagicMock()
        mock_notebook.Frame.return_value = mock_frame
        
        # We need the HyperlinkLabel mocks to be distinct so we can verify grid/grid_remove
        mock_private_link = MagicMock()
        mock_direct_link = MagicMock() # This is a Label in code, not Hyperlink, but uses notebook.Label
        
        mock_hyperlink.HyperlinkLabel.side_effect = [MagicMock(), MagicMock(), MagicMock(), mock_private_link] # 4th one is the private link
        mock_notebook.Label.side_effect = lambda *args, **kwargs: mock_direct_link if "user_config.ini" in kwargs.get('text', '') else MagicMock()
        
        # Actually logic is:
        # 1. website link
        # 2. community link
        # 3. credentials label
        # 4. cred label 2
        # 5. apply link
        # ...
        # self._private_fc_link = HyperlinkLabel(...)
        # self._direct_fc_link = Label(...)
        
        # To robustly test this without fragile side_effects on mocks, we can inspect setting attributes
        # But prefs_ui sets them.
        
        self.ui.prefs_ui(self.mock_parent)
        
        # Now test the toggle method
        toggle_method = getattr(self.ui, "_EDRClientUI__toggle_fc_links")
        
        # Private
        toggle_method('Private')
        self.ui._private_fc_link.grid.assert_called()
        self.ui._direct_fc_link.grid_remove.assert_called()
        
        self.ui._private_fc_link.reset_mock()
        self.ui._direct_fc_link.reset_mock()

        # Direct
        toggle_method('Direct')
        self.ui._direct_fc_link.grid.assert_called()
        self.ui._private_fc_link.grid_remove.assert_called()
        
        self.ui._private_fc_link.reset_mock()
        self.ui._direct_fc_link.reset_mock()

        # Other (Never/Public)
        toggle_method('Never')
        self.ui._private_fc_link.grid_remove.assert_called()
        self.ui._direct_fc_link.grid_remove.assert_called()

if __name__ == '__main__':
    unittest.main()
