import re
import os
import json
from collections import deque
from math import log10

from edtime import EDTime
import edrconfig
import edrhitppoints
import edmodule
import edmodulesinforeader
import edcargoreader
import edrlog
import edcargo
import utils2to3
from edshield import EDPowerDistributor, EDShieldGenerator, EDShieldingFactory
from edarmour import EDHullFactory
from edweapons import EDWeaponFactory

EDRLOG = edrlog.EDRLog()

class EDVehicleSize(object):
    UNKNOWN = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 4

class EDVehicle(object):
    def __init__(self):
        self.type = None
        self.size = None
        self.name = None
        self.id = None
        self.identity = None
        self.rebuy = None
        self._value = None
        self.hot = False
        now = EDTime.py_epoch_now()
        config = edrconfig.EDR_CONFIG
        self._hull_health = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.hull_mass = 0
        self.hull_hardness = 0
        self.hull_base_strength = 0
        self._shield_health = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.shield_up = True
        self.shield_base_strength = 0
        self.subsystems = {}
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
        self.max_jump_range = None
        self.module_info_timestamp = None
        self.slots_timestamp = None
        self.slots = {}
        self.modules = None
        self.power_capacity = None
        self.cargo_capacity = 0
        self.cargo = edcargo.EDCargo()
        self.whole_loadout = False
        self.distro = EDPowerDistributor()
        self.shield_gen = EDShieldGenerator()
        self.boosters = [] # TODO maybe merge into modules? maybe keep them?
        self.gsrps = [] # TODO maybe merge into modules? maybe keep them?
        self.armour = EDHullFactory.default_armour()
        self.weapons = []
        self.hrps = []
        self.scbs = []
        self.over_heating = False

    def hull_strength(self):
        strength = self.armour.strength(self.hull_base_strength)
        hrps_bonus = 0
        for h in self.hrps:
            if h.enabled:
                hrps_bonus += h.armour
        
        strength += hrps_bonus
        return strength

    def hull_resistances(self):
        thermal = 1.0
        kinetic = 1.0
        explosive = 1.0
        caustic = 1.0

        for h in self.hrps:
            thermal   *= (1.0 - h.resistances.thermal)
            kinetic   *= (1.0 - h.resistances.kinetic)
            explosive *= (1.0 - h.resistances.explosive)
            caustic   *= (1.0 - h.resistances.caustic)
            
        if thermal < 0.7:
            thermal   = 0.7 - (0.7 - thermal)/2.0
            
        if kinetic < 0.7:
            kinetic   = 0.7 - (0.7 - kinetic)/2.0
            
        if explosive < 0.7:
            explosive = 0.7 - (0.7 - explosive)/2.0
            
        if caustic < 0.7:
            caustic   = 0.7 - (0.7 - caustic)/2.0
        
        thermal   = (1.0 - self.armour.hull_resistances.thermal)   * thermal
        kinetic   = (1.0 - self.armour.hull_resistances.kinetic)   * kinetic
        explosive = (1.0 - self.armour.hull_resistances.explosive) * explosive
        caustic   = (1.0 - self.armour.hull_resistances.caustic)   * caustic
        
        overall_resistances = edmodule.EDResistances()
        overall_resistances.thermal = 1.0 - thermal
        overall_resistances.kinetic = 1.0 - kinetic
        overall_resistances.explosive = 1.0 - explosive
        overall_resistances.caustic = 1.0 - caustic

        return overall_resistances
     
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

    def shield_strength(self):
        strength = self.shield_gen.strength(self.hull_mass, self.shield_base_strength)
        boosters_bonus = 0
        for b in self.boosters:
            if b.enabled:
                boosters_bonus += b.strength_bonus
        
        strength *= 1.0 + boosters_bonus
        
        gsrp_bonus = 0
        for g in self.gsrps:
            if g.enabled:
                gsrp_bonus += g.strength

        strength += gsrp_bonus
        strength *= (1.0 - self.distro.sys_resistance())
        
        return strength

    # TODO verify, cor is doing that differently
    def shield_resistances(self):
        thermal = 1.0
        kinetic = 1.0
        explosive = 1.0
        caustic = 1.0

        for b in self.boosters:
            thermal   *= (1.0 - b.resistances.thermal)
            kinetic   *= (1.0 - b.resistances.kinetic)
            explosive *= (1.0 - b.resistances.explosive)
            caustic   *= (1.0 - b.resistances.caustic)
            
        if thermal < 0.7:
            thermal   = 0.7 - (0.7 - thermal)/2.0
            
        if kinetic < 0.7:
            kinetic   = 0.7 - (0.7 - kinetic)/2.0
            
        if explosive < 0.7:
            explosive = 0.7 - (0.7 - explosive)/2.0
            
        if caustic < 0.7:
            caustic   = 0.7 - (0.7 - caustic)/2.0
        
        thermal   = (1.0 - self.shield_gen.shield_resistances.thermal)   * thermal
        kinetic   = (1.0 - self.shield_gen.shield_resistances.kinetic)   * kinetic
        explosive = (1.0 - self.shield_gen.shield_resistances.explosive) * explosive
        caustic   = (1.0 - self.shield_gen.shield_resistances.caustic)   * caustic
        
        overall_resistances = edmodule.EDResistances()
        overall_resistances.thermal = 1.0 - thermal
        overall_resistances.kinetic = 1.0 - kinetic
        overall_resistances.explosive = 1.0 - explosive
        overall_resistances.caustic = 1.0 - caustic

        return overall_resistances

    
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
            u"hyperdrive_overcharge": u"fsd (sco)",
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
        other_type = EDVehicleFactory.canonicalize(event.get("Ship", "unknown")) 

        if other_id != self.id or other_type != self.type:
            EDRLOG.log(u"Mismatch between ID ({} vs {}) and/or Type ({} vs. {}), can't update from loadout".format(self.id, other_id, self.type, other_type), "WARNING")
            return

        self.identity = event.get('ShipIdent', None)
        self.name = event.get('ShipName', None)
        self.hull_health = event.get('HullHealth', None) * 100.0 # normalized to 0.0 ... 1.0
        if not 'Modules' in event:
            return
        self.update_from_modules_dict(event['Modules'])
        self.whole_loadout = True
        self.cargo_capacity = event.get("CargoCapacity", 0)
        self.cargo.update(event)
        self.max_jump_range = event.get("MaxJumpRange", None)

    def update_from_modules_dict(self, modules):
        self.modules = modules
        self.slots = {}
        self.boosters = []
        self.gsrps = []
        self.hrps = []
        self.weapons = []
        self.scbs = []
        timestamp = EDTime() 
        self.slots_timestamp = timestamp
        self.module_info_timestamp = self.slots_timestamp # To prevent reading stale data from modulesinfo.json
        for module in self.modules:
            ed_module = edmodule.EDModule(module)
            if module["Slot"]:
                self.slots[module['Slot']] = ed_module

            if module.get("Slot", "").lower() == "powerplant":
                self.power_capacity = ed_module.power_generation
            elif module.get("Slot", "").lower() == "armour":
                self.armour = EDHullFactory.from_module(module)
            elif module.get("Item", "").lower().startswith('int_shieldgenerator'):
                self.shield_gen = EDShieldingFactory.from_module(module)
            elif module.get("Item", "").lower().startswith('int_shieldcellbank'):
                self.__add_scb(module)
            elif module.get("Item", "").lower().startswith('hpt_shieldbooster'):
                self.__add_booster(module)
            elif module.get("Item", "").lower().startswith('int_guardianshieldreinforcement'):
                self.__add_gsrp(module)
            elif module.get("Item", "").lower().startswith('int_hullreinforcement'):
                self.__add_hrp(module)
            elif module.get("Item", "").lower().startswith('int_guardianhullreinforcement'):
                self.__add_hrp(module)
            
            m = re.match(r'([a-zA-Z]+)Hardpoint([0-9]+)', module.get("Slot", ""))
            if m and m.group(1) in ["Huge", "Large", "Medium"]:
                self.__add_weapon(module)

            #TODO other
            health = module['Health'] * 100.0 if 'Health' in module else None 
            self.subsystem_health(module.get('Item', None), health)

    def __add_booster(self, module):
        booster = EDShieldingFactory.from_module(module)
        if booster:
            self.boosters.append(booster)

    def __add_scb(self, module):
        scb = EDShieldingFactory.from_module(module)
        if scb:
            self.boosters.append(scb)

    def __add_gsrp(self, module):
        gsrp = EDShieldingFactory.from_module(module)
        if gsrp:
           self.gsrps.append(gsrp)

    def __add_hrp(self, module):
        hrp = EDHullFactory.from_module(module)
        if hrp:
           self.hrps.append(hrp)
           
    def __add_weapon(self, module):
        weapon = EDWeaponFactory.from_module(module)
        if weapon:
           self.weapons.append(weapon)
           
    def update_from_modules_edmc(self, modules):
        self.modules = modules # TODO not exactly the same
        self.slots = {}
        self.boosters = []
        self.gsrps = []
        self.hrps = []
        self.weapons = []
        self.scbs = []
        timestamp = EDTime() 
        self.slots_timestamp = timestamp
        self.module_info_timestamp = self.slots_timestamp # To prevent reading stale data from modulesinfo.json
        for name in self.modules:
            module = self.modules[name]
            ed_module = edmodule.EDModule(module)
            if module["Slot"]:
                self.slots[module['Slot']] = ed_module
                
            if module.get("Slot", "").lower() == "powerplant":
                self.power_capacity = ed_module.power_generation
            elif module.get("Slot", "").lower() == "armour":
                self.armour = EDHullFactory.from_module(module)
            elif module.get("Item", "").lower().startswith('int_shieldgenerator'):
                self.shield_gen = EDShieldingFactory.from_module(module)
            elif module.get("Item", "").lower().startswith('hpt_shieldbooster'):
                self.__add_booster(module)
            elif module.get("Item", "").lower().startswith('int_shieldcellbank'):
                self.__add_scb(module)
            elif module.get("Item", "").lower().startswith('int_guardianshieldreinforcement'):
                self.__add_gsrp(module)
            elif module.get("Item", "").lower().startswith('int_hullreinforcement'):
                self.__add_hrp(module)
            elif module.get("Item", "").lower().startswith('int_guardianhullreinforcement'):
                self.__add_hrp(module)

            m = re.match(r'([a-zA-Z]+)Hardpoint([0-9]+)', module.get("Slot", ""))
            if m and m.group(1) in ["Huge", "Large", "Medium"]:
                self.__add_weapon(module)

            health = module['Health'] * 100.0 if 'Health' in module else None 
            self.subsystem_health(module.get('Item', None), health)
            

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
        other_type = EDVehicleFactory.canonicalize(event.get("Ship", "unknown")) 
        if other_id != self.id or other_type != self.type:
            EDRLOG.log(u"Mismatch between ID ({} vs {}) and/or Type ({} vs. {}), can't update name/identity".format(self.id, other_id, self.type, other_type), "WARNING")
            return
        self.identity = event.get('UserShipId', None)
        self.name = event.get('UserShipName', None)

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
        self.distro.reset()
        self.shield_gen.reset()
        self.boosters = [] # TODO maybe merge into modules?
        self.gsrps = [] # TODO maybe merge into modules?
        self.armour = EDHullFactory.default_armour()
        self.hrps = []
        self.weapons = []
        self.scbs = []
        self.over_heating = False
    
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
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        now = EDTime.ms_epoch_now()
        self.timestamp = now
        if canonical not in self.subsystems:
            config = edrconfig.EDR_CONFIG
            self.subsystems[canonical] = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.subsystems[canonical].update(health)

    def subsystem_details(self, subsystem):
        if subsystem is None:
            return
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        if canonical not in self.subsystems:
            return
        readable_name, short_name = EDVehicleFactory.readable_module_names(subsystem)
        return {"name": readable_name, "shortname": short_name, "stats": self.subsystems[canonical]}

    def add_subsystem(self, subsystem):
        if not subsystem:
            return
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        now = EDTime.ms_epoch_now()
        self.timestamp = now
        self.outfit_probably_changed()
        config = edrconfig.EDR_CONFIG
        self.subsystems[canonical] = edrhitppoints.EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.subsystems[canonical].update(None)
    
    def remove_subsystem(self, subsystem):
        if subsystem is None:
            return
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        if canonical.startswith("shieldgenerator_"):
            self.shield_health = 0.0
        now = EDTime.py_epoch_now()
        self.timestamp = now
        try:
            del self.subsystems[canonical]
            self.outfit_probably_changed()
        except:
            pass

    def needs_large_landing_pad(self):
        return self.size in [EDVehicleSize.LARGE, EDVehicleSize.UNKNOWN]
    
    def needs_medium_landing_pad(self):
        return self.size in [EDVehicleSize.MEDIUM, EDVehicleSize.UNKNOWN]

    def supports_slf(self):
        return False

    def supports_srv(self):
        return True

    def supports_crew(self):
        return self.seats > 1

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

    def damage_per_shot(self):
        overall = {
            "absolute": 0,         
            "explosive": 0,
            "kinetic": 0,
            "thermal": 0,
            "caustic": 0,
        }
        # TODO premium, basic, standard ammo
        for w in self.weapons:
            if self.over_heating:
                w.temperature_percent(1.0) # TODO not exact but the minimum value required to trigger the over heating flag
            damage = w.damage_per_shot()
            overall = {k: overall.get(k, 0) + damage.get(k, 0) for k in set(overall) | set(damage)}
        return overall


    def shield_state(self, is_up):
        if not is_up:
            self.shield_health = 0.0
        self.shield_up = is_up

    def pips(self, values):
        return self.distro.update(values)

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
        for internal_name in self.subsystems:
            module_tags = EDVehicle.module_tags(internal_name)
            for tag in module_tags:
                weighted_tags[tag] = module_tags[tag] + weighted_tags.get(tag, 0)

        return sorted(weighted_tags, key=weighted_tags.get, reverse=True)

    def __eq__(self, other):
        if not isinstance(other, EDVehicle):
            return False
        return self.__dict__ == other.__dict__
        
    def __ne__(self, other):
        return not self.__eq__(other)

