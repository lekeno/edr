
import unittest
import math
from unittest.mock import MagicMock, patch
from edr.models.edsitu import EDPlanetaryLocation, EDLocation, EDAttitude, EDDestination, EDOnFootLocation, EDSpaceDimension

class TestEDPlanetaryLocation(unittest.TestCase):
    def test_init_update(self):
        poi = {"latitude": 10.0, "longitude": 20.0, "altitude": 100.0, "heading": 90}
        loc = EDPlanetaryLocation(poi)
        self.assertEqual(loc.latitude, 10.0)
        self.assertEqual(loc.heading, 90)
        
        attitude = {"latitude": 15.0, "longitude": 25.0, "altitude": 200.0, "heading": 180}
        loc.update(attitude)
        self.assertEqual(loc.latitude, 15.0)
        self.assertEqual(loc.altitude, 200.0)

    def test_valid(self):
        loc = EDPlanetaryLocation()
        self.assertFalse(loc.valid())
        
        loc.latitude = 100.0 # invalid
        loc.longitude = 0.0
        loc.altitude = 0.0
        self.assertFalse(loc.valid())
        
        loc.latitude = 90.0
        loc.longitude = 180.0
        self.assertTrue(loc.valid())

    def test_distance(self):
        # Point A: 0, 0
        # Point B: 0, 1 (1 degree longitude diff at equator)
        # Radius 1000 km
        # Distance should be approx 2 * pi * R * (1/360) 
        # = 2 * 3.14159 * 1000 / 360 = 17.45 km
        
        loc1 = EDPlanetaryLocation({"latitude": 0, "longitude": 0, "altitude": 0})
        loc2 = EDPlanetaryLocation({"latitude": 0, "longitude": 1, "altitude": 0})
        
        dist = loc1.distance(loc2, 1000)
        self.assertAlmostEqual(dist, 17.45, delta=0.1)

    def test_bearing(self):
        # A (0,0) to B (0,1) -> East -> 90 degrees?
        # Bearing calc: 
        # loc1.bearing(loc2) is bearing FROM loc2 TO loc1? or FROM loc1 TO loc2?
        # definition:
        # current_latitude = math.radians(loc.latitude) ... loc is the argument
        # destination_latitude = math.radians(self.latitude) ... self is "destination"??
        # Usually bearing(target) means bearing TO target. 
        # But here logic uses 'self' as destination and 'loc' as current?
        # Let's verify usage.
        
        loc_from = EDPlanetaryLocation({"latitude": 0, "longitude": 0, "altitude": 0})
        loc_to = EDPlanetaryLocation({"latitude": 0, "longitude": 1, "altitude": 0})
        
        # If I want bearing FROM loc_from TO loc_to:
        # If the method is `dist_to.bearing(dist_from)`, then:
        
        b = loc_to.bearing(loc_from)
        # From (0,0) to (0,1) is East -> 90.
        self.assertEqual(b, 90)

    def test_pitch(self):
        # Altitude 100, Dist 100 -> 45 degrees down (-45)
        loc = EDPlanetaryLocation({"latitude": 0, "longitude": 0, "altitude": 100})
        pitch = EDPlanetaryLocation.pitch(loc, 100)
        self.assertEqual(pitch, -45)

class TestEDLocation(unittest.TestCase):
    def test_init(self):
        loc = EDLocation(star_system="Sol", body="Earth")
        self.assertEqual(loc.star_system, "Sol")
        self.assertEqual(loc.body, "Earth")
        self.assertEqual(loc.space_dimension, EDSpaceDimension.UNKNOWN)

    def test_from_entry(self):
        loc = EDLocation()
        entry = {
            "event": "Location",
            "StarSystem": "Sol",
            "SystemAddress": 12345,
            "Body": "Earth",
            "BodyID": 1,
            "StationName": "Abraham Lincoln"
        }
        loc.from_entry(entry)
        self.assertEqual(loc.star_system, "Sol")
        self.assertEqual(loc.place, "Abraham Lincoln")
        self.assertEqual(loc.body, "Earth")

    def test_space_dimension(self):
        loc = EDLocation()
        loc.to_supercruise()
        self.assertTrue(loc.in_supercruise())
        self.assertFalse(loc.in_normal_space())
        
        loc.to_normal_space()
        self.assertTrue(loc.in_normal_space())

    def test_pretty_print(self):
        loc = EDLocation(star_system="Sol", place="Abraham Lincoln")
        self.assertEqual(loc.pretty_print(), "Sol, Abraham Lincoln")
        
        loc = EDLocation(star_system="Sol", place="Sol A 1")
        # starts with system name
        self.assertEqual(loc.pretty_print(), "Sol, A 1")

class TestEDDestination(unittest.TestCase):
    def test_update(self):
        dest = EDDestination()
        dest.system = "Sol"
        
        new_dest = {"System": "Sol", "Body": "Earth", "Name": "Something"}
        updated = dest.update(new_dest)
        self.assertTrue(updated)
        self.assertEqual(dest.body, "Earth")
        
        updated = dest.update(new_dest) # No change
        self.assertFalse(updated)

    def test_is_fleet_carrier(self):
        dest = EDDestination()
        dest.system = "Sol"
        dest.body = 1
        dest.name = "Q7W-123"
        self.assertTrue(dest.is_fleet_carrier())
        
        dest.name = "My Carrier Q7W-123"
        self.assertTrue(dest.is_fleet_carrier())
        
        dest.name = "Earth"
        self.assertFalse(dest.is_fleet_carrier())

class TestEDOnFootLocation(unittest.TestCase):
    def test_update(self):
        # We need to mock edmc_data flags
        # Since we can't easily import the original module if it's missing or guarded
        # we will patch the module attribute lookups in the class method potentially?
        # But the class imports edmc_data at module level.
        # We can simulate the flags.
        
        with patch('edr.models.edsitu.edmc_data') as mock_edmc:
            mock_edmc.Flags2OnFoot = 1
            mock_edmc.Flags2OnFootInStation = 2
            mock_edmc.Flags2OnFootOnPlanet = 4
            mock_edmc.Flags2OnFootInHangar = 8
            mock_edmc.Flags2OnFootSocialSpace = 16
            mock_edmc.Flags2OnFootExterior = 32
            
            loc = EDOnFootLocation()
            # Flags = 3 (1 | 2) -> OnFoot + InStation. OnPlanet(4) is absent.
            loc.update(3)
            
            self.assertTrue(loc.on_foot)
            self.assertTrue(loc.in_station)
            self.assertFalse(loc.on_planet)

if __name__ == '__main__':
    unittest.main()
