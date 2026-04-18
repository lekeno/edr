import sys
import unittest
from unittest.mock import MagicMock, patch

class TestDockingSquadronCarrier(unittest.TestCase):
    def setUp(self):
        # Create mocks for dependencies
        self.mock_overlay = MagicMock()
        self.mock_notebook = MagicMock()
        self.mock_hyperlink = MagicMock()
        self.mock_config = MagicMock()
        self.mock_config.config.get_str.return_value = "en"
        self.mock_tkinter = MagicMock()

        self.modules_patcher = patch.dict('sys.modules', {
            'EDMCOverlay': self.mock_overlay,
            'EDMCOverlay.edmcoverlay': self.mock_overlay,
            'myNotebook': self.mock_notebook,
            'ttkHyperlinkLabel': self.mock_hyperlink,
            'config': self.mock_config,
            'tkinter': self.mock_tkinter,
            'edr.ui.edrclientui': MagicMock(),
        })
        self.modules_patcher.start()

        # Import EDRClient after patching
        # We need to ensure we don't use a cached version that might have real imports
        import sys
        sys.modules.pop('edr.controllers.edrclient', None)
        # Also ensure parent package is not a mock (if it was mocked)
        if 'edr.controllers' in sys.modules and not hasattr(sys.modules['edr.controllers'], '__path__'):
            sys.modules.pop('edr.controllers', None)
            
        from edr.controllers.edrclient import EDRClient
        self.EDRClient = EDRClient

    def tearDown(self):
        self.modules_patcher.stop()
        # Remove polluted modules from sys.modules
        import sys
        sys.modules.pop('edr.controllers.edrclient', None)
        sys.modules.pop('edr.ui.edrclientui', None)

    def test_docking_guidance_cache(self):
        # Mock dependencies
        client = self.EDRClient()
        client.visual_feedback = True
        client.IN_GAME_MSG = MagicMock()
        client.edrsystems = MagicMock()
        client.edrcmdrs = MagicMock()
        client.edrcmdrs.player = MagicMock()
        client.edrcmdrs.player.star_system = "Sol"
        client.edrfactions = MagicMock()
        client.client_ui = MagicMock()
        client.edrfactions = MagicMock()
        client.client_ui = MagicMock()
        client.audio_feedback = False
        
        # Mock station return value for describe_station
        client.edrsystems.station.return_value = {
            "name": "Mock Station",
            "updateTime": {"information": "2023-01-01 12:00:00"},
            "allegiance": "Federation",
            "government": "Democracy",
            "type": "Orbis",
            "otherServices": ["Refuel", "Repair", "Restock"],
            "economy": "High Tech",
            "secondEconomy": "Industrial",
            "haveMarket": True,
            "haveOutfitting": True,
            "haveShipyard": True
        }
        
        # 1. Test DockingRequested (Squadron Carrier)
        market_id = 987654321
        requested_event = {
            "event": "DockingRequested",
            "MarketID": market_id,
            "StationType": "FleetCarrier",
            "LandingPads": {"Small": 10, "Medium": 10, "Large": 12} # Total = 32
        }
        
        print("Simulating DockingRequested for Squadron Carrier...")
        client.docking_guidance(requested_event)
        
        self.assertTrue(hasattr(client, "requests_cache"))
        self.assertIn(market_id, client.requests_cache)
        self.assertEqual(client.requests_cache[market_id]["LandingPads"]["Large"], 12)
        print("OK: Data cached correctly.")
    
        # 2. Test DockingGranted (Squadron Carrier)
        granted_event = {
            "event": "DockingGranted",
            "MarketID": market_id,
            "StationName": "Squadron Carrier X",
            "StationType": "FleetCarrier",
            "LandingPad": 5
        }
        
        print("Simulating DockingGranted...")
        client.docking_guidance(granted_event)
        
        # Verify edrsystems.station was called with correct override
        # station(star_system, station_name, station_type, pad_count_override=None)
        client.edrsystems.station.assert_called_with("Sol", "Squadron Carrier X", "FleetCarrier", 32)
        print("OK: edrsystems.station called with pad_count_override=32.")
        
        # Verify cache cleanup
        self.assertNotIn(market_id, client.requests_cache)
        print("OK: Cache cleaned up.")
    
        # 3. Test Standard Station (no override)
        market_id_standard = 123456789
        standard_requested = {
            "event": "DockingRequested",
            "MarketID": market_id_standard,
            "StationType": "Orbis"
            # No LandingPads in this event usually, or if it is, it's not a FC
        }
        
        print("Simulating DockingRequested for standard station...")
        client.docking_guidance(standard_requested)
        
        standard_granted = {
            "event": "DockingGranted",
            "MarketID": market_id_standard,
            "StationName": "Standard Station",
            "StationType": "Orbis",
            "LandingPad": 1
        }
        
        print("Simulating DockingGranted for standard station...")
        client.docking_guidance(standard_granted)
        client.edrsystems.station.assert_called_with("Sol", "Standard Station", "Orbis", None)
        print("OK: Standard station called with pad_count_override=None.")

if __name__ == "__main__":
    unittest.main()
