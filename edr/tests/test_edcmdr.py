import config_tests
from unittest import TestCase, main
from edentities import EDCmdr

class TestEDCmdr(TestCase):
    def test_in_solo_private(self):
        cmdr = EDCmdr()
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = ""
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = "dummy"
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = "Open"
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = "Solo"
        self.assertTrue(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = "Group"
        self.assertTrue(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = "solo"
        self.assertFalse(cmdr.in_solo_or_private())

        cmdr = EDCmdr()
        cmdr.game_mode = "group"
        self.assertFalse(cmdr.in_solo_or_private())

    def test_in_open(self):
        cmdr = EDCmdr()
        self.assertFalse(cmdr.in_open())

        cmdr = EDCmdr()
        cmdr.game_mode = ""
        self.assertFalse(cmdr.in_open())

        cmdr = EDCmdr()
        cmdr.game_mode = "dummy"
        self.assertFalse(cmdr.in_open())

        cmdr = EDCmdr()
        cmdr.game_mode = "Open"
        self.assertTrue(cmdr.in_open())

        cmdr = EDCmdr()
        cmdr.game_mode = "open"
        self.assertFalse(cmdr.in_open())

        cmdr = EDCmdr()
        cmdr.game_mode = "Group"
        self.assertFalse(cmdr.in_open())

        cmdr = EDCmdr()
        cmdr.game_mode = "Solo"
        self.assertFalse(cmdr.in_open())

    def test_lifecycle_and_mode(self):
        cmdr = EDCmdr()
        cmdr.game_mode = "Open"
        cmdr.inception()
        self.assertTrue(cmdr.in_open())
        cmdr.killed()
        self.assertFalse(cmdr.in_open())
        cmdr.resurrect()
        self.assertTrue(cmdr.in_open())

    def test_join_wing(self):
        cmdr = EDCmdr()
        cmdr.inception()
        wing_members = ["Ozram", "Arguendo", "Patch"]
        for member in wing_members:
            self.assertFalse(cmdr.is_friend_or_in_wing(member))
        self.assertFalse(cmdr.is_friend_or_in_wing("dummy"))

        cmdr.join_wing(wing_members)
        for member in wing_members:
            self.assertTrue(cmdr.is_friend_or_in_wing(member))
        self.assertEquals(len(cmdr.wing), 3)

        self.assertFalse(cmdr.is_friend_or_in_wing("dummy"))
        cmdr.leave_wing()
        self.assertEquals(len(cmdr.wing), 0)

        for member in wing_members:
            self.assertFalse(cmdr.is_friend_or_in_wing(member))
    
    def test_add_to_wing(self):
        cmdr = EDCmdr()
        cmdr.inception()
        wing_members = ["Ozram", "Arguendo", "Patch"]
        for member in wing_members:
            cmdr.add_to_wing(member)
            self.assertTrue(cmdr.is_friend_or_in_wing(member))

        self.assertEquals(len(cmdr.wing), 3)
        cmdr.add_to_wing(wing_members[0])
        self.assertEquals(len(cmdr.wing), 3)

        
        for member in wing_members:
            self.assertTrue(cmdr.is_friend_or_in_wing(member))

        self.assertFalse(cmdr.is_friend_or_in_wing("dummy"))
    
    def test_ship(self):
        cmdr = EDCmdr()
        cmdr.ship ="empire_trader"
        self.assertEqual(cmdr.ship, "Imperial Clipper")

        cmdr.ship = "DuMmY"
        self.assertEqual(cmdr.ship, "DuMmY".lower())

if __name__ == '__main__':
    main()