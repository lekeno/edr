from os import stat
import re

from edtime import EDTime
import edrconfig

class EDSpaceSuit(object):    
    def __init__(self):
        self.type = None
        self.id = None
        self._grade = 1
        # TODO mods slot, weapons/...
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
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, new_value):
        self._grade = new_value
        # TODO add relevant number of mods slots
    
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
        other_type = EDSuitFactory.canonicalize(event.get("SuitName", "unknown")) 

        if other_id != self.id or other_type != self.type:
            EDRLOG.log(u"Mismatch between Suit ID ({} vs {}) and/or Type ({} vs. {}), can't update from loadout".format(self.id, other_id, self.type, other_type), "WARNING")
            return
        # TODO "SuitMods":[  ], "LoadoutID":4293000003, "LoadoutName":"Maverick G3", "Modules":[ { "SlotName":"PrimaryWeapon1", "SuitModuleID":1700370764353759, "ModuleName":"wpn_m_assaultrifle_kinetic_fauto", "ModuleName_Localised":"Karma AR-50", "Class":3, "WeaponMods":[ "weapon_reloadspeed" ] }, { "SlotName":"SecondaryWeapon", "SuitModuleID":1700369275710090, "ModuleName":"wpn_s_pistol_laser_sauto", "ModuleName_Localised":"TK Zenith", "Class":3, "WeaponMods":[ "weapon_backpackreloading" ] } ] }


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


class EDSuitFactory(object):
    __suit_classes = {
        "flightsuit": EDFlightSuit,
        "utilitysuit": EDMaverickSuit,
        "explorersuit": EDArtemisSuit,
        "assaultsuit": EDDominatorSuit,
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
    def canonicalize(name):
        if name is None:
            return u"unknown" # Note: this shouldn't be translated
        cname = name.lower()
        player_space_suit_regexp = r"^(flightsuit|(explorationsuit|utilitysuit|tacticalsuit)_class[1-5])$" # TODO confirm that those are the internal names used for players
        m = re.match(player_space_suit_regexp, cname)
        if m:
            cname = m.group(1)
        return cname

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
        suit_name = EDSuitFactory.canonicalize(internal_name)
        grade = EDSuitFactory.grade(internal_name)
        suit = EDSuitFactory.__suit_classes.get(suit_name, EDUnknownSuit)()
        suit.grade = grade
    
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
        # TODO suit modules "SuitMods":[  ],
        # TODO loadoutID and name
        # TODO Modules "Modules":[ { "SlotName":"PrimaryWeapon1", "SuitModuleID":1700370764353759, "ModuleName":"wpn_m_assaultrifle_kinetic_fauto", "ModuleName_Localised":"Karma AR-50", "Class":3, "WeaponMods":[ "weapon_reloadspeed" ] }, { "SlotName":"SecondaryWeapon", "SuitModuleID":1700369275710090, "ModuleName":"wpn_s_pistol_laser_sauto", "ModuleName_Localised":"TK Zenith", "Class":3, "WeaponMods":[ "weapon_backpackreloading" ] } ] }

        return suit

    #@staticmethod
    #def from_stored_ship(ship_info): # TODO suitloadout swapping?
        
    @staticmethod
    def unknown_suit():
        return EDUnknownSuit()