
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
from edr.controllers.edrroutes import (
    BidiWaypointIterator,
    GenericRoute,
    EDRNavRoute,
    SpanshPlotterJourneyJSON,
    SpanshBodiesJourneyJSON,
    EDRRouteStatistics,
    EDRNavigator
)
from edr.utils.edtime import EDTime

class TestBidiWaypointIterator(unittest.TestCase):
    def test_iterator_basics(self):
        waypoints = [{"StarSystem": "System A"}, {"StarSystem": "System B"}, {"StarSystem": "System C"}]
        iterator = BidiWaypointIterator(waypoints)
        
        self.assertEqual(iterator.current, waypoints[0])
        self.assertEqual(next(iterator), waypoints[1])
        self.assertEqual(next(iterator), waypoints[2])
        self.assertIsNone(next(iterator))
        
        self.assertEqual(iterator.previous(), waypoints[2])
        self.assertEqual(iterator.previous(), waypoints[1])
        self.assertEqual(iterator.previous(), waypoints[0])
        self.assertIsNone(iterator.previous())

    def test_get_system_name(self):
        self.assertEqual(BidiWaypointIterator.get_system_name({"StarSystem": "A"}), "A")
        self.assertEqual(BidiWaypointIterator.get_system_name({"system": "B"}), "B")
        self.assertEqual(BidiWaypointIterator.get_system_name({"name": "C"}), "C")
        self.assertIsNone(BidiWaypointIterator.get_system_name({}))
        self.assertEqual(BidiWaypointIterator.get_system_name({"other": "D"}), "???")

    def test_includes(self):
        waypoints = [{"StarSystem": "System A"}, {"StarSystem": "System B"}]
        iterator = BidiWaypointIterator(waypoints)
        self.assertTrue(iterator.includes("System A"))
        self.assertTrue(iterator.includes("System B"))
        self.assertFalse(iterator.includes("System C"))

    def test_get(self):
        waypoints = [{"StarSystem": "System A"}, {"StarSystem": "System B"}]
        iterator = BidiWaypointIterator(waypoints)
        self.assertEqual(iterator.get("System A"), waypoints[0])
        self.assertIsNone(iterator.get("System C"))

class TestEDRNavRoute(unittest.TestCase):
    def setUp(self):
        self.config_patch = patch('edr.controllers.edrroutes.EDR_CONFIG')
        self.mock_config = self.config_patch.start()
        self.mock_config.navroute_jumps_threshold_to_show.return_value = 5
        self.mock_config.navroute_jumps_threshold_to_give_up.return_value = 50

    def tearDown(self):
        self.config_patch.stop()

    def test_empty_route(self):
        route = EDRNavRoute({})
        self.assertTrue(route.empty())
        self.assertTrue(route.trivial())

    def test_simple_route(self):
        navroute_data = {
            "Route": [
                {"StarSystem": "Sys A", "StarPos": [0,0,0]},
                {"StarSystem": "Sys B", "StarPos": [10,0,0]}
            ]
        }
        route = EDRNavRoute(navroute_data)
        self.assertFalse(route.empty())
        # 1 jump (A -> B), threshold is 5, so it is trivial
        self.assertTrue(route.trivial())
        self.assertFalse(route.too_complex())

    def test_update(self):
        navroute_data = {
            "Route": [
                {"StarSystem": "Sys A"},
                {"StarSystem": "Sys B"},
                {"StarSystem": "Sys C"}
            ]
        }
        route = EDRNavRoute(navroute_data)
        
        # Initial state is Sys A
        self.assertEqual(route.jumps.current_wp_sysname(), "Sys A")
        
        # Update with Sys A (start) moves to next?
        # Logic in update: current_system == jumps.current.
        # if match, set position = current, next(), return next is not None.
        
        updated = route.update("Sys A")
        self.assertTrue(updated)
        self.assertEqual(route.jumps.current_wp_sysname(), "Sys B")
        
        updated = route.update("Sys B")
        self.assertTrue(updated)
        self.assertEqual(route.jumps.current_wp_sysname(), "Sys C")
        
        updated = route.update("Sys C")
        self.assertFalse(updated) # No next waypoint
        self.assertIsNone(route.jumps.current)

class TestEDRNavigator(unittest.TestCase):
    def setUp(self):
        self.navigator = EDRNavigator()
        # Mock route and journey for testing updates
        self.navigator.route = MagicMock()
        self.navigator.journey = MagicMock()
        self.navigator.route_stats = MagicMock()
        self.navigator.journey_stats = MagicMock()

    def test_update_calls_route_and_journey(self):
        self.navigator.no_route = MagicMock(return_value=False)
        self.navigator.no_journey = MagicMock(return_value=False)
        self.navigator.route.update.return_value = True
        
        # Setup journey mock behavior
        self.navigator.journey.current_wp_sysname.return_value = "System A"
        self.navigator.journey.current_wp_surveyed.return_value = True
        self.navigator.journey.next.return_value = "System B"
        
        status = self.navigator.update("System A", {"x": 0, "y": 0, "z": 0})
        
        self.assertTrue(status["route_updated"])
        self.assertTrue(status["journey_updated"])
        self.navigator.route_stats.update.assert_called()
        self.navigator.journey_stats.update.assert_called()

    @patch('edr.controllers.edrroutes.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_persistence(self, mock_file, mock_pickle):
        navigator = EDRNavigator()
        navigator.journey = "Test Journey"
        
        navigator.persist()
        
        mock_file.assert_called_with(EDRNavigator.EDR_JOURNEY_CACHE, 'wb')
        mock_pickle.dump.assert_called()

class TestEDRRouteStatistics(unittest.TestCase):
    @patch('edr.controllers.edrroutes.EDTime')
    def test_statistics_update(self, mock_time):
        mock_time.py_epoch_now.return_value = 1000
        
        route = MagicMock()
        route.start = {"StarSystem": "A", "StarPos": [0,0,0]}
        route.destination = {"StarSystem": "C", "StarPos": [20,0,0]}
        route.total_jumps = 2
        route.total_waypoints = 2
        route.distance = 20
        
        stats = EDRRouteStatistics(route)
        
        # First update
        mock_time.py_epoch_now.return_value = 1100 # +100s
        stats.update("B", {"x": 10, "y": 0, "z": 0}, 1)
        
        self.assertEqual(len(stats.intervals), 1)
        self.assertEqual(stats.intervals[0], 100) # 1100 - 1000
        self.assertEqual(stats.distances[0], 10.0)
        
        # Check meaningul
        self.assertTrue(stats.meaningful())
        
        # Check calculations
        self.assertEqual(stats.s_jmp(), 100)
        self.assertEqual(stats.ly_jmp(), 10.0) # 10 ly / 1 jump
        
        # Remaining
        # Dist remaining: 10
        self.assertEqual(stats.remaining_ly(), 10.0)
        
if __name__ == '__main__':
    unittest.main()