class EDSidewinder(EDVehicle):
    def __init__(self):
        super(EDSidewinder, self).__init__()
        self.type = u'Sidewinder'
        self.size = EDVehicleSize.SMALL
        self.value = 31000
        self.shield_base_strength = 40
        self.hull_mass = 25
        self.hull_hardness = 35
        self.hull_base_strength = 108 / 1.8

class EDHauler(EDVehicle):
    def __init__(self):
        super(EDHauler, self).__init__()
        self.type = u'Hauler'
        self.size = EDVehicleSize.SMALL
        self.value = 51720
        self.shield_base_strength = 50
        self.hull_mass = 14
        self.hull_hardness = 20
        self.hull_base_strength = 180 / 1.8

class EDEagle(EDVehicle):
    def __init__(self):
        super(EDEagle, self).__init__()
        self.type = u'Eagle'
        self.size = EDVehicleSize.SMALL
        self.value = 43800
        self.shield_base_strength = 60
        self.hull_mass = 50
        self.hull_hardness = 20
        self.hull_base_strength = 72 / 1.8

class EDAdder(EDVehicle):
    def __init__(self):
        super(EDAdder, self).__init__()
        self.type = u'Adder'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 86472
        self.shield_base_strength = 60
        self.hull_mass = 35
        self.hull_hardness = 35
        self.hull_base_strength = 162 / 1.8

