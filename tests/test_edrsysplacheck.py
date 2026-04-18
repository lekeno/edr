
import unittest
from unittest.mock import Mock, MagicMock
from edr.controllers import edrsysplacheck

class TestEDRSystemPlanetCheck(unittest.TestCase):
    def setUp(self):
        self.edrsystems = Mock()
        self.checker = edrsysplacheck.EDRSystemPlanetCheck(self.edrsystems)

    def test_check_system_distance(self):
        self.checker.max_distance = 50
        self.assertTrue(self.checker.check_system({"distance": 10}))
        self.assertFalse(self.checker.check_system({"distance": 60}))
        self.assertFalse(self.checker.check_system(None))

    def test_check_planet_basic(self):
        self.checker.max_sc_distance = 1000
        
        # Valid planet
        planet = {"distanceToArrival": 500, "surfaceTemperature": 500, "gravity": 1.0}
        self.edrsystems.canonical_atmosphere.return_value = "earthlike"
        self.edrsystems.canonical_planet_class.return_value = "earthlike"
        self.assertTrue(self.checker.check_planet(planet, "Sol"))

        # Too far
        planet_far = {"distanceToArrival": 2000}
        self.assertFalse(self.checker.check_planet(planet_far, "Sol"))

    def test_atmosphere_filtering(self):
        self.checker.atmospheres = {"ammonia"}
        self.edrsystems.canonical_atmosphere.return_value = "ammonia"
        self.assertTrue(self.checker.check_planet({"distanceToArrival": 100}, "Sol"))

        self.edrsystems.canonical_atmosphere.return_value = "earthlike"
        self.assertFalse(self.checker.check_planet({"distanceToArrival": 100}, "Sol"))

class TestEDRAmmoniaAtmosphereCheck(unittest.TestCase):
    def test_ammonia_check(self):
        edrsystems = Mock()
        checker = edrsysplacheck.EDRAmmoniaAtmosphereCheck(edrsystems)
        self.assertIn("ammonia", checker.atmospheres)

class TestEDRBiologyCheck(unittest.TestCase):
    def test_biology_check(self):
        edrsystems = Mock()
        checker = edrsysplacheck.EDRBiologyCheck(edrsystems)
        edrsystems.meets_biome_conditions.return_value = True
        
        planet = {"distanceToArrival": 100}
        self.assertTrue(checker.check_planet(planet, "Sol"))
        
        edrsystems.meets_biome_conditions.return_value = False
        self.assertFalse(checker.check_planet(planet, "Sol"))

if __name__ == '__main__':
    unittest.main()
