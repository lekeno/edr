import re
import json
from math import log10
import os

from edr.utils.edtime import EDTime
from edr.core.edrconfig import EDR_CONFIG
from .edrhitppoints import EDRHitPPoints
from .edmodule import EDModule, EDResistances
from .edmodulesinforeader import EDModulesInfoReader
from .edcargoreader import EDCargoReader
from edr.core.edrlog import EDR_LOG
from .edcargo import EDCargo
from .edshield import EDPowerDistributor, EDShieldGenerator, EDShieldingFactory
from .edarmour import EDHullFactory
from .edweapons import EDWeaponFactory
from edr.utils.edrpath import edr_data_path

class EDVehicleSize:
    """
    Vehicle size constants.
    """
    UNKNOWN = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 4

class EDVehicle:
    """
    Base class for Elite Dangerous vehicles.
    """
    def __init__(self):
        """
        Initialize a vehicle.
        """
        self.type = None
        self.size = None
        self.name = None
        self.id = None
        self.identity = None
        self.rebuy = None
        self._value = None
        self.hot = False
        now = EDTime.py_epoch_now()
        config = EDR_CONFIG
        self._hull_health = EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.hull_mass = 0
        self.hull_hardness = 0
        self.hull_base_strength = 0
        self._shield_health = EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.shield_up = True
        self.shield_base_strength = 0
        self.subsystems = {}
        self.timestamp = now
        self.fight = {"value": False, "large": False, "timestamp": now}
        self._hardpoints_deployed = {"value": False, "timestamp": now}
        self._attacked = {"value": False, "timestamp": now}
        self.heat_damaged = {"value": False, "timestamp": now}
        self._in_danger = {"value": False, "timestamp": now}
        self._low_fuel = {"value": False, "timestamp": now}
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
        self.cargo = EDCargo()
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
        """
        Calculate current hull strength.
        
        Returns:
            float: Hull strength (effective hitpoints).
        """
        strength = self.armour.strength(self.hull_base_strength)
        hrps_bonus = 0
        for h in self.hrps:
            if h.enabled:
                hrps_bonus += h.armour
        
        strength += hrps_bonus
        return strength

    def hull_resistances(self):
        """
        Calculate hull resistances.

        Returns:
            EDResistances: Overall hull resistances.
        """
        thermal = 1.0
        kinetic = 1.0
        explosive = 1.0
        caustic = 1.0

        for h in self.hrps:
            thermal *= (1.0 - h.resistances.thermal)
            kinetic *= (1.0 - h.resistances.kinetic)
            explosive *= (1.0 - h.resistances.explosive)
            caustic *= (1.0 - h.resistances.caustic)
            
        if thermal < 0.7:
            thermal = 0.7 - (0.7 - thermal)/2.0
            
        if kinetic < 0.7:
            kinetic = 0.7 - (0.7 - kinetic)/2.0
            
        if explosive < 0.7:
            explosive = 0.7 - (0.7 - explosive)/2.0
            
        if caustic < 0.7:
            caustic = 0.7 - (0.7 - caustic)/2.0
        
        thermal = (1.0 - self.armour.hull_resistances.thermal) * thermal
        kinetic = (1.0 - self.armour.hull_resistances.kinetic) * kinetic
        explosive = (1.0 - self.armour.hull_resistances.explosive) * explosive
        caustic = (1.0 - self.armour.hull_resistances.caustic) * caustic
        
        overall_resistances = EDResistances()
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
        """
        Calculate shield strength.

        Returns:
            float: Shield strength (raw MJ).
        """
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
        
        return strength

    def effective_shield_strength(self, damage_type="absolute"):
        """
        Calculate effective shield strength for a specific damage type.

        Args:
            damage_type (str): Damage type ('absolute', 'thermal', 'kinetic', 'explosive', 'caustic').

        Returns:
            float: Effective shield strength (MJ).
        """
        raw_mj = self.shield_strength()
        if raw_mj == 0:
            return 0
        
        pip_mitigation = self.distro.sys_resistance()
        
        if damage_type == "absolute":
            return raw_mj / (1.0 - pip_mitigation)
        
        res = self.shield_resistances()
        type_res = getattr(res, damage_type, 0.0)
        
        return raw_mj / ((1.0 - type_res) * (1.0 - pip_mitigation))

    # TODO verify, cor is doing that differently
    def shield_resistances(self):
        """
        Calculate shield resistances.

        Returns:
            EDResistances: Overall shield resistances.
        """
        thermal = 1.0
        kinetic = 1.0
        explosive = 1.0
        caustic = 1.0

        for b in self.boosters:
            thermal *= (1.0 - b.resistances.thermal)
            kinetic *= (1.0 - b.resistances.kinetic)
            explosive *= (1.0 - b.resistances.explosive)
            caustic *= (1.0 - b.resistances.caustic)
            
        if thermal < 0.7:
            thermal = 0.7 - (0.7 - thermal)/2.0
            
        if kinetic < 0.7:
            kinetic = 0.7 - (0.7 - kinetic)/2.0
            
        if explosive < 0.7:
            explosive = 0.7 - (0.7 - explosive)/2.0
            
        if caustic < 0.7:
            caustic = 0.7 - (0.7 - caustic)/2.0
        
        thermal = (1.0 - self.shield_gen.shield_resistances.thermal) * thermal
        kinetic = (1.0 - self.shield_gen.shield_resistances.kinetic) * kinetic
        explosive = (1.0 - self.shield_gen.shield_resistances.explosive) * explosive
        caustic = (1.0 - self.shield_gen.shield_resistances.caustic) * caustic
        
        overall_resistances = EDResistances()
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
        """
        Returns:
            dict: JSON representation of the vehicle status.
        """
        shield_default = 100 if self.whole_loadout and self.has_shield_generator() else -1
        result = {
            "timestamp": int(self.timestamp * 1000),
            "type": self.type,
            "hullHealth": {"timestamp": int(self.timestamp * 1000), "value": 100} if self._hull_health.empty() else self._hull_health.last(),
            "shieldHealth": {"timestamp": int(self.timestamp * 1000), "value": shield_default} if self._shield_health.empty() else self._shield_health.last(),
            "shieldUp": self.shield_up and shield_default != -1,
            "keySubsystems": self.__key_subsystems()
        }
        if fuel_info:
            result["fuelLevel"] = self.fuel_level
            result["fuelCapacity"] = self.fuel_capacity
            result["lowFuel"] = self.low_fuel

        return result

    # TODO adjust all timestamp to ms?
    def __js_t_v(self, t_v):
        """
        Convert timestamp to ms for JSON.
        """
        result = t_v.copy()
        result["timestamp"] = int(t_v["timestamp"] * 1000)
        return result

    def __key_subsystems(self):
        """
        Get key subsystems.

        Returns:
            dict: Key subsystems with status.
        """
        key_prefixes_lut = {
            "drive_": "thrusters",
            "hyperdrive_": "fsd",
            "hyperdrive_overcharge": "fsd (sco)",
            "powerdistributor_": "power distributor",
            "shieldgenerator_": "shield generator",
            "powerplant_": "power plant"
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
        """
        Update vehicle from Loadout event.

        Args:
            event (dict): Loadout event.
        """
        other_id = event.get("ShipID", None)
        from .edshipyard import EDVehicleFactory
        other_type = EDVehicleFactory.canonicalize(event.get("Ship", "unknown")) 

        if other_id != self.id or other_type != self.type:
            EDR_LOG.warning("Mismatch between ID ({} vs {}) and/or Type ({} vs. {}), can't update from loadout".format(self.id, other_id, self.type, other_type))
            return

        self.identity = event.get('ShipIdent', None)
        self.name = event.get('ShipName', None)
        self.hull_health = event.get('HullHealth', None) * 100.0 # normalized to 0.0 ... 1.0
        if 'Modules' not in event:
            return
        self.update_from_modules_dict(event['Modules'])
        self.whole_loadout = True
        self.cargo_capacity = event.get("CargoCapacity", 0)
        self.cargo.update(event)
        self.max_jump_range = event.get("MaxJumpRange", None)

    def update_from_modules_dict(self, modules):
        """
        Update modules from dictionary.

        Args:
            modules (list): List of module dicts.
        """
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
            ed_module = EDModule(module)
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
        """
        Update from EDMC modules data.

        Args:
            modules (dict): Modules data.
        """
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
            ed_module = EDModule(module)
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
        """
        Update modules from modulesinfo.json.

        Returns:
            bool: True if updated.
        """
        reader = EDModulesInfoReader()
        modules_info = reader.process()
        stale = (self.slots_timestamp is None) or (self.module_info_timestamp and (self.slots_timestamp.as_py_epoch() < self.module_info_timestamp.as_py_epoch()))
        if not stale:
            EDR_LOG.debug("Modules info: up-to-date")
            return True

        if not modules_info or not modules_info.get("Modules", None):
            EDR_LOG.debug("No info on modules!")
            return False

        timestamp = EDTime()
        timestamp.from_journal_timestamp(modules_info['timestamp'])
        if self.slots_timestamp and (timestamp.as_py_epoch() < self.slots_timestamp.as_py_epoch() or timestamp.as_py_epoch() < self.module_info_timestamp.as_py_epoch()):
            EDR_LOG.debug("Stale info in modulesinfo.json: {} vs. {})".format(timestamp, self.slots_timestamp))
            return False
        
        EDR_LOG.debug("Trying an update of modules: json@{}, slots@{}, panel looked@{}".format(timestamp, self.slots_timestamp, self.module_info_timestamp))
        updated = self.slots_timestamp is None
        EDR_LOG.debug("This will be our first time with actual info")
        self.slots_timestamp = timestamp
        modules = modules_info.get("Modules", [])
        for module in modules:
            slot_name = module.get("Slot", None)
            if slot_name in self.slots:
                module_updated = self.slots[slot_name].update(module)
                if self.slots[slot_name].power_draw > 0:
                    if module_updated:
                        EDR_LOG.debug("{} in {}: power_draw: {}, priority: {}".format(self.slots[slot_name].cname, slot_name, self.slots[slot_name].power_draw, self.slots[slot_name].priority))
                    updated |= module_updated
            else:
                the_module = EDModule(module)
                self.slots[slot_name] = the_module
                if the_module.power_draw > 0 or the_module.power_generation > 0:
                    EDR_LOG.debug("[New] {} in {}: power_draw: {}, priority: {}".format(self.slots[slot_name].cname, slot_name, self.slots[slot_name].power_draw, self.slots[slot_name].priority))
                updated |= the_module.power_draw > 0 or the_module.power_generation > 0
        self.whole_loadout = True
        return updated

    def update_name(self, event):
        """
        Update vehicle name/identity from event.

        Args:
            event (dict): Journal event.
        """
        other_id = event.get("ShipID", None)
        from .edshipyard import EDVehicleFactory
        other_type = EDVehicleFactory.canonicalize(event.get("Ship", "unknown")) 
        if other_id != self.id or other_type != self.type:
            EDR_LOG.warning(f"Mismatch between ID {self.id} vs {other_id} and/or Type {self.type} vs {other_type}, can't update name/identity")
            return
        self.identity = event.get('UserShipId', None)
        self.name = event.get('UserShipName', None)

    def update_cargo(self):
        """
        Update cargo from cargo.json.
        """
        reader = EDCargoReader()
        cargo = reader.process()
        self.cargo.update(cargo)

    def reset(self):
        """
        Reset vehicle status.
        """
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = 100.0
        self.shield_health = 100.0
        self.shield_up = True
        self.subsystems = {}
        self.fight = {"value": False, "large": False, "timestamp": now}
        self._hardpoints_deployed = {"value": False, "timestamp": now}
        self._attacked = {"value": False, "timestamp": now}
        self.heat_damaged = {"value": False, "timestamp": now}
        self._in_danger = {"value": False, "timestamp": now}
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
        """
        Record vehicle destruction.
        """
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = 0.0

    def cockpit_breached(self):
        """
        Record cockpit breach.
        """
        self.cockpit_health(0.0)

    def cockpit_health(self, value):
        """
        Update cockpit health.

        Args:
            value (float): Health value (0.0-100.0).
        """
        now = EDTime.py_epoch_now()
        self.timestamp = now
        cockpit_suffix = "_cockpit"
        for internal_name in self.subsystems:
            if not internal_name.endswith(cockpit_suffix):
                continue
            self.subsystem_health(internal_name, value)
            break

    def taking_hull_damage(self, remaining_health):
        """
        Update hull health from damage event.

        Args:
            remaining_health (float): Remaining hull health.
        """
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = remaining_health

    def taking_heat_damage(self):
        """
        Record heat damage event.
        """
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.heat_damaged = {"value": True, "timestamp": now}

    def outfit_probably_changed(self, timestamp=None):
        """
        Mark outfit as likely changed.

        Args:
            timestamp (str/int): Optional timestamp.
        """
        edt = EDTime()
        if timestamp:
            edt.from_journal_timestamp(timestamp)
        self.module_info_timestamp = edt


    def subsystem_health(self, subsystem, health):
        """
        Update subsystem health.

        Args:
            subsystem (str): Subsystem name.
            health (float): Health value.
        """
        if subsystem is None:
            return
        from .edshipyard import EDVehicleFactory
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        now = EDTime.ms_epoch_now()
        self.timestamp = now
        if canonical not in self.subsystems:
            config = EDR_CONFIG
            self.subsystems[canonical] = EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.subsystems[canonical].update(health)

    def subsystem_details(self, subsystem):
        """
        Get subsystem details.

        Args:
            subsystem (str): Subsystem name.

        Returns:
            dict: Subsystem details.
        """
        if subsystem is None:
            return
        from .edshipyard import EDVehicleFactory
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        if canonical not in self.subsystems:
            return
        from .edshipyard import EDVehicleFactory
        readable_name, short_name = EDVehicleFactory.readable_module_names(subsystem)
        return {"name": readable_name, "shortname": short_name, "stats": self.subsystems[canonical]}

    def add_subsystem(self, subsystem):
        """
        Add a subsystem.

        Args:
            subsystem (str): Subsystem name.
        """
        if not subsystem:
            return
        from .edshipyard import EDVehicleFactory
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        now = EDTime.ms_epoch_now()
        self.timestamp = now
        self.outfit_probably_changed()
        config = EDR_CONFIG
        self.subsystems[canonical] = EDRHitPPoints(config.hpp_history_max_points(), config.hpp_history_max_span(), config.hpp_trend_span())
        self.subsystems[canonical].update(None)
    
    def remove_subsystem(self, subsystem):
        """
        Remove a subsystem.

        Args:
            subsystem (str): Subsystem name.
        """
        if subsystem is None:
            return
        from .edshipyard import EDVehicleFactory
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
        """
        Returns:
            bool: True if needs large pad.
        """
        return self.size in [EDVehicleSize.LARGE, EDVehicleSize.UNKNOWN]
    
    def needs_medium_landing_pad(self):
        """
        Returns:
            bool: True if needs medium pad.
        """
        return self.size in [EDVehicleSize.MEDIUM, EDVehicleSize.UNKNOWN]

    def supports_slf(self):
        return False

    def supports_srv(self):
        return True

    def supports_crew(self):
        """
        Returns:
            bool: True if supports multicrew.
        """
        return self.seats > 1

    def attacked(self):
        """
        Record being attacked.
        """
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._attacked = {"value": True, "timestamp": now}

    def under_attack(self):
        """
        Returns:
            bool: True if currently under attack (within threshold).
        """
        if self._attacked["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._attacked["timestamp"]) and ((now - self._attacked["timestamp"]) <= self.danger_staleness_threshold)
        return False

    def safe(self):
        """
        Mark as safe (not under attack/in danger).
        """
        now = EDTime.py_epoch_now()
        self._attacked = {"value": False, "timestamp": now}
        self.fight = {"value": False, "large": False, "timestamp": now}
        self._in_danger = {"value": False, "timestamp": now}
    
    def unsafe(self):
        """
        Mark as unsafe (in danger).
        """
        now = EDTime.py_epoch_now()
        self._in_danger = {"value": True, "timestamp": now}

    def in_danger(self):
        """
        Returns:
            bool: True if in danger (within threshold).
        """
        if self._in_danger["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._in_danger["timestamp"]) and ((now - self._in_danger["timestamp"]) <= self.danger_staleness_threshold)
        return False

    def hardpoints(self, deployed):
        """
        Set hardpoints status.

        Args:
            deployed (bool): True if deployed.
        """
        self._hardpoints_deployed = {"value": deployed, "timestamp": EDTime.py_epoch_now()}

    def hardpoints_deployed(self):
        """
        Returns:
            bool: True if hardpoints deployed (within threshold).
        """
        if self._hardpoints_deployed["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._hardpoints_deployed["timestamp"]) and ((now - self._hardpoints_deployed["timestamp"]) <= self.fight_staleness_threshold)
        return False

    def damage_per_shot(self):
        """
        Calculate damage per shot from weapons.

        Returns:
            dict: Damage breakdown by type.
        """
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
        """
        Update shield state.

        Args:
            is_up (bool): True if shield is up.
        """
        if not is_up:
            self.shield_health = 0.0
        self.shield_up = is_up

    def pips(self, values):
        """
        Update power distributor pips.

        Args:
            values (list): Pips configuration.
        """
        return self.distro.update(values)

    def skirmish(self):
        """
        Record skirmish (small fight).
        """
        now = EDTime.py_epoch_now()
        self.fight = {"value": True, "large": False, "timestamp": now}

    def battle(self):
        """
        Record battle (large fight).
        """
        now = EDTime.py_epoch_now()
        self.fight = {"value": True, "large": True, "timestamp": now}

    def in_a_fight(self):
        """
        Returns:
            bool: True if in a fight (within threshold).
        """
        if self.fight["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self.fight["timestamp"]) and ((now - self.fight["timestamp"]) <= self.fight_staleness_threshold)
        return False

    def refuel(self, amount=None):
        """
        Handle refueling event.

        Args:
            amount (float): Amount refueled.
        """
        if amount:
            self.fuel_level = self.fuel_level + amount if self.fuel_level else amount
            if self.fuel_capacity:
                self.low_fuel = self.fuel_level < self.fuel_capacity * .25
        else:
            self.low_fuel = False
            self.fuel_level = self.fuel_capacity

    def fuel_scooping(self, new_level):
        """
        Handle fuel scooping event.

        Args:
            new_level (float): New fuel level.
        """
        self.fuel_level = new_level
        if self.fuel_capacity:
            self.low_fuel = self.fuel_level < self.fuel_capacity * .25

    def repair(self, item=None):
        """
        Handle repair event.

        Args:
            item (str): Optional subsystem to repair.
        """
        if item:
            self.subsystem_health(item, 100.0)
        else:
            self.hull_health = 100.0
            for subsystem in self.subsystems:
                self.subsystem_health(subsystem, 100.0)

    def could_use_limpets(self, mining_only=False):
        """
        Check if vehicle could use limpets.

        Args:
            mining_only (bool): If True, check specifically for mining.

        Returns:
            bool: True if could use limpets.
        """
        if self.cargo_capacity <= 0:
            return False
        
        if mining_only:
            if not self.is_mining_rig():
                return False
        elif not self.has_drone_controller():
            return False

        return  self.cargo.how_many("drones") < self.cargo_capacity

    def is_mining_rig(self):
        """
        Check if vehicle is equipped for mining.

        Returns:
            bool: True if vehicle has mining prospector drone.
        """
        for slot_name in self.slots:
            if self.slots[slot_name].is_prospector_drone_controller():
                return True
        return False


    def has_drone_controller(self):
        """
        Check for drone controller.

        Returns:
            bool: True if vehicle has any drone controller.
        """
        for slot_name in self.slots:
            if self.slots[slot_name].is_drone_controller():
                return True
        return False

    def has_shield_generator(self):
        """
        Check for shield generator.

        Returns:
            bool: True if vehicle has shield generator.
        """
        for slot_name in self.slots:
            if self.slots[slot_name].is_shield():
                return True
        return False
    
    def describe_loadout(self):
        """
        Describe the loadout with tags.

        Returns:
            list: Sorted list of tags describing the loadout.
        """
        weighted_tags = {}
        for internal_name in self.subsystems:
            module_tags = EDVehicle.module_tags(internal_name)
            for tag in module_tags:
                weighted_tags[tag] = module_tags[tag] + weighted_tags.get(tag, 0)

        return sorted(weighted_tags, key=weighted_tags.get, reverse=True)

    def __eq__(self, other):
        """
        Equality check.
        """
        if not isinstance(other, EDVehicle):
            return False
        return self.__dict__ == other.__dict__
        
    def __ne__(self, other):
        """
        Inequality check.
        """
        return not self.__eq__(other)

class EDTaxi(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown (taxi)'
        self.size = EDVehicleSize.UNKNOWN
        self.destination = {"system": None, "location": None}
    
    def bound_for(self, system, location):
        self.destination["system"]= system
        self.destination["location"]= location

class EDShipLaunchedFighter(EDVehicle):
    def __init__(self):
        super().__init__()

    def supports_slf(self):
        return False
    
    def supports_srv(self):
        return False

class EDSurfaceVehicle(EDVehicle):
    def __init__(self):
        super().__init__()

    def supports_slf(self):
        return False

    def supports_srv(self):
        return False

class EDUnknownVehicle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDCrewUnknownVehicle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown (crew)'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDCaptainUnknownVehicle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown (captain)'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

from .edshipyard import *
