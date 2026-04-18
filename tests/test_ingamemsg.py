import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock modules that might not exist or are hard to test
sys.modules['EDMCOverlay'] = MagicMock()
from edr.ui import ingamemsg
from edr.models.edsitu import EDPlanetaryLocation

class TestInGameMsg(unittest.TestCase):
    def setUp(self):
        self.igm = ingamemsg.InGameMsg()
        self.igm._overlay = Mock()
        
        # We need a proper configuration for tests to not throw KeyError
        self.igm.cfg = {
            "general": {"large": {"h": 100, "w": 100}, "normal": {"h": 100, "w": 100}},
            "intel": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "intel-legal": {"enabled": False},
            "warning": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "warning-legal": {"enabled": False},
            "notice": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "help": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "sitrep": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "navigation": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "biology": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "docking": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "docking-station": {"enabled": True, "schema": {"rotate": False, "x": 0, "y": 0, "w": 10, "h": 10, "rgb": ["#000"]*10, "fill": ["#000"]*10, "ttl": 1}}
        }

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    def test_intel(self, mock_msg_body, mock_msg_header):
        self.igm.intel("Cmdr Name", ["Known outlaw", "Bounty: 1,000,000"])
        mock_msg_header.assert_called_with("intel", "Cmdr Name")
        mock_msg_body.assert_called_with("intel", ["Known outlaw", "Bounty: 1,000,000"])

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    def test_warning(self, mock_msg_body, mock_msg_header):
        self.igm.warning("Danger", ["Griefer in system", "High risk"])
        mock_msg_header.assert_called_with("warning", "Danger")
        mock_msg_body.assert_called_with("warning", ["Griefer in system", "High risk"])

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    def test_notify(self, mock_msg_body, mock_msg_header):
        self.igm.notify("Information", ["Market data updated"])
        mock_msg_header.assert_called_with("notice", "Information")
        mock_msg_body.assert_called_with("notice", ["Market data updated"])

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    def test_help(self, mock_msg_body, mock_msg_header):
        self.igm.help("Help Menu", ["Command 1", "Command 2"])
        mock_msg_header.assert_called_with("help", "Help Menu")
        mock_msg_body.assert_called_with("help", ["Command 1", "Command 2"])
        self.assertTrue(self.igm.must_clear)

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    @patch.object(ingamemsg.InGameMsg, '_InGameMsg__clear_kind')
    def test_sitrep(self, mock_clear_kind, mock_msg_body, mock_msg_header):
        self.igm.sitrep("Sol Sitrep", ["Traffic: High", "Crimes: Low"])
        mock_clear_kind.assert_called_with("sitrep")
        mock_msg_header.assert_called_with("sitrep", "Sol Sitrep")
        mock_msg_body.assert_called_with("sitrep", ["Traffic: High", "Crimes: Low"])

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    @patch.object(ingamemsg.InGameMsg, 'clear_navigation')
    def test_navigation(self, mock_clear_nav, mock_msg_body, mock_msg_header):
        dest = MagicMock()
        dest.title = "Dav's Hope"
        dest.latitude = 12.34
        dest.longitude = 56.78
        dest.heading = 90
        dest.altitude = 1200 # m
        
        self.igm.navigation(bearing=45, destination=dest, distance=2.5, pitch=10)
        
        mock_clear_nav.assert_called_once()
        mock_msg_header.assert_called_with("navigation", "› 045 ‹     ↓ 10 ↓")
        
        # Check that proper strings are formatted
        expected_body = [
            "Dav's Hope",
            "Dis: 2km", # Because 2.5 >= 1.0, distance is int(2.5)=2km
            "Lat: 12.3400",
            "Lon: 56.7800",
            "Head: > 090 <",
            "Alt: 1200km" # Wait, 1200 > 1.0, so 1200km
        ]
        mock_msg_body.assert_called_with("navigation", expected_body)

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    @patch.object(ingamemsg.InGameMsg, 'clear_biology')
    def test_biology_guidance(self, mock_clear_bio, mock_msg_body, mock_msg_header):
        self.igm.biology_guidance("Bacterium Bullaris", ccr=500, value=1500000, distances_meters=[200, 600], bearings=[15, 180])
        
        mock_clear_bio.assert_called_once()
        mock_msg_header.assert_called_with("biology", "Bacterium Bullaris")
        
        expected_body = [
            "Value: 1.5 m credits",
            "Gene diversity: +500m",
            "\u25cc Sample #1: 200m  \u203a015\u2039",
            "\u25cf Sample #2: 600m  \u203a180\u2039"
        ]
        mock_msg_body.assert_called_with("biology", expected_body)

    @patch.object(ingamemsg.InGameMsg, 'ui_msg_header')
    @patch.object(ingamemsg.InGameMsg, 'ui_msg_body')
    @patch.object(ingamemsg.InGameMsg, 'clear_docking')
    def test_docking_station(self, mock_clear_docking, mock_msg_body, mock_msg_header):
        station = {"name": "Jameson Memorial", "economy": "High Tech", "secondEconomy": "Refinery", "type": "Orbis Starport"}
        result = self.igm.docking("Shinrarta Dezhra", station, pad=1, faction=None, description=["Welcome"])
        
        mock_clear_docking.assert_called_once()
        mock_msg_header.assert_called_with("docking", "Jameson Memorial (High Tech/Refinery)")
        mock_msg_body.assert_called_with("docking", ["Welcome"])
        self.assertIsNotNone(result)
        self.assertEqual(result["header"], "Jameson Memorial (High Tech/Refinery)")

    def test_clear_all_messages(self):
        self.igm.must_clear = True
        self.igm.msg_ids.set("EDR-intel-header", True)
        self.igm.clear()
        
        self.assertFalse(self.igm.must_clear)
        self.assertFalse(self.igm.msg_ids.has_key("EDR-intel-header"))

if __name__ == '__main__':
    unittest.main()
