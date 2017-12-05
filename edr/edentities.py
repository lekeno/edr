import os
import pickle

import json

import edtime
import lrucache
import edrconfig
import edrlog

EDRLOG = edrlog.EDRLog()

class EDVehicles(object):
    CANONICAL_SHIP_NAMES = json.loads(open(os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'data/shipnames.json')).read())

    @staticmethod
    def canonicalize(name):
        if name is None:
            return u"Unknown"

        if name.lower() in EDVehicles.CANONICAL_SHIP_NAMES:
            return EDVehicles.CANONICAL_SHIP_NAMES[name.lower()]

        return name.lower()

class EDLocation(object):
    def __init__(self):
        self.star_system = None
        self.place = None

class EDCmdr(object):
    EDR_FRIENDS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/friends.p')

    def __init__(self):
        config = edrconfig.EDRConfig()

        self.name = None
        self._ship = None
        self.location = EDLocation()
        self.game_mode = None
        self.previous_mode = None
        self.previous_wing = []
        self.from_birth = False
        self._timestamp = edtime.EDTime()
        self.wing = []

        try:
            with open(self.EDR_FRIENDS_CACHE, 'rb') as handle:
                self.friends = pickle.load(handle)
        except IOError:
            self.friends = lrucache.LRUCache(config.lru_max_size(), config.friends_max_age())

    def persist(self):
        with open(self.EDR_FRIENDS_CACHE, 'wb') as handle:
            pickle.dump(self.friends, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def in_solo_or_private(self):
        return self.game_mode in ["Solo", "Group"]

    def in_open(self):
        return self.game_mode == "Open"

    def inception(self):
        self.from_birth = True
        self.previous_mode = None
        self.previous_wing = []
        self.wing = []

    def killed(self):
        self.previous_mode = self.game_mode 
        self.previous_wing = list(self.wing)

        self.game_mode = None
        self.wing = []

    def resurrect(self):
        self.game_mode = self.previous_mode 
        self.wing = list(self.previous_wing)

        self.previous_mode = None
        self.previous_wing = []

    def has_partial_social_info(self):
        return not self.from_birth

    def leave_wing(self):
        self.wing = []

    def join_wing(self, others):
        self.wing = others

    def add_to_wing(self, other):
        self.wing = self.wing.append(other)

    def is_in_wing(self, name):
        if not self.wing:
            return False

        return name in self.wing 

    def remove_friend(self, name):
        try:
            del self.friends.evict[name]
        except KeyError:
            pass

    def update_friend(self, name, status):
        if status == "Requested":
            return False

        if status == "Lost":
            self.remove_friend(name)
            return True

        if status in ["Accepted", "Online", "Offline"]:
            self.friends.set(name, status)
            return True

        return False
    
    def is_friend(self, name):
        return not (self.friends.get(name) is None)

    def is_friend_online(self, name):
        if not self.is_friend(name):
            return None

        return self.friends.get(name) == "Online"

    def is_only_reachable_locally(self, interlocutor):
        if self.has_partial_social_info():
            return False

        return not(self.is_friend(interlocutor) or self.is_in_wing(interlocutor))

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self, new_ship):
        self._ship = EDVehicles.canonicalize(new_ship)

    @property
    def timestamp(self):
        return self._timestamp.as_journal_timestamp()

    @timestamp.setter
    def timestamp(self, ed_timestamp):
        self._timestamp.from_journal_timestamp(ed_timestamp)

    def timestamp_js_epoch(self):
        return self._timestamp.as_js_epoch()

    @property
    def star_system(self):
        return self.location.star_system

    @star_system.setter
    def star_system(self, star_system):
        self.location.star_system = star_system

    @property
    def place(self):
        if self.location.place is None:
            return "Unknown"

        return self.location.place

    @place.setter
    def place(self, place):
        self.location.place = place


    def has_partial_status(self):
        return self._ship is None or self.location.star_system is None or self.location.place is None


    def update_ship_if_obsolete(self, ship, ed_timestamp):
        if self._ship is None or self._ship != EDVehicles.canonicalize(ship):
            EDRLOG.log("Updating ship info (was missing or obsolete). {old} vs. {ship}".format(old=self._ship, ship=ship), "DEBUG")
            self._ship = EDVehicles.canonicalize(ship)
            self._timestamp.from_journal_timestamp(ed_timestamp)
            return True

        return False


    def update_star_system_if_obsolete(self, star_system, ed_timestamp):
        if self.location.star_system is None or self.location.star_system != star_system:
            EDRLOG.log(u"Updating system info (was missing or obsolete). {old} vs. {system}".format(old=self.location.star_system, system=star_system), "INFO")
            self.location.star_system = star_system
            self._timestamp.from_journal_timestamp(ed_timestamp)
            return True

        return False


    def update_place_if_obsolete(self, place, ed_timestamp):
        if self.location.place is None or self.location.place != place:
            EDRLOG.log(u"Updating place info (was missing or obsolete). {old} vs. {place}".format(old=self.location.place, place=place), "INFO")
            self.location.place = place
            self._timestamp.from_journal_timestamp(ed_timestamp)
            return True

        return False
