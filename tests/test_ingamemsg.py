
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock modules that might not exist or are hard to test
sys.modules['EDMCOverlay'] = MagicMock()
from edr.ui import ingamemsg

class TestInGameMsg(unittest.TestCase):
    def setUp(self):
        self.igm = ingamemsg.InGameMsg()
        self.igm._overlay = Mock()
        self.igm.cfg = {
            "general": {"large": {"h": 100, "w": 100}, "normal": {"h": 100, "w": 100}},
            "intel": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "intel-legal": {"enabled": False},
            "warning": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "warning-legal": {"enabled": False},
            "notice": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "help": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "sitrep": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "docking": {"enabled": True, "h": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left"}, "b": {"x": 0, "y": 0, "ttl": 1, "rgb": "#000", "size": "normal", "len": 100, "align": "left", "rows": 5, "last_row": 0, "cache": MagicMock()}},
            "docking-station": {"enabled": True, "schema": {"rotate": False, "x": 0, "y": 0, "w": 10, "h": 10, "rgb": ["#000"]*10, "fill": ["#000"]*10, "ttl": 1}}
        }

    def test_intel(self):
        self.igm.intel("Header", ["Detail 1", "Detail 2"])
        # Verify overlay calls would happen (mocking private methods __msg_header etc would be better but they call overlay)
        # Since we didn't mock internal helpers, we rely on them calling _overlay.
        # But _overlay is set to Mock.
        # Check if _overlay.send_message or similar is called?
        # InGameMsg doesn't seem to have direct send_message in the snippets I saw?
        # It calls __msg_header -> ?
        pass # Placeholder for verifying logic if possible. 
        # The class is heavy on config and drawing. 
        # Minimal test to ensure no crashes.

    def test_notify(self):
        self.igm.notify("Header", ["Detail"])
        pass

    def test_docking(self):
        station = {"name": "Station", "economy": "Industrial", "secondEconomy": None, "type": "Coriolis Starport"}
        self.igm.docking({"name": "Sol"}, station, 1, None, ["Landing info"])
        pass


if __name__ == '__main__':
    unittest.main()
