
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
from edr.models.edengineers import (
    EDEngineer,
    EDDominoGreen,
    EDKitFowler,
    EDEngineerFactory,
    EDEngineers,
    EDUnknownEngineer
)

class TestEDEngineer(unittest.TestCase):
    def test_base_engineer(self):
        engineer = EDEngineer()
        self.assertIsNone(engineer.name)
        self.assertIsNone(engineer.progress)
        self.assertFalse(engineer.relevant("Anything"))
        self.assertFalse(engineer.interested_in("Anything"))
        self.assertIsNone(engineer.dibs({}))

    def test_update_progress(self):
        engineer = EDEngineer()
        engineer.name = "Test Engineer"
        
        progress_data = {
            "Engineer": "Test Engineer",
            "Progress": "Unlocked",
            "Rank": 5,
            "RankProgress": 100
        }
        engineer.update(progress_data)
        
        self.assertEqual(engineer.progress, "Unlocked")
        self.assertEqual(engineer.rank, 5)
        self.assertEqual(engineer.rank_progress, 100)

    def test_update_mismatch_name(self):
        engineer = EDEngineer()
        engineer.name = "Test Engineer"
        
        progress_data = {
            "Engineer": "Other Engineer",
            "Progress": "Unlocked"
        }
        engineer.update(progress_data)
        # Should not update
        self.assertIsNone(engineer.progress)

class TestSpecificEngineers(unittest.TestCase):
    def test_kit_fowler(self):
        engineer = EDKitFowler()
        self.assertEqual(engineer.name, "Kit Fowler")
        
        # Initial state (Locked)
        self.assertTrue(engineer.relevant("opinionpolls"))
        self.assertTrue(engineer.interested_in("push"))
        self.assertTrue(engineer.interested_in("opinionpolls"))
        
        dibs = engineer.dibs({})
        self.assertEqual(dibs.get("push"), 5)

        # Unlocked state
        engineer.update({"Engineer": "Kit Fowler", "Progress": "Unlocked"})
        self.assertFalse(engineer.interested_in("push"))
        self.assertFalse(engineer.interested_in("opinionpolls"))
        self.assertFalse(engineer.dibs({}))

class TestEDEngineerFactory(unittest.TestCase):
    def test_factory_creation(self):
        e = EDEngineerFactory.from_engineer_name("Domino Green")
        self.assertIsInstance(e, EDDominoGreen)
        
        e = EDEngineerFactory.from_engineer_name("Unknown Name")
        self.assertIsInstance(e, EDUnknownEngineer)

    def test_from_progress(self):
        progress = {"Engineer": "Kit Fowler", "Progress": "Unlocked"}
        e = EDEngineerFactory.from_engineer_progress_dict(progress)
        self.assertIsInstance(e, EDKitFowler)
        self.assertEqual(e.progress, "Unlocked")

class TestEDEngineers(unittest.TestCase):
    def setUp(self):
        self.odyssey_mats_mock = {
            "carbonfibreplating": {"used": 1},
            "encryptedmemorychip": {"used": 0}
        }
        self.patcher = patch('builtins.open', mock_open(read_data=json.dumps(self.odyssey_mats_mock)))
        self.patcher.start()
        
        # Also need to patch os.path.join because the class level attribute initialization uses it
        # However, the class attribute is initialized at import time. 
        # So we might need to rely on the side_effect or just instantiate it and hope the file read behaves mocked if we were re-importing or if we patch before class definition...
        # Since class is already imported, the ODYSSEY_MATS is already populated.
        # We should patch the attribute on the class directly for the test instance.
        EDEngineers.ODYSSEY_MATS = self.odyssey_mats_mock

    def tearDown(self):
        self.patcher.stop()

    def test_process_update(self):
        engineers = EDEngineers()
        event = {
            "Engineers": [
                {"Engineer": "Kit Fowler", "Progress": "Unlocked"},
                {"Engineer": "Domino Green", "Progress": "Invited"}
            ]
        }
        engineers.update(event)
        
        self.assertEqual(engineers.engineers["kit fowler"].progress, "Unlocked")
        self.assertEqual(engineers.engineers["domino green"].progress, "Invited")

    def test_relevance_checks(self):
        engineers = EDEngineers()
        # Kit Fowler needs OpinionPolls
        self.assertTrue(engineers.is_contributing("OpinionPolls"))
        
        # Carbon Fibre Plating is used (mocked data)
        # Note: EDEngineers logic for useless check:
        # if not in odyssey_mats -> return False (safe)
        # if used > 0 -> return False
        # else -> check if contributing
        
        # "carbonfibreplating" used=1
        self.assertFalse(engineers.is_useless("carbonfibreplating")) 
        
        # "encryptedmemorychip" used=0, and not relevant to any engineer
        self.assertTrue(engineers.is_useless("encryptedmemorychip"))

if __name__ == '__main__':
    unittest.main()
