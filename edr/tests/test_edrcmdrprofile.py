import random

import config_tests
from unittest import TestCase, main
from edrcmdrprofile import EDRCmdrProfile

class TestEDRCmdrProfile(TestCase):
    def test_karma(self):
        cprof = EDRCmdrProfile()
        for n in range(0, 9):
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
            # TODO
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
            # TODO
        }

        cprof = EDRCmdrProfile()
        cprof.from_dict(json_cmdr)
        self.assertEqual(cprof.cid, "")
        self.assertEqual(cprof.name, "LeKeno")
        self.assertEqual(cprof.karma, 0)
        self.assertFalse(cprof.dyn_karma)
        self.assertIsNone(cprof.patreon)
        self.assertIsNone(cprof.dex_profile)
        self.assertIsNone(cprof.sqdrdex_profile)
        self.assertIsNone(cprof.alignment_hints)

        self.assertIsNone(cprof.squadron)
        self.assertIsNone(cprof.squadron_id)
        self.assertIsNone(cprof.squadron_rank)
        self.assertIsNone(cprof.role)
        self.assertIsNone(cprof.powerplay)


if __name__ == '__main__':
    main()