import re
import os
import json
from collections import deque

from edtime import EDTime
import edrconfig
import edrhitppoints
import edmodule
import edmodulesinforeader
import edcargoreader
import edrlog
import edcargo
import utils2to3
EDRLOG = edrlog.EDRLog()

class EDSpaceSuitModule(object):
    self.id = None
    self.name = None

class EDSpaceSuitLoadout(object):
    def __init__(self):
        self.name = None
        self.id = None
        self.slots = {}

class EDSpaceSuit(object):
    def __init__(self):
        self.type = None
        self.id = None
        self.loadout = EDSpaceSuitLoadout()
        # TODO verify if needed/available
        self.rebuy = None
        self._value = None
        self.hot = False
        now = EDTime.py_epoch_now()
        now_ms = EDTime.ms_epoch_now()
        config = edrconfig.EDR_CONFIG
        self._hull_health = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self._shield_health = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.shield_up = True
        self.timestamp = now
        self.fight = {u"value": False, "large": False, u"timestamp": now}
        self._hardpoints_deployed = {u"value": False, u"timestamp": now}
        self._attacked = {u"value": False, u"timestamp": now}
        self.heat_damaged = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        self._low_fuel = {u"value": False, u"timestamp": now}
        self.fight_staleness_threshold = config.instance_fight_staleness_threshold()
        self.danger_staleness_threshold = config.instance_danger_staleness_threshold()
        self.seats = 1
        self.fuel_capacity = None
        self.fuel_level = None
        self.attitude = EDVehicleAttitude()
        self.module_info_timestamp = None
        self.slots_timestamp = None
        self.slots = {}
        self.modules = None
        self.power_capacity = None
        self.cargo_capacity = 0
        self.cargo = edcargo.EDCargo()
        self.whole_loadout = False
        
    @property
    def hull_health(self):
        if self._hull_health.empty():
            return None
        return self._hull_health.last_value()

    def hull_health_stats(self):
        return self._hull_health

    @hull_health.setter
    def hull_health(self, new_value):
        self._hull_health.update(new_value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.rebuy = .1 * new_value

    @property
    def shield_health(self):
        if self._shield_health.empty():
            return None
        return self._shield_health.last_value()

    def shield_health_stats(self):
        return self._shield_health
    
    @shield_health.setter
    def shield_health(self, new_value):
        if new_value == 0:
            self.shield_up = False
        elif not self.shield_up and new_value >= 90:
            self.shield_up = True # highly speculative...
        self._shield_health.update(new_value)

    @property
    def low_fuel(self):
        return self._low_fuel["value"]

    @low_fuel.setter
    def low_fuel(self, low):
        before = self._low_fuel["value"]
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._low_fuel = {"timestamp": now, "value": low}
        if before != low and self.fuel_capacity:
            if low:
                self.fuel_level = min(self.fuel_level, self.fuel_capacity * .25)
            else:
                self.fuel_level = max(self.fuel_level, self.fuel_capacity * .25)

    def json(self, fuel_info=False):
        shield_default = 100 if self.whole_loadout and self.has_shield_generator() else -1
        result = {
            u"timestamp": int(self.timestamp * 1000),
            u"type": self.type,
            u"hullHealth": {"timestamp": int(self.timestamp * 1000), "value": 100} if self._hull_health.empty() else self._hull_health.last(),
            u"shieldHealth": {"timestamp": int(self.timestamp * 1000), "value": shield_default} if self._shield_health.empty() else self._shield_health.last(),
            u"shieldUp": self.shield_up and shield_default != -1,
            u"keySubsystems": self.__key_subsystems()
        }
        if fuel_info:
            result[u"fuelLevel"] = self.fuel_level
            result[u"fuelCapacity"] = self.fuel_capacity
            result[u"lowFuel"] = self.low_fuel

        return result

    # TODO adjust all timestamp to ms?
    def __js_t_v(self, t_v):
        result = t_v.copy()
        result["timestamp"] = int(t_v["timestamp"]*1000)
        return result

    def __key_subsystems(self):
        key_prefixes_lut = {
            u"drive_": u"thrusters",
            u"hyperdrive_": u"fsd",
            u"powerdistributor_": u"power distributor",
            u"shieldgenerator_": u"shield generator",
            u"powerplant_": u"power plant"
        }
        key_subsys = {}
        for internal_name in self.subsystems:
            if not internal_name.startswith(tuple(key_prefixes_lut.keys())):
                continue
            match = re.search('([a-zA-Z]*_)', internal_name)
            if match:
                prefix = match.group(1)
                canonical_name = key_prefixes_lut[prefix]
                key_subsys[canonical_name] = self.subsystems[internal_name].last()
        return key_subsys

    def __repr__(self):
        return str(self.__dict__)

    def update_from_loadout(self, event):
        other_id = event.get("ShipID", None)
        other_type = EDSpaceSuitFactory.canonicalize(event.get("Ship", "unknown")) 

        if other_id != self.id or other_type != self.type:
            EDRLOG.log(u"Mismatch between ID ({} vs {}) and/or Type ({} vs. {}), can't update from loadout".format(self.id, other_id, self.type, other_type), "WARNING")
            return

        self.identity = event.get('ShipIdent', None)
        self.name = event.get('ShipName', None)
        self.hull_health = event.get('HullHealth', None) * 100.0 # normalized to 0.0 ... 1.0
        if not 'Modules' in event:
            return
        self.modules = event['Modules']
        self.slots = {}
        timestamp = EDTime() 
        self.slots_timestamp = timestamp.from_journal_timestamp(event['timestamp']) if 'timestamp' in event else timestamp
        self.module_info_timestamp = self.slots_timestamp # To prevent reading stale data from modulesinfo.json
        for module in self.modules:
            ed_module = edmodule.EDModule(module)
            self.slots[module['Slot']] = ed_module
            if module.get("Slot", "").lower() == "powerplant":
                self.power_capacity = ed_module.power_generation
            health = module['Health'] * 100.0 if 'Health' in module else None 
            self.subsystem_health(module.get('Item', None), health)
        self.whole_loadout = True
        self.cargo_capacity = event.get("CargoCapacity", 0)
        self.cargo.update(event)

    def update_modules(self):
        reader = edmodulesinforeader.EDModulesInfoReader()
        modules_info = reader.process()
        stale = (self.slots_timestamp is None) or (self.module_info_timestamp and (self.slots_timestamp.as_py_epoch() < self.module_info_timestamp.as_py_epoch()))
        if not stale:
            EDRLOG.log(u"Modules info: up-to-date", "DEBUG")
            return True

        if not modules_info or not modules_info.get("Modules", None):
            EDRLOG.log(u"No info on modules!", "DEBUG")
            return False

        timestamp = EDTime()
        timestamp.from_journal_timestamp(modules_info['timestamp'])
        if self.slots_timestamp and (timestamp.as_py_epoch() < self.slots_timestamp.as_py_epoch() or timestamp.as_py_epoch() < self.module_info_timestamp.as_py_epoch()):
            EDRLOG.log(u"Stale info in modulesinfo.json: {} vs. {})".format(timestamp, self.slots_timestamp), "DEBUG")
            return False
        
        EDRLOG.log(u"Trying an update of modules: json@{}, slots@{}, panel looked@{}".format(timestamp, self.slots_timestamp, self.module_info_timestamp), "DEBUG")
        updated = self.slots_timestamp is None
        EDRLOG.log(u"This will be our first time with actual info", "DEBUG")
        self.slots_timestamp = timestamp
        modules = modules_info.get("Modules", [])
        for module in modules:
            slot_name = module.get("Slot", None)
            if slot_name in self.slots:
                module_updated = self.slots[slot_name].update(module)
                if self.slots[slot_name].power_draw > 0:
                    if module_updated:
                        EDRLOG.log(u"{} in {}: power_draw: {}, priority: {}".format(self.slots[slot_name].cname, slot_name, self.slots[slot_name].power_draw, self.slots[slot_name].priority), "DEBUG")
                    updated |= module_updated
            else:
                the_module = edmodule.EDModule(module)
                self.slots[slot_name] = the_module
                if the_module.power_draw > 0 or the_module.power_generation > 0:
                    EDRLOG.log(u"[New] {} in {}: power_draw: {}, priority: {}".format(self.slots[slot_name].cname, slot_name, self.slots[slot_name].power_draw, self.slots[slot_name].priority), "DEBUG")
                updated |= the_module.power_draw > 0 or the_module.power_generation > 0
        self.whole_loadout = True
        return updated

    def update_name(self, event):
        other_id = event.get("ShipID", None)
        other_type = EDSpaceSuitFactory.canonicalize(event.get("Ship", "unknown")) 
        if other_id != self.id or other_type != self.type:
            EDRLOG.log(u"Mismatch between ID ({} vs {}) and/or Type ({} vs. {}), can't update name/identity".format(self.id, other_id, self.type, other_type), "WARNING")
            return
        self.identity = event.get('UserShipId', None)
        self.name = event.get('UserShipName', None)
        
    def update_attitude(self, attitude):
        self.attitude.update(attitude)

    def update_cargo(self):
        reader = edcargoreader.EDCargoReader()
        cargo = reader.process()
        self.cargo.update(cargo)

    def reset(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = 100.0
        self.shield_health = 100.0
        self.shield_up = True
        self.subsystems = {}
        self.fight = {u"value": False, u"large": False, u"timestamp": now}
        self._hardpoints_deployed = {u"value": False, u"timestamp": now}
        self._attacked = {u"value": False, u"timestamp": now}
        self.heat_damaged = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        self.modules = None
        self.slots = {}
        self.slots_timestamp = None
        self.module_info_timestamp = None
        self.whole_loadout = False
    
    def destroy(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = 0.0

    def cockpit_breached(self):
        self.cockpit_health(0.0)

    def cockpit_health(self, value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        cockpit_suffix = "_cockpit"
        for internal_name in self.subsystems:
            if not internal_name.endswith(cockpit_suffix):
                continue
            self.subsystem_health(internal_name, value)
            break

    def taking_hull_damage(self, remaining_health):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = remaining_health

    def taking_heat_damage(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.heat_damaged = {u"value": True, u"timestamp": now}        

    def outfit_probably_changed(self, timestamp=None):
        edt = EDTime()
        if timestamp:
            edt.from_journal_timestamp(timestamp)
        self.module_info_timestamp = edt


    def subsystem_health(self, subsystem, health):
        if subsystem is None:
            return
        canonical = EDSpaceSuitFactory.normalize_module_name(subsystem)
        now = EDTime.ms_epoch_now()
        self.timestamp = now
        if canonical not in self.subsystems:
            config = edrconfig.EDR_CONFIG
            self.subsystems[canonical] = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.subsystems[canonical].update(health)

    def subsystem_details(self, subsystem):
        if subsystem is None:
            return
        canonical = EDSpaceSuitFactory.normalize_module_name(subsystem)
        if canonical not in self.subsystems:
            return
        readable_name, short_name = EDSpaceSuitFactory.readable_module_names(subsystem)
        return {"name": readable_name, "shortname": short_name, "stats": self.subsystems[canonical]}

    def add_subsystem(self, subsystem):
        if not subsystem:
            return
        canonical = EDSpaceSuitFactory.normalize_module_name(subsystem)
        now = EDTime.ms_epoch_now()
        self.timestamp = now
        self.outfit_probably_changed()
        config = edrconfig.EDR_CONFIG
        self.subsystems[canonical] = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.subsystems[canonical].update(None)
    
    def remove_subsystem(self, subsystem):
        if subsystem is None:
            return
        canonical = EDSpaceSuitFactory.normalize_module_name(subsystem)
        if canonical.startswith("shieldgenerator_"):
            self.shield_health = 0.0
        now = EDTime.py_epoch_now()
        self.timestamp = now
        try:
            del self.subsystems[canonical]
            self.outfit_probably_changed()
        except:
            pass

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

    def hardpoints(self, deployed):
        self._hardpoints_deployed = {u"value": deployed, u"timestamp": EDTime.py_epoch_now()}

    def hardpoints_deployed(self):
        if self._hardpoints_deployed["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._hardpoints_deployed["timestamp"]) and ((now - self._hardpoints_deployed["timestamp"]) <= self.fight_staleness_threshold)
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

    def refuel(self, amount=None):
        if amount:
            self.fuel_level = self.fuel_level + amount if self.fuel_level else amount
            if self.fuel_capacity:
                self.low_fuel = self.fuel_level < self.fuel_capacity * .25
        else:
            self.low_fuel = False
            self.fuel_level = self.fuel_capacity

    def fuel_scooping(self, new_level):
        self.fuel_level = new_level
        if self.fuel_capacity:
            self.low_fuel = self.fuel_level < self.fuel_capacity * .25

    def repair(self, item=None):
        if item:
            self.subsystem_health(item, 100.0)
        else:
            self.hull_health = 100.0
            for subsystem in self.subsystems:
                self.subsystem_health(subsystem, 100.0)

    def could_use_limpets(self, mining_only=False):
        if self.cargo_capacity <= 0:
            return False
        
        if mining_only:
            if not self.is_mining_rig():
                return False
        elif not self.has_drone_controller():
            return False

        return  self.cargo.how_many("drones") < self.cargo_capacity

    def is_mining_rig(self):
        for slot_name in self.slots:
            if self.slots[slot_name].is_prospector_drone_controller():
                return True
        return False


    def has_drone_controller(self):
        for slot_name in self.slots:
            if self.slots[slot_name].is_drone_controller():
                return True
        return False

    def has_shield_generator(self):
        for slot_name in self.slots:
            if self.slots[slot_name].is_shield():
                return True
        return False
    
    def describe_loadout(self):
        weighted_tags = {}
        for  module in self.subsystems:
            module_tags = EDVehicle.module_tags(slot_name)
            for tag in module_tags:
                weighted_tags[tag] = module_tags[tag] + weighted_tags.get(tag, 0) 

        return sorted(weighted_tags, key=weighted_tags.get, reverse=True)

    def __eq__(self, other):
        if not isinstance(other, EDVehicle):
            return False
        return self.__dict__ == other.__dict__
        
    def __ne__(self, other):
        return not self.__eq__(other)

class EDFlightSuit(EDSpaceSuit):
    def __init__(self):
        super(EDFlightSuit, self).__init__()
        self.type = u'Flight Suit'
        self.value = 31000 # TODO

class EDMaverickSuit(EDSpaceSuit):
    def __init__(self):
        super(EDMaverickSuit, self).__init__()
        self.type = u'Maverick Suit'
        self.value = 150000

class EDDominatorSuit(EDSpaceSuit):
    def __init__(self):
        super(EDDominatorSuit, self).__init__()
        self.type = u'Dominator Suit'
        self.value = 150000

class EDArtemisSuit(EDSpaceSuit):
    def __init__(self):
        super(EDDominatorSuit, self).__init__()
        self.type = u'Artemis Suit'
        self.value = 150000


class EDUnknownSuit(EDSpaceSuit):
    def __init__(self):
        super(EDUnknownSuit, self).__init__()
        self.type = u'Unknown Suit'

class EDSpaceSuitFactory(object):
    __suit_classes = {
        "flightsuit": EDFlightSuit,
        "tacticalsuit_class1": EDDominatorSuit,
        "explorationsuit_class1": EDArtemisSuit,
        "utilitysuit_class1": EDMaverickSuit,
        "unknown": EDUnknownSuit,
    }

    CANONICAL_SPACESUIT_NAMES = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'spacesuitnames.json')).read())
    CANONICAL_SUITMODULE_NAMES = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'suitsmodulenames.json'), encoding="utf-8", errors='ignore').read())

    @staticmethod
    def canonicalize(name):
        if name is None:
            return u"Unknown" # Note: this shouldn't be translated

        if name in EDSpaceSuitFactory.CANONICAL_SPACESUIT_NAMES.values():
            return name # Already canonical

        if name.lower() in EDSpaceSuitFactory.CANONICAL_SPACESUIT_NAMES:
            return EDSpaceSuitFactory.CANONICAL_SPACESUIT_NAMES[name.lower()]

        return name.lower()

    @staticmethod
    def normalize_module_name(name):
        # TODO
        normalized = name.lower()
        
        # suffix _name or _name; is not used in loadout or afmurepair events 
        if normalized.endswith(u"_name"):
            useless_suffix_length = len(u"_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith(u"_name;"):
            useless_suffix_length = len(u"_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith(u"$"):
            normalized = normalized[1:]

        # just get rid of prefixes because sometimes int_ becomes ext_ depending on the event
        if normalized.startswith((u"int_", u"ext_", u"hpt_")):
            normalized = normalized[4:]
        return normalized

    @staticmethod
    def readable_module_names(name):
        #TODO
        if name is None:
            return u"Unknown" # Note: this shouldn't be translated

        if name in EDSpaceSuitFactory.CANONICAL_MODULE_NAMES.values():
            return name # Already canonical

        normalized = EDSpaceSuitFactory.normalize_module_name(name)
        if normalized in EDSpaceSuitFactory.CANONICAL_MODULE_NAMES:
            return (EDSpaceSuitFactory.CANONICAL_MODULE_NAMES[normalized]["name"], EDSpaceSuitFactory.CANONICAL_MODULE_NAMES[normalized]["shortname"])

        match = re.search('([a-zA-Z_]*)_size([0-9])_class([0-9])_?([a-zA-Z_]*)?', normalized)
        if match:
            class_letter = chr(70-int(match.group(3)))
            synthetic_name = ""
            if match.group(4):
                synthetic_name = u"{} {} ({}{})".format(match.group(1), match.group(4), match.group(2), class_letter)
            else:
                synthetic_name = u"{} ({}{})".format(match.group(1), match.group(2), class_letter)
            return (synthetic_name, synthetic_name)
        return (normalized.lower(), normalized.lower())

    @staticmethod
    def module_tags(name):
        # TODO
        if name is None:
            return {}

        normalized = EDSpaceSuitFactory.normalize_module_name(name)
        if normalized not in EDSpaceSuitFactory.CANONICAL_MODULE_NAMES:
            return {}
        return EDSpaceSuitFactory.CANONICAL_MODULE_NAMES[normalized].get("tags", {})

    @staticmethod
    def from_edmc_state(state):
        # TODO equivalent option?
        return
        name = state.get('ShipType', None)

        if name is None:
            name = 'unknown'

        vehicle_class = EDSpaceSuitFactory.__vehicle_classes.get(name.lower(), None)
        if vehicle_class is None:
            raise NotImplementedError("The requested vehicle has not been implemented")
        
        vehicle = vehicle_class()
        vehicle.id = state.get('ShipID', None)
        vehicle.identity = state.get('ShipIdent', None)
        vehicle.name = state.get('ShipName', None)
        vehicle.hull_value = state.get('HullValue', None)
        vehicle.rebuy = state.get('Rebuy', None)

        modules = state.get('Modules', None)
        if modules:
            for module in modules:
                health = modules[module]['Health'] * 100.0 if 'Health' in modules[module] else None 
                vehicle.subsystem_health(modules[module].get('Item', None), health)
        return vehicle

    # TODO after this
    @staticmethod
    def from_internal_name(internal_name):
        return EDSpaceSuitFactory.__vehicle_classes.get(internal_name.lower(), EDUnknownVehicle)()

    @staticmethod
    def from_load_game_event(event):
        vehicle = EDSpaceSuitFactory.from_internal_name(event.get("Ship", 'unknown'))
        vehicle.id = event.get('ShipID', None)
        vehicle.identity = event.get('ShipIdent', None)
        vehicle.name = event.get('ShipName', None)
        vehicle.fuel_capacity = event.get('FuelCapacity', None)
        vehicle.fuel_level = event.get('FuelLevel', None)
        return vehicle

    @staticmethod
    def from_loadout_event(event):
        vehicle = EDSpaceSuitFactory.from_internal_name(event.get("Ship", 'unknown'))
        vehicle.id = event.get('ShipID', None)
        vehicle.identity = event.get('ShipIdent', None)
        vehicle.name = event.get('ShipName', None)
        vehicle.hull_health = event.get('HullHealth', None) * 100.0 # normalized to 0.0 ... 1.0
        vehicle.fuel_capacity = event.get('FuelCapacity', None) #missing from loadout event...
        vehicle.fuel_level = event.get('FuelLevel', None) #missing from loadout event...
        if not 'Modules' in event:
            return vehicle

        modules = event['Modules']
        for module in modules:
            health = modules[module]['Health'] * 100.0 if 'Health' in modules[module] else None 
            vehicle.subsystem_health(modules[module].get('Item', None), health)
        return vehicle

    @staticmethod
    def from_stored_ship(ship_info):
        vehicle = EDSpaceSuitFactory.from_internal_name(ship_info.get("ShipType", 'unknown'))
        vehicle.id = ship_info.get('ShipID', None)
        vehicle.name = ship_info.get('Name', None)
        vehicle.value = ship_info.get('Value', None)
        vehicle.hot = ship_info.get('Hot', None)
        return vehicle

    @staticmethod
    def unknown_spacesuit():
        return EDUnknownSuit()