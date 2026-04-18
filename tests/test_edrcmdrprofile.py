
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edrcmdrprofile import EDRCmdrProfile, EDRCmdrDexProfile

class TestEDRCmdrDexProfile(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.models.edrcmdrprofile.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.js_epoch_now.return_value = 1000
        
        self.i18n_patch = patch('edr.models.edrcmdrprofile._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        self.i18n_patch.stop()

    def test_init_empty(self):
        dex = EDRCmdrDexProfile()
        self.assertIsNone(dex._alignment)
        self.assertFalse(dex.friend)
        self.assertIsNone(dex.memo)
        self.assertEqual(dex.created, 1000)
        self.assertEqual(dex.updated, 1000)

    def test_alignment(self):
        dex = EDRCmdrDexProfile()
        
        # Set alignment
        self.mock_time.js_epoch_now.return_value = 1001
        dex.alignment = "outlaw"
        self.assertEqual(dex.alignment, "outlaw")
        self.assertEqual(dex._alignment, "outlaw")
        self.assertEqual(dex.updated, 1001)
        
        # Invalid alignment
        dex.alignment = "invalid"
        self.assertEqual(dex.alignment, "outlaw") # Unchanged
        
        # Clear alignment
        dex.alignment = None
        self.assertIsNone(dex.alignment)

    def test_iff(self):
        dex = EDRCmdrDexProfile()
        dex.iff = "enemy"
        self.assertEqual(dex.iff, "enemy")
        self.assertFalse(dex.is_ally())
        
        dex.iff = "ally"
        self.assertTrue(dex.is_ally())

    def test_tags_and_tagging(self):
        dex = EDRCmdrDexProfile()
        
        # Tagging alignment
        dex.tag("outlaw")
        self.assertEqual(dex.alignment, "outlaw")
        
        # Tagging IFF
        dex.tag("enemy")
        self.assertEqual(dex.iff, "enemy")
        
        # Tagging Friend
        dex.tag("friend")
        self.assertTrue(dex.friend)
        
        # Generic tag
        dex.tag("ganker")
        self.assertIn("ganker", dex.tags)
        
        # Untagging
        dex.untag("ganker")
        self.assertNotIn("ganker", dex.tags)
        
        dex.untag("enemy")
        self.assertIsNone(dex.iff)

class TestEDRCmdrProfile(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.models.edrcmdrprofile.EDTime')
        self.mock_time = self.time_patch.start()
        
        self.i18n_patch = patch('edr.models.edrcmdrprofile._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        self.i18nc_patch = patch('edr.models.edrcmdrprofile._c', side_effect=lambda x, y=None: x)
        self.mock_i18nc = self.i18nc_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        self.i18n_patch.stop()
        self.i18nc_patch.stop()

    def test_karma(self):
        profile = EDRCmdrProfile()
        profile.karma = 500
        self.assertEqual(profile.karma, 500)
        
        profile.karma = 2000 # Max cap
        self.assertEqual(profile.karma, 1000)
        
        profile.karma = -2000 # Min cap
        self.assertEqual(profile.karma, -1000)

    def test_from_inara(self):
        profile = EDRCmdrProfile()
        json_cmdr = {
            "commanderName": "CmdrInara",
            "commanderWing": {"wingName": "The Wing", "wingID": 123, "wingMemberRank": "Leader"},
            "preferredGameRole": "Trader",
            "preferredPowerName": "Aisling Duval",
            "inaraURL": "http://inara.cz/cmdr/1"
        }
        profile.from_inara_api(json_cmdr)
        
        self.assertEqual(profile.name, "CmdrInara")
        self.assertEqual(profile.squadron, "The Wing")
        self.assertEqual(profile.squadron_id, 123)
        self.assertEqual(profile.role, "Trader")
        self.assertEqual(profile.powerplay, "Aisling Duval")
        self.assertEqual(profile.url, "http://inara.cz/cmdr/1")

    def test_from_dict(self):
        profile = EDRCmdrProfile()
        json_cmdr = {
            "name": "CmdrEDR",
            "karma": 100,
            "alignmentHints": {"outlaw": 5, "neutral": 1}
        }
        profile.from_dict(json_cmdr)
        
        self.assertEqual(profile.name, "CmdrEDR")
        self.assertEqual(profile.karma, 100)
        self.assertEqual(profile.alignment_hints["outlaw"], 5)

    def test_complement(self):
        p1 = EDRCmdrProfile()
        p1.name = "CmdrTest"
        p1.role = "Pirate"
        
        p2 = EDRCmdrProfile()
        p2.name = "CmdrTest"
        p2.squadron = "Dark Wheel"
        
        p1.complement(p2)
        
        self.assertEqual(p1.squadron, "Dark Wheel")
        self.assertEqual(p1.role, "Pirate") # Preserved
        
        p3 = EDRCmdrProfile()
        p3.name = "OtherCmdr"
        res = p1.complement(p3)
        self.assertFalse(res) # Mismatch name

    def test_dex_augmentation(self):
        profile = EDRCmdrProfile()
        profile.name = "CmdrTest"
        
        dex_data = {
            "name": "CmdrTest",
            "alignment": "outlaw",
            "tags": ["ganker"]
        }
        
        augmented = profile.dex(dex_data)
        self.assertTrue(augmented)
        self.assertEqual(profile.dex_profile.alignment, "outlaw")
        self.assertIn("ganker", profile.dex_profile.tags)
        
        # Test dangerous check
        self.assertTrue(profile.is_dangerous())

    def test_is_dangerous_karma(self):
        profile = EDRCmdrProfile()
        profile.karma = -500
        self.assertTrue(profile.is_dangerous())
        
        profile.karma = 500
        self.assertFalse(profile.is_dangerous())

    def test_short_profile(self):
        profile = EDRCmdrProfile()
        profile.name = "CmdrTest"
        profile.karma = -1000
        
        # Short profile should contain "Outlaw++++" (from readable karma)
        # Mocked i18n returns "Outlaw++++" as is? No, EDRCmdrProfile.readable_karma uses LUT.
        # Lut strings are wrapped in _().
        # My mock returns input. 
        # So it should be "Outlaw++++".
        
        summary = profile.short_profile()
        self.assertIn("Outlaw++++", summary)
        self.assertIn("✪EDR", summary)

if __name__ == '__main__':
    unittest.main()