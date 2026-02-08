import sys
import os
from unittest.mock import MagicMock

# Mock EDMCOverlay and other generic EDMC modules before importing edrclient
sys.modules['EDMCOverlay'] = MagicMock()
sys.modules['EDMCOverlay.edmcoverlay'] = MagicMock()
sys.modules['myNotebook'] = MagicMock()
sys.modules['ttkHyperlinkLabel'] = MagicMock()
sys.modules['config'] = MagicMock()

from edrclient import EDRClient # EDR_INTERNAL

def test_docking_guidance_cache():
    # Mock dependencies
    client = EDRClient()
    client.visual_feedback = True
    client.IN_GAME_MSG = MagicMock()
    client.edrsystems = MagicMock()
    client.player = MagicMock()
    client.player.star_system = "Sol"
    client.edrfactions = MagicMock()
    client.client_ui = MagicMock()
    client.audio_feedback = False
    
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
    
    assert hasattr(client, "requests_cache")
    assert market_id in client.requests_cache
    assert client.requests_cache[market_id]["LandingPads"]["Large"] == 12
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
    assert market_id not in client.requests_cache
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
    try:
        test_docking_guidance_cache()
        print("\nAll verification tests PASSED!")
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
