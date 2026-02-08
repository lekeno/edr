import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edrcommands import EDRCommands # EDR_INTERNAL

class TestEDRCommands(unittest.TestCase):
    def setUp(self):
        self.edr_client = MagicMock()
        self.edr_client.player.target_pilot.return_value = None # Default no target
        self.edr_commands = EDRCommands(self.edr_client)

        self.logger_patch = patch('edrcommands.EDR_LOG')
        self.mock_logger = self.logger_patch.start()

    def tearDown(self):
        self.logger_patch.stop()

    def test_process_empty(self):
        self.edr_commands.process("")
        self.edr_client.assert_not_called()

    def test_process_overlay(self):
        self.edr_commands.process("!overlay on")
        self.assertTrue(self.edr_client.visual_feedback)
        
        self.edr_commands.process("!overlay off")
        self.assertFalse(self.edr_client.visual_feedback)

    def test_process_audiocues(self):
        self.edr_commands.process("!audiocue on")
        self.assertTrue(self.edr_client.audio_feedback)
        
        self.edr_commands.process("!audiocue off")
        self.assertFalse(self.edr_client.audio_feedback)

    def test_process_sitrep(self):
        self.edr_commands.process("!sitrep System Name")
        self.edr_client.check_system.assert_called_with("System Name")

    def test_process_help(self):
        self.edr_commands.process("!help")
        self.edr_client.help.assert_called()

    def test_process_clear(self):
        self.edr_commands.process("!clear")
        self.edr_client.clear.assert_called()

    def test_process_dist(self):
        self.edr_client.player.star_system = "Sol"
        self.edr_commands.process("!distance Colonia")
        self.edr_client.distance.assert_called_with("Sol", "Colonia")
        
    def test_process_who(self):
        self.edr_commands.process("!who CmdrName")
        self.edr_client.who.assert_called_with("CmdrName")

    def test_process_unknown_command(self):
        self.edr_commands.process("!unknown foo")
        # Should verify no critical method called
        self.edr_client.who.assert_not_called()