class EDTaxi(EDVehicle):
    def __init__(self):
        super(EDTaxi, self).__init__()
        self.type = u'Unknown (taxi)'
        self.size = EDVehicleSize.UNKNOWN
        self.destination = {"system": None, "location": None}
    
    def bound_for(self, system, location):
        self.destination["system"]= system
        self.destination["location"]= location

class EDAdderApex(EDTaxi):
    def __init__(self):
        super(EDAdderApex, self).__init__()
        self.type = u'Adder Apex'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 86472
        self.shield_base_strength = 60
        self.hull_mass = 35
        self.hull_hardness = 35
        self.hull_base_strength = 162 / 1.8
    

class EDViperMkIII(EDVehicle):
    def __init__(self):
        super(EDViperMkIII, self).__init__()
        self.type = u'Viper Mk III'
        self.size = EDVehicleSize.SMALL
        self.value = 141592
        self.shield_base_strength = 105
        self.hull_mass = 50
        self.hull_hardness = 35
        self.hull_base_strength = 126 / 1.8

class EDCobraMkIII(EDVehicle):
    def __init__(self):
        super(EDCobraMkIII, self).__init__()
        self.type = u'Cobra Mk III'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 346634
        self.shield_base_strength = 80
        self.hull_mass = 180
        self.hull_hardness = 35
        self.hull_base_strength = 216 / 1.8

