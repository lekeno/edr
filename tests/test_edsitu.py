
from edr.models.edsitu import EDLocation, EDAttitude, EDPlanetaryLocation

def test_planetary_location_distance():
    loc1 = EDPlanetaryLocation({"latitude": 0, "longitude": 0, "altitude": 0})
    loc2 = EDPlanetaryLocation({"latitude": 0, "longitude": 1, "altitude": 0})
    radius = 6371 # Earth roughly
    
    # 1 degree lat/lon at equator is approx 111km
    dist = loc1.distance(loc2, radius)
    assert 110 < dist < 112

def test_bearing():
    loc1 = EDPlanetaryLocation({"latitude": 0, "longitude": 0})
    loc2 = EDPlanetaryLocation({"latitude": 1, "longitude": 0})
    
    # Bearing from 1 to 2 should be 0 (North)
    # Wait, the implementation is self.bearing(loc) -> bearing from self to loc?
    # Let's check implementation:
    # current_latitude = loc.latitude (arg)
    # destination_latitude = self.latitude (self)
    # So it calculates bearing FROM loc TO self.
    
    bearing = loc2.bearing(loc1) # From loc1 to loc2
    assert bearing == 0
    
    bearing_reverse = loc1.bearing(loc2) # From loc2 to loc1 (South)
    assert bearing_reverse == 180

def test_location_updates():
    loc = EDLocation()
    entry = {"System": "Sol", "Body": "Earth", "BodyID": 1, "event": "Location"}
    loc.from_entry(entry)
    assert loc.star_system == "Sol"
    assert loc.body == "Earth"
    assert loc.body_id == 1

def test_attitude_validity():
    att = EDAttitude()
    assert not att.valid()
    att.update({"latitude": 10, "longitude": 20, "heading": 180})
    assert att.valid()
    
    att.update({"latitude": 100, "longitude": 20, "heading": 180})
    assert not att.valid()
