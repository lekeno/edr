
import unittest
from edr.edrstatecheck import (
    EDRBasicStateCheck,
    EDRPharmaceuticalIsolatorsCheck,
    EDRImperialShieldingCheck,
    EDRProtoLightAlloysCheck
)

class TestEDRStateCheck(unittest.TestCase):
    def test_basic_state_check(self):
        checker = EDRBasicStateCheck()
        checker.mandatory_state("Boom")
        
        # Good state
        self.assertTrue(checker.grade_state("Boom") > 0)
        
        # Bad state
        self.assertEqual(checker.grade_state("Bust"), 0)

    def test_pharmaceutical_isolators(self):
        checker = EDRPharmaceuticalIsolatorsCheck()
        # Mandatory state: Outbreak
        self.assertTrue(checker.grade_state("Outbreak") > 0)
        self.assertEqual(checker.grade_state("Boom"), 0)
        
        # Allegiance hints (optional)
        self.assertTrue(checker.grade_allegiance("Independent") > 1) # base is 1, match adds 1

    def test_imperial_shielding(self):
        checker = EDRImperialShieldingCheck()
        # Mandatory state: None or Election
        self.assertTrue(checker.grade_state("Election") > 0)
        self.assertTrue(checker.grade_state("None") > 0)
        self.assertEqual(checker.grade_state("Boom"), 0)
        
        # Mandatory allegiance: Empire
        self.assertEqual(checker.grade_allegiance("Federation"), 0)
        self.assertTrue(checker.grade_allegiance("Empire") > 0)

    def test_proto_light_alloys(self):
        checker = EDRProtoLightAlloysCheck()
        # Mandatory state: Boom
        self.assertTrue(checker.grade_state("Boom") > 0)
        self.assertEqual(checker.grade_state("War"), 0)
