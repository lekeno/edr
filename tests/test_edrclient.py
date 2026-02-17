import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os



class TestEDRClient(unittest.TestCase):
    def setUp(self):
        # Configure Tkinter mocks
        def mock_string_var(value=None):
            mock = MagicMock()
            mock.get.return_value = value
            def set_val(new_val):
                mock.get.return_value = new_val
            mock.set.side_effect = set_val
            return mock

        def mock_int_var(value=0):
            mock = MagicMock()
            mock.get.return_value = value
            def set_val(new_val):
                mock.get.return_value = new_val
            mock.set.side_effect = set_val
            return mock

        self.mock_tkinter = MagicMock()
        self.mock_tkinter.StringVar = mock_string_var
        self.mock_tkinter.IntVar = mock_int_var

        # Create mocks for dependencies
        self.modules_patcher = patch.dict('sys.modules', {
            'myNotebook': MagicMock(),
            'EDMCOverlay': MagicMock(),
            'ttkHyperlinkLabel': MagicMock(),
            'tkinter': self.mock_tkinter,
            'tkinter.ttk': MagicMock(),
        })
        self.modules_patcher.start()
        
        # Reload edrclient to use our mocks
        import importlib
        import edr.controllers.edrclient
        importlib.reload(edr.controllers.edrclient)
        from edr.controllers import edrclient

        # Mocking config before initializing EDRClient because it reads config in __init__
        # Use patch.object to ensure we patch the exact module we loaded
        self.mock_config_patcher = patch.object(edrclient, 'config')
        self.mock_config = self.mock_config_patcher.start()
        self.mock_config.get_str.return_value = "Run" # Default for many things
        self.mock_config.get_int.return_value = 0
        
        # Mock EDR_CONFIG
        self.mock_edr_config_patcher = patch('edr.controllers.edrclient.EDR_CONFIG')
        self.mock_edr_config = self.mock_edr_config_patcher.start()
        self.mock_edr_config.lru_max_size.return_value = 100
        self.mock_edr_config.blips_max_age.return_value = 60
        self.mock_edr_config.traffic_max_age.return_value = 60
        self.mock_edr_config.scans_max_age.return_value = 60
        self.mock_edr_config.alerts_max_age.return_value = 60
        self.mock_edr_config.fights_max_age.return_value = 60
        self.mock_edr_config.enemy_alerts_pledge_threshold.return_value = 1000
        self.mock_edr_config.system_novelty_threshold.return_value = 1000
        self.mock_edr_config.place_novelty_threshold.return_value = 1000
        self.mock_edr_config.ship_novelty_threshold.return_value = 1000
        self.mock_edr_config.cognitive_novelty_threshold.return_value = 1000
        self.mock_edr_config.intel_even_if_clean.return_value = False
        self.mock_edr_config.edr_needs_u_novelty_threshold.return_value = 1000
        
        # Mock dependent classes to avoid complex initialization
        self.mock_server_patcher = patch('edr.controllers.edrclient.EDRServer')
        self.mock_server_class = self.mock_server_patcher.start()
        
        self.mock_edsm_server_patcher = patch('edr.controllers.edrclient.EDSMServer')
        self.mock_edsm_server = self.mock_edsm_server_patcher.start()
        
        self.mock_ui_patcher = patch('edr.controllers.edrclient.EDRClientUI')
        self.mock_ui = self.mock_ui_patcher.start()

        self.mock_edrsystems_patcher = patch('edr.controllers.edrclient.EDRSystems')
        self.mock_edrsystems_class = self.mock_edrsystems_patcher.start()

        self.mock_edrcmdrs_patcher = patch('edr.controllers.edrclient.EDRCmdrs')
        self.mock_edrcmdrs = self.mock_edrcmdrs_patcher.start()
        
        self.mock_ingamemsg_patcher = patch('edr.controllers.edrclient.InGameMsg')
        self.mock_ingamemsg = self.mock_ingamemsg_patcher.start()
        
        self.client = edrclient.EDRClient()

    def tearDown(self):
        self.mock_config_patcher.stop()
        self.mock_edr_config_patcher.stop()
        self.mock_server_patcher.stop()
        self.mock_edsm_server_patcher.stop()
        self.mock_ui_patcher.stop()
        self.mock_edrsystems_patcher.stop()
        self.mock_edrcmdrs_patcher.stop()
        self.mock_ingamemsg_patcher.stop()
        self.modules_patcher.stop()
        
        # Remove polluted modules from sys.modules so next test imports them fresh
        sys.modules.pop('edr.controllers.edrclient', None)
        sys.modules.pop('edr.ui.edrclientui', None)

    def test_init(self):
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.server)
        self.assertIsNotNone(self.client.edsm_server)

    def test_traffic(self):
        star_system = "Shinrarta Dezhra"
        traffic_data = {
            "cmdr": "Cmdr Test",
            "ship": "Anaconda",
            "timestamp": "2023-01-01T12:00:00Z"
        }
        
        with patch('edr.controllers.edrclient.EDRClient.player', new_callable=PropertyMock) as mock_player_prop:
            mock_player = MagicMock()
            mock_player_prop.return_value = mock_player
            mock_player.in_solo.return_value = False
            
            # Monkeypatch is_anonymous on the instance
            self.client.is_anonymous = MagicMock(return_value=False)
            self.client.edrsystems.system_id.return_value = 12345
            self.client.server.traffic.return_value = True
            
            # Run method
            result = self.client.traffic(star_system, traffic_data)
            
            # Assertions
            self.assertTrue(result)
            self.client.server.traffic.assert_called_once()

    def test_scanned(self):
        cmdr_name = "Cmdr Target"
        scan_data = {
            "ScanType": "Detailed",
            "BodyName": "Earth",
            "wanted": True,
            "bounty": 1000
        }
        
        with patch('edr.controllers.edrclient.EDRClient.player', new_callable=PropertyMock) as mock_player_prop:
            mock_player = MagicMock()
            mock_player_prop.return_value = mock_player
            mock_player.in_solo.return_value = False
            mock_player.in_open.return_value = True
            mock_player.has_partial_status.return_value = False
            
            # Monkeypatch is_anonymous on the instance
            self.client.is_anonymous = MagicMock(return_value=False)
            self.client.server.is_authenticated.return_value = True
            
            # Mock cmdr_id
            self.client.cmdr_id = MagicMock(return_value="cid_123")
            
            # Mock cmdr profile lookup
            profile_mock = MagicMock()
            profile_mock.cid = "cid_123"
            profile_mock.is_dangerous.return_value = False
            self.client.edrcmdrs.cmdr.return_value = profile_mock
            
            # Monkeypatch novel_enough_scan on the instance
            self.client.novel_enough_scan = MagicMock(return_value=True)
            self.client.__show_cmdr_intel_if_warranted = MagicMock() # Mock internal method
            
            # Also mock __is_opsec_protected since access to private method might need it
            # Actually mangled name _EDRClient__is_opsec_protected
            self.client._EDRClient__is_opsec_protected = MagicMock(return_value=False)
            self.client._EDRClient__show_cmdr_intel_if_warranted = MagicMock()
            
            self.client.server.scanned.return_value = True
            
            result = self.client.scanned(cmdr_name, scan_data)
            self.assertTrue(result)
            self.client.server.scanned.assert_called_once()

    def test_tag_cmdr(self):
        cmdr_name = "Cmdr Enemy"
        tag = "enemy"
        
        with patch('edr.controllers.edrclient.EDRClient.player', new_callable=PropertyMock) as mock_player_prop:
            mock_player = MagicMock()
            mock_player_prop.return_value = mock_player
            mock_player.in_solo.return_value = False
            # Mocking squadron empowerment
            mock_player.squadron = {"name": "Test Squadron"}
            mock_player.is_empowered_by_squadron.return_value = True
            
            # Monkeypatch is_anonymous on the instance
            self.client.is_anonymous = MagicMock(return_value=False)
            self.client.edrcmdrs.tag_cmdr.return_value = True
            
            result = self.client.tag_cmdr(cmdr_name, tag)
            self.assertTrue(result)
            self.client.edrcmdrs.tag_cmdr.assert_called_with(cmdr_name, tag)

    def test_interstellar_factors(self):
        star_system = "Shinrarta Dezhra"
        
        with patch('edr.controllers.edrclient.EDRClient.player', new_callable=PropertyMock) as mock_player_prop:
            mock_player = MagicMock()
            mock_player_prop.return_value = mock_player
            mock_player.needs_large_landing_pad.return_value = True
            mock_player.needs_medium_landing_pad.return_value = False
            
            self.client.edrsystems.in_bubble.return_value = True
            self.client.edrsystems.search_interstellar_factors.return_value = None
            
            result = self.client.interstellar_factors_near(star_system)
            
            self.client.edrsystems.search_interstellar_factors.assert_called_once()

    def test_journey(self):
        # Mock routenav
        mock_routenav = MagicMock()
        mock_routenav.no_journey.return_value = False
        mock_routenav.journey_next.return_value = True
        mock_routenav.current_wp_sysname.return_value = "Colonia"
        
        with patch('edr.controllers.edrclient.EDRClient.player', new_callable=PropertyMock) as mock_player_prop:
            mock_player = MagicMock()
            mock_player_prop.return_value = mock_player
            mock_player.routenav = mock_routenav
            
            # Test journey_next
            self.client.journey_next()
            mock_routenav.journey_next.assert_called_once()
            
            # Test journey_clear
            self.client.journey_clear()
            mock_routenav.clear_journey.assert_called_once()

    def test_version_check(self):
        self.client.server.server_version.return_value = {
            "min": "1.0.0",
            "latest": "9.9.9",
            "l10n_motd": "Hello"
        }
        self.client.edr_version = "1.0.0"
        
        self.client.check_version()
        self.assertEqual(self.client.mandatory_update, False)
        # 1.0.0 < 9.9.9 -> True, it is obsolete compared to latest
        
    def test_is_obsolete(self):
        self.client.edr_version = "1.0.0"
        self.assertTrue(self.client.is_obsolete("2.0.0"))
        self.assertFalse(self.client.is_obsolete("0.9.0"))
        self.assertFalse(self.client.is_obsolete("1.0.0"))

    def test_email_property(self):
        self.client._email.set("test@example.com")
        self.assertEqual(self.client.email, "test@example.com")
        
        self.client.email = "new@example.com"
        self.assertEqual(self.client._email.get(), "new@example.com")

    def test_describe_ed_settlement(self):
        entry = {
            "event": "ApproachSettlement",
            "StationServices": ["refuel", "repair", "commodities"],
            "StationFaction": {"Name": "Test Faction"},
            "StationAllegiance": "Federation",
            "StationGovernment_Localised": "Democracy"
        }
        faction = MagicMock()
        faction.isPMF = True
        faction.state = "Boom"
        faction.name = "Test Faction"
        faction.government = "Democracy"
        faction.allegiance = "Federation"
        # MagicMock.__str__ needs to return a string if used in str() context? 
        # But textwrap usually fails on the mock itself not str(mock).
        # Let's ensure properties return strings
        type(faction).name = PropertyMock(return_value="Test Faction")

        
        # Mocking _ function from edri18n (it's imported in edrclient)
        # However, since we import EDRClient, it imports everything.
        # We can just check if it runs without error and returns list
        
        details = self.client.describe_ed_settlement(entry, faction)
        self.assertIsInstance(details, list)
        self.assertTrue(len(details) > 0)
        # Check for presence of key strings (localized in real app, but mocks are tricky)


    def test_eval_mission(self):
        entry = {
            "event": "MissionAccepted",
            "Commodity": "biowaste",
            "Commodity_Localised": "Biowaste"
        }
        
        # Test eval_mission
        self.client.eval_mission(entry)
        # Verify no crash
        
        entry_completed = {
            "event": "MissionCompleted",
            "MaterialsReward": [
                {"Name": "iron", "Count": 5}
            ]
        }
        self.client.eval_mission(entry_completed)
        # Verify no crash

    @patch('edr.controllers.edrclient.EDR_LOG')
    def test_shutdown(self, mock_log):
        self.client.shutdown()
        # shutdown() calls persist() on components, but NOT server.shutdown() (it doesn't exist)
        # It calls logout() only if everything=True
        self.client.edrcmdrs.persist.assert_called_once()
        self.client.edrsystems.persist.assert_called_once()
        self.client.player.persist.assert_called_once()

    def test_app_main(self):
        parent = MagicMock()
        
        # Ensure server.server_version calls return None to avoid side effects
        self.client.server.server_version.return_value = None
        
        # Ensure EDRClientUI class mock returns a mock instance
        # self.mock_ui is the Class mock. self.mock_ui.return_value is the instance.
        mock_ui_instance = self.mock_ui.return_value
        mock_ui_instance.app_ui.return_value = MagicMock()
        
        # Call app_ui
        result = self.client.app_ui(parent)
        
        # Verify EDRClientUI was instantiated with (self.client, parent)
        self.mock_ui.assert_called_with(self.client, parent)
        
        # Verify app_ui() was called on the instance
        mock_ui_instance.app_ui.assert_called()
        
        # Verify the result is what app_ui() returned
        self.assertEqual(result, mock_ui_instance.app_ui.return_value)


if __name__ == '__main__':
    unittest.main()
