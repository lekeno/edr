from __future__ import absolute_import
from __future__ import division
#from builtins import round

import os
import json
import math
import pickle

from edtime import EDTime
from edvehicles import EDVehicleFactory 
from edinstance import EDInstance
from edrlog import EDRLog
from edrconfig import EDRConfig #TODO replace config object with singleton
from edreconbox import EDReconBox
from edrinventory import EDRInventory
from edri18n import _, _c
import edrfleet
import edrfleetcarrier
import edrminingstats
import edrbountyhuntingstats
import utils2to3
EDRLOG = EDRLog()

class EDRCrew(object):
    def __init__(self, captain):
        self.captain = captain
        self.creation = EDTime.py_epoch_now()
        self.members = {captain: self.creation}

    def add(self, crew_member):
        if crew_member in self.members:
            return False
        self.members[crew_member] = EDTime.py_epoch_now()
        return True

    def remove(self, crew_member):
        try:
            del self.members[crew_member]
            return True
        except:
            return False

    def all_members(self):
        return self.members.keys()
    
    def disband(self):
        self.members = {}
        self.captain = None
        self.creation = None

    def is_captain(self, member):
        return member == self.captain

    def duration(self, member):
        if member not in self.members:
            return 0
        now = EDTime.py_epoch_now()
        then = self.members[member]
        return now - then
   

class EDRSquadronMember(object):
    SOMEWHAT_TRUSTED_LEVEL = {u"rank": u"wingman", u"level": 100}
    FULLY_TRUSTED_LEVEL = {u"rank": u"co-pilot", u"level": 300}

    def __init__(self, squadron_dict):
        self.name = squadron_dict.get(u"squadronName", None)
        self.inara_id = squadron_dict.get(u"squadronId", None)
        self.rank = squadron_dict.get(u"squadronRank", None)
        self.heartbeat = squadron_dict.get(u"heartbeat", None)
        self.level = squadron_dict.get(u"squadronLevel", None)
    
    def is_somewhat_trusted(self):
        return self.level >= EDRSquadronMember.SOMEWHAT_TRUSTED_LEVEL[u"level"]

    def is_fully_trusted(self):
        return self.level >= EDRSquadronMember.FULLY_TRUSTED_LEVEL[u"level"]

    def info(self):
        return {u"squadronName": self.name, u"squadronId": self.inara_id, u"squadronRank": self.rank, u"squadronLevel": self.level }

class EDRPowerplay(object):
    def __init__(self, pledged_to, time_pledged):
        self.pledged_to = pledged_to
        self.since = EDTime.py_epoch_now() - time_pledged

    def is_enemy(self, power): 
        POWERS_AFFILIATION = {
            u"a_lavigny-duval": u"Empire",
            u"arissa lavigny duval": u"Empire",
            u"aisling_duval": u"Empire",
            u"aisling duval": u"Empire",
            u"archon_delaine": None,
            u"archon delaine": None,
            u"denton_patreus": u"Empire",
            u"denton patreus": u"Empire",
            u"edmund_mahon": u"Alliance",
            u"edmund mahon": u"Alliance",
            u"felicia_winters": u"Federation",
            u"felicia winters": u"Federation",
            u"li_yong-rui": None,
            u"li yong-rui": None,
            u"pranav_antal": None,
            u"pranav antal": None,
            u"yuri_grom": None,
            u"yuri grom": None,
            u"zachary_hudson": u"Federation",
            u"zachary hudson": u"Federation",
            u"zemina_torval": u"Empire",
            u"zemina torval": u"Empire",   
        }

        power = power.lower()
        if not (self.pledged_to in POWERS_AFFILIATION and power in POWERS_AFFILIATION):
            return False
        my_affiliation = POWERS_AFFILIATION[self.pledged_to]
        their_affiliation = POWERS_AFFILIATION[power]
        return my_affiliation != their_affiliation if my_affiliation else True

    def pretty_print(self):
        POWERS_AFFILIATION = {
            u"a_lavigny-duval": u"Lavigny",
            u"aisling_duval": u"Aisling",
            u"archon_delaine": u"Archon",
            u"denton_patreus": u"Patreus",
            u"edmund_mahon": u"Mahon",
            u"felicia_winters": u"Winters",
            u"li_yong-rui": u"Li Yong-rui",
            u"pranav_antal": u"Antal",
            u"yuri_grom": u"Yuri",
            u"zachary_hudson": u"Zachary",
            u"zemina_torval": u"Zemina",
            u"independent": u"Independent",
            u"unknown": u"Unknown"  
        }

        if self.pledged_to in POWERS_AFFILIATION:
            return POWERS_AFFILIATION[self.pledged_to]
        return self.pledged_to

    def canonicalize(self):
        if self.pledged_to:
            return self.pledged_to.lower().replace(u" ", u"_")
        else:
            return u""

    def time_pledged(self):
        return EDTime.py_epoch_now() - self.since

    def is_somewhat_trusted(self):
        return False
        #TODO return true if enough time has passed (parameterize)

    def is_fully_trusted(self):
        return False
        #TODO return true if enough time has passed (parameterize)

