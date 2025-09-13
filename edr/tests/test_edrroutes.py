import config_tests
from unittest import TestCase, main
from edrroutes import BidiWaypointIterator

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

if __name__ == '__main__':
    main()
