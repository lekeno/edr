import re
import os
import json
from edtime import EDTime
import edrconfig
import edrlog
EDRLOG = edrlog.EDRLog()

class EDVehicleAttitude(object):
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
        self.rebuy = 0
        now = EDTime.py_epoch_now()
        self._hull_health = {"timestamp": now, "value": 100.0}
        self._shield_health = {"timestamp": now, "value": 100.0}
        self.shield_up = True
        self.subsystems = {}
        self.timestamp = now
        self.fight = {u"value": False, "large": False, u"timestamp": now}
        self._hardpoints_deployed = {u"value": False, u"timestamp": now}
        self._attacked = {u"value": False, u"timestamp": now}
        self.heat_damaged = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        self._low_fuel = {u"value": False, u"timestamp": now}
        config = edrconfig.EDRConfig()
        self.fight_staleness_threshold = config.instance_fight_staleness_threshold()
        self.danger_staleness_threshold = config.instance_danger_staleness_threshold()
        self.seats = 1
        self.fuel_capacity = None
        self.fuel_level = None
        self.attitude = EDVehicleAttitude()
        
    @property
    def hull_health(self):
        return self._hull_health["value"]

    @hull_health.setter
    def hull_health(self, new_value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._hull_health = {"timestamp": now, "value": new_value}

    @property
    def shield_health(self):
        return self._shield_health["value"]
    
    @shield_health.setter
    def shield_health(self, new_value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._shield_health = {"timestamp": now, "value": new_value}

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
        result = {
            u"timestamp": int(self.timestamp * 1000),
            u"type": self.type,
            u"hullHealth": self.__js_t_v(self._hull_health),
            u"shieldHealth": self.__js_t_v(self._shield_health),
            u"shieldUp": self.shield_up,
            u"keySubsystems": self.__key_subsystems()
        }
        if fuel_info:
            result[u"fuelLevel"] = self.fuel_level
            result[u"fuelCapacity"] = self.fuel_capacity
            result[u"lowFuel"] = self.low_fuel

        return result

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
                key_subsys[canonical_name] = self.subsystems[internal_name]
                key_subsys[canonical_name]["timestamp"] *= 1000
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
        modules = event['Modules']
        for module in modules:
            health = modules[module]['Health'] * 100.0 if 'Health' in modules[module] else None 
            self.subsystem_health(modules[module].get('Item', None), health)

    def update_attitude(self, attitude):
        self.attitude.update(attitude)

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

    def subsystem_health(self, subsystem, health):
        if subsystem is None:
            return
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.subsystems[canonical] = {u"timestamp": now, u"value": health}

    def add_subsystem(self, subsystem):
        if not subsystem:
            return
        canonical = EDVehicleFactory.normalize_module_name(subsystem)
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.subsystems[canonical] = {u"timestamp": now, u"value": None}
    
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
        except:
            pass

    def needs_large_landing_pad(self):
        return self.size in [EDVehicleSize.LARGE, EDVehicleSize.UNKNOWN]

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

class EDHauler(EDVehicle):
    def __init__(self):
        super(EDHauler, self).__init__()
        self.type = u'Hauler'
        self.size = EDVehicleSize.SMALL

class EDEagle(EDVehicle):
    def __init__(self):
        super(EDEagle, self).__init__()
        self.type = u'Eagle'
        self.size = EDVehicleSize.SMALL

class EDAdder(EDVehicle):
    def __init__(self):
        super(EDAdder, self).__init__()
        self.type = u'Adder'
        self.size = EDVehicleSize.SMALL
        self.seats = 2

class EDViperMkIII(EDVehicle):
    def __init__(self):
        super(EDViperMkIII, self).__init__()
        self.type = u'Viper Mk III'
        self.size = EDVehicleSize.SMALL

class EDCobraMkIII(EDVehicle):
    def __init__(self):
        super(EDCobraMkIII, self).__init__()
        self.type = u'Cobra Mk III'
        self.size = EDVehicleSize.SMALL
        self.seats = 2

class EDT6Transporter(EDVehicle):
    def __init__(self):
        super(EDT6Transporter, self).__init__()
        self.type = u'Type-6 Transporter'
        self.size = EDVehicleSize.MEDIUM

class EDDolphin(EDVehicle):
    def __init__(self):
        super(EDDolphin, self).__init__()
        self.type = u'Dolphin'
        self.size = EDVehicleSize.SMALL

class EDT7Transporter(EDVehicle):
    def __init__(self):
        super(EDT7Transporter, self).__init__()
        self.type = u'Type-7 Transporter'
        self.size = EDVehicleSize.LARGE

class EDAspExplorer(EDVehicle):
    def __init__(self):
        super(EDAspExplorer, self).__init__()
        self.type = u'Asp Explorer'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDVulture(EDVehicle):
    def __init__(self):
        super(EDVulture, self).__init__()
        self.type = u'Vulture'
        self.size = EDVehicleSize.SMALL
        self.seats = 2

class EDImperialClipper(EDVehicle):
    def __init__(self):
        super(EDImperialClipper, self).__init__()
        self.type = u'Imperial Clipper'
        self.size = EDVehicleSize.LARGE
        self.seats = 2

class EDFederalDropship(EDVehicle):
    def __init__(self):
        super(EDFederalDropship, self).__init__()
        self.type = u'Federal Dropship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDOrca(EDVehicle):
    def __init__(self):
        super(EDOrca, self).__init__()
        self.type = u'Orca'
        self.size = EDVehicleSize.LARGE
        self.seats = 2

class EDT9Heavy(EDVehicle):
    def __init__(self):
        super(EDT9Heavy, self).__init__()
        self.type = u'Type-9 Heavy'
        self.size = EDVehicleSize.LARGE
        self.seats = 3

    def supports_slf(self):
        return True

class EDT10Defender(EDVehicle):
    def __init__(self):
        super(EDT10Defender, self).__init__()
        self.type = u'Type-10 Defender'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
    
    def supports_slf(self):
        return True

class EDPython(EDVehicle):
    def __init__(self):
        super(EDPython, self).__init__()
        self.type = u'Python'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
    
class EDBelugaLiner(EDVehicle):
    def __init__(self):
        super(EDBelugaLiner, self).__init__()
        self.type = u'Beluga Liner'
        self.size = EDVehicleSize.LARGE
        self.seats = 3

    def supports_slf(self):
        return True

class EDFerDeLance(EDVehicle):
    def __init__(self):
        super(EDFerDeLance, self).__init__()
        self.type = u'Fer-de-Lance'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDAnaconda(EDVehicle):
    def __init__(self):
        super(EDAnaconda, self).__init__()
        self.type = u'Anaconda'
        self.size = EDVehicleSize.LARGE
        self.seats = 3

    def supports_slf(self):
        return True

class EDFederalCorvette(EDVehicle):
    def __init__(self):
        super(EDFederalCorvette, self).__init__()
        self.type = u'Federal Corvette'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
    
    def supports_slf(self):
        return True

class EDImperialCutter(EDVehicle):
    def __init__(self):
        super(EDImperialCutter, self).__init__()
        self.type = u'Imperial Cutter'
        self.size = EDVehicleSize.LARGE
        self.seats = 3

    def supports_slf(self):
        return True

class EDDiamondbackScout(EDVehicle):
    def __init__(self):
        super(EDDiamondbackScout, self).__init__()
        self.type = u'Diamondback Scout'
        self.size = EDVehicleSize.SMALL

class EDImperialCourier(EDVehicle):
    def __init__(self):
        super(EDImperialCourier, self).__init__()
        self.type = u'Imperial Courier'
        self.size = EDVehicleSize.SMALL

class EDDiamondbackExplorer(EDVehicle):
    def __init__(self):
        super(EDDiamondbackExplorer, self).__init__()
        self.type = u'Diamondback Explorer'
        self.size = EDVehicleSize.SMALL

class EDImperialEagle(EDVehicle):
    def __init__(self):
        super(EDImperialEagle, self).__init__()
        self.type = u'Imperial Eagle'
        self.size = EDVehicleSize.SMALL

class EDFederalAssaultShip(EDVehicle):
    def __init__(self):
        super(EDFederalAssaultShip, self).__init__()
        self.type = u'Federal Assault Ship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDFederalGunship(EDVehicle):
    def __init__(self):
        super(EDFederalGunship, self).__init__()
        self.type = u'Federal Gunship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

    def supports_slf(self):
        return True

class EDViperMkIV(EDVehicle):
    def __init__(self):
        super(EDViperMkIV, self).__init__()
        self.type = u'Viper Mk IV'
        self.size = EDVehicleSize.SMALL

class EDCobraMkIV(EDVehicle):
    def __init__(self):
        super(EDCobraMkIV, self).__init__()
        self.type = u'Cobra Mk IV'
        self.size = EDVehicleSize.SMALL
        self.seats = 2

class EDKeelback(EDVehicle):
    def __init__(self):
        super(EDKeelback, self).__init__()
        self.type = u'Keelback'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

    def supports_slf(self):
        return True

class EDAspScout(EDVehicle):
    def __init__(self):
        super(EDAspScout, self).__init__()
        self.type = u'Asp Scout'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDAllianceChieftain(EDVehicle):
    def __init__(self):
        super(EDAllianceChieftain, self).__init__()
        self.type = u'Alliance Chieftain'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDAllianceChallenger(EDVehicle):
    def __init__(self):
        super(EDAllianceChallenger, self).__init__()
        self.type = u'Alliance Challenger'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDAllianceCrusader(EDVehicle):
    def __init__(self):
        super(EDAllianceCrusader, self).__init__()
        self.type = u'Alliance Crusader'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 3

    def supports_slf(self):
        return True

class EDKraitMkII(EDVehicle):
    def __init__(self):
        super(EDKraitMkII, self).__init__()
        self.type = u'Krait Mk II'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 3

    def supports_slf(self):
        return True

class EDKraitPhantom(EDVehicle):
    def __init__(self):
        super(EDKraitPhantom, self).__init__()
        self.type = u'Krait Phantom'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

class EDMamba(EDVehicle):
    def __init__(self):
        super(EDMamba, self).__init__()
        self.type = u'Mamba'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2

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

class EDF63Condor(EDShipLaunchedFighter):
    def __init__(self):
        super(EDF63Condor, self).__init__()
        self.type = u'F63 Condor'
        self.size = EDVehicleSize.UNKNOWN

class EDTaipanFighter(EDShipLaunchedFighter):
    def __init__(self):
        super(EDTaipanFighter, self).__init__()
        self.type = u'Taipan Fighter'
        self.size = EDVehicleSize.UNKNOWN

class EDTrident(EDShipLaunchedFighter):
    def __init__(self):
        super(EDTrident, self).__init__()
        self.type = u'Trident'
        self.size = EDVehicleSize.UNKNOWN

class EDJavelin(EDShipLaunchedFighter):
    def __init__(self):
        super(EDJavelin, self).__init__()
        self.type = u'Javelin'
        self.size = EDVehicleSize.UNKNOWN

class EDLance(EDShipLaunchedFighter):
    def __init__(self):
        super(EDLance, self).__init__()
        self.type = u'Lance'
        self.size = EDVehicleSize.UNKNOWN

class EDSurfaceVehicle(EDVehicle):
    def __init__(self):
        super(EDSurfaceVehicle, self).__init__()

    def supports_slf(self):
        return False

    def supports_srv(self):
        return False

class EDSRV(EDSurfaceVehicle):
    def __init__(self):
        super(EDSRV, self).__init__()
        self.type = u'SRV'
        self.size = EDVehicleSize.UNKNOWN

class EDUnknownVehicle(EDVehicle):
    def __init__(self):
        super(EDUnknownVehicle, self).__init__()
        self.type = u'Unknown'
        self.size = EDVehicleSize.UNKNOWN

class EDCrewUnknownVehicle(EDVehicle):
    def __init__(self):
        super(EDCrewUnknownVehicle, self).__init__()
        self.type = u'Unknown (crew)'
        self.size = EDVehicleSize.UNKNOWN

class EDCaptainUnknownVehicle(EDVehicle):
    def __init__(self):
        super(EDCaptainUnknownVehicle, self).__init__()
        self.type = u'Unknown (captain)'
        self.size = EDVehicleSize.UNKNOWN

class EDVehicleFactory(object):
    __vehicle_classes = {
        "sidewinder": EDSidewinder,
        "eagle": EDEagle,
        "hauler": EDHauler,
        "adder": EDAdder,
        "viper": EDViperMkIII,
        "cobramkiii": EDCobraMkIII,
        "type6": EDT6Transporter,
        "dolphin": EDDolphin,
        "type7": EDT7Transporter,
        "asp": EDAspExplorer,
        "vulture": EDVulture,
        "empire_trader": EDImperialClipper,
        "federation_dropship": EDFederalDropship,
        "orca": EDOrca,
        "type9": EDT9Heavy,
        "type9_military": EDT10Defender,
        "python": EDPython,
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
        "empire_fighter": EDImperialFighter,
        "federation_fighter": EDF63Condor,
        "independent_fighter" : EDTaipanFighter,
        "gdn_hybrid_fighter_v1": EDTrident,
        "gdn_hybrid_fighter_v2": EDJavelin,
        "gdn_hybrid_fighter_v3": EDLance,
        "testbuggy": EDSRV,
        "unknown": EDUnknownVehicle,
        "unknown (crew)": EDCrewUnknownVehicle,
        "unknown (captain)": EDCaptainUnknownVehicle
    }

    CANONICAL_SHIP_NAMES = json.loads(open(os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'data/shipnames.json')).read())

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
    def from_edmc_state(state):
        name = state.get('ShipType', None)

        if name is None:
            name = 'unknown'

        vehicle_class = EDVehicleFactory.__vehicle_classes.get(name.lower(), None)
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

    @staticmethod
    def from_internal_name(internal_name):
        return EDVehicleFactory.__vehicle_classes.get(internal_name.lower(), EDUnknownVehicle)()

    @staticmethod
    def from_load_game_event(event):
        vehicle = EDVehicleFactory.from_internal_name(event.get("Ship", 'unknown'))
        vehicle.id = event.get('ShipID', None)
        vehicle.identity = event.get('ShipIdent', None)
        vehicle.name = event.get('ShipName', None)
        vehicle.fuel_capacity = event.get('FuelCapacity', None)
        vehicle.fuel_level = event.get('FuelLevel', None)
        return vehicle

    @staticmethod
    def from_loadout_event(event):
        vehicle = EDVehicleFactory.from_internal_name(event.get("Ship", 'unknown'))
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
    def is_ship_launched_fighter(vehicle):
        return isinstance(vehicle, EDShipLaunchedFighter)

    @staticmethod
    def is_surface_vehicle(vehicle):
        return isinstance(vehicle, EDSurfaceVehicle)

    @staticmethod
    def unknown_vehicle():
        return EDUnknownVehicle()

    @staticmethod
    def default_srv():
        return EDSRV()

    @staticmethod
    def unknown_slf():
        return EDShipLaunchedFighter()
