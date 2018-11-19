import config_tests
from unittest import TestCase, main
from edinstance import EDInstance
import calendar, time

class MockCmdr(object):
    def __init__(self, name):
        self.name = name
    
    def json(self):
        return {
            "cmdr": self.name
        }

class TestEDInstance(TestCase):
    def test_anyone_beside(self):
        instance = EDInstance()
        self.assertFalse(instance.anyone_beside(None))

        instance.player_in(MockCmdr("LeKeno"))
        self.assertTrue(instance.anyone_beside(None))
        self.assertFalse(instance.anyone_beside(["LeKeno"]))
        self.assertFalse(instance.anyone_beside(["lekeno"]))

        instance.player_in(MockCmdr("Arguendo"))
        self.assertTrue(instance.anyone_beside(None))
        self.assertTrue(instance.anyone_beside(["LeKeno"]))
        self.assertTrue(instance.anyone_beside(["lekeno"]))
        self.assertFalse(instance.anyone_beside(["lekeno", "arguendo"]))

        instance.player_in(MockCmdr("Ozram"))
        self.assertTrue(instance.anyone_beside(None))
        self.assertTrue(instance.anyone_beside(["LeKeno"]))
        self.assertTrue(instance.anyone_beside(["lekeno"]))
        self.assertTrue(instance.anyone_beside(["lekeno", "arguendo"]))
        self.assertFalse(instance.anyone_beside(["lekeno", "arguendo", "ozram"]))

    def test_empty(self):
        instance = EDInstance()
        self.assertTrue(instance.is_empty())

        instance.player_in(MockCmdr("LeKeno"))
        self.assertFalse(instance.is_empty())

        instance.reset()
        self.assertTrue(instance.is_empty())

        instance.player_in(MockCmdr("LeKeno"))
        self.assertFalse(instance.is_empty())
        instance.player_out("LeKeno")
        self.assertTrue(instance.is_empty())

    def test_player_in_n_out(self):
        instance = EDInstance()
        self.assertIsNone(instance.player("LeKeno"))

        lekeno = MockCmdr("LeKeno")
        instance.player_in(lekeno)
        self.assertEqual(instance.player("LeKeno"), lekeno)

        instance.player_out("lekeno")
        self.assertIsNone(instance.player("LeKeno"))

    
    def test_player_noteworthy_changes(self):
        now = 1000 * calendar.timegm(time.gmtime())
        instance = EDInstance()
        changes = instance.noteworthy_changes_json()
        self.assertAlmostEquals(changes["timestamp"], now)
        self.assertEqual(changes["players"], [])

        changes = instance.noteworthy_changes_json()
        self.assertIsNone(changes)

        instance.player_in(MockCmdr("LeKeno"))
        changes = instance.noteworthy_changes_json()
        self.assertAlmostEquals(changes["timestamp"], now)
        self.assertEqual(changes["players"], [{"cmdr": "LeKeno"}])

        instance.player_out("LeKeno")
        changes = instance.noteworthy_changes_json()
        self.assertAlmostEquals(changes["timestamp"], now)
        self.assertEqual(changes["players"], [])

        instance.player_out("LeKeno")
        changes = instance.noteworthy_changes_json()
        self.assertIsNone(changes)

    def test_players_nb(self):
        instance = EDInstance()
        self.assertEqual(instance.players_nb(), 0)

        instance.player_in(MockCmdr("LeKeno"))
        self.assertEqual(instance.players_nb(), 1)

        instance.player_out("LeKeno")
        self.assertEqual(instance.players_nb(), 0)

        instance.player_in(MockCmdr("LeKeno"))
        self.assertEqual(instance.players_nb(), 1)
        instance.player_in(MockCmdr("Arguendo"))
        self.assertEqual(instance.players_nb(), 2)
        instance.player_in(MockCmdr("Ozram"))
        self.assertEqual(instance.players_nb(), 3)

        instance.player_out("LeKeno")
        self.assertEqual(instance.players_nb(), 2)
        instance.player_out("Ozram")
        self.assertEqual(instance.players_nb(), 1)
        instance.player_out("Ozram")
        self.assertEqual(instance.players_nb(), 1)
        instance.player_out("Dummy")
        self.assertEqual(instance.players_nb(), 1)
        instance.player_out("Arguendo")
        self.assertEqual(instance.players_nb(), 0)
        instance.player_out("Dummy")
        self.assertEqual(instance.players_nb(), 0)

if __name__ == '__main__':
    main()