import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock UI dependencies before importing edrclientui
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['myNotebook'] = MagicMock()
sys.modules['ttkHyperlinkLabel'] = MagicMock()

from edrclientui import EDRClientUI # EDR_INTERNAL

class TestEDRClientUI(unittest.TestCase):
    def setUp(self):
        self.edr_client = MagicMock()
        self.edr_client._status = MagicMock()
        self.edr_client._visual_alt_feedback = MagicMock()
        self.edr_client.edrcommands.process = MagicMock()
        self.parent = MagicMock()

    @patch('edr.edrclientui.EDRTogglingPanel')
    def test_init(self, mock_panel_cls):
        mock_panel = Mock()
        mock_panel_cls.return_value = mock_panel
        
        ui = EDRClientUI(self.edr_client, self.parent)
        
        self.assertEqual(ui.edr_client, self.edr_client)
        self.assertEqual(ui.parent, self.parent)
        mock_panel_cls.assert_called_once()
        self.assertEqual(ui.ui, mock_panel)
        mock_panel.notify.assert_called_once()  # Initial troubleshooting msg

    @patch('edr.edrclientui.EDRTogglingPanel')
    def test_methods_delegation(self, mock_panel_cls):
        mock_panel = Mock()
        mock_panel_cls.return_value = mock_panel
        ui = EDRClientUI(self.edr_client, self.parent)

        ui.refresh_theme()
        mock_panel.refresh_theme.assert_called_once()

        ui.enable_entry()
        mock_panel.enable_entry.assert_called_once()

        ui.disable_entry()
        mock_panel.disable_entry.assert_called_once()

        ui.notify("Header", "Body")
        mock_panel.notify.assert_called_with("Header", "Body")
        
        ui.help("Header", "Body")
        mock_panel.help.assert_called_with("Header", "Body")

        ui.clear()
        mock_panel.clear.assert_called_once()

        ui.intel("Header", "Body")
        mock_panel.intel.assert_called_with("Header", "Body")

        ui.sitrep("Header", "Body")
        mock_panel.sitrep.assert_called_with("Header", "Body")

        ui.warning("Header", "Body")
        mock_panel.warning.assert_called_with("Header", "Body")

        ui.nolink()
        mock_panel.nolink.assert_called_once()

        ui.link("http://example.com")
        mock_panel.link.assert_called_with("http://example.com")

    @patch('edr.edrclientui.notebook')
    @patch('edr.edrclientui.ttkHyperlinkLabel')
    @patch('edr.edrclientui.EDRTogglingPanel')
    def test_prefs_ui(self, mock_panel_cls, mock_hyperlink, mock_notebook):
        ui = EDRClientUI(self.edr_client, self.parent)
        parent_frame = MagicMock()
        
        # Setup mocks for widgets
        mock_notebook.Frame.return_value = MagicMock()
        mock_notebook.Label.return_value = MagicMock()
        mock_notebook.EntryMenu.return_value = MagicMock()
        mock_notebook.Checkbutton.return_value = MagicMock()
        mock_notebook.OptionMenu.return_value = MagicMock()
        
        frame = ui.prefs_ui(parent_frame)
        
        self.assertTrue(mock_notebook.Frame.called)
        self.assertTrue(mock_hyperlink.HyperlinkLabel.called)
        self.assertTrue(mock_notebook.Label.called)
        self.assertTrue(mock_notebook.EntryMenu.called)
        self.assertTrue(mock_notebook.Checkbutton.called)
        self.assertTrue(mock_notebook.OptionMenu.called)
        
        return frame
