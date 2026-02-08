
import unittest
from unittest.mock import MagicMock, patch
from edrparkingsystemfinder import EDRParkingSystemFinder

class TestEDRParkingSystemFinder(unittest.TestCase):
    def setUp(self):
        self.edr_systems = MagicMock()
        self.callback = MagicMock()
        self.finder = EDRParkingSystemFinder("Sol", self.edr_systems, self.callback)

    def test_init(self):
        self.assertEqual(self.finder.star_system, "Sol")
        self.assertEqual(self.finder.radius, 25)

    def test_theoretical_parking_slots(self):
        # Known body count
        system = {"bodyCount": 5}
        slots = self.finder._theoretical_parking_slots(system)
        self.assertEqual(slots, 5 * 16) # 80

        # Limited to 128
        system = {"bodyCount": 10}
        slots = self.finder._theoretical_parking_slots(system)
        self.assertEqual(slots, 128)

        # Body count missing, fetched from EDR systems
        system = {"name": "TestSystem"}
        self.edr_systems.bodies.return_value = [{}, {}, {}] # 3 bodies
        slots = self.finder._theoretical_parking_slots(system)
        self.assertEqual(slots, 3 * 16)

    def test_parking_info(self):
        system = {"name": "TestSystem"}
        bodies = [
            {"distanceToArrival": 100, "type": "Planet"},
            {"distanceToArrival": 500, "type": "Star"},
            {"distanceToArrival": 1000, "type": "Planet"}
        ]
        self.edr_systems.bodies.return_value = bodies
        
        info = self.finder._parking_info(system)
        
        self.assertEqual(info["all"]["stats"]["min"], 100)
        self.assertEqual(info["all"]["stats"]["max"], 1000)
        self.assertEqual(info["all"]["stats"]["avg"], (100+500+1000)/3)
        self.assertEqual(info["all"]["stats"]["median"], 500)
        
        self.assertEqual(info["stars"]["stats"]["count"], 1)
        self.assertEqual(info["stars"]["stats"]["max"], 500)

    def test_check_system_good(self):
        system = {"name": "GoodSystem", "bodyCount": 5, "distance": 15}
        self.edr_systems.bodies.return_value = [{"distanceToArrival": 10}]
        
        result = self.finder._check_system(system)
        self.assertTrue(result)
        self.assertIn("parking", system)
        self.assertEqual(system["parking"]["slots"], 80)

    def test_check_system_permit_locked(self):
        system = {"name": "LockedSystem", "bodyCount": 5, "requirePermit": True}
        result = self.finder._check_system(system)
        self.assertFalse(result)

    def test_nearby(self):
        # Setup: Current system is bad (permit), nearby system is good
        self.edr_systems.system.return_value = [{"name": "Sol", "requirePermit": True}]
        
        neighbor = {"name": "Neighbor", "distance": 10, "bodyCount": 2, "requirePermit": False}
        self.edr_systems.systems_within_radius.return_value = [neighbor]
        self.edr_systems.bodies.return_value = [{"distanceToArrival": 100}]

        result = self.finder.nearby()
        self.assertEqual(result["name"], "Neighbor")

if __name__ == '__main__':
    unittest.main()
