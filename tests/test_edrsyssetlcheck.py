
import unittest
from unittest.mock import Mock, MagicMock
from edr.controllers import edrsyssetlcheck

class TestEDRSystemSettlementCheck(unittest.TestCase):
    def setUp(self):
        self.checker = edrsyssetlcheck.EDRSystemSettlementCheck()

    def test_check_system(self):
        self.assertTrue(self.checker.check_system({"distance": 10}))
        self.assertFalse(self.checker.check_system({"distance": 100}))

    def test_check_settlement_type(self):
        self.checker.max_sc_distance = 1000
        
        # Valid settlement
        settlement = {"name": "Settlement A", "type": "Odyssey Settlement", "distanceToArrival": 500}
        self.assertTrue(self.checker.check_settlement(settlement))

        # Not a settlement
        starport = {"name": "Starport A", "type": "Coriolis Starport", "distanceToArrival": 500}
        self.assertFalse(self.checker.check_settlement(starport))

        # Too far
        far_settlement = {"name": "Settlement B", "type": "Odyssey Settlement", "distanceToArrival": 2000}
        self.assertFalse(self.checker.check_settlement(far_settlement))

class TestEDRSettlementCheckerFactory(unittest.TestCase):
    def test_recognized_settlement(self):
        self.assertTrue(edrsyssetlcheck.EDRSettlementCheckerFactory.recognized_settlement("anarchy"))
        self.assertTrue(edrsyssetlcheck.EDRSettlementCheckerFactory.recognized_settlement("restore"))
        self.assertFalse(edrsyssetlcheck.EDRSettlementCheckerFactory.recognized_settlement("foobar"))

    def test_get_checker(self):
        edrsystems = Mock()
        
        # Combo check
        checker = edrsyssetlcheck.EDRSettlementCheckerFactory.get_checker("restore", 1000, edrsystems)
        self.assertIsInstance(checker, edrsyssetlcheck.EDRRetoreSettlementChecker)
        
        # Attribute check (Anarchy government)
        checker = edrsyssetlcheck.EDRSettlementCheckerFactory.get_checker("anarchy", 1000, edrsystems)
        self.assertIsInstance(checker, edrsyssetlcheck.EDROdySettlementCheck)
        self.assertIn("anarchy", checker.governments)

if __name__ == '__main__':
    unittest.main()
