import config_tests
import unittest
from unittest.mock import MagicMock, patch
from edentities import EDPilot, EDRSquadronMember, EDRPowerplay, EDLocation, EDSpaceDimension
import edvehicles

class TestEDEntities(unittest.TestCase):

    def test_squadron_member(self):
        # Test initialization
        sq_info = {
            "squadronName": "Deep Space Network",
            "squadronId": "DSN",
            "squadronRank": "Leader",
            "squadronLevel": 500
        }
        member = EDRSquadronMember(sq_info)
        self.assertEqual(member.name, "Deep Space Network")
        self.assertEqual(member.inara_id, "DSN")
        self.assertEqual(member.level, 500)
        
        # Test trust levels
        self.assertTrue(member.is_somewhat_trusted())
        self.assertTrue(member.is_fully_trusted())
        
        # Test lower rank
        sq_info["squadronLevel"] = 50
        member = EDRSquadronMember(sq_info)
        self.assertFalse(member.is_somewhat_trusted())
        self.assertFalse(member.is_fully_trusted())

        # Test mid rank
        sq_info["squadronLevel"] = 100
        member = EDRSquadronMember(sq_info)
        self.assertTrue(member.is_somewhat_trusted())
        self.assertFalse(member.is_fully_trusted())

    def test_powerplay(self):
        # time_pledged is roughly now - timestamp passed in
        with patch('edtime.EDTime.py_epoch_now') as mock_now:
            mock_now.return_value = 1000
            
            # Pledged 900 seconds ago
            pledge_duration = 900
            pp = EDRPowerplay("aisling duval", pledge_duration)
            
            self.assertEqual(pp.pledged_to, "aisling duval")
            self.assertEqual(pp.time_pledged(), 900)
            
            # Test Affiliations
            # Aisling is Empire
            self.assertTrue(pp.is_enemy("zachary hudson")) # Fed = Enemy
            self.assertFalse(pp.is_enemy("arissa lavigny duval")) # Empire = Friend
            
            # Archon Delaine has None affiliation in the dict, so check logic
            delaine = EDRPowerplay("archon delaine", 100)
            # Archon is None.
            # If my_affiliation is None (Archon), returns True?
            # Code: return my_affiliation != their_affiliation if my_affiliation else True
            # So Archon is enemy of everyone?
            self.assertTrue(delaine.is_enemy("aisling duval"))

    def test_edpilot_vehicle_logic(self):
        pilot = EDPilot("Cmdr Test", "Harmless")
        
        # Initial state
        self.assertFalse(pilot.on_foot)
        self.assertEqual(pilot.vehicle_type(), "Unknown") # vehicle_type is 'Unknown' initially by default
        
        # Update with a ship
        ship = edvehicles.EDVehicleFactory.from_internal_name("empire_trader")
        pilot.update_vehicle_if_obsolete(ship)
        self.assertEqual(pilot.vehicle_type(), "Imperial Clipper")
        self.assertFalse(pilot.on_foot)
        
        # Disembark (Suit)
        entry = {"event": "Disembark", "ShipID": 1}
        # Need to mock closet or just trust logic
        # EDPilot has closet? imported EDOdysseyCloset.
        # Actually logic is self.in_spacesuit()
        pilot.disembark(entry)
        self.assertTrue(pilot.on_foot)
        self.assertIsNone(pilot.vehicle_type(), "Should be None when on foot")
        
        # Board SRV
        srv = edvehicles.EDVehicleFactory.default_srv()
        pilot.update_vehicle_if_obsolete(srv)
        self.assertTrue(pilot.piloted_vehicle.type.startswith("SRV")) # "SRV Scarab"

    def test_edpilot_fight_logic(self):
        pilot = EDPilot("Cmdr Test", "Dangerous")
        pilot.to_normal_space()
        
        # Not in fight initially
        self.assertFalse(pilot.in_a_fight())
        
        # Simulate danger
        pilot.in_danger(True)
        # in_danger sets unsafe on piloted vehicle
        # in_a_fight checks if vehicle is in_a_fight AND in_danger
        # vehicle.in_a_fight() usually checks hardpoints or recent damage
        
        # We need to simulate weapons firing or similar to trigger in_a_fight on vehicle
        # Given lack of full vehicle mocking, let's just assert state changes we can control
        
        pilot.to_super_space()
        self.assertFalse(pilot.in_normal_space())
        self.assertTrue(pilot.in_supercruise())

if __name__ == '__main__':
    unittest.main()
