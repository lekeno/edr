
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrparkingsystemfinder import EDRParkingSystemFinder

class TestEDRParkingSystemFinder(unittest.TestCase):
    def setUp(self):
        self.edr_systems = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRParkingSystemFinder("Sol", self.edr_systems, self.callback)
        
        self.i18n_patch = patch('edr.controllers.edrparkingsystemfinder._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        self.log_patch = patch('edr.controllers.edrparkingsystemfinder.EDR_LOG')
        self.mock_log = self.log_patch.start()

    def tearDown(self):
        self.i18n_patch.stop()
        self.log_patch.stop()

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 25)
        self.assertEqual(self.finder.rank, 0)

    def test_nearby_checked_system_matches(self):
        # Setup: Current system is suitable
        current_system = {
            "name": "Sol",
            "distance": 0,
            "requirePermit": False,
            "bodyCount": 10
        }
        self.edr_systems.system.return_value = [current_system]
        self.edr_systems.bodies.return_value = [
            {"type": "Star", "distanceToArrival": 0},
            {"type": "Planet", "distanceToArrival": 500}
        ]
        
        result = self.finder.nearby()
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Sol")
        self.assertTrue(result["parking"]["slots"] > 0)
        self.callback.assert_not_called() # nearby doesn't call callback, run does

    def test_nearby_search(self):
        # Setup: Current system not suitable (e.g. permit required), but neighbor is
        current_system = {"name": "Sol", "distance": 0, "requirePermit": True}
        self.edr_systems.system.return_value = [current_system]
        
        neighbor = {
            "name": "Alpha Centauri",
            "distance": 4.37,
            "requirePermit": False,
            "bodyCount": 5
        }
        self.edr_systems.systems_within_radius.return_value = [neighbor]
        self.edr_systems.bodies.side_effect = lambda name: [{"type": "Star", "distanceToArrival": 0}] if name == "Alpha Centauri" else None
        
        result = self.finder.nearby()
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Alpha Centauri")

    def test_check_system_no_slots(self):
        system = {"name": "Empty", "distance": 10, "requirePermit": False, "bodyCount": 0}
        self.edr_systems.bodies.return_value = []
        
        self.assertFalse(self.finder._check_system(system))

    def test_check_system_permit_required(self):
        system = {"name": "Locked", "distance": 10, "requirePermit": True, "bodyCount": 10}
        self.assertFalse(self.finder._check_system(system))

    def test_theoretical_parking_slots(self):
        system = {"name": "Sol", "bodyCount": 5} 
        # 5 * 16 = 80
        self.assertEqual(self.finder._theoretical_parking_slots(system), 80)
        
        system = {"name": "Big", "bodyCount": 100}
        # 100 * 16 = 1600, capped at 128
        self.assertEqual(self.finder._theoretical_parking_slots(system), 128)

    def test_parking_info_stats(self):
        system = {"name": "Sol"}
        self.edr_systems.bodies.return_value = [
            {"type": "Star", "distanceToArrival": 0},
            {"type": "Planet", "distanceToArrival": 100},
            {"type": "Planet", "distanceToArrival": 200}
        ]
        
        info = self.finder._parking_info(system)
        
        # All bodies stats
        self.assertEqual(info["all"]["stats"]["min"], 0)
        self.assertEqual(info["all"]["stats"]["max"], 200)
        self.assertEqual(info["all"]["stats"]["avg"], 100) # (0+100+200)/3
        self.assertEqual(info["all"]["stats"]["count"], 3)
        
        # Stars stats
        self.assertEqual(info["stars"]["stats"]["count"], 1)
        self.assertEqual(info["stars"]["stats"]["max"], 0)

    def test_run_callback(self):
        # Test that run calls callback
        self.edr_systems.system.return_value = []
        self.edr_systems.systems_within_radius.return_value = [] # No result
        
        self.finder.run()
        self.callback.assert_called_once()
        args = self.callback.call_args[0]
        self.assertEqual(args[0], "Sol") # system
        self.assertIsNone(args[3]) # result

if __name__ == '__main__':
    unittest.main()
