from os import stat
import re
import json
import utils2to3
from copy import deepcopy

from edtime import EDTime
import edrconfig
from edrlog import EDR_LOG



class EDSuitLoadout(object):
    def __init__(self):
        self.id = None
        self.loadout_id = None
        self.name = None
        self.suit_mods = []
        self.modules = []

    def update_from_suitloadout(self, event):
        self.id = event.get("LoadoutID", None)
        self.name = event.get("LoadoutName", None)
        self.suit_mods = event.get("SuitMods", [])
        self.modules = event.get("Modules", [])


class EDSpaceSuit(object):
    def __init__(self):
        self.type = None
        self.id = None
        self.grade = 1
        self.loadout = EDSuitLoadout()
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._health = {u"value": 1.0, u"timestamp": now}
        self._oxygen = {u"value": 1.0, u"timestamp": now}
        self._low_oxygen = {u"value": False, u"timestamp": now}
        self._low_health = {u"value": False, u"timestamp": now}
        self.shield_up = True
        self.fight = {u"value": False, "large": False, u"timestamp": now}
        self._attacked = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        config = edrconfig.EDR_CONFIG
        self.fight_staleness_threshold = config.instance_fight_staleness_threshold()
        self.danger_staleness_threshold = config.instance_danger_staleness_threshold()

    @property
    def health(self):
        return self._health["value"]

    @health.setter
    def health(self, new_value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._health = {u"value": new_value, u"timestamp": now}

    @property
    def oxygen(self):
        return self._oxygen["value"]

    @oxygen.setter
    def oxygen(self, new_value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._oxygen = {u"value": new_value, u"timestamp": now}

    @property
    def low_health(self):
        return self._low_oxygen["value"]

    @low_health.setter
    def low_health(self, low):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._low_health = {"timestamp": now, "value": low}

    @property
    def low_oxygen(self):
        return self._low_oxygen["value"]

    @low_oxygen.setter
    def low_oxygen(self, low):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._low_oxygen = {"timestamp": now, "value": low}

    def json(self):
        result = {
            u"timestamp": int(self.timestamp * 1000),
            u"type": self.type,
            u"health": self.__js_t_v(self._health),
            u"oxygen": self.__js_t_v(self._oxygen),
            u"shieldUp": self.shield_up,
            u"lowHealth":self.__js_t_v(self._low_health),
            u"lowOxygen":self.__js_t_v(self._low_oxygen),
        }
        
        return result

    def __js_t_v(self, t_v):
        result = t_v.copy()
        result["timestamp"] = int(t_v["timestamp"]*1000)
        return result

    def __repr__(self):
        return str(self.__dict__)

    def reset(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.health = 100.0
        self.oxygen = 100.0
        self.shield_up = True
        self.fight = {u"value": False, u"large": False, u"timestamp": now}
        # self._hardpoints_deployed = {u"value": False, u"timestamp": now} ? SelectedWeapon?
        self._attacked = {u"value": False, u"timestamp": now}
        self.heat_damaged = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        
    def destroy(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.health = 0.0

    def attacked(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._attacked = {u"value": True, u"timestamp": now}

    def under_attack(self):
        if self._attacked["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._attacked["timestamp"]) and ((now - self._attacked["timestamp"]) <= self.danger_staleness_threshold)
        return False

    def safe(self):
        now = EDTime.py_epoch_now()
        self._attacked = {u"value": False, u"timestamp": now}
        self.fight = {u"value": False, "large": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
    
    def unsafe(self):
        now = EDTime.py_epoch_now()
        self._in_danger = {u"value": True, u"timestamp": now}

    def in_danger(self):
        if self._in_danger["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._in_danger["timestamp"]) and ((now - self._in_danger["timestamp"]) <= self.danger_staleness_threshold)
        return False

    def shield_state(self, is_up):
        if not is_up:
            self.shield_health = 0.0
        self.shield_up = is_up

    def skirmish(self):
        now = EDTime.py_epoch_now()
        self.fight = {u"value": True, "large": False, u"timestamp": now}

    def battle(self):
        now = EDTime.py_epoch_now()
        self.fight = {u"value": True, "large": True, u"timestamp": now}

    def in_a_fight(self):
        if self.fight["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self.fight["timestamp"]) and ((now - self.fight["timestamp"]) <= self.fight_staleness_threshold)
        return False

    def update_from_suitloadout(self, event):
        other_id = event.get("SuitID", None)
        other_type = EDSuitFactory.suit_type(event.get("SuitName", "unknown")) 

        if other_id != self.id or other_type != self.type:
            EDR_LOG.log(u"Mismatch between Suit ID ({} vs {}) and/or Type ({} vs. {}), can't update from loadout".format(self.id, other_id, self.type, other_type), "WARNING")
            return
        
        self.loadout.update_from_suitloadout(event)


    def __eq__(self, other):
        if not isinstance(other, EDSpaceSuit):
            return False
        return self.__dict__ == other.__dict__
        
    def __ne__(self, other):
        return not self.__eq__(other)

class EDUnknownSuit(EDSpaceSuit):
    def __init__(self):
        super(EDUnknownSuit, self).__init__()
        self.type = u'Unknown'

class EDFlightSuit(EDSpaceSuit):
    def __init__(self):
        super(EDFlightSuit, self).__init__()
        self.type = u'Flight'

class EDMaverickSuit(EDSpaceSuit):
    def __init__(self):
        super(EDMaverickSuit, self).__init__()
        self.type = u'Maverick'

class EDArtemisSuit(EDSpaceSuit):
    def __init__(self):
        super(EDArtemisSuit, self).__init__()
        self.type = u'Artemis'


class EDDominatorSuit(EDSpaceSuit):
    def __init__(self):
        super(EDDominatorSuit, self).__init__()
        self.type = u'Dominator'

class EDOdysseyCloset(object):
    # because why not

    def __init__(self):
        self.loadouts = {}
        self.genetic_sampler = EDGeneticSampler()
        # other tools, not interesting for now
        #   arc cutter
        #   profile analyzer
        #   energy link

    def switch_suit_loadout(self, entry):
        loadout_id = entry["LoadoutID"] if "LoadoutID" in entry else entry.get("ShipID", -1)
        suit_name = entry["SuitName"] if "SuitName" in entry else entry.get("Ship", "unknown")
        if loadout_id not in self.loadouts or self.loadouts[loadout_id].type != EDSuitFactory.suit_type(suit_name):
            self.loadouts[loadout_id] = EDSuitFactory.from_suitloadout_event(entry)
        else:
            # todo: update loadout
            pass
        return self.loadouts[loadout_id]

class EDGeneticSampler(object):
    BIOLOGY = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'biology.json')).read())
    
    def __init__(self):
        self.samples = {}
        self.genus = {}
        self.species = {}
        self.last_system_body = {}

    def reset(self):
        self.samples = {}
        self.genus = {}
        self.species = {}
        self.last_system_body = {}
    
    def process(self, scan_event, location):
        if scan_event["ScanType"] == "Analyse":
            self.reset()
            return

        if scan_event["ScanType"] == "Log":
            self.reset()
        
        if scan_event["ScanType"] in ["Log", "Sample"]:
            self.last_system_body = {
                "systemAddress": scan_event["SystemAddress"],
                "bodyNb": scan_event["Body"],
            }
            
            genus = scan_event.get("Genus", "").lower()
            self.genus = {
                "internal_name": genus,
                "name": scan_event["Genus_Localised"]
            }

            species = scan_event.get("Species", "").lower()
            self.species = {
                "internal_name": species,
                "name": scan_event["Species_Localised"]
            }
            system_body_id = EDGeneticSampler.__sys_body_id(scan_event["SystemAddress"], scan_event["Body"])
            if system_body_id in self.samples:
                self.samples[system_body_id].append(deepcopy(location))
            else:
                self.samples[system_body_id] = [ deepcopy(location) ]
        
    def is_tracking(self):
        return self.genus != {}

    def clonal_colony_range(self):
        if not self.genus:
            return None

        genus = EDGeneticSampler.BIOLOGY["genuses"].get(self.genus["internal_name"], None)
        if not genus:
            return None
        
        ccr = genus.get("ccr", None)
        
        return ccr

    def tracked_species_credits(self):
        if not self.species_tracked():
            return None
        
        species = EDGeneticSampler.BIOLOGY["species"].get(self.species["internal_name"], None)
        if not species:
            return None
        
        credits = species.get("credits", None)
        
        return credits
        
    def species_tracked(self):
        return self.species.get("name", None)

    def samples_locations(self, system_address=None, body_nb=None):
        system_address = system_address or self.last_system_body.get("systemAddress", None)
        body_nb = body_nb or self.last_system_body.get("bodyNb", None)
        system_body_id = EDGeneticSampler.__sys_body_id(system_address, body_nb)
        locs = self.samples.get(system_body_id, [])
        
        return locs

    @staticmethod
    def __sys_body_id(system_address, body_nb):
        return "S{}-B{}".format(system_address, body_nb)
    
    def has_samples_from(self, star_system_address, body_nb):
        if not self.last_system_body:
            return False
        
        if not self.last_system_body["systemAddress"]:
            return False
        
        if not self.last_system_body["bodyNb"]:
            return False
        
        return self.last_system_body["systemAddress"] == star_system_address and self.last_system_body["bodyNb"] == body_nb

class EDSuitFactory(object):
    __suit_classes = {
        "flightsuit": EDFlightSuit,
        "utilitysuit": EDMaverickSuit,
        "explorationsuit": EDArtemisSuit,
        "tacticalsuit": EDDominatorSuit,
        "unknown": EDUnknownSuit
    }

    @staticmethod
    def is_spacesuit(name):
        return EDSuitFactory.is_player_spacesuit(name) or EDSuitFactory.is_ai_spacesuit(name) 

    @staticmethod
    def is_player_spacesuit(name):
        cname = name.lower()
        player_space_suit_regexp = r"^(?:flightsuit|(?:exploration|utility|tactical)suit_class[1-5])$" # TODO confirm that those are the internal names used for players
        return re.match(player_space_suit_regexp, cname)

    @staticmethod
    def is_ai_spacesuit(name):
        cname = name.lower()
        # ai_space_suit_regexp = r"^(?:assault|lightassault|close|ranged)aisuit_class[1-5])$" # TODO use this to tighten up things?
        ai_space_suit_lax_regexp = r"^[a-z0-9_]*aisuit_class[1-5]$"
        return re.match(ai_space_suit_lax_regexp, cname)

    @staticmethod
    def canonicalize_name(name):
        if name is None:
            return u"unknown" # Note: this shouldn't be translated
        cname = name.lower()
        player_space_suit_regexp = r"^(flightsuit|explorationsuit|utilitysuit|tacticalsuit)_class[1-5]$" # TODO confirm that those are the internal names used for players
        m = re.match(player_space_suit_regexp, cname)
        if m:
            cname = m.group(1)
        return cname

    @staticmethod
    def suit_type(internal_name):
        cname = EDSuitFactory.canonicalize_name(internal_name)
        LUT = {
            "flightsuit": "Flight",
            "utilitysuit": "Maverick",
            "explorationsuit": "Artemis",
            "tacticalsuit": "Dominator",
            "unknown": "Unknown"
        }
        return LUT.get(cname, "Unknown")

    @staticmethod
    def grade(name):
        cname = name.lower()
        player_space_suit_regexp = r"^[a-z0-9_]suit_class([1-5])$" # TODO confirm that those are the internal names used for players
        m = re.match(player_space_suit_regexp, cname)
        if m:
            return m.group(1)
        return 1

    # TODO @staticmethod
    # def from_edmc_state(state):

    @staticmethod
    def from_internal_name(internal_name):
        suit_name = EDSuitFactory.canonicalize_name(internal_name)
        grade = EDSuitFactory.grade(internal_name)
        suit = EDSuitFactory.__suit_classes.get(suit_name, EDUnknownSuit)()
        suit.grade = grade
        return suit
    
    @staticmethod
    def from_load_game_event(event):
        suit = EDSuitFactory.from_internal_name(event.get("Ship", 'unknown'))
        suit.id = event.get('ShipID', None)
        suit.identity = event.get('ShipIdent', None) # Always empty?
        suit.name = event.get('ShipName', None) # Always empty
        # TODO the event also has Fuel and Fuelcapacity but it's unclear if this is a bug or reusing fields for Energy levels?
        return suit

    @staticmethod
    def from_suitloadout_event(event):
        suit = EDSuitFactory.from_internal_name(event.get("SuitName", 'unknown'))
        suit.id = event.get('SuitID', None)
        suit.loadout.update_from_suitloadout(event)
        return suit

    #@staticmethod
    #def from_stored_ship(ship_info): # TODO suitloadout swapping?
        
    @staticmethod
    def unknown_suit():
        return EDUnknownSuit()