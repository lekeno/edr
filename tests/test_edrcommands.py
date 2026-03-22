
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrcommands import EDRCommands

class TestEDRCommands(unittest.TestCase):
    def setUp(self):
        self.mock_edr_client = MagicMock()
        self.mock_player = MagicMock()
        self.mock_edr_client.player = self.mock_player
        self.commands = EDRCommands(self.mock_edr_client)

    def test_process_empty(self):
        self.assertFalse(self.commands.process(""))

    def test_process_bang_command_who(self):
        self.commands.process("!who cmdr_name")
        self.mock_edr_client.who.assert_called_with("cmdr_name")

    def test_process_bang_command_who_implicit_target(self):
        # Mock a target
        mock_target = MagicMock()
        mock_target.name = "TargetCmdr"
        mock_target.is_human.return_value = True
        self.mock_player.target_pilot.return_value = mock_target

        self.commands.process("!who")
        self.mock_edr_client.who.assert_called_with("TargetCmdr")

    def test_process_bang_command_sitrep(self):
        self.mock_player.star_system = "CurrentSys"
        self.commands.process("!sitrep")
        self.mock_edr_client.check_system.assert_called_with("CurrentSys")

    def test_process_query_command_outlaws(self):
        # Test enabling
        self.commands.process("?outlaws on")
        self.mock_edr_client.enable_outlaws_alerts.assert_called_once()
        
        # Test disabling
        self.commands.process("?outlaws off")
        self.mock_edr_client.disable_outlaws_alerts.assert_called_once()

    def test_process_hash_command_tag(self):
        # Implicit target from earlier mock or set up new one
        mock_target = MagicMock()
        mock_target.name = "BadGuy"
        mock_target.is_human.return_value = True
        self.mock_player.target_pilot.return_value = mock_target
        
        self.commands.process("#outlaw")
        self.mock_edr_client.tag_cmdr.assert_called_with("BadGuy", "outlaw")

        self.commands.process("#enemy")
        self.mock_edr_client.tag_cmdr.assert_called_with("BadGuy", "enemy")

    def test_process_minus_command_untag(self):
        mock_target = MagicMock()
        mock_target.name = "GoodGuy"
        mock_target.is_human.return_value = True
        self.mock_player.target_pilot.return_value = mock_target

        self.commands.process("-#outlaw")
        self.mock_edr_client.untag_cmdr.assert_called_with("GoodGuy", "outlaw")

    def test_process_at_command_memo(self):
        mock_target = MagicMock()
        mock_target.name = "MemoTarget"
        mock_target.is_human.return_value = True
        self.mock_player.target_pilot.return_value = mock_target

        # The command expects " memo=" as a separator and the prefix to be "@# " (with a space)
        self.commands.process("@#  memo=this is a memo")
        self.mock_edr_client.memo_cmdr.assert_called_with("MemoTarget", "this is a memo")

    def test_o7_command(self):
        self.commands.process("o7", recipient="CmdrFriend")
        self.mock_edr_client.who.assert_called_with("CmdrFriend", autocreate=True)

    def test_overlay_command(self):
        self.commands.process("!overlay on")
        self.assertTrue(self.mock_edr_client.visual_feedback)
        
        self.commands.process("!overlay off")
        self.assertFalse(self.mock_edr_client.visual_feedback)

    def test_audiocue_command(self):
        self.commands.process("!audiocue loud")
        self.mock_edr_client.loud_audio_feedback.assert_called_once()
        self.assertTrue(self.mock_edr_client.audio_feedback)

    def test_crimes_command(self):
        self.commands.process("!crimes on")
        self.assertTrue(self.mock_edr_client.crimes_reporting)
        
        self.commands.process("!crimes off")
        self.assertFalse(self.mock_edr_client.crimes_reporting)

    def test_macro_set_implicit(self):
        self.commands.last_success_command = "!intel"
        self.commands.process("!macro set 1")
        self.mock_edr_client.hotkey_manager.update_macro.assert_called_with("1", "!intel")

    def test_macro_set_explicit(self):
        self.commands.process("!macro set 2 !status")
        self.mock_edr_client.hotkey_manager.update_macro.assert_called_with("2", "!status")

    def test_macro_show(self):
        self.mock_edr_client.hotkey_manager.mappings = {"edr.macro_1": {"label": "L1", "command": "!intel"}}
        self.commands.process("!macro show 1")
        self.assertTrue(self.mock_edr_client.notify_with_details.called)

    def test_macro_name_valid(self):
        self.commands.process("!macro name 1 ValidName")
        self.mock_edr_client.hotkey_manager.update_label.assert_called_with("1", "ValidName")

    def test_macro_name_invalid(self):
        self.mock_edr_client.hotkey_manager.update_label.reset_mock()
        self.commands.process("!macro name 1 Invalid Name")
        self.assertFalse(self.mock_edr_client.hotkey_manager.update_label.called)
        self.assertTrue(self.mock_edr_client.notify_with_details.called)

    def test_macro_clear(self):
        self.commands.process("!macro clear 1")
        self.mock_edr_client.hotkey_manager.clear_macro.assert_called_with("1")

    def test_macro_list(self):
        self.commands.process("!macro list")
        self.mock_edr_client.hotkey_manager.get_macros.assert_called_once()


if __name__ == '__main__':
    unittest.main()
