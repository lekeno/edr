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
        self.assertEquals(sample.alignment, dex["alignment"])
        self.assertEquals(sample.created, dex["created"])
        self.assertEquals(sample.friend, dex["friend"])
        self.assertEquals(sample.memo, dex["memo"])
        self.assertEquals(sample.updated, dex["updated"])
        self.assertFalse(sample.is_useless())
        self.assertFalse(tags.difference(sample.tags))

        dex = {}
        now = EDTime.js_epoch_now()
        sample = EDRCmdrDexProfile(dex)
        self.assertTrue(sample.is_useless())
        self.assertEquals(sample.alignment, None)
        self.assertEquals(sample.friend, False)
        self.assertEquals(sample.memo, None)
        self.assertEquals(sample.tags, set([]))
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
        self.assertEquals(sample.alignment, u"outlaw")
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        sample.alignment = u"neutral"
        self.assertEquals(sample.alignment, u"neutral")
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        sample.alignment = u"enforcer"
        self.assertEquals(sample.alignment, u"enforcer")
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        current = sample.alignment
        updated = sample.updated
        sample.alignment = u"dummy"
        self.assertEquals(sample.alignment, current)
        self.assertEqual(sample.updated, updated)
        self.assertEqual(sample.created, created)

        sample.alignment = u"Outlaw"
        self.assertEquals(sample.alignment, current)
        self.assertEqual(sample.updated, updated)
        self.assertEqual(sample.created, created)

        sample.alignment = None
        self.assertEquals(sample.alignment, None)
        now = EDTime.js_epoch_now()
        self.assertAlmostEqual(sample.updated/100.0, now/100.0, 1)
        self.assertEqual(sample.created, created)

        current = sample.alignment
        updated = sample.updated
        sample.alignment = current
        self.assertEquals(sample.alignment, current)
        self.assertEqual(sample.updated, updated)
        self.assertEqual(sample.created, created)
        

if __name__ == '__main__':
    main()