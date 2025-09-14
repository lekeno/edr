import config_tests
from unittest import TestCase, main
from edrfleet import EDRFleet
import os
import sqlite3

class TestEDRFleet(TestCase):
    def setUp(self):
        self.fleet = EDRFleet()
        # In-memory database for testing
        self.fleet.db = sqlite3.connect(":memory:")
        cursor = self.fleet.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                    ships(id INTEGER PRIMARY KEY, type TEXT, localised TEXT, name TEXT,
                    star_system TEXT, ship_market_id INTEGER, value INTEGER, hot INTEGER, piloted INTEGER DEFAULT 0, eta INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                    transits(id INTEGER PRIMARY KEY AUTOINCREMENT, ship_id INTEGER, eta INTEGER, source_system TEXT,
                    destination_system TEXT, source_market_id INTEGER, destination_market_id INTEGER)''')
        self.fleet.db.commit()

    def test_where(self):
        self.fleet.db.execute('''INSERT INTO ships(id, type, localised, name, star_system, ship_market_id, value, hot)
                        VALUES(?,?,?,?,?,?,?,?)''', (1, "python", "python", "My Python", "Sol", 123, 1000, 0))
        self.fleet.db.commit()

        result = self.fleet.where("python")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "My Python")
        self.assertEqual(result[0][1], "python")
        self.assertEqual(result[0][2], "Sol")

    def test_update(self):
        event = {
            "StarSystem": "Sol",
            "StationName": "Earth",
            "MarketID": 123,
            "ShipsHere": [
                { "ShipID": 1, "ShipType": "python", "Name": "My Python", "Value": 1000, "Hot": False }
            ],
            "ShipsRemote": [
                { "ShipID": 2, "ShipType": "cobra", "Name": "My Cobra", "Value": 500, "Hot": False, "StarSystem": "Alpha Centauri", "ShipMarketID": 456 }
            ]
        }
        self.fleet.update(event)

        cursor = self.fleet.db.execute("SELECT * FROM ships")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], 1)
        self.assertEqual(rows[0][1], "python")
        self.assertEqual(rows[0][3], "my python")
        self.assertEqual(rows[1][0], 2)
        self.assertEqual(rows[1][1], "cobra")
        self.assertEqual(rows[1][3], "my cobra")

if __name__ == '__main__':
    main()
