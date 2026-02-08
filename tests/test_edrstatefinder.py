
import unittest
from unittest.mock import MagicMock, patch
from edrstatefinder import EDRStateFinder

class TestEDRStateFinder(unittest.TestCase):
    def setUp(self):
        self.checker = MagicMock()
        self.checker.name = "TestChecker"
        self.edr_systems = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRStateFinder("Sol", self.checker, self.edr_systems, self.callback)
        # Mock translation to avoid import issues
        self.patcher = patch('edrstatefinder._', side_effect=lambda x: x)
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

if __name__ == '__main__':
    unittest.main()