class EDT6Transporter(EDVehicle):
    def __init__(self):
        super(EDT6Transporter, self).__init__()
        self.type = u'Type-6 Transporter'
        self.size = EDVehicleSize.MEDIUM
        self.value = 1044612
        self.shield_base_strength = 90
        self.hull_mass = 155
        self.hull_hardness = 35
        self.hull_base_strength = 324 / 1.8

class EDDolphin(EDVehicle):
    def __init__(self):
        super(EDDolphin, self).__init__()
        self.type = u'Dolphin'
        self.size = EDVehicleSize.SMALL
        self.value = 1334244
        self.shield_base_strength = 110
        self.hull_mass = 140
        self.hull_hardness = 35
        self.hull_base_strength = 198 / 1.8

class EDT7Transporter(EDVehicle):
    def __init__(self):
        super(EDT7Transporter, self).__init__()
        self.type = u'Type-7 Transporter'
        self.size = EDVehicleSize.LARGE
        self.value = 17469174
        self.shield_base_strength = 155
        self.hull_mass = 350
        self.hull_hardness = 54
        self.hull_base_strength = 612 / 1.8

class EDT8Transporter(EDVehicle):
    def __init__(self):
        super(EDT8Transporter, self).__init__()
        self.type = u'Type-8 Transporter'
        self.size = EDVehicleSize.MEDIUM
        self.value = 0 # TODO
        self.shield_base_strength = 122
        self.hull_mass = 400
        self.hull_hardness = 54 # TODO
        self.hull_base_strength = 792 / 1.8

class EDAspExplorer(EDVehicle):
    def __init__(self):
        super(EDAspExplorer, self).__init__()
        self.type = u'Asp Explorer'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 6650520
        self.shield_base_strength = 140
        self.hull_mass = 280
        self.hull_hardness = 52
        self.hull_base_strength = 378 / 1.8

class EDVulture(EDVehicle):
    def __init__(self):
        super(EDVulture, self).__init__()
        self.type = u'Vulture'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 4922534
        self.shield_base_strength = 240
        self.hull_mass = 230
        self.hull_hardness = 55
        self.hull_base_strength = 288 / 1.8
    
class EDVultureFrontlines(EDTaxi):
    def __init__(self):
        super(EDVultureFrontlines, self).__init__()
        self.type = u'Vulture Frontlines'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 4922534
        self.shield_base_strength = 240
        self.hull_mass = 230
        self.hull_hardness = 55
        self.hull_base_strength = 288 / 1.8

class EDImperialClipper(EDVehicle):
    def __init__(self):
        super(EDImperialClipper, self).__init__()
        self.type = u'Imperial Clipper'
        self.size = EDVehicleSize.LARGE
        self.seats = 2
        self.value = 22256248
        self.shield_base_strength = 180
        self.hull_mass = 400
        self.hull_hardness = 60
        self.hull_base_strength = 486 / 1.8

class EDFederalDropship(EDVehicle):
    def __init__(self):
        super(EDFederalDropship, self).__init__()
        self.type = u'Federal Dropship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 14273598
        self.shield_base_strength = 200
        self.hull_mass = 580
        self.hull_hardness = 60
        self.hull_base_strength = 540 / 1.8

class EDOrca(EDVehicle):
    def __init__(self):
        super(EDOrca, self).__init__()
        self.type = u'Orca'
        self.size = EDVehicleSize.LARGE
        self.seats = 2
        self.value = 48529270
        self.shield_base_strength = 220
        self.hull_mass = 290
        self.hull_hardness = 55
        self.hull_base_strength = 396 / 1.8

class EDT9Heavy(EDVehicle):
    def __init__(self):
        super(EDT9Heavy, self).__init__()
        self.type = u'Type-9 Heavy'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 77693648
        self.shield_base_strength = 240
        self.hull_mass = 850
        self.hull_hardness = 65
        self.hull_base_strength = 864 / 1.8

    def supports_slf(self):
        return True

