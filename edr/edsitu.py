import math

class EDSpaceDimension(object):
    UNKNOWN = 0
    NORMAL_SPACE = 1
    SUPER_SPACE = 2
    HYPER_SPACE = 3

class EDPlanetaryLocation(object):
    def __init__(self, poi=None):
        self.latitude = poi[u"latitude"] if poi else None
        self.longitude = poi[u"longitude"] if poi else None
        self.altitude = poi.get(u"altitude", 0.0) if poi else None
        self.title = poi.get(u"title", None) if poi else None

    def update(self, attitude):
        self.latitude = attitude.get(u"latitude", None)
        self.longitude = attitude.get(u"longitude", None)
        self.altitude = attitude.get(u"altitude", None)

    def valid(self):
        if self.latitude is None or self.longitude is None or self.altitude is None:
            return False
        if abs(self.latitude) > 90:
            return False
        if abs(self.longitude) > 180:
            return False
        return True

    def distance(self, loc, planet_radius):
        dlat = math.radians(loc.latitude - self.latitude)
        dlon = math.radians(loc.longitude - self.longitude)
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(loc.latitude)
        a = math.sin(dlat/2.0) * math.sin(dlat/2.0) + math.sin(dlon/2.0) * math.sin(dlon/2.0) * math.cos(lat1) * math.cos(lat2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
        return int(round(planet_radius * c, 0))

    def bearing(self, loc):
        current_latitude = math.radians(loc.latitude)
        destination_latitude = math.radians(self.latitude)
        delta_longitude = math.radians(self.longitude - loc.longitude)
        delta_latitude = math.log(math.tan(math.pi/4.0 + destination_latitude/2.0)/math.tan(math.pi/4.0 + current_latitude/2.0))
        bearing = math.degrees(math.atan2(delta_longitude, delta_latitude))
        if bearing < 0:
            bearing += 360
            
        return int(round(bearing, 0))

    @staticmethod
    def pitch(loc, distance):
        if loc.altitude < 1.0 or abs(distance) < 1.0:
            return None
        pitch = -math.degrees(math.atan(loc.altitude / distance))
        return int(round(pitch, 0))

class EDLocation(object):
    def __init__(self, star_system=None, place=None, security=None, space_dimension=EDSpaceDimension.UNKNOWN):
        self.star_system = star_system
        self.place = place
        self.security = security
        self.space_dimension = space_dimension
        self.population = None
        self.allegiance = None
        self.star_system_address = None

    def __repr__(self):
        return str(self.__dict__)

    def from_other(self, other_location):
        self.star_system = other_location.star_system
        self.place = other_location.place
        self.security = other_location.security
        self.space_dimension = other_location.space_dimension
        self.population = other_location.population
        self.allegiance = other_location.allegiance
        self.star_system_address = other_location.star_system_address
   
    def in_normal_space(self):
        return self.space_dimension == EDSpaceDimension.NORMAL_SPACE

    def in_supercruise(self):
        return self.space_dimension == EDSpaceDimension.SUPER_SPACE

    def in_hyper_space(self):
        return self.space_dimension == EDSpaceDimension.HYPER_SPACE

    def to_normal_space(self):
        self.space_dimension = EDSpaceDimension.NORMAL_SPACE

    def to_supercruise(self):
        self.space_dimension = EDSpaceDimension.SUPER_SPACE

    def to_hyper_space(self):
        self.space_dimension = EDSpaceDimension.HYPER_SPACE

    def is_anarchy_or_lawless(self):
        return self.security in [u"$GAlAXY_MAP_INFO_state_anarchy;", u"$GALAXY_MAP_INFO_state_lawless;"]

    def pretty_print(self):
        location = u"{system}".format(system=self.star_system)
        if self.place and self.place != self.star_system:
            if self.place.startswith(self.star_system + " "):
                # Translators: this is a continuation of the previous item (location of recently sighted outlaw) and shows a place in the system (e.g. supercruise, Cleve Hub) 
                location += u", {place}".format(place=self.place.partition(self.star_system + u" ")[2])
            else:
                location += u", {place}".format(place=self.place)
        return location

class EDAttitude(object):
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.heading = None

    def update(self, attitude):
        self.latitude = attitude.get("latitude", None)
        self.longitude = attitude.get("longitude", None)
        self.altitude = attitude.get("altitude", None)
        self.heading = attitude.get("heading", None)

    def valid(self):
        if self.latitude is None or self.longitude is None or self.altitude is None or self.heading is None:
            return False
        if abs(self.latitude) > 90:
            return False
        if abs(self.longitude) > 180:
            return False
        if abs(self.heading) > 360:
            return False
        return True
