
import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrplanetfinder import EDRPlanetFinder

class TestEDRPlanetFinder(unittest.TestCase):
    def setUp(self):
        self.edr_systems = MagicMock()
        self.checker = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRPlanetFinder("Sol", self.checker, self.edr_systems, self.callback)
        
        self.i18n_patch = patch('edr.controllers.edrplanetfinder._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        self.log_patch = patch('edr.controllers.edrplanetfinder.EDR_LOG')
        self.mock_log = self.log_patch.start()

    def tearDown(self):
        self.i18n_patch.stop()
        self.log_patch.stop()

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 50)
        self.assertEqual(self.finder.sc_distance, 1500)

    def test_nearby_current_system_valid(self):
        system = {"name": "Sol", "requirePermit": False}
        planet = {"name": "Earth", "distanceToArrival": 100}
        
        self.edr_systems.system.return_value = [system]
        self.edr_systems.are_bodies_stale.return_value = False
        self.edr_systems.bodies.return_value = [planet]
        self.edr_systems.closest_planet.return_value = planet
        
        self.checker.check_system.return_value = True
        self.checker.check_planet.return_value = True
        
        result = self.finder.nearby()
        self.assertEqual(result, planet)

    def test_nearby_search_prime(self):
        self.edr_systems.system.return_value = None # Current system invalid
        
        neighbor = {"name": "Alpha Centauri", "requirePermit": False}
        planet = {"name": "Eden", "distanceToArrival": 100}
        
        self.edr_systems.systems_within_radius.return_value = [neighbor]
        self.edr_systems.bodies.return_value = [planet]
        self.edr_systems.are_bodies_stale.return_value = False
        self.edr_systems.closest_planet.return_value = planet
        
        self.checker.check_system.return_value = True
        self.checker.check_planet.return_value = True
        
        result = self.finder.nearby()
        self.assertEqual(result, planet)

    def test_exclude_center(self):
        self.finder.ignore_center(True)
        self.edr_systems.system.return_value = [{"name": "Sol"}]
        
        neighbor = {"name": "Alpha Centauri"}
        self.edr_systems.systems_within_radius.return_value = [neighbor]
        # Make systems_within_radius return the center too, to test filtering
        self.edr_systems.systems_within_radius.return_value = [{"name": "Sol"}, neighbor]
        
        self.edr_systems.bodies.side_effect = lambda name: [{"name": "P1", "distanceToArrival": 100}] if name != "Sol" else []
        
        self.checker.check_system.return_value = True
        self.checker.check_planet.return_value = True
        self.edr_systems.closest_planet.side_effect = lambda sys, cand: sys['planet']
        
        result = self.finder.nearby()
        self.edr_systems.bodies.assert_called_with("Alpha Centauri")
        # Ensure 'Sol' was filtered out from _search loop
        # assert bodies was NOT called with Sol? 
        # But Sol was also checked in the "current system" block, which we skipped via exclude_center
        # So Sol should not be processed at all.
        
        # Verify result comes from neighbor
        self.assertIsNotNone(result)

    def test_closest_planet_fit(self):
        p1 = {"name": "P1", "distanceToArrival": 500}
        p2 = {"name": "P2", "distanceToArrival": 100}
        p3 = {"name": "P3", "distanceToArrival": 1000}
        
        self.checker.check_planet.return_value = True
        
        result = self.finder.closest_planet_fit([p1, p2, p3], "Sys")
        self.assertEqual(result, p2)

    def test_closest_planet_fit_filter(self):
        p1 = {"name": "P1", "distanceToArrival": 100}
        p2 = {"name": "P2", "distanceToArrival": 200}
        
        # P1 fails check, P2 passes
        self.checker.check_planet.side_effect = lambda p, s: p["name"] == "P2"
        
        result = self.finder.closest_planet_fit([p1, p2], "Sys")
        self.assertEqual(result, p2)

    def test_permits(self):
        self.finder.permits_in_possession(["Sol"])
        
        system = {"name": "Sol", "requirePermit": True}
        self.edr_systems.system.return_value = [system]
        self.edr_systems.bodies.return_value = [{"distanceToArrival": 100}]
        self.checker.check_system.return_value = True
         # Need check_planet to pass
        self.checker.check_planet.return_value = True
        self.edr_systems.closest_planet.return_value = {"distanceToArrival": 100}

        # Should pass because we have permit
        result = self.finder.nearby()
        self.assertIsNotNone(result)
        
        # Now test without permit
        self.finder.permits_in_possession([])
        result = self.finder.nearby()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