class EDT10Defender(EDVehicle):
    def __init__(self):
        super(EDT10Defender, self).__init__()
        self.type = u'Type-10 Defender'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 124874411
        self.shield_base_strength = 320
        self.hull_mass = 1200
        self.hull_hardness = 75
        self.hull_base_strength = 1044 / 1.8
    
    def supports_slf(self):
        return True

class EDPython(EDVehicle):
    def __init__(self):
        super(EDPython, self).__init__()
        self.type = u'Python'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 56824391
        self.shield_base_strength = 260
        self.hull_mass = 350
        self.hull_hardness = 65
        self.hull_base_strength = 468 / 1.8

class EDPythonMkII(EDVehicle):
    def __init__(self):
        super(EDPythonMkII, self).__init__()
        self.type = u'Python Mk II'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 68906009
        self.shield_base_strength = 335
        self.hull_mass = 450
        self.hull_hardness = 70
        self.hull_base_strength = 504 / 1.8
    
class EDBelugaLiner(EDVehicle):
    def __init__(self):
        super(EDBelugaLiner, self).__init__()
        self.type = u'Beluga Liner'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 84492158
        self.shield_base_strength = 280
        self.hull_mass = 950
        self.hull_hardness = 60
        self.hull_base_strength = 504 / 1.8

    def supports_slf(self):
        return True

class EDFerDeLance(EDVehicle):
    def __init__(self):
        super(EDFerDeLance, self).__init__()
        self.type = u'Fer-de-Lance'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 51556410
        self.shield_base_strength = 300
        self.hull_mass = 250
        self.hull_hardness = 70
        self.hull_base_strength = 405 / 1.8

class EDAnaconda(EDVehicle):
    def __init__(self):
        super(EDAnaconda, self).__init__()
        self.type = u'Anaconda'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 146402444
        self.shield_base_strength = 350
        self.hull_mass = 400
        self.hull_hardness = 65
        self.hull_base_strength = 945 / 1.8

    def supports_slf(self):
        return True

class EDFederalCorvette(EDVehicle):
    def __init__(self):
        super(EDFederalCorvette, self).__init__()
        self.type = u'Federal Corvette'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 187402444
        self.shield_base_strength = 555
        self.hull_mass = 900
        self.hull_hardness = 70
        self.hull_base_strength = 666 / 1.8
    
    def supports_slf(self):
        return True

class EDImperialCutter(EDVehicle):
    def __init__(self):
        super(EDImperialCutter, self).__init__()
        self.type = u'Imperial Cutter'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 208402444
        self.shield_base_strength = 600
        self.hull_mass = 1100
        self.hull_hardness = 70
        self.hull_base_strength = 720 / 1.8

    def supports_slf(self):
        return True

class EDDiamondbackScout(EDVehicle):
    def __init__(self):
        super(EDDiamondbackScout, self).__init__()
        self.type = u'Diamondback Scout'
        self.size = EDVehicleSize.SMALL
        self.value = 561244
        self.shield_base_strength = 120
        self.hull_mass = 170
        self.hull_hardness = 40
        self.hull_base_strength = 216 / 1.8

class EDImperialCourier(EDVehicle):
    def __init__(self):
        super(EDImperialCourier, self).__init__()
        self.type = u'Imperial Courier'
        self.size = EDVehicleSize.SMALL
        self.value = 2539844
        self.shield_base_strength = 200
        self.hull_mass = 35
        self.hull_hardness = 30
        self.hull_base_strength = 144 / 1.8

class EDDiamondbackExplorer(EDVehicle):
    def __init__(self):
        super(EDDiamondbackExplorer, self).__init__()
        self.type = u'Diamondback Explorer'
        self.size = EDVehicleSize.SMALL
        self.value = 1891674
        self.shield_base_strength = 150
        self.hull_mass = 260
        self.hull_hardness = 42
        self.hull_base_strength = 270 / 1.8

class EDImperialEagle(EDVehicle):
    def __init__(self):
        super(EDImperialEagle, self).__init__()
        self.type = u'Imperial Eagle'
        self.size = EDVehicleSize.SMALL
        self.value = 109492
        self.shield_base_strength = 80
        self.hull_mass = 50
        self.hull_hardness = 28
        self.hull_base_strength = 108 / 1.8

class EDFederalAssaultShip(EDVehicle):
    def __init__(self):
        super(EDFederalAssaultShip, self).__init__()
        self.type = u'Federal Assault Ship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 19774598
        self.shield_base_strength = 200
        self.hull_mass = 480
        self.hull_hardness = 60
        self.hull_base_strength = 540 / 1.8

class EDFederalGunship(EDVehicle):
    def __init__(self):
        super(EDFederalGunship, self).__init__()
        self.type = u'Federal Gunship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 35773598
        self.shield_base_strength = 250
        self.hull_mass = 580
        self.hull_hardness = 60
        self.hull_base_strength = 630 / 1.8

    def supports_slf(self):
        return True

class EDViperMkIV(EDVehicle):
    def __init__(self):
        super(EDViperMkIV, self).__init__()
        self.type = u'Viper Mk IV'
        self.size = EDVehicleSize.SMALL
        self.value = 434844
        self.shield_base_strength = 150
        self.hull_mass = 190
        self.hull_hardness = 35
        self.hull_base_strength = 270 / 1.8

