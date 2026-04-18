
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrstatecheck import EDRBasicStateCheck, EDRPharmaceuticalIsolatorsCheck

class TestEDRStateCheck(unittest.TestCase):
    def setUp(self):
        self.i18n_patch = patch('edr.controllers.edrstatecheck._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()

    def tearDown(self):
        self.i18n_patch.stop()

    def test_grade_system_population(self):
        checker = EDRBasicStateCheck()
        # Pop < 1M -> Grade 1
        system = {'information': {'population': 500000}}
        self.assertEqual(checker.grade_system(system), 1)
        
        # Pop 1M -> Grade 1 + max(3, log10(10)) = 1 + 3 = 4?
        # log10(1M/100k) = log10(10) = 1. max(3, 1) = 3. Grade = 1 + 3 = 4.
        system = {'information': {'population': 1000000}}
        self.assertEqual(checker.grade_system(system), 4)

    def test_grade_system_security(self):
        checker = EDRBasicStateCheck()
        checker.mandatory_security('anarchy')
        
        # Matching security
        system = {'information': {'security': 'Anarchy', 'population': 0}}
        self.assertEqual(checker.grade_system(system), 1)
        
        # Mismatch
        system = {'information': {'security': 'High', 'population': 0}}
        self.assertEqual(checker.grade_system(system), 0)

    def test_grade_state(self):
        checker = EDRBasicStateCheck()
        checker.mandatory_state('boom')
        checker.optional_state('expansion')
        checker.forbidden_state('war')
        
        # Mandatory match
        self.assertEqual(checker.grade_state('Boom'), 1)
        
        # Mandatory match + optional
        # Check logic: 
        # cstate = 'expansion'. not in mandatory ('boom') -> returns 0.
        # So a state cannot be BOTH mandatory and optional usually, 
        # OR grade_state checks if THE state passed in matches constraints.
        # If mandatory is set, state MUST be in mandatory.
        # If I want to test optional, I should have it in mandatory too?
        # Or logic is: if mandatory_states is set, input state must be in it.
        # If optional_states is set, if input state is in it, +1.
        
        # If I have mandatory=['boom'], optional=['expansion'].
        # Input 'Boom': in mandatory. Not in optional. Grade 1.
        # Input 'Expansion': not in mandatory. Returns 0.
        
        # Let's verify code:
        # if self.mandatory_states: if cstate not in self.mandatory_states: return 0
        
        self.assertEqual(checker.grade_state('War'), 0) # Forbidden
        
    def test_grade_allegiance(self):
        checker = EDRBasicStateCheck()
        checker.mandatory_allegiance('Empire')
        
        self.assertEqual(checker.grade_allegiance('Empire'), 1)
        self.assertEqual(checker.grade_allegiance('Federation'), 0)

    def test_pharmaceutical_isolators_check(self):
        checker = EDRPharmaceuticalIsolatorsCheck()
        
        # Mandatory: Outbreak
        self.assertEqual(checker.grade_state('Outbreak'), 1)
        self.assertEqual(checker.grade_state('Boom'), 0)
        
        # Optional: Independent, Alliance
        # Mandatory: None set (default empty)
        # So any allegiance is fine, but Independent/Alliance gets +1
        self.assertEqual(checker.grade_allegiance('Federation'), 1)
        self.assertEqual(checker.grade_allegiance('Independent'), 2)

if __name__ == '__main__':
    unittest.main()
