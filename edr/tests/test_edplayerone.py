import config_tests
from unittest import TestCase, main
from edentities import EDPlayerOne
import edvehicles

class TestEDPlayerOne(TestCase):
    def test_in_solo_private(self):
        cmdr = EDPlayerOne()
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = ""
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "dummy"
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "Open"
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "Solo"
        self.assertTrue(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "Group"
        self.assertTrue(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "solo"
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "group"
        self.assertFalse(cmdr.in_solo_or_private())

    def test_in_open(self):
        cmdr = EDPlayerOne()
        self.assertFalse(cmdr.in_open())

        cmdr = EDPlayerOne()
        cmdr.game_mode = ""
        self.assertFalse(cmdr.in_open())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "dummy"
        self.assertFalse(cmdr.in_open())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "Open"
        self.assertTrue(cmdr.in_open())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "open"
        self.assertFalse(cmdr.in_open())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "Group"
        self.assertFalse(cmdr.in_open())

        cmdr = EDPlayerOne()
        cmdr.game_mode = "Solo"
        self.assertFalse(cmdr.in_open())

    def test_lifecycle_and_mode(self):
        cmdr = EDPlayerOne()
        ship = edvehicles.EDVehicleFactory.from_internal_name("empire_trader")
        cmdr.game_mode = "Open"
        cmdr.inception()
        cmdr.update_vehicle_if_obsolete(ship)
        self.assertTrue(cmdr.in_open())
        self.assertEqual(cmdr.vehicle_type(), "Imperial Clipper")
        cmdr.killed()
        self.assertFalse(cmdr.in_open())
        self.assertEqual(cmdr.vehicle_type(), "Imperial Clipper")
        cmdr.resurrect()
        self.assertTrue(cmdr.in_open())
        self.assertEqual(cmdr.vehicle_type(), "Imperial Clipper")
        cmdr.killed()
        cmdr.resurrect(rebought = False)
        self.assertTrue(cmdr.in_open())
        self.assertNotEqual(cmdr.vehicle_type(), "Imperial Clipper")

    def test_join_wing(self):
        cmdr = EDPlayerOne()
        cmdr.inception()
        wing_members = ["Ozram", "Arguendo", "Patch"]
        for member in wing_members:
            self.assertFalse(cmdr.is_friend_or_in_wing(member))
        self.assertFalse(cmdr.is_friend_or_in_wing("dummy"))

        cmdr.join_wing(wing_members)
        for member in wing_members:
            self.assertTrue(cmdr.is_friend_or_in_wing(member))
        self.assertEquals(len(cmdr.wing.wingmates), 3)

        self.assertFalse(cmdr.is_friend_or_in_wing("dummy"))
        cmdr.leave_wing()
        self.assertEquals(len(cmdr.wing.wingmates), 0)

        for member in wing_members:
            self.assertFalse(cmdr.is_friend_or_in_wing(member))
    
    def test_add_to_wing(self):
        cmdr = EDPlayerOne()
        cmdr.inception()
        wing_members = ["Ozram", "Arguendo", "Patch"]
        for member in wing_members:
            cmdr.add_to_wing(member)
            self.assertTrue(cmdr.is_friend_or_in_wing(member))

        self.assertEquals(len(cmdr.wing.wingmates), 3)
        cmdr.add_to_wing(wing_members[0])
        self.assertEquals(len(cmdr.wing.wingmates), 3)

        
        for member in wing_members:
            self.assertTrue(cmdr.is_friend_or_in_wing(member))

        self.assertFalse(cmdr.is_friend_or_in_wing("dummy"))
    
    def test_vehicle_type(self):
        cmdr = EDPlayerOne()
        ship = edvehicles.EDVehicleFactory.from_internal_name("empire_trader")
        cmdr.update_vehicle_if_obsolete(ship)
        self.assertEqual(cmdr.vehicle_type(), "Imperial Clipper")

if __name__ == '__main__':
    main()