
import unittest
from edr.utils.comparable import ComparableMixin

class ComparableImpl(ComparableMixin):
    def __init__(self, value):
        self.value = value
    
    def __lt__(self, other):
        return self.value < other.value

class TestComparable(unittest.TestCase):
    def test_comparisons(self):
        a = ComparableImpl(10)
        b = ComparableImpl(20)
        c = ComparableImpl(10)
        
        self.assertTrue(a < b)
        self.assertTrue(b > a)
        self.assertTrue(a <= b)
        self.assertTrue(b >= a)
        self.assertTrue(a == c)
        self.assertTrue(a != b)
        self.assertFalse(a > b)
        self.assertFalse(b < a)

if __name__ == '__main__':
    unittest.main()