class EDRPowerplayUnknown(EDRPowerplay):
    def __init__(self):
        super(EDRPowerplayUnknown, self).__init__(u"Unknown", EDTime.py_epoch_now())

    def is_enemy(self, power): 
        return False

    def pretty_print(self):
        return u"Unknown"

    def canonicalize(self):
        return u"unknown"

    def time_pledged(self):
        return 0

    def is_somewhat_trusted(self):
        return False

    def is_fully_trusted(self):
        return False
    

class EDFineOrBounty(object):
    def __init__(self, value):
        self.value = value
        config = EDRConfig()
        self.threshold = config.intel_bounty_threshold()
    
    def is_significant(self):
        return self.value >= self.threshold

    def __repr__(self):
        return str(self.__dict__)


    def __iadd__(self, other):
        self.value += other
        return self 

    def pretty_print(self):
        readable = u""
        if self.value is None:
            return _(u"N/A")
        if self.value >= 10000000000:
            # Translators: this is a short representation for a bounty >= 10 000 000 000 credits (b stands for billion)  
            readable = _(u"{} b").format(self.value // 1000000000)
        elif self.value >= 1000000000:
            # Translators: this is a short representation for a bounty >= 1 000 000 000 credits (b stands for billion)
            readable = _(u"{:.1f} b").format(self.value / 1000000000.0)
        elif self.value >= 10000000:
            # Translators: this is a short representation for a bounty >= 10 000 000 credits (m stands for million)
            readable = _(u"{} m").format(self.value // 1000000)
        elif self.value >= 1000000:
            # Translators: this is a short representation for a bounty >= 1 000 000 credits (m stands for million)
            readable = _(u"{:.1f} m").format(self.value / 1000000.0)
        elif self.value >= 10000:
            # Translators: this is a short representation for a bounty >= 10 000 credits (k stands for kilo, i.e. thousand)
            readable = _(u"{} k").format(self.value // 1000)
        elif self.value >= 1000:
            # Translators: this is a short representation for a bounty >= 1000 credits (k stands for kilo, i.e. thousand)
            readable = _(u"{:.1f} k").format(self.value / 1000.0)
        else:
            # Translators: this is a short representation for a bounty < 1000 credits (i.e. shows the whole bounty, unabbreviated)
            readable = _(u"{}").format(self.value)
        return readable

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

class EDPilot(object):
    def __init__(self, name, rank):
        now = EDTime.py_epoch_now()
        self._name = name
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.srv = None
        self.slf = None
        self.location = EDLocation()
        self.powerplay = EDRPowerplayUnknown()
        self.squadron = None
        self.sqid = None
        self.destroyed = False
        self.wanted = False
        self.enemy = False
        self._bounty = None
        self._fine = None
        self.targeted_vehicle = None
        self.timestamp = now
        self.rank = rank
        self.is_docked = False

    def __repr__(self):
        return str(self.__dict__)

    def json(self):
        blob = {
            u"name": self.name,
            u"timestamp": self.timestamp * 1000,
            u"wanted": self.wanted,
            u"bounty": self.bounty,
            u"power": self.powerplay.canonicalize() if self.powerplay else u'',
            u"enemy": self.enemy,
            u"ship": self.piloted_vehicle.json(),
        }
        
        if self.sqid:
            blob[u"sqid"] = self.sqid
        return blob
    
    def is_human(self):
        return False

    def killed(self):
        self._touch()
        self.destroyed = True
        self.wanted = False
        self._bounty = None
        self._fine = None
        self.targeted_vehicle = None
        if self.mothership:
            self.mothership.destroy()
        if self.srv:
            self.srv.destroy()
        if self.slf:
            self.slf.destroy()    
        self.to_normal_space()
        self.is_docked = False # probably OK (assuming a proper event after resurrection)

    def needs_large_landing_pad(self):
        return self.mothership is None or self.mothership.needs_large_landing_pad()

    @property
    def vehicle(self):
        return self.piloted_vehicle or self.mothership

    def vehicle_type(self):
        return self.piloted_vehicle.type or self.mothership.type

    @property
    def name(self):
        return self._name

    @property
    def star_system(self):
        return self.location.star_system

    @star_system.setter
    def star_system(self, star_system):
        self._touch()
        self.location.star_system = star_system

    @property
    def place(self):
        if self.location.place is None:
            # Translators: this is used when a location, comprised of a system and a place (e.g. Alpha Centauri & Hutton Orbital), has no place specified
            return _c(u"For an unknown or missing place|Unknown")
        return self.location.place

    @place.setter
    def place(self, place):
        self._touch()
        self.location.place = place
    
    def location_security(self, ed_security_state):
        self._touch()
        self.location.security = ed_security_state

    def in_bad_neighborhood(self):
        return self.location.is_anarchy_or_lawless()

    def in_supercruise(self):
        return self.location.space_dimension == EDSpaceDimension.SUPER_SPACE

    def in_hyper_space(self):
        return self.location.space_dimension == EDSpaceDimension.HYPER_SPACE

    def in_normal_space(self):
        return self.location.space_dimension == EDSpaceDimension.NORMAL_SPACE

    def in_a_fight(self):
        if not self.in_normal_space():
            return False

        if self.mothership and self.mothership.in_a_fight() and self.mothership.in_danger():
            return True
        
        if self.slf and self.slf.in_a_fight() and self.slf.in_danger():
            return True

        if self.srv and self.srv.in_a_fight() and self.srv.in_danger():
            return True
        
        return False

    def in_mothership(self):
        self._touch()
        if not self.mothership:
            self.mothership = EDVehicleFactory.unknown_vehicle() 
        self.piloted_vehicle = self.mothership

    def in_srv(self):
        self._touch()
        self.is_docked = False
        if not self.mothership or not self.mothership.supports_srv():
            self.mothership = EDVehicleFactory.unknown_vehicle() 
        if not self.srv:
            self.srv = EDVehicleFactory.default_srv()
        self.piloted_vehicle = self.srv

    def in_slf(self):
        self._touch()
        if not self.mothership or not self.mothership.supports_slf():
            self.mothership = EDVehicleFactory.unknown_vehicle() 
        if not self.slf:
            self.slf = EDVehicleFactory.unknown_slf()
        self.piloted_vehicle = self.slf

    def docked(self, is_docked = True):
        self._touch()
        self.is_docked = is_docked
        if is_docked:
            self.mothership.safe()
            if self.slf:
                self.slf.safe()
            if self.srv:
                self.srv.safe()

    def hardpoints(self, deployed):
        self._touch()
        self.piloted_vehicle.hardpoints(deployed)

    def in_danger(self, danger = True):
        self._touch()
        if not danger:
            self.piloted_vehicle.safe()
        else:
            self.piloted_vehicle.unsafe()

    def to_normal_space(self):
        self._touch()
        self.blue_tunnel = False
        self.location.space_dimension = EDSpaceDimension.NORMAL_SPACE
        self.mothership.safe()
        self.targeted_vehicle = None
        if self.slf:
            self.slf.safe()
        if self.srv:
            self.srv.safe()

    def to_super_space(self):
        self._touch()
        self.blue_tunnel = False
        self.location.space_dimension = EDSpaceDimension.SUPER_SPACE
        self.mothership.safe()
        self.targeted_vehicle = None
        self.is_docked = False
        if self.slf:
            self.slf.safe()
        if self.srv:
            self.srv.safe()

    def to_hyper_space(self):
        self._touch()
        self.blue_tunnel = True
        self.location.space_dimension = EDSpaceDimension.HYPER_SPACE
        self.planetary_destination = None # leaving the system, so no point in keep a planetary destination
        self.mothership.safe()
        self.targeted_vehicle = None
        self.is_docked = False
        if self.slf:
            self.slf.safe()
        if self.srv:
            self.srv.safe()

    def targeted(self, mothership=True, slf=False, srv=False):
        if mothership:
            self.targeted_vehicle = self.mothership
        elif slf:
            self.targeted_vehicle = self.slf
        elif srv:
            self.targeted_vehicle = self.srv
        else:
            self.targeted_vehicle = None
        self._touch()
    
    def untargeted(self):
        self.targeted_vehicle = None
        self._touch()

    def is_targeted(self):
        return self.targeted_vehicle is not None
    
    @property
    def bounty(self):
        if self._bounty:
            return self._bounty.value
        return 0

    @bounty.setter
    def bounty(self, credits):
        self._touch()
        if credits:
            self._bounty = EDFineOrBounty(credits)
        else:
            self._bounty = None

    @property
    def fine(self):
        if self._fine:
            return self._fine.value
        return 0

    @fine.setter
    def fine(self, credits):
        self._touch()
        if credits:
            self._fine = EDFineOrBounty(credits)
        else:
            self._fine = None

    @property
    def power(self):
        if self.is_independent():
            return None
        return self.powerplay.pledged_to
    
    @property
    def time_pledged(self):
        if self.is_independent():
            return None
        return self.powerplay.time_pledged()

    def pledged_to(self, power, time_pledged=0):
        self._touch()
        if power is None:
            self.powerplay = None
        else:
            self.powerplay = EDRPowerplay(power, time_pledged)
    
    def pledged_since(self):
        if self.is_independent():
            return None
        return self.powerplay.since

    def squadron_member(self, squadron_dict):
        self.squadron = EDRSquadronMember(squadron_dict)

    def lone_wolf(self):
        self.squadron = None

    def squadron_info(self):
        if self.is_lone_wolf():
            return None
        return self.squadron.info()
    
    def is_independent(self):
        return self.powerplay is None

    def is_lone_wolf(self):
        return self.squadron is None

    def has_partial_status(self):
        return self.mothership is None or self.location.star_system is None or self.location.place is None

    def update_vehicle_if_obsolete(self, vehicle, piloted=True):
        if vehicle is None:
            return False
        updated = False
        if EDVehicleFactory.is_ship_launched_fighter(vehicle):
            updated = self.__update_slf_if_obsolete(vehicle)
            if not self.mothership.supports_slf():
                self.mothership = EDVehicleFactory.unknown_vehicle()
            if piloted:
                self.piloted_vehicle = self.slf
        elif EDVehicleFactory.is_surface_vehicle(vehicle):
            updated = self.__update_srv_if_obsolete(vehicle)
            if not self.mothership.supports_srv():
                self.mothership = EDVehicleFactory.unknown_vehicle()
            if piloted:
                self.piloted_vehicle = self.srv
        else:
            updated = self.__update_mothership_if_obsolete(vehicle)
            if piloted:
                self.piloted_vehicle = self.mothership
        if updated:
            self._touch()
        return updated
    
    def __update_mothership_if_obsolete(self, vehicle):
        if self.mothership is None or self.mothership.type != vehicle.type:
            self.mothership = vehicle
            return True
        return False

    def __update_slf_if_obsolete(self, vehicle):
        if self.slf is None or self.slf.type != vehicle.type:
            self.slf = vehicle
            return True
        return False

    def __update_srv_if_obsolete(self, vehicle):
        if self.srv is None or self.srv.type != vehicle.type:
            self.srv = vehicle
            return True
        return False

    def update_star_system_if_obsolete(self, star_system):
        self._touch()
        if self.location.star_system is None or self.location.star_system != star_system:
            EDRLOG.log(u"Updating system info (was missing or obsolete). {old} vs. {system}".format(old=self.location.star_system, system=star_system), u"INFO")
            self.location.star_system = star_system
            return True
        return False

    def update_place_if_obsolete(self, place):
        self._touch()
        if self.location.place is None or self.location.place != place:
            EDRLOG.log(u"Updating place info (was missing or obsolete). {old} vs. {place}".format(old=self.location.place, place=place), u"INFO")
            self.location.place = place
            return True
        return False

    def _touch(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now

class EDPlayer(EDPilot):
    def __init__(self, name, rank=None):
        super(EDPlayer, self).__init__(name, rank)
        self.blue_tunnel = False

    def json(self):
        blob = {
            u"cmdr": self.name,
            u"timestamp": self.timestamp * 1000,
            u"wanted": self.wanted,
            u"bounty": self.bounty,
            u"power": self.powerplay.canonicalize() if self.powerplay else u'',
            u"enemy": self.enemy,
            u"ship": self.piloted_vehicle.json(),
        }
        
        if self.sqid:
            blob[u"sqid"] = self.sqid
        return blob
    
    def is_human(self):
        return True

    def to_normal_space(self):
        self.blue_tunnel = False
        super(EDPlayer, self).to_normal_space()

    def to_super_space(self):
        self.blue_tunnel = False
        super(EDPlayer, self).to_super_space()

    def to_hyper_space(self):
        self.blue_tunnel = True
        super(EDPlayer, self).to_hyper_space()

    def in_blue_tunnel(self, tunnel=True):
        if tunnel != self.blue_tunnel:
            EDRLOG.log(u"Blue Tunnel update: {old} vs. {new}".format(old=self.blue_tunnel, new=tunnel), u"DEBUG")
        self.blue_tunnel = tunnel

    def is_trusted_by_squadron(self):
        if self.is_lone_wolf():
            return False
        return self.squadron.is_somewhat_trusted()

    def squadron_trusted_rank(self):
        return EDRSquadronMember.SOMEWHAT_TRUSTED_LEVEL[u"rank"]

    def squadron_empowered_rank(self):
        return EDRSquadronMember.FULLY_TRUSTED_LEVEL[u"rank"]

    def is_empowered_by_squadron(self):
        if self.is_lone_wolf():
            return False
        return self.squadron.is_fully_trusted()
    
    def is_trusted_by_power(self):
        if self.is_independent():
            return False
        return self.powerplay.is_somewhat_trusted()

    def is_empowered_by_power(self):
        if self.is_independent():
            return True
        return self.powerplay.is_fully_trusted()

class EDWing(object):
    def __init__(self, wingmates=set()):
        self.wingmates = wingmates.copy()
        self.timestamp = None
        self.last_check_timestamp = None
        self._touched = False        

    def leave(self):
        self.wingmates = set()
        self._touch()

    def join(self, others):
        self.wingmates = set(others)
        self._touch()

    def add(self, other):
        self.wingmates.add(other)
        self._touch()

    def formed(self):
        return len(self.wingmates) > 0

    def _touch(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._touched = True

    def noteworthy_changes_json(self, instance):
        changes = []
        if not self._touched:
            for wingmate in self.wingmates:
                if instance.player(wingmate) is None:
                    continue
                timestamp, _ = instance.blip(wingmate).values()
                if self.last_check_timestamp is None or timestamp >= self.last_check_timestamp:
                    changes.append({u"cmdr": wingmate, u"instanced": True})
        elif self.last_check_timestamp is None or self.timestamp is None or self.timestamp >= self.last_check_timestamp:
            changes = [ {u"cmdr": wingmate, u"instanced": instance.player(wingmate) != None} for wingmate in self.wingmates]
        self._touched = False
        now = EDTime.py_epoch_now()
        self.last_check_timestamp = now
        return changes

class EDPlayerOne(EDPlayer):
    EDR_FLEET_CARRIER_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'fleet_carrier.v1.p')

    def __init__(self, name=None):
        super(EDPlayerOne, self).__init__(name)
        self.powerplay = None
        self.game_mode = None
        self.private_group = None
        self.previous_mode = None
        self.previous_wing = set()
        self.from_genesis = False
        self.wing = EDWing()
        self.friends = set()
        self.crew = None
        self._target = None
        self.instance = EDInstance()
        self.planetary_destination = None
        self.recon_box = EDReconBox()
        self.inventory = EDRInventory()
        self.fleet = edrfleet.EDRFleet()
        try:
            with open(self.EDR_FLEET_CARRIER_CACHE, 'rb') as handle:
                self.fleet_carrier = pickle.load(handle)
        except:
            self.fleet_carrier = edrfleetcarrier.EDRFleetCarrier()
        self.mining_stats = edrminingstats.EDRMiningStats()
        self.bounty_hunting_stats = edrbountyhuntingstats.EDRBountyHuntingStats()

    def __repr__(self):
        return str(self.__dict__)

    def persist(self):
        self.inventory.persist()
        with open(self.EDR_FLEET_CARRIER_CACHE, 'wb') as handle:
            pickle.dump(self.fleet_carrier, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def target_pilot(self):
        return self._target

    def target_vehicle(self):
        if not self._target:
            return None
        return self._target.targeted_vehicle

    def targeting(self, pilot, ship_internal_name=None):
        if pilot.is_human():
            self.instance.player_in(pilot)
        else:
            self.instance.npc_in(pilot)

        if self._target:
            self._target.untargeted()
            self._target._touch()
        self._target = pilot
        
        mothership = True
        slf = False
        srv = False
        if ship_internal_name:
            vehicle = EDVehicleFactory.from_internal_name(ship_internal_name)
            slf = EDVehicleFactory.is_ship_launched_fighter(vehicle)
            srv = EDVehicleFactory.is_surface_vehicle(vehicle)
            mothership = not(slf or srv)
        
        pilot.targeted(mothership, slf, srv)
        pilot._touch()
        self._touch()

    def untarget(self):
        if self._target:
            self._target.untargeted()
            self._target._touch()
        self._target = None
        self._touch()

    def lowish_fuel(self):
        if self.mothership.fuel_level is None or self.mothership.fuel_capacity is None:
            return True # Better safe than sorry
        return (self.mothership.fuel_level / self.mothership.fuel_capacity) <= 0.3

    def heavily_damaged(self):
        if self.mothership.hull_health is None:
            return True # Better safe than sorry
        return self.mothership.hull_health <= 50

    def json(self, fuel_info=False, with_target=False):
        result = {
            u"cmdr": self.name,
            u"timestamp": self.timestamp * 1000,
            u"wanted": self.wanted,
            u"bounty": self.bounty,
            u"starSystem": self.star_system,
            u"place": self.place,
            u"wingof": len(self.wing.wingmates),
            u"wing": self.wing.noteworthy_changes_json(self.instance),
            u"byPledge": self.powerplay.canonicalize() if self.powerplay else u'',
            u"ship": self.piloted_vehicle.json(fuel_info=fuel_info),
            u"mode": self.game_mode,
            u"group": self.private_group
        }
        if with_target:
            result[u"target"] = self.target_pilot().json() if self._target else {}

        result[u"crew"] = []
        if self.crew:
            result[u"crew"] = [ {u"cmdr": crew_member} for crew_member in self.crew.all_members()] 
            
        return result
   
    def force_new_name(self, new_name):
        self._name = new_name

    def in_solo_or_private(self):
        return self.game_mode in [u"Solo", u"Group"]

    def in_solo(self):
        return self.game_mode == u"Solo"

    def in_open(self):
        return self.game_mode == u"Open"

    def inception(self, genesis=False):
        if genesis:
            self.from_genesis = True
        self.previous_mode = None
        self.previous_wing = set()
        self.wing = EDWing()
        self.crew = None
        self.destroyed = False
        self.untarget()
        self.wanted = False
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.targeted_vehicle = None
        self.srv = None
        self.slf = None
        self.location = EDLocation()
        self._bounty = None
        self.instance.reset()
        self.to_normal_space()
        self._touch()
        self.reset_stats()

    def killed(self):
        super(EDPlayerOne, self).killed()
        self.previous_mode = self.game_mode
        self.previous_private_group = self.private_group
        self.previous_wing = self.wing.wingmates.copy()
        self.game_mode = None
        self.private_group = None
        self.wing = EDWing()
        self.crew = None
        self.untarget()
        self.instance.reset()
        self.recon_box.reset()
        self._touch()

    def resurrect(self, rebought=True):
        self.game_mode = self.previous_mode
        self.private_group = self.previous_private_group
        self.wing = EDWing(self.previous_wing)
        self.previous_mode = None
        self.previous_wing = set()
        self.destroyed = False
        self.untarget()
        self.to_normal_space()
        self.instance.reset()
        self._touch()
        if rebought:
            self.mothership.reset()
            if self.slf:
                self.slf.reset()
            if self.srv:
                self.srv.reset()
        else:
            self.mothership = EDVehicleFactory.unknown_vehicle()
            self.piloted_vehicle = self.mothership
            self.slf = None
            self.srv = None

    def is_crew_member(self):
        if not self.crew:
            return False
        return self.crew.captain != self.name

    def in_a_crew(self):
        return self.crew is not None

    def leave_wing(self):
        self.wing.leave()
        self._touch()

    def join_wing(self, others):
        self.wing.join(others)
        self.crew = None
        self._touch()

    def add_to_wing(self, other):
        self.wing.add(other)
        self._touch()

    def in_a_wing(self):
        return self.wing.formed()

    def leave_crew(self):
        self._touch()
        if not self.crew:
            return
        self.crew = None
        self.instance.reset()

    def disband_crew(self):
        self._touch()
        if not self.crew:
            return
        for member in self.crew.members:
            self.instance.player_out(member)
        self.crew.disband()

    def join_crew(self, captain):
        self.wing = EDWing()
        self.instance.reset()
        self.crew = EDRCrew(captain)
        self.crew.add(self.name)
        self.instanced_player(captain)
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.slf = None
        self.srv = None
        self._touch()

    def add_to_crew(self, member):
        self._touch()
        if not self.crew:
            self.crew = EDRCrew(self.name)
            self.wing = EDWing()
            self.instance.reset()
        self.instanced_player(member)
        return self.crew.add(member)
    
    def remove_from_crew(self, member):
        self._touch()
        if not self.crew:
            self.crew = EDRCrew(self.name)
            self.wing = EDWing()
            self.instance.reset()
        self.instance.player_out(member)
        return self.crew.remove(member)

    def crew_time_elapsed(self, member):
        if not self.crew:
            return 0
        return self.crew.duration(member)
    
    def is_captain(self, member=None):
        if not self.crew:
            return False
        if not member:
            member = self.name 
        return self.crew.is_captain(member)

    def is_friend(self, cmdr_name):
        return cmdr_name in self.friends

    def is_wingmate(self, cmdr_name):
        return cmdr_name in self.wing.wingmates

    def is_crewmate(self, cmdr_name):
        if not self.crew:
            return False
        return cmdr_name in self.crew.all_members()

    def is_enemy_with(self, power):
        if self.is_independent() or not power:
            return False
        return self.powerplay.is_enemy(power)

    def to_normal_space(self):
        if self.in_normal_space():
            return
        super(EDPlayerOne, self).to_normal_space()
        self.instance.reset()

    def to_super_space(self):
        if self.in_supercruise():
            return
        super(EDPlayerOne, self).to_super_space()
        self.instance.reset()
        self.recon_box.reset()

    def to_hyper_space(self):
        if self.in_hyper_space():
            return
        super(EDPlayerOne, self).to_hyper_space()
        self.instance.reset()
        self.recon_box.reset()

    def wing_and_crew(self):
        wing_and_crew = self.wing.wingmates.copy()
        if self.crew:
            wing_and_crew.update(self.crew.all_members() )
        return wing_and_crew

    def maybe_in_a_pvp_fight(self):
        if not self.in_a_fight():
            return False

        if self.instance.is_void_of_player():
            # Can't PvP if there is no other player.
            return False
        
        if not self.instance.any_player_beside(self.wing_and_crew()):
            return False

        return True

    def leave_vehicle(self):
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.slf = None
        self.srv = None
        self.instance.reset()
        self.recon_box.reset()
        self._touch()

    def destroy(self, cmdr):
        self._touch()
        cmdr.killed()
        self.instance.player_out(cmdr.name)
        if self.target_pilot() and self.target_pilot().name == cmdr.name:
            self.untarget()

    def interdiction(self, interdicted, success):
        self._touch()
        self.to_normal_space()
        if success and interdicted:
            interdicted.location = self.location
            if interdicted.is_human():
                self.instance.player_in(interdicted)
            else:
                self.instance.npc_in(interdicted)
        else:
            self.recon_box.reset()

    def interdicted(self, interdictor, success):
        self._touch()
        if success:
            self.to_normal_space()
            if interdictor:
                interdictor.location = self.location
                if interdictor.is_human():
                    self.instance.player_in(interdictor)
                else:
                    self.instance.npc_in(interdictor)
        else:
            if interdictor:
                if interdictor.is_human():
                    self.instance.player_out(interdictor.name)
                else:
                    self.instance.npc_out(interdictor.name)
            self.recon_box.reset()

    def is_instanced_with_player(self, cmdr_name):
        return self.instance.player(cmdr_name) != None

    def instanced_player(self, cmdr_name, rank=None, ship_internal_name=None, piloted=True):
        self._touch()
        cmdr = self.instance.player(cmdr_name)
        if not cmdr:
            cmdr = EDPlayer(cmdr_name, rank)
        cmdr.location = self.location
        if ship_internal_name:
            vehicle = EDVehicleFactory.from_internal_name(ship_internal_name)
            cmdr.update_vehicle_if_obsolete(vehicle, piloted)
        self.instance.player_in(cmdr)
        return cmdr

    def deinstanced_player(self, cmdr_name):
        self._touch()
        self.instance.player_out(cmdr_name)

    def instanced_npc(self, name, rank=None, ship_internal_name=None, piloted=True):
        self._touch()
        npc = self.instance.npc(name, rank, ship_internal_name)
        if not npc:
            npc = EDPilot(name, rank)
        npc.location = self.location
        if ship_internal_name:
            vehicle = EDVehicleFactory.from_internal_name(ship_internal_name)
            npc.update_vehicle_if_obsolete(vehicle, piloted)
        self.instance.npc_in(npc)
        return npc

    def attacked(self, target):
        self._touch()
        if target == u"Mothership":
            self.mothership.attacked()
        elif target == u"Fighter":
            if self.slf:
                self.slf.attacked()
            else:
                EDRLOG.log(u"SLF attacked but player had none", u"WARNING")
        elif target == u"You":
            self.piloted_vehicle.attacked()

    def update_fleet(self, stored_ships_entry):
        self.fleet.update(stored_ships_entry)

    def prospected(self, entry):
        self.mining_stats.prospected(entry)

    def refined(self, entry):
        self.mining_stats.refined(entry)

    def bounty_scanned(self, entry):
        self.bounty_hunting_stats.scanned(entry)

    def bounty_awarded(self, entry):
        self.bounty_hunting_stats.awarded(entry)

    def reset_stats(self):
        self.mining_stats.reset()
        self.bounty_hunting_stats.reset()
