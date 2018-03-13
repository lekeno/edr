import config_tests
from unittest import TestCase, main
from edentities import EDVehicles
import calendar, time
import os
import json

class TestEDVehicles(TestCase):
    def test_canonicalize_missing(self):
        result = EDVehicles.canonicalize(None)
        self.assertEqual(result, u"Unknown")

        result = EDVehicles.canonicalize(u"")
        self.assertEqual(result, u"")


    def test_canonicalize_valid(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/shipnames.json')) as shipnames:
            lut = json.loads(shipnames.read())
            for ship in lut:
                result = EDVehicles.canonicalize(ship)
                self.assertEqual(result, lut[ship])

    def test_canonicalize_non_official(self):
        result = EDVehicles.canonicalize(u"Panther X")
        self.assertEqual(result, u"panther x")

if __name__ == '__main__':
    main()