class EDCobraMkIV(EDVehicle):
    def __init__(self):
        super(EDCobraMkIV, self).__init__()
        self.type = u'Cobra Mk IV'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 744574
        self.shield_base_strength = 120
        self.hull_mass = 210
        self.hull_hardness = 35
        self.hull_base_strength = 216 / 1.8

class EDKeelback(EDVehicle):
    def __init__(self):
        super(EDKeelback, self).__init__()
        self.type = u'Keelback'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 3123064
        self.shield_base_strength = 135
        self.hull_mass = 180
        self.hull_hardness = 45
        self.hull_base_strength = 486 / 1.8

    def supports_slf(self):
        return True

class EDAspScout(EDVehicle):
    def __init__(self):
        super(EDAspScout, self).__init__()
        self.type = u'Asp Scout'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 3959064
        self.shield_base_strength = 120
        self.hull_mass = 150
        self.hull_hardness = 52
        self.hull_base_strength = 324 / 1.8

class EDAllianceChieftain(EDVehicle):
    def __init__(self):
        super(EDAllianceChieftain, self).__init__()
        self.type = u'Alliance Chieftain'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 18952161
        self.shield_base_strength = 200
        self.hull_mass = 400
        self.hull_hardness = 65
        self.hull_base_strength = 504 / 1.8

class EDAllianceChallenger(EDVehicle):
    def __init__(self):
        super(EDAllianceChallenger, self).__init__()
        self.type = u'Alliance Challenger'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 30540973
        self.shield_base_strength = 220
        self.hull_mass = 450
        self.hull_hardness = 65
        self.hull_base_strength = 540 / 1.8


class EDAllianceCrusader(EDVehicle):
    def __init__(self):
        super(EDAllianceCrusader, self).__init__()
        self.type = u'Alliance Crusader'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 3
        self.value = 23635619
        self.shield_base_strength = 200
        self.hull_mass = 500
        self.hull_hardness = 65
        self.hull_base_strength = 540 / 1.8

    def supports_slf(self):
        return True

class EDKraitMkII(EDVehicle):
    def __init__(self):
        super(EDKraitMkII, self).__init__()
        self.type = u'Krait Mk II'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 3
        self.value = 45660416
        self.shield_base_strength = 220
        self.hull_mass = 320
        self.hull_hardness = 55
        self.hull_base_strength = 396 / 1.8

    def supports_slf(self):
        return True

class EDKraitPhantom(EDVehicle):
    def __init__(self):
        super(EDKraitPhantom, self).__init__()
        self.type = u'Krait Phantom'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 44139676
        self.shield_base_strength = 200
        self.hull_mass = 270
        self.hull_hardness = 60
        self.hull_base_strength = 324 / 1.8

class EDMamba(EDVehicle):
    def __init__(self):
        super(EDMamba, self).__init__()
        self.type = u'Mamba'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 56289969
        self.shield_base_strength = 270
        self.hull_mass = 250
        self.hull_hardness = 70
        self.hull_base_strength = 414 / 1.8

class EDMandalay(EDVehicle):
    def __init__(self):
        super(EDMandalay, self).__init__()
        self.type = u'Mandalay'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 15614644
        self.shield_base_strength = 220
        self.hull_mass = 230
        self.hull_hardness = 55
        self.hull_base_strength = 414 / 1.8

class EDShipLaunchedFighter(EDVehicle):
    def __init__(self):
        super(EDShipLaunchedFighter, self).__init__()

    def supports_slf(self):
        return False
    
    def supports_srv(self):
        return False

class EDImperialFighter(EDShipLaunchedFighter):
    def __init__(self):
        super(EDImperialFighter, self).__init__()
        self.type = u'Imperial Fighter'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 15
        self.hull_mass = 10
        self.hull_base_strength = 15 / 1.8
        # Hull of 15, Shield of 15

class EDF63Condor(EDShipLaunchedFighter):
    def __init__(self):
        super(EDF63Condor, self).__init__()
        self.type = u'F63 Condor'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 20
        self.hull_base_strength = 25 / 1.8
        # 50 total: Hull of 25, Shield of 25

class EDTaipanFighter(EDShipLaunchedFighter):
    def __init__(self):
        super(EDTaipanFighter, self).__init__()
        self.type = u'Taipan Fighter'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 22
        self.hull_base_strength = 45 / 1.8
        # Hull of 45, Shield of 30

class EDTrident(EDShipLaunchedFighter):
    def __init__(self):
        super(EDTrident, self).__init__()
        self.type = u'Trident'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 20
        self.hull_base_strength = 10 / 1.8

class EDJavelin(EDShipLaunchedFighter):
    def __init__(self):
        super(EDJavelin, self).__init__()
        self.type = u'Javelin'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 20
        self.hull_base_strength = 10 / 1.8

class EDLance(EDShipLaunchedFighter):
    def __init__(self):
        super(EDLance, self).__init__()
        self.type = u'Lance'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 20
        self.hull_base_strength = 10 / 1.8

class EDSurfaceVehicle(EDVehicle):
    def __init__(self):
        super(EDSurfaceVehicle, self).__init__()

    def supports_slf(self):
        return False

    def supports_srv(self):
        return False

class EDSRVScorpion(EDSurfaceVehicle):
    def __init__(self):
        super(EDSRVScorpion, self).__init__()
        self.type = u'SRV Scorpion'
        self.size = EDVehicleSize.UNKNOWN
        self.seats = 2
        self.shield_base_strength = 130
        self.hull_mass = 30
        self.hull_base_strength = 162 / 1.8

