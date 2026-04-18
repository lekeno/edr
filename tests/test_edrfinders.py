import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrservicefinder import EDRServiceFinder
from edr.controllers.edrparkingsystemfinder import EDRParkingSystemFinder
from edr.controllers.edrplanetfinder import EDRPlanetFinder
from edr.controllers.edrsettlementfinder import EDRSettlementFinder
from edr.controllers.edrstatefinder import EDRStateFinder

class TestEDRFinders(unittest.TestCase):
    def setUp(self):
        self.edr_systems = MagicMock()
        self.checker = MagicMock()
        self.callback = MagicMock()

    def test_service_finder(self):
        finder = EDRServiceFinder("Sol", self.checker, self.edr_systems, self.callback)
        
        # Setup mocks
        self.edr_systems.system.return_value = [{"name": "Sol", "requirePermit": False}]
        self.edr_systems.systems_within_radius.return_value = [{"name": "Barnard's Star", "distance": 5}]
        self.edr_systems.stations_in_system.return_value = [
            {"name": "Station A", "type": "Orbis Starport", "distanceToArrival": 100}
        ]
        self.edr_systems.system_state.return_value = ("None", 0) # Mock tuple return
        self.checker.check_system.return_value = True
        self.checker.check_station.return_value = True
        self.checker.is_service_availability_ambiguous.return_value = False
        self.edr_systems.closest_station.return_value = {"name": "Station A"}

        # Run finder
        finder.run()
        
        # Verify callback
        self.callback.assert_called()
        args = self.callback.call_args[0]
        # Args: star_system, radius, sc_distance, checker, results
        self.assertEqual(args[0], "Sol")
        self.assertIsNotNone(args[4]) # Results should not be None

    def test_parking_finder(self):
        finder = EDRParkingSystemFinder("Sol", self.edr_systems, self.callback)
        
        self.edr_systems.system.return_value = [{"name": "Sol"}]
        self.edr_systems.systems_within_radius.return_value = [{"name": "Nearby", "distance": 10, "bodyCount": 10, "requirePermit": False}]
        self.edr_systems.bodies.return_value = [{"name": "Star", "type": "Star", "distanceToArrival": 0}]
        
        finder.run()
        
        self.callback.assert_called()
        # Args: star_system, radius, rank, result
        self.assertIsNotNone(self.callback.call_args[0][3])

    def test_planet_finder(self):
        finder = EDRPlanetFinder("Sol", self.checker, self.edr_systems, self.callback)
        
        self.edr_systems.system.return_value = [{"name": "Sol"}]
        self.edr_systems.systems_within_radius.return_value = [{"name": "Nearby", "distance": 10}]
        self.edr_systems.bodies.return_value = [{"name": "Planet A", "distanceToArrival": 500}]
        self.checker.check_planet.return_value = True
        self.checker.check_system.return_value = True
        self.edr_systems.closest_planet.return_value = {"name": "Planet A"}
        
        finder.run()
        
        self.callback.assert_called()
        
    def test_settlement_finder(self):
        finder = EDRSettlementFinder("Sol", self.checker, self.edr_systems, self.callback)
        
        self.edr_systems.system.return_value = [{"name": "Sol"}]
        self.edr_systems.systems_within_radius.return_value = [{"name": "Nearby", "distance": 10}]
        self.edr_systems.stations_in_system.return_value = [{"name": "Settlement A", "distanceToArrival": 100}]
        self.checker.check_settlement.return_value = True
        self.checker.check_system.return_value = True
        self.edr_systems.closest_settlement.return_value = {"name": "Settlement A"}

        finder.run()
        
        self.callback.assert_called()

    def test_state_finder(self):
        finder = EDRStateFinder("Sol", self.checker, self.edr_systems, self.callback)
        
        self.edr_systems.system.return_value = [{"name": "Sol"}]
        self.edr_systems.systems_within_radius.return_value = [{"name": "War System", "distance": 10}]
        
        self.checker.grade_system.return_value = 5
        self.checker.grade_allegiance.return_value = 1
        self.checker.grade_state.return_value = 1
        
        self.edr_systems.system_state.return_value = ("War", 123456)
        self.edr_systems.system_allegiance.return_value = "Federation"
        
        finder.run()
        
        self.callback.assert_called()
        # callback(checker.name, star_system, radius, checker, results, grade)
        args = self.callback.call_args[0]
        self.assertIsNotNone(args[4]) # Results

if __name__ == '__main__':
    unittest.main()
