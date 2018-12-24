import config_tests
from unittest import TestCase, main
import edvehicles
import calendar, time
import os
import json

class TestEDVehicles(TestCase):
    def test_canonicalize_missing(self):
        result = edvehicles.EDVehicleFactory.canonicalize(None)
        self.assertEqual(result, u"Unknown")

        result = edvehicles.EDVehicleFactory.canonicalize(u"")
        self.assertEqual(result, u"")


    def test_canonicalize_valid(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/shipnames.json')) as shipnames:
            lut = json.loads(shipnames.read())
            for ship in lut:
                result = edvehicles.EDVehicleFactory.canonicalize(ship)
                self.assertEqual(result, lut[ship])

    def test_canonicalize_non_official(self):
        result = edvehicles.EDVehicleFactory.canonicalize(u"Panther X")
        self.assertEqual(result, u"panther x")

    def test_from_internal_name(self):
        result = edvehicles.EDVehicleFactory.from_internal_name(u"sidewinder")
        self.assertIsInstance(result, edvehicles.EDSidewinder)

        result = edvehicles.EDVehicleFactory.from_internal_name(u"Anaconda")
        self.assertIsInstance(result, edvehicles.EDAnaconda)

        result = edvehicles.EDVehicleFactory.from_internal_name(u"doesnotexist")
        self.assertIsInstance(result, edvehicles.EDUnknownVehicle)

    def test_from_load_game_event(self):
        load_game_event = { "timestamp":"2018-03-15T01:47:06Z", "event":"LoadGame", "Commander":"LeKeno", "Horizons":True, "Ship":"DiamondBackXL", "Ship_Localised":"Diamondback Explorer", "ShipID":57, "ShipName":"cBRKAI/TAXI", "ShipIdent":"CBRKAI", "FuelLevel":32.000000, "FuelCapacity":32.000000, "GameMode":"Open", "Credits":480666945, "Loan":0 }
        result = edvehicles.EDVehicleFactory.from_load_game_event(load_game_event)
        self.assertIsInstance(result, edvehicles.EDDiamondbackExplorer)


if __name__ == '__main__':
    main()