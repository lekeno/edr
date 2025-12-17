import random

import config_tests
from unittest import TestCase, main
from edrcmdrprofile import EDRCmdrProfile

class TestEDRCmdrProfile(TestCase):
    def test_karma(self):
        cprof = EDRCmdrProfile()
        for _ in range(0, 9):
            karma = random.randint(cprof.min_karma(), cprof.max_karma())
            cprof.karma = karma
            self.assertEqual(cprof.karma, karma)

        cprof.karma = cprof.max_karma()
        self.assertEqual(cprof.karma, cprof.max_karma())

        cprof.karma = cprof.min_karma()
        self.assertEqual(cprof.karma, cprof.min_karma())

        cprof.karma = cprof.max_karma() + 1
        self.assertEqual(cprof.karma, cprof.max_karma())

        cprof.karma = cprof.min_karma() - 1
        self.assertEqual(cprof.karma, cprof.min_karma())
        
    def test_from_inara(self):
        json_cmdr = {
            "commanderName": "LeKeno",
            "commanderWing": {
                "wingName": "Cobra Kai",
                "wingID": 2135,
                "wingMemberRank": "Deputy Wing Commander"
            },
            "preferredGameRole": "Enforcer / Bounty Hunter",
            "preferredPowerName": "Edmund Mahon",
            "inaraAvatar": "http://example.com/avatar",
            "inaraURL": "http://example.com/profile"
        }

        cprof = EDRCmdrProfile()
        cprof.from_inara_api(json_cmdr)
        self.assertEqual(cprof.name, "LeKeno")
        self.assertEqual(cprof.squadron, "Cobra Kai")
        self.assertEqual(cprof.squadron_id, 2135)
        self.assertEqual(cprof.squadron_rank, "Deputy Wing Commander")
        self.assertEqual(cprof.role, "Enforcer / Bounty Hunter")
        self.assertEqual(cprof.powerplay, "Edmund Mahon")

        self.assertEqual(cprof.karma, 0)
        self.assertFalse(cprof.dyn_karma)
        self.assertIsNone(cprof.cid)
        self.assertIsNone(cprof.patreon)
        self.assertIsNone(cprof.dex_profile)
        self.assertIsNone(cprof.sqdrdex_profile)
        self.assertIsNone(cprof.alignment_hints)

    def test_from_dict(self):
        json_cmdr = {
            "name": "LeKeno",
            "squadron": "Cobra Kai",
            "squadronID": 2135,
            "squadronRank": "Deputy Wing Commander",
            "role": "Enforcer / Bounty Hunter",
            "karma": 100,
            "alignmentHints": {"outlaw": 0, "neutral": 5, "enforcer": 95}
        }

        cprof = EDRCmdrProfile()
        cprof.from_dict(json_cmdr)
        self.assertIsNone(cprof.cid)
        self.assertEqual(cprof.name, "LeKeno")
        self.assertEqual(cprof.karma, 100)
        self.assertFalse(cprof.dyn_karma)
        self.assertIsNone(cprof.patreon)
        self.assertIsNone(cprof.dex_profile)
        self.assertIsNone(cprof.sqdrdex_profile)
        self.assertEqual(cprof.alignment_hints, {"outlaw": 0, "neutral": 5, "enforcer": 95})

        self.assertEqual(cprof.squadron, "Cobra Kai")
        self.assertEqual(cprof.squadron_id, 2135)
        self.assertEqual(cprof.squadron_rank, "Deputy Wing Commander")
        self.assertEqual(cprof.role, "Enforcer / Bounty Hunter")
        self.assertIsNone(cprof.powerplay)

    def test_dex(self):
        cprof = EDRCmdrProfile()
        cprof.name = "Pirate"
        
        # Test creating a new dex profile via tag
        cprof.tag("outlaw")
        self.assertIsNotNone(cprof.dex_profile)
        self.assertEqual(cprof.dex_profile.alignment, "outlaw")
        self.assertTrue(cprof.is_dangerous())

        # Test tagging as friend
        cprof.tag("friend")
        self.assertTrue(cprof.is_friend())

        # Test memo
        cprof.memo("Watch out")
        self.assertEqual(cprof.dex_profile.memo, "Watch out")

        # Reuse existing dex profile logic
        dex_dict = {
            "name": "Pirate",
            "alignment": "outlaw",
            "tags": ["griefer"],
            "friend": False,
            "memo": "Avoid"
        }
        cprof2 = EDRCmdrProfile()
        cprof2.name = "Pirate"
        cprof2.dex(dex_dict)
        self.assertEqual(cprof2.dex_profile.alignment, "outlaw")
        self.assertEqual(cprof2.dex_profile.memo, "Avoid")
        self.assertIn("griefer", cprof2.dex_profile.tags)

    def test_is_dangerous(self):
        cprof = EDRCmdrProfile()
        self.assertFalse(cprof.is_dangerous())

        # Bad karma
        cprof.karma = -500
        self.assertTrue(cprof.is_dangerous())
        cprof.karma = 0

        # Outlaw alignment via dex
        cprof.name = "Bandit"
        cprof.tag("outlaw")
        self.assertTrue(cprof.is_dangerous())

        # Enemy squad
        cprof.name = "Enemy"
        cprof.sqdrdex({"name": "Enemy", "rel": "enemy", "by": "Me"})
        self.assertTrue(cprof.is_dangerous())

    def test_short_profile(self):
        cprof = EDRCmdrProfile()
        cprof.name = "CleanCmdr"
        cprof.karma = 500
        
        # Simple profile
        profile = cprof.short_profile()
        self.assertIn("Lawful++", profile)

        # Detailed profile
        cprof.squadron = "SpaceForce"
        cprof.role = "Explorer"
        profile = cprof.short_profile()
        self.assertIn("Lawful++", profile)
        self.assertIn("SpaceForce", profile)
        self.assertIn("Explorer", profile)

        # Dangerous profile
        cprof.karma = -1000
        cprof.tag("outlaw")
        profile = cprof.short_profile()
        self.assertIn("Outlaw++++", profile)
        self.assertIn("#outlaw", profile)

if __name__ == '__main__':
    main()