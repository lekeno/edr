
from unittest import TestCase, main
from edr.edvehicles import EDVehicleFactory, EDUnknownVehicle, EDSidewinder, EDAnaconda, EDDiamondbackExplorer
import calendar, time
import os
import json

class TestEDVehicles(TestCase):
    def test_canonicalize_missing(self):
        result = EDVehicleFactory.canonicalize(None)
        self.assertEqual(result, u"Unknown")

        result = EDVehicleFactory.canonicalize(u"")
        self.assertEqual(result, u"")


    def test_canonicalize_valid(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../edr/data/shipnames.json')) as shipnames:
            lut = json.loads(shipnames.read())
            for ship in lut:
                result = EDVehicleFactory.canonicalize(ship)
                self.assertEqual(result, lut[ship])

    def test_canonicalize_non_official(self):
        result = EDVehicleFactory.canonicalize(u"Panther X")
        self.assertEqual(result, u"panther x")

    def test_from_internal_name(self):
        result = EDVehicleFactory.from_internal_name(u"sidewinder")
        self.assertIsInstance(result, EDSidewinder)

        result = EDVehicleFactory.from_internal_name(u"Anaconda")
        self.assertIsInstance(result, EDAnaconda)

        result = EDVehicleFactory.from_internal_name(u"doesnotexist")
        self.assertIsInstance(result, EDUnknownVehicle)

    def test_from_load_game_event(self):
        load_game_event = { "timestamp":"2018-03-15T01:47:06Z", "event":"LoadGame", "Commander":"LeKeno", "Horizons":True, "Ship":"DiamondBackXL", "Ship_Localised":"Diamondback Explorer", "ShipID":57, "ShipName":"cBRKAI/TAXI", "ShipIdent":"CBRKAI", "FuelLevel":32.000000, "FuelCapacity":32.000000, "GameMode":"Open", "Credits":480666945, "Loan":0 }
        result = EDVehicleFactory.from_load_game_event(load_game_event)
        self.assertIsInstance(result, EDDiamondbackExplorer)


if __name__ == '__main__':
    main()