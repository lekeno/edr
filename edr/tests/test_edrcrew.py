import config_tests
from unittest import TestCase, main
from edentities import EDRCrew
import calendar, time

class TestEDCrew(TestCase):
    def test_add_remove(self):
        captain = "LeKeno"
        now = calendar.timegm(time.gmtime())
        crew = EDRCrew(captain)

        self.assertEqual(crew.captain, captain)
        self.assertAlmostEqual(crew.creation, now, 100)
        self.assertEqual(crew.members.keys(), [captain])
        self.assertAlmostEqual(crew.members[captain], now, 100)

        result = crew.add(captain)
        self.assertFalse(result)
        self.assertEqual(crew.captain, captain)
        self.assertAlmostEqual(crew.creation, now, 100)
        self.assertEqual(crew.members.keys(), [captain])
        self.assertAlmostEqual(crew.members[captain], now, 100)

        member = "Ozram"
        result = crew.add(member)
        self.assertTrue(result)
        self.assertEqual(crew.captain, captain)
        self.assertAlmostEqual(crew.creation, now, 100)
        self.assertEqual(crew.members.keys(), [captain, member])
        self.assertAlmostEqual(crew.members[captain], now, 100)
        nower = calendar.timegm(time.gmtime())
        self.assertAlmostEqual(crew.members[member], nower, 100)

        result = crew.remove("not-a-member")
        self.assertFalse(result)
        self.assertEqual(crew.captain, captain)
        self.assertAlmostEqual(crew.creation, now, 100)
        self.assertEqual(crew.members.keys(), [captain, member])
        self.assertAlmostEqual(crew.members[captain], now, 100)
        self.assertAlmostEqual(crew.members[member], nower, 100)

        result = crew.remove(member)
        self.assertTrue(result)
        self.assertEqual(crew.captain, captain)
        self.assertAlmostEqual(crew.creation, now, 100)
        self.assertEqual(crew.members.keys(), [captain])
        self.assertAlmostEqual(crew.members[captain], now, 100)

    def test_disband(self):
        captain = "LeKeno"
        now = calendar.timegm(time.gmtime())
        crew = EDRCrew(captain)
        crew.add("Ozram")
        crew.add("Arguendo")
        crew.add("Patch")
        self.assertEqual(crew.captain, captain)
        self.assertAlmostEqual(crew.creation, now, 100)
        self.assertAlmostEqual(crew.members[captain], now, 100)
        self.assertAlmostEqual(crew.members["Ozram"], now, 100)
        self.assertAlmostEqual(crew.members["Arguendo"], now, 100)
        self.assertAlmostEqual(crew.members["Patch"], now, 100)

        crew.disband()
        self.assertIsNone(crew.captain)
        self.assertIsNone(crew.creation)
        self.assertDictEqual(crew.members, {})
        self.assertFalse(crew.is_captain(captain))
        self.assertEqual(crew.duration("Ozram"), 0)

    def test_is_captain(self):
        captain = "LeKeno"
        crew = EDRCrew(captain)
        self.assertTrue(crew.is_captain(captain))
        self.assertTrue("Ozram")

        crew.add("Ozram")
        self.assertFalse(crew.is_captain("Ozram"))
        self.assertTrue(crew.is_captain(captain))        

    def test_duration(self):
        captain = "LeKeno"
        crew = EDRCrew(captain)
        crew.add("Ozram")
        
        self.assertAlmostEqual(crew.duration(captain), 0, 100)
        self.assertAlmostEqual(crew.duration("Ozram"), 0, 100)
        time.sleep(1.0)
        self.assertAlmostEqual(crew.duration(captain), 1, 100)
        self.assertAlmostEqual(crew.duration("Ozram"), 1, 100)
        
if __name__ == '__main__':
    main()