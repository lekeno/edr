
import unittest
from edsitu import EDLocation, EDAttitude, EDPlanetaryLocation, EDSpaceDimension

class TestEDSitu(unittest.TestCase):
    def test_planetary_location_distance(self):
        loc1 = EDPlanetaryLocation({"latitude": 0, "longitude": 0, "altitude": 0})
        loc2 = EDPlanetaryLocation({"latitude": 0, "longitude": 1, "altitude": 0})
        radius = 6371 # Earth roughly
        
        # 1 degree lat/lon at equator is approx 111km
        dist = loc1.distance(loc2, radius)
        self.assertTrue(110 < dist < 112)

    def test_bearing(self):
        loc1 = EDPlanetaryLocation({"latitude": 0, "longitude": 0})
        loc2 = EDPlanetaryLocation({"latitude": 1, "longitude": 0})
        
        # Bearing from 1 to 2 should be 0 (North)
        # Wait, the implementation is self.bearing(loc) -> bearing from self to loc?
        # Let's check implementation:
        # current_latitude = loc.latitude (arg)
        # destination_latitude = self.latitude (self)
        # So it calculates bearing FROM loc TO self.
        
        bearing = loc2.bearing(loc1) # From loc1 to loc2
        self.assertEqual(bearing, 0)
        
        bearing_reverse = loc1.bearing(loc2) # From loc2 to loc1 (South)
        self.assertEqual(bearing_reverse, 180)

    def test_location_updates(self):
        loc = EDLocation()
        entry = {"System": "Sol", "Body": "Earth", "BodyID": 1, "event": "Location"}
        loc.from_entry(entry)
        self.assertEqual(loc.star_system, "Sol")
        self.assertEqual(loc.body, "Earth")
        self.assertEqual(loc.body_id, 1)

    def test_attitude_validity(self):
        att = EDAttitude()
        self.assertFalse(att.valid())
        att.update({"latitude": 10, "longitude": 20, "heading": 180})
        self.assertTrue(att.valid())
        
        att.update({"latitude": 100, "longitude": 20, "heading": 180})
        self.assertFalse(att.valid())

if __name__ == '__main__':
    unittest.main()
