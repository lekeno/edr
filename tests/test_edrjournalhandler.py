import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path safely
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '..', 'edr', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

class TestEDRJournalHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patches = []
        for mod in ['ingamemsg', 'myNotebook', 'EDMCOverlay', 'ttkHyperlinkLabel', 'tkinter', 'tkinter.ttk', 'config']:
            p = patch.dict('sys.modules', {mod: MagicMock()})
            p.start()
            cls.patches.append(p)

    @classmethod
    def tearDownClass(cls):
        for p in reversed(cls.patches):
            p.stop()

    def setUp(self):
        from edr.controllers.edrjournalhandler import EDRJournalHandler
        self.mock_client = MagicMock()
        self.mock_player = MagicMock()
        self.mock_player.in_solo.return_value = False
        self.mock_player.has_partial_status.return_value = False
        self.mock_player.name = "Self"
        self.mock_client.player = self.mock_player
        self.mock_client.blip.return_value = True
        self.handler = EDRJournalHandler(self.mock_client)

    def test_journal_entry_delegation(self):
        entry = {"event": "FSDJump", "timestamp": "2023-01-01T00:00:00Z"}
        state = {}
        mock_fsd = MagicMock()
        # event_map holds references to methods established at init, so we must replace it there too
        self.handler.event_map["FSDJump"] = mock_fsd
        self.handler.journal_entry("Self", False, "Sol", "Station", entry, state)
        mock_fsd.assert_called_with(entry, state)

    def test_on_fsd_jump(self):
        entry = {"event": "FSDJump", "StarSystem": "Sol", "FuelLevel": 10.0, "timestamp": "2023-01-01T00:00:00Z"}
        state = {}
        # We need a real EDTime for this or mock it locally
        with patch('edr.controllers.edrjournalhandler.EDTime') as mock_edtime:
            self.handler._on_fsd_jump(entry, state)
            self.mock_player.to_super_space.assert_called()
            self.mock_player.update_place_if_obsolete.assert_called_with("Supercruise")
            self.mock_client.noteworthy_about_system.assert_called_with(entry)

    def test_on_ship_targeted_no_target(self):
        entry = {"event": "ShipTargeted", "TargetLocked": False, "timestamp": "2023-01-01T00:00:00Z"}
        state = {}
        self.handler._on_ship_targeted(entry, state)
        self.mock_player.untarget.assert_called()
        self.mock_client.bounty_hunting_guidance.assert_called_with(turn_off=True)

    def test_on_ship_targeted_with_target(self):
        entry = {"event": "ShipTargeted", "TargetLocked": True, "ScanStage": 3, "PilotName": "Target", "Ship": "anaconda", "Bounty": 1000, "timestamp": "2023-01-01T00:00:00Z"}
        state = {}
        with patch.object(self.handler, 'handle_scan_events') as mock_scan:
            with patch.object(self.handler, '_handle_bounty_hunting_events') as mock_bounty:
                self.handler._on_ship_targeted(entry, state)
                mock_scan.assert_called_with(entry)
                mock_bounty.assert_called_with(entry)

    def test_on_bounty(self):
        entry = {"event": "Bounty", "Rewards": [{"Commander": "Cmdr Test", "Reward": 1000}], "timestamp": "2023-01-01T00:00:00Z"}
        state = {}
        self.handler._on_bounty(entry, state)
        self.mock_player.bounty_awarded.assert_called_with(entry)
        self.mock_client.bounty_hunting_guidance.assert_called()

    def test_finalize_and_report_multicrew(self):
        entry = {"event": "FSDJump", "timestamp": "2023-01-01T00:00:00Z"}
        self.mock_player.in_a_crew.return_value = True
        self.mock_player.crew.members = ["Self", "Crew1"]
        self.mock_player.name = "Self"
        self.mock_player.is_captain.return_value = True
        
        with patch('edr.controllers.edrjournalhandler.EDPlayer') as mock_edplayer_class:
            mock_crew_member = MagicMock()
            mock_edplayer_class.return_value = mock_crew_member
            
            with patch.object(self.handler, '_should_report', return_value=True):
                self.handler._finalize_and_report(entry)
                
                mock_edplayer_class.assert_called_with("Crew1")
                self.assertEqual(mock_crew_member.mothership, self.mock_player.mothership)
                self.mock_client.blip.assert_called() # _update_cmdr_status calls blip

    def test_legacy_journal_entry_multicrew(self):
        entry = {"event": "FSDJump", "timestamp": "2023-01-01T00:00:00Z"}
        state = {"ShipType": "anaconda"}
        self.mock_player.in_a_crew.return_value = True
        self.mock_player.crew.members = ["Self", "Crew1"]
        self.mock_player.name = "Self"
        self.mock_player.is_captain.return_value = False
        
        with patch('edr.controllers.edrjournalhandler.EDPlayer') as mock_edplayer_class:
            mock_crew_member = MagicMock()
            mock_edplayer_class.return_value = mock_crew_member
            
            # Legacy journal entry logic
            self.handler.legacy_journal_entry("Self", False, "Sol", "Station", entry, state)
            
            mock_edplayer_class.assert_called_with("Crew1")
            self.mock_client.blip.assert_called() # legacy_journal_entry calls _update_cmdr_status if updated

if __name__ == '__main__':
    unittest.main()
