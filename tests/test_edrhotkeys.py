import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
from edr.controllers.edrhotkeys import EDRHotkeyManager

class TestEDRHotkeyManager(unittest.TestCase):
    def setUp(self):
        self.mock_edr_client = MagicMock()
        self.mock_config = MagicMock()
        self.mock_config.get_config_path.return_value = "config"
        self.mock_edr_client.config = self.mock_config
        
        # Mock file operations
        self.hotkeys_json_path = os.path.join("config", "hotkeys.json")
        self.initial_mappings = {
            "edr.macro_1": {"label": "Macro 1", "command": "!intel"}
        }

    @patch("edr.controllers.edrhotkeys.open", new_callable=mock_open, read_data='{"edr.macro_1": {"label": "Macro 1", "command": "!intel"}}')
    @patch("edr.controllers.edrhotkeys.os.path.exists")
    def test_load_mappings(self, mock_exists, mock_file):
        mock_exists.return_value = True
        manager = EDRHotkeyManager(self.mock_edr_client)
        self.assertEqual(manager.mappings["edr.macro_1"]["command"], "!intel")

    @patch("edr.controllers.edrhotkeys.open", new_callable=mock_open)
    @patch("edr.controllers.edrhotkeys.os.path.exists")
    @patch("edr.controllers.edrhotkeys.json.dump")
    def test_save_mappings(self, mock_json_dump, mock_exists, mock_file):
        mock_exists.return_value = False
        manager = EDRHotkeyManager(self.mock_edr_client)
        manager.mappings = {"edr.macro_1": {"label": "Macro 1", "command": "!intel"}}
        manager._save()
        mock_json_dump.assert_called_once()

    @patch("edr.controllers.edrhotkeys.ehp")
    @patch("edr.controllers.edrhotkeys.open", new_callable=mock_open, read_data='{}')
    @patch("edr.controllers.edrhotkeys.os.path.exists")
    def test_register(self, mock_exists, mock_file, mock_ehp):
        mock_exists.return_value = True
        manager = EDRHotkeyManager(self.mock_edr_client)
        manager.mappings = {"edr.macro_1": {"label": "Macro 1", "command": "!intel"}}
        manager.enabled = True
        manager.register()
        self.assertTrue(mock_ehp.register_action.called)

    @patch("edr.controllers.edrhotkeys.open", new_callable=mock_open, read_data='{}')
    @patch("edr.controllers.edrhotkeys.os.path.exists")
    def test_hotkey_callback(self, mock_exists, mock_file):
        mock_exists.return_value = True
        manager = EDRHotkeyManager(self.mock_edr_client)
        manager.mappings = {"edr.macro_1": {"label": "Macro 1", "command": "!intel"}}
        
        payload = {"action_id": "edr.macro_1"}
        manager.hotkey_callback(payload)
        self.mock_edr_client.process_command.assert_called_with("!intel")

    @patch("edr.controllers.edrhotkeys.open", new_callable=mock_open, read_data='{}')
    @patch("edr.controllers.edrhotkeys.os.path.exists")
    @patch("edr.controllers.edrhotkeys.EDRHotkeyManager._save")
    def test_update_macro(self, mock_save, mock_exists, mock_file):
        mock_exists.return_value = True
        manager = EDRHotkeyManager(self.mock_edr_client)
        
        manager.update_macro("1", "!status")
        self.assertEqual(manager.mappings["edr.macro_1"]["command"], "!status")
        mock_save.assert_called_once()

    @patch("edr.controllers.edrhotkeys.open", new_callable=mock_open, read_data='{}')
    @patch("edr.controllers.edrhotkeys.os.path.exists")
    @patch("edr.controllers.edrhotkeys.EDRHotkeyManager._save")
    def test_update_label(self, mock_save, mock_exists, mock_file):
        mock_exists.return_value = True
        manager = EDRHotkeyManager(self.mock_edr_client)
        
        manager.update_label("1", "StatusCheck")
        self.assertEqual(manager.mappings["edr.macro_1"]["label"], "StatusCheck")
        mock_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()