class EDSRVScarab(EDSurfaceVehicle):
    def __init__(self):
        super(EDSRVScarab, self).__init__()
        self.type = u'SRV Scarab'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 4
        self.hull_base_strength = 108 / 1.8

class EDUnknownVehicle(EDVehicle):
    def __init__(self):
        super(EDUnknownVehicle, self).__init__()
        self.type = u'Unknown'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDCrewUnknownVehicle(EDVehicle):
    def __init__(self):
        super(EDCrewUnknownVehicle, self).__init__()
        self.type = u'Unknown (crew)'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDCaptainUnknownVehicle(EDVehicle):
    def __init__(self):
        super(EDCaptainUnknownVehicle, self).__init__()
        self.type = u'Unknown (captain)'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDVehicleFactory(object):
    __vehicle_classes = {
        "sidewinder": EDSidewinder,
        "eagle": EDEagle,
        "hauler": EDHauler,
        "adder": EDAdder,
        "adder_taxi": EDAdderApex,
        "viper": EDViperMkIII,
        "cobramkiii": EDCobraMkIII,
        "type6": EDT6Transporter,
        "dolphin": EDDolphin,
        "type7": EDT7Transporter,
        "type8": EDT8Transporter,
        "asp": EDAspExplorer,
        "vulture": EDVulture,
        "vulture_taxi": EDVultureFrontlines,
        "empire_trader": EDImperialClipper,
        "federation_dropship": EDFederalDropship,
        "orca": EDOrca,
        "type9": EDT9Heavy,
        "type9_military": EDT10Defender,
        "python": EDPython,
        "python_nx": EDPythonMkII,
        "belugaliner": EDBelugaLiner,
        "ferdelance": EDFerDeLance,
        "anaconda": EDAnaconda,
        "federation_corvette": EDFederalCorvette,
        "cutter": EDImperialCutter,
        "diamondback": EDDiamondbackScout,
        "empire_courier": EDImperialCourier,
        "diamondbackxl": EDDiamondbackExplorer,
        "empire_eagle": EDImperialEagle,
        "federation_dropship_mkii": EDFederalAssaultShip,
        "federation_gunship": EDFederalGunship,
        "viper_mkiv": EDViperMkIV,
        "cobramkiv": EDCobraMkIV,
        "independant_trader": EDKeelback,
        "asp_scout": EDAspScout,
        "typex": EDAllianceChieftain,
        "typex_2": EDAllianceCrusader,
        "typex_3": EDAllianceChallenger,
        "krait_mkii": EDKraitMkII,
        "krait_light": EDKraitPhantom, 
        "mamba": EDMamba,
        "mandalay": EDMandalay,
        "empire_fighter": EDImperialFighter,
        "federation_fighter": EDF63Condor,
        "independent_fighter" : EDTaipanFighter,
        "gdn_hybrid_fighter_v1": EDTrident,
        "gdn_hybrid_fighter_v2": EDJavelin,
        "gdn_hybrid_fighter_v3": EDLance,
        "testbuggy": EDSRVScarab,
        "combat_multicrew_srv_01": EDSRVScorpion,
        "unknown": EDUnknownVehicle,
        "unknown (taxi)": EDTaxi,
        "unknown (crew)": EDCrewUnknownVehicle,
        "unknown (captain)": EDCaptainUnknownVehicle
    }

    CANONICAL_SHIP_NAMES = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'shipnames.json')).read())
    CANONICAL_MODULE_NAMES = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'modulenames.json'), encoding="utf-8", errors='ignore').read())

    @staticmethod
    def canonicalize(name):
        if name is None:
            return u"Unknown" # Note: this shouldn't be translated

        if name in EDVehicleFactory.CANONICAL_SHIP_NAMES.values():
            return name # Already canonical

        if name.lower() in EDVehicleFactory.CANONICAL_SHIP_NAMES:
            return EDVehicleFactory.CANONICAL_SHIP_NAMES[name.lower()]

        return name.lower()

    @staticmethod
    def normalize_module_name(name):
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
        if name is None:
            return u"Unknown" # Note: this shouldn't be translated

        if name in EDVehicleFactory.CANONICAL_MODULE_NAMES.values():
            return name # Already canonical

        normalized = EDVehicleFactory.normalize_module_name(name)
        if normalized in EDVehicleFactory.CANONICAL_MODULE_NAMES:
            return (EDVehicleFactory.CANONICAL_MODULE_NAMES[normalized]["name"], EDVehicleFactory.CANONICAL_MODULE_NAMES[normalized]["shortname"])

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
        if name is None:
            return {}

        normalized = EDVehicleFactory.normalize_module_name(name)
        if normalized not in EDVehicleFactory.CANONICAL_MODULE_NAMES:
            return {}
        return EDVehicleFactory.CANONICAL_MODULE_NAMES[normalized].get("tags", {})

    @staticmethod
    def from_edmc_state(state):
        name = state.get('ShipType', None)

        if name is None:
            name = 'unknown'

        vehicle_class = EDVehicleFactory.__vehicle_classes.get(name.lower(), None)
        if vehicle_class is None:
            EDRLOG.log("The requested vehicle has not been implemented: {}".format(name), "ERROR")
            vehicle_class = EDUnknownVehicle
        
        vehicle = vehicle_class()
        vehicle.id = state.get('ShipID', None)
        vehicle.identity = state.get('ShipIdent', None)
        vehicle.name = state.get('ShipName', None)
        vehicle.hull_value = state.get('HullValue', None)
        vehicle.rebuy = state.get('Rebuy', None)

        modules = state.get('Modules', None)
        if modules:
            vehicle.update_from_modules_edmc(modules)
        return vehicle

    @staticmethod
    def from_internal_name(internal_name):
        return EDVehicleFactory.__vehicle_classes.get(internal_name.lower(), EDUnknownVehicle)()

    
    @staticmethod
    def from_loadgame_or_loadout_event(event):
        vehicle = EDVehicleFactory.from_internal_name(event.get("Ship", 'unknown'))
        vehicle.id = event.get('ShipID', None)
        vehicle.identity = event.get('ShipIdent', None)
        vehicle.name = event.get('ShipName', None)
        vehicle.hull_health = event.get('HullHealth', 0) * 100.0 # normalized to 0.0 ... 1.0
        fuel_capacity = event.get('FuelCapacity', None)
        vehicle.fuel_capacity = fuel_capacity
        if fuel_capacity:
            try:
                vehicle.fuel_capacity = fuel_capacity["Main"]
            except:
                pass
        vehicle.fuel_level = event.get('FuelLevel', None)
        vehicle.max_jump_range = event.get("MaxJumpRange", None)

        if not 'Modules' in event:
            return vehicle

        modules = event['Modules']
        for module in modules:
            health = modules[module]['Health'] * 100.0 if 'Health' in modules[module] else None 
            vehicle.subsystem_health(modules[module].get('Item', None), health)
        return vehicle
    
    @staticmethod
    def from_load_game_event(event):
        vehicle = EDVehicleFactory.from_internal_name(event.get("Ship", 'unknown'))
        vehicle.id = event.get('ShipID', None)
        vehicle.identity = event.get('ShipIdent', None)
        vehicle.name = event.get('ShipName', None)
        fuel_capacity = event.get('FuelCapacity', None)
        vehicle.fuel_capacity = fuel_capacity
        if fuel_capacity:
            try:
                vehicle.fuel_capacity = fuel_capacity["Main"]
            except:
                pass
        vehicle.fuel_level = event.get('FuelLevel', None)
        return vehicle

    @staticmethod
    def from_loadout_event(event):
        vehicle = EDVehicleFactory.from_internal_name(event.get("Ship", 'unknown'))
        vehicle.id = event.get('ShipID', None)
        vehicle.identity = event.get('ShipIdent', None)
        vehicle.name = event.get('ShipName', None)
        vehicle.hull_health = event.get('HullHealth', 0) * 100.0 # normalized to 0.0 ... 1.0
        fuel_capacity = event.get('FuelCapacity', None)
        vehicle.fuel_capacity = fuel_capacity
        if fuel_capacity:
            try:
                vehicle.fuel_capacity = fuel_capacity["Main"]
            except:
                pass
        vehicle.fuel_level = event.get('FuelLevel', None) #missing from loadout event...
        vehicle.max_jump_range = event.get("MaxJumpRange", None)
        if not 'Modules' in event:
            return vehicle

        modules = event['Modules']
        for module in modules:
            health = modules[module]['Health'] * 100.0 if 'Health' in modules[module] else None 
            vehicle.subsystem_health(modules[module].get('Item', None), health)
        return vehicle

    @staticmethod
    def from_stored_ship(ship_info):
        vehicle = EDVehicleFactory.from_internal_name(ship_info.get("ShipType", 'unknown'))
        vehicle.id = ship_info.get('ShipID', None)
        vehicle.name = ship_info.get('Name', None)
        vehicle.value = ship_info.get('Value', None)
        vehicle.hot = ship_info.get('Hot', None)
        return vehicle

    @staticmethod
    def is_ship_launched_fighter(vehicle):
        return isinstance(vehicle, EDShipLaunchedFighter)

    @staticmethod
    def is_surface_vehicle(vehicle):
        return isinstance(vehicle, EDSurfaceVehicle)

    @staticmethod
    def unknown_vehicle():
        return EDUnknownVehicle()

    @staticmethod
    def unknown_taxi():
        return EDTaxi()
    
    @staticmethod
    def unknown_crew_vehicle():
        return EDCrewUnknownVehicle()

    @staticmethod
    def default_srv():
        return EDSRVScarab()

    @staticmethod
    def unknown_slf():
        return EDShipLaunchedFighter()

    @staticmethod
    def apex_taxi(entry=None):
        vehicle = EDAdderApex()
        if entry and entry.get("event", None) == "BookTaxi":
            vehicle.bound_for(entry.get("DestinationSystem", None), entry.get("DestinationLocation", None))
        return vehicle

    @staticmethod
    def frontlines_dropship(entry=None):
        vehicle = EDVultureFrontlines()
        if entry and entry.get("event", None) == "BookDropship":
            vehicle.bound_for(entry.get("DestinationSystem", None), entry.get("DestinationLocation", None))
        return vehicle

    @staticmethod
    def unknown_slf():
        return EDShipLaunchedFighter()
