
import unittest
from unittest.mock import MagicMock, patch
from edrplanetfinder import EDRPlanetFinder

class TestEDRPlanetFinder(unittest.TestCase):
    def setUp(self):
        self.checker = MagicMock()
        self.edr_systems = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRPlanetFinder("Sol", self.checker, self.edr_systems, self.callback)
        # Mock translation
        self.patcher = patch('edrplanetfinder._', side_effect=lambda x: x)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 50)

    def test_nearby_prime_found(self):
        # Setup current system as having a good planet
        self.edr_systems.system.return_value = [{"name": "Sol", "requirePermit": False}]
        self.checker.check_system.return_value = True
        self.edr_systems.are_bodies_stale.return_value = False
        
        # Planet fit
        planet = {"name": "Earth", "distanceToArrival": 100}
        self.edr_systems.bodies.return_value = [planet]
        self.checker.check_planet.return_value = True
        
        # Closest logic
        self.edr_systems.closest_planet.return_value = planet
        
        result = self.finder.nearby()
        self.assertEqual(result, planet)

    def test_nearby_alt_found(self):
        # Current system bad
        self.edr_systems.system.return_value = None
        
        # Nearby system with far planet (alt candidate)
        self.edr_systems.systems_within_radius.return_value = [{"name": "Proxima", "distance": 5}]
        self.checker.check_system.return_value = True
        
        planet = {"name": "Proxima b", "distanceToArrival": 5000} # > 1500 sc_distance
        self.edr_systems.bodies.return_value = [planet]
        self.checker.check_planet.return_value = True
        
        self.edr_systems.closest_planet.return_value = planet
        
        result = self.finder.nearby()
        self.assertEqual(result, planet) # Should return alt if no prime

    def test_closest_planet_fit(self):
        p1 = {"name": "P1", "distanceToArrival": 1000}
        p2 = {"name": "P2", "distanceToArrival": 500}
        p3 = {"name": "P3", "distanceToArrival": 2000}
        
        # All pass checker
        self.checker.check_planet.return_value = True
        
        result = self.finder.closest_planet_fit([p1, p2, p3], "System")
        self.assertEqual(result, p2)

    def test_ignore_center(self):
        self.finder.ignore_center(True)
        self.edr_systems.system.return_value = [{"name": "Sol"}]
        # Should skip current system check and go straight to search
        self.edr_systems.systems_within_radius.return_value = []
        
        result = self.finder.nearby()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
