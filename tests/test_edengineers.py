import unittest
from unittest.mock import MagicMock, patch
from edr.edengineers import EDEngineers, EDEngineerFactory, EDKitFowler

class TestEDEngineers(unittest.TestCase):
    def setUp(self):
        # Mock ODYSSEY_MATS to avoid dependency on actual JSON file
        self.mock_mats = {
            "push": {"used": 1},
            "opinionpolls": {"used": 1},
            "useless_mat": {"used": 0}
        }
        self.patcher = patch.dict(EDEngineers.ODYSSEY_MATS, self.mock_mats, clear=True)
        self.patcher.start()
        
        self.engineers = EDEngineers()

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        self.assertIn("kit fowler", self.engineers.engineers)
        self.assertIsInstance(self.engineers.engineers["kit fowler"], EDKitFowler)

    def test_update(self):
        event = {
            "Engineers": [
                {
                    "Engineer": "Kit Fowler",
                    "Progress": "Unlocked",
                    "RankProgress": 0,
                    "Rank": 5
                }
            ]
        }
        self.engineers.update(event)
        kit = self.engineers.engineers["kit fowler"]
        self.assertEqual(kit.progress, "Unlocked")
        self.assertEqual(kit.rank, 5)

    def test_dibs_unlocked_engineer(self):
        # Kit Fowler needs opinionpolls if not unlocked, but checks 'dibs' logic
        # Implementation of EDKitFowler.dibs:
        # if progress is None: needed["push"] = 5
        # if progress != "Unlocked": needed["opinionpolls"] = 5
        
        # Default is progress None
        kit = self.engineers.engineers["kit fowler"]
        self.assertIsNone(kit.progress)
        
        materials = {"push": 10}
        dibs = self.engineers.dibs(materials)
        # Should want push
        self.assertTrue(any("push" in d for d in dibs))

    def test_is_useless(self):
        self.assertTrue(self.engineers.is_useless("useless_mat"))
        # push is used by engineer (Kit Fowler) so not useless
        self.assertFalse(self.engineers.is_useless("push"))
        # Unknown mat is safe (False)
        self.assertFalse(self.engineers.is_useless("unknown_mat"))

    def test_factory_unknown(self):
        eng = EDEngineerFactory.from_engineer_name("NonExistent")
        self.assertEqual(eng.type, "Unknown")
        
    def test_factory_known(self):
        eng = EDEngineerFactory.from_engineer_name("Domino Green")
        self.assertEqual(eng.name, "Domino Green")

    def test_is_contributing(self):
        # Push is relevant to Kit Fowler
        self.assertTrue(self.engineers.is_contributing("push"))
        self.assertFalse(self.engineers.is_contributing("useless_mat"))

if __name__ == '__main__':
    unittest.main()
