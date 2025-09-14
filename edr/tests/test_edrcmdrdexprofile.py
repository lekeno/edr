import config_tests
from unittest import TestCase, main
from edrcmdrprofile import EDRCmdrDexProfile
from edtime import EDTime

class TestEDRCmdrDexProfile(TestCase):
    def test_alignments(self):
        alignments = [u"outlaw", u"neutral", u"enforcer"]
        self.assertListEqual(alignments, EDRCmdrDexProfile.alignments())
    
    def test_constructor(self):
        tags = set(["test", "test2"])
        dex = {
            "alignment": "outlaw",
            "tags": tags,
            "friend": True,
            "memo": "This is a test.",
            "created": 1520655013854,
            "updated": 1520655037090
        }

        sample = EDRCmdrDexProfile(dex)
        self.assertEqual(sample.alignment, dex["alignment"])
        self.assertEqual(sample.created, dex["created"])
        self.assertEqual(sample.friend, dex["friend"])
        self.assertEqual(sample.memo, dex["memo"])
        self.assertEqual(sample.updated, dex["updated"])
        self.assertFalse(sample.is_useless())
        self.assertFalse(tags.difference(sample.tags))

        dex = {}
        now = EDTime.js_epoch_now()
        sample = EDRCmdrDexProfile(dex)
        self.assertTrue(sample.is_useless())
        self.assertEqual(sample.alignment, None)
        self.assertEqual(sample.friend, False)
        self.assertEqual(sample.memo, None)
        self.assertEqual(sample.tags, set([]))
        self.assertAlmostEqual(sample.created/100.0, now/100.0, 1)
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)

        raw_tags = ["Test1", "TeSt2", "t e s t  3", "test1"]
        tags = set(["test1", "test2", "test3"]) 
        dex = { "tags": set(raw_tags)}
        sample = EDRCmdrDexProfile(dex)
        self.assertFalse(sample.is_useless())
        self.assertFalse(tags.difference(sample.tags))

    def test_alignment(self):
        sample = EDRCmdrDexProfile()
        created = sample.created
        sample.alignment = u"outlaw"
        self.assertEqual(sample.alignment, u"outlaw")
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        sample.alignment = u"neutral"
        self.assertEqual(sample.alignment, u"neutral")
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        sample.alignment = u"enforcer"
        self.assertEqual(sample.alignment, u"enforcer")
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        current = sample.alignment
        updated = sample.updated
        sample.alignment = u"dummy"
        self.assertEqual(sample.alignment, current)
        self.assertEqual(sample.updated, updated)
        self.assertEqual(sample.created, created)

        sample.alignment = u"Outlaw"
        self.assertEqual(sample.alignment, current)
        self.assertEqual(sample.updated, updated)
        self.assertEqual(sample.created, created)

        sample.alignment = None
        self.assertEqual(sample.alignment, None)
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        current = sample.alignment
        updated = sample.updated
        sample.alignment = current
        self.assertEqual(sample.alignment, current)
        self.assertEqual(sample.updated, updated)
        self.assertEqual(sample.created, created)
        

if __name__ == '__main__':
    main()