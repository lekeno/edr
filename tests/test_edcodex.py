import unittest
from edcodex import EDCodex # EDR_INTERNAL

class TestEDCodex(unittest.TestCase):
    def setUp(self):
        self.codex = EDCodex()

    def test_init(self):
        self.assertIsInstance(self.codex.entries, dict)
        self.assertEqual(len(self.codex.entries), 0)

    def test_process_scan_organic_analyse(self):
        # Currently a pass-through, but verifying it doesn't crash
        event = {
            "event": "ScanOrganic",
            "ScanType": "Analyse",
            "Genus": "Tubus",
            "Species": "Tubus Sororibus"
        }
        try:
            self.codex.process(event)
        except Exception as e:
            self.fail(f"process raised {e} unexpectedly!")

    def test_process_codex_entry(self):
        # Currently a pass-through
        event = {
            "event": "CodexEntry",
            "Name": "Some Discovery",
            "SubCategory": "Geology"
        }
        try:
            self.codex.process(event)
        except Exception as e:
            self.fail(f"process raised {e} unexpectedly!")

    def test_process_irrelevant_event(self):
        event = {
            "event": "FSDJump",
            "StarSystem": "Sol"
        }
        # Should do nothing
        self.codex.process(event)
        self.assertEqual(len(self.codex.entries), 0)

if __name__ == '__main__':
    unittest.main()
