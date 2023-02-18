import math
import re

try:
    import edmc_data
except ImportError:
    import plug as edmc_data


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
        self.heading = poi.get(u"heading", None) if poi else None
        self.title = poi.get(u"title", None) if poi else None

    def update(self, attitude_bag):
        self.latitude = attitude_bag.get(u"latitude", None)
        self.longitude = attitude_bag.get(u"longitude", None)
        self.altitude = attitude_bag.get(u"altitude", None)
        self.heading = attitude_bag.get(u"heading", None)

    def update_from_obj(self, attitude):
        self.latitude = attitude.latitude
        self.longitude = attitude.longitude
        self.altitude = attitude.altitude
        self.heading = attitude.heading

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
        alt1 = self.altitude
        alt2 = loc.altitude
        dist = planet_radius * c
        if (alt1 is not None and alt2 is not None) and dist <= 10.0:
            dist = math.sqrt((planet_radius * c)**2 + (alt1 - alt2)**2)
        # TODO check if other callers actually needed the rounding and int()
        return dist

    def bearing(self, loc):
        current_latitude = math.radians(loc.latitude)
        destination_latitude = math.radians(self.latitude)
        delta_longitude = math.radians(self.longitude - loc.longitude)
        delta_latitude = math.log(math.tan(math.pi/4.0 + destination_latitude/2.0)/math.tan(math.pi/4.0 + current_latitude/2.0))
        bearing = math.degrees(math.atan2(delta_longitude, delta_latitude)) % 360
        if bearing < 0:
            bearing += 360
            
        return int(round(bearing, 0))

    @staticmethod
    def pitch(loc, distance):
        if loc.altitude is None or loc.altitude < 1.0 or abs(distance) < 1.0:
            return None
        pitch = -math.degrees(math.atan(loc.altitude / distance))
        return int(round(pitch, 0))

class EDOnFootLocation(object):
    def __init__(self):
        self.on_foot = False
        self.in_hangar = False
        self.in_station = False
        self.on_planet = False
        self.in_social_space = False
        self.in_social_space = False
        self.outside = False
        
    def update(self, flags2):
        self.on_foot = flags2 & edmc_data.Flags2OnFoot
        self.in_station = flags2 & edmc_data.Flags2OnFootInStation
        self.on_planet = flags2 & edmc_data.Flags2OnFootOnPlanet
        self.in_hangar = flags2 & edmc_data.Flags2OnFootInHangar
        self.in_social_space = flags2 & edmc_data.Flags2OnFootSocialSpace
        self.outside = flags2 & edmc_data.Flags2OnFootExterior


class EDLocation(object):
    def __init__(self, star_system=None, body=None, place=None, security=None, space_dimension=EDSpaceDimension.UNKNOWN):
        self.star_system = star_system
        self.place = place
        self.body = body
        self.security = security
        self.space_dimension = space_dimension
        self.on_foot_location = EDOnFootLocation()
        self.population = None
        self.allegiance = None
        self.star_system_address = None
        self.body_id = None

    def __repr__(self):
        return str(self.__dict__)

    def from_entry(self, entry):
        # TODO consistency is lacking (e.g. if body changes, then bodyID should too, etc.)
        self.star_system_address = entry.get("SystemAddress", self.star_system_address)
        if "StarSystem" in entry:
            self.star_system = entry["StarSystem"]
        elif "System" in entry:
            self.star_system = entry["System"]
        
        if entry["event"] == "ScanOrganic":
            self.body_id = entry.get("Body", self.body_id)
        elif entry["event"] in ["SAAScanComplete", "ApproachSettlement"]:
            self.body = entry.get("BodyName", self.body)
            self.body_id = entry.get("BodyID", self.body_id)
        else:
            self.body = entry.get("Body", self.body)
            self.body_id = entry.get("BodyID", self.body_id)
        
        if "StationName" in entry:
            self.place = entry["StationName"]
        elif "NearestDestination" in entry:
            self.place = entry["NearestDestination"]

    def from_other(self, other_location):
        self.star_system = other_location.star_system
        self.body = other_location.body
        self.body_id = other_location.body_id
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
        if self.star_system is None:
            return u"Unknown"
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
        if self.latitude is None or self.longitude is None or self.heading is None:
            return False
        if abs(self.latitude) > 90:
            return False
        if abs(self.longitude) > 180:
            return False
        if abs(self.heading) > 360:
            return False
        return True

    def __repr__(self):
        return str(self.__dict__)

class EDDestination(object):
    def __init__(self):
        self.system = None
        self.body = None
        self.name = None

    def update(self, destination):
        updated = False
        if self.system != destination.get("System", self.system):
            self.system = destination["System"]
            updated = True

        if self.body != destination.get("Body", self.body):
            self.body = destination["Body"]
            updated = True

        if self.name != destination.get("Name", self.name):
            self.name = destination["Name"]
            updated = True

        return updated

    def is_valid(self):
        if self.system is None:
            return False

        if self.body is None:
            return False

        if self.name is None:
            return False
        return True

    def is_system(self):
        return self.system != None and self.body == 0

    def is_fleet_carrier(self):
        if not self.is_valid():
            return False
            
        if self.body == 0: # TODO do FC near the sun have body set to 1?
            return False
        
        fc_regexp = r"^(?:.+ )?([A-Z0-9]{3}-[A-Z0-9]{3})$"
        return bool(re.match(fc_regexp, self.name))