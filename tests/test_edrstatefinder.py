
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrstatefinder import EDRStateFinder

class TestEDRStateFinder(unittest.TestCase):
    def setUp(self):
        self.checker = MagicMock()
        self.checker.name = "TestChecker"
        self.edr_systems = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRStateFinder("Sol", self.checker, self.edr_systems, self.callback)
        # Mock translation to avoid import issues
        self.patcher = patch('edr.controllers.edrstatefinder._', side_effect=lambda x: x)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 50)

    def test_nearby_no_system(self):
        self.edr_systems.system.return_value = None
        result = self.finder.nearby()
        self.assertEqual(result, (None, None))

    def test_nearby_current_system_good(self):
        # Setup current system as good candidate
        system_data = {'name': 'Sol', 'requirePermit': True}
        self.edr_systems.system.return_value = [system_data]
        self.finder.permits_in_possession(['Sol'])
        
        self.checker.grade_system.return_value = 1
        self.edr_systems.system_state.return_value = ('Boom', 123456)
        self.edr_systems.system_allegiance.return_value = 'Federation'
        self.checker.grade_allegiance.return_value = 2
        self.checker.grade_state.return_value = 2
        
        # Total grade = 1 + 2 + 2 = 5 -> Should return immediately
        result, grade = self.finder.nearby()
        self.assertEqual(result['name'], 'Sol')
        self.assertEqual(grade, 5)

    def test_nearby_search_radius(self):
        # Current system bad
        self.edr_systems.system.return_value = [{'name': 'Sol', 'requirePermit': False}]
        self.checker.grade_system.side_effect = [0, 1] # First call Sol (bad), second call Neighbor
        
        # Neighbor system
        neighbor = {'name': 'Alpha Centauri', 'requirePermit': False}
        self.edr_systems.systems_within_radius.return_value = [neighbor]
        
        # Mock stale check
        self.edr_systems.are_factions_stale.return_value = False
        
        # Neighbor details
        self.edr_systems.system_state.return_value = ('War', 234567)
        self.edr_systems.system_allegiance.return_value = 'Empire'
        self.checker.grade_allegiance.return_value = 1
        self.checker.grade_state.return_value = 1
        
        # Grade = 1 (base) + 1 + 1 = 3
        
        result, grade = self.finder.nearby()
        self.assertEqual(result['name'], 'Alpha Centauri')
        self.assertEqual(grade, 3)

    def test_run_callback(self):
        # Mock nearby to return something
        with patch.object(self.finder, 'nearby', return_value=('System', 10)):
            self.finder.run()
            self.callback.assert_called_with("TestChecker", "Sol", 50, self.checker, 'System', 10)

    def test_max_trials_reached(self):
        # Setup many systems that are all stale
        systems = [{'name': f'Sys{i}', 'requirePermit': False} for i in range(30)]
        self.edr_systems.systems_within_radius.return_value = systems
        self.checker.grade_system.return_value = 1
        
        # Always stale
        self.edr_systems.are_factions_stale.return_value = True
        
        # Mock system_state to avoid ValueError during unpacking
        self.edr_systems.system_state.return_value = ('None', 0)
        self.edr_systems.system_allegiance.return_value = 'None'
        self.checker.grade_allegiance.return_value = 0
        self.checker.grade_state.return_value = 0

        # run search
        result, grade = self.finder.nearby()
        
        # Should return None because it exhausted max_trials (25) without finding a fresh one
        # Actually, the code breaks the loop but doesn't necessarily return None if it had a previous best?
        # In this test setup, best_system_so_far starts as None.
        # Inside loop:
        # It checks stale. If stale, trials++, if trials > max_trials break.
        # If it breaks, it returns best_system_so_far (which is None).
        
        self.assertIsNone(result)
        self.assertEqual(grade, 0)
        # Verify we checked at least max_trials + 1 times (since check happens before increment?)
        # trials starts at 0. 
        # Check 1: stale. trials=1.
        # ...
        # Check 26: stale. trials=26. break.
        # So are_factions_stale called 26 times?
        self.assertGreater(self.edr_systems.are_factions_stale.call_count, 20)

if __name__ == '__main__':
    unittest.main()
