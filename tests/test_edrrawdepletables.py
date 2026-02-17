
import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os
from edr.models import edrrawdepletables
from edr.utils.edtime import EDTime

class TestEDRRawDepletables(unittest.TestCase):
    def setUp(self):
        self.depletables = edrrawdepletables.EDRRawDepletables()
        # Use in-memory DB for testing
        self.depletables.db = sqlite3.connect(":memory:")
        cursor = self.depletables.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                        hotspots(id INTEGER PRIMARY KEY, name TEXT, planet TEXT, gravity REAL, distance_to_arrival INTEGER, type TEXT, confirmed INTEGER DEFAULT 0, last_visit INTEGER DEFAULT 0)
                        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                        concentrations(id INTEGER PRIMARY KEY, hotspotid INTEGER SECONDARY KEY, resource TEXT, concentration REAL)
                        ''')
        # Insert some test data matching the class's hardcoded data structure
        cursor.execute("INSERT INTO hotspots(id, name, planet, gravity, distance_to_arrival, type, confirmed, last_visit) VALUES (1, 'TestSystem', 'TestPlanet', 0.1, 100, 'ice geysers', 1, 0)")
        cursor.execute("INSERT INTO concentrations(hotspotid, resource, concentration) VALUES (1, 'selenium', 0.05)")
        self.depletables.db.commit()

    def tearDown(self):
        if self.depletables.db:
            self.depletables.db.close()

    def test_hotspots_retrieval(self):
        # Should return the hotspot we inserted
        results = self.depletables.hotspots('selenium')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'TestSystem')
        self.assertEqual(results[0][1], 'TestPlanet')
        self.assertEqual(results[0][6], 0.05)

    def test_hotspots_none_found(self):
        results = self.depletables.hotspots('polonium') # Not in our test data
        self.assertEqual(len(results), 0)

    @patch('edr.utils.edtime.EDTime.py_epoch_now')
    def test_visit_updates_timestamp(self, mock_now):
        mock_now.return_value = 1000000000
        
        # Manually insert into LUT for testing visit
        edrrawdepletables.EDRRawDepletables.POI_LUT["test poi"] = {"system": "TestSystem", "planet": "TestPlanet"}
        
        self.depletables.visit("test poi")
        
        cursor = self.depletables.db.execute("SELECT last_visit FROM hotspots WHERE name='TestSystem' AND planet='TestPlanet'")
        last_visit = cursor.fetchone()[0]
        self.assertEqual(last_visit, 1000000000)

    def test_hotspots_depleted_filtering(self):
        # Set last visit to recently
        now = EDTime.py_epoch_now()
        self.depletables.db.execute("UPDATE hotspots SET last_visit=? WHERE id=1", (now,))
        self.depletables.db.commit()

        # Should be filtered out as depleted/recently visited
        results = self.depletables.hotspots('selenium')
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
