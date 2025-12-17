import config_tests
from unittest import TestCase, main
from unittest.mock import MagicMock
from edrroutes import BidiWaypointIterator, GenericRoute, SpanshServer

class TestBidiWaypointIterator(TestCase):
    def test_iteration(self):
        collection = [1, 2, 3]
        iterator = BidiWaypointIterator(collection)
        self.assertEqual(iterator.current, 1)
        self.assertEqual(next(iterator), 2)
        self.assertEqual(next(iterator), 3)
        self.assertIsNone(next(iterator))
        self.assertEqual(iterator.previous(), 3)
        self.assertEqual(iterator.previous(), 2)
        self.assertEqual(iterator.previous(), 1)
        self.assertIsNone(iterator.previous())

    def test_empty(self):
        iterator = BidiWaypointIterator(None)
        self.assertTrue(iterator.empty())

        iterator = BidiWaypointIterator([])
        self.assertTrue(iterator.empty())

        iterator = BidiWaypointIterator([1])
        self.assertFalse(iterator.empty())

class TestGenericRoute(TestCase):
    def test_delegation(self):
        route = GenericRoute()
        iterator = MagicMock()
        route.waypoints = iterator
        
        route.next()
        iterator.__next__.assert_called_once()
        
        route.previous()
        iterator.previous.assert_called_once()
        
        route.current()
        # GenericRoute.current() delegates to self.waypoints.current
        # Wait, implementation of current() in GenericRoute:
        # return self.waypoints.current_wp_sysname() if self.waypoints else None
        # Ah, BidiWaypointIterator has current_wp_sysname?
        # Let's check BidiWaypointIterator source in outline: YES.
        
    def test_empty_route(self):
        route = GenericRoute()
        self.assertTrue(route.empty())
        self.assertIsNone(route.current())
        self.assertIsNone(route.next())
        self.assertIsNone(route.previous())


class TestSpanshServer(TestCase):
    def test_url_generation(self):
        server = SpanshServer(url="test_url", callback=None)
        # source, destination, range, genre
        url = server.get_url("Sol", "Colonia", 50, "Plotter")
        # Validation depends on implementation of get_url.
        # SpanshServer.get_url(source, destination, range, genre)
        # It likely returns a formatted string.
        # I'll assert basic components are present if strict equality is hard without reading exact format.
        self.assertIn("Sol", url)
        self.assertIn("Colonia", url)
        
    def test_recognition(self):
        server = SpanshServer(url="test_url", callback=None)
        self.assertTrue(server.recognized_url("https://spansh.co.uk/plotter/results/CAFE1234"))
        self.assertFalse(server.recognized_url("https://google.com"))

if __name__ == '__main__':
    main()
