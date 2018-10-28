import os
import json
from edtime import EDTime
import edrconfig

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
        self.fight = {"value": False, "large": False, "timestamp": now}
        self.hardpoints_deployed = {"value": False, "timestamp": now}
        self._attacked = {"value": False, "timestamp": now}
        self.heat_damaged = {"value": False, "timestamp": now}
        self.in_danger = {"value": False, "timestamp": now}
        config = edrconfig.EDRConfig()
        self.fight_staleness_threshold = config.instance_fight_staleness_threshold()
        
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

    # TODO transform pyhton timestamp to js timestamp * 1000
    def json(self):
        return {
            "timestamp": int(self.timestamp * 1000),
            "type": self.type,
            "hull_health": self.__js_t_v(self._hull_health),
            "shield_health": self.__js_t_v(self._shield_health),
            "modules": self.key_subsystems()
        }

    def __js_t_v(self, t_v):
        result = t_v
        result["timestamp"] = int(result["timestamp"]*1000)
        return t_v

    def key_subsystems(self):
        key_prefixes_lut = {
            "int_engine_": "thrusters",
            "int_hyperdrive_": "fsd",
            "int_powerdistributor_": "power distributor",

        }
        #  u'diamondbackxl_cockpit': 1.0
        #  u'int_powerdistributor_size4_class5': 1.0, 
        # 'int_shieldgenerator_size4_class3_fast': 0.995536,
        #  u'int_sensors_size3_class2': 0.980392, 
        # u'int_buggybay_size2_class2': 1.0, 
        # u'int_powerplant_size4_class5': 1.0, 
        # u'int_fuelscoop_size4_class5': 1.0, 
        # u'int_detailedsurfacescanner_tiny': 1.0, 
        # u'nameplate_combat02_white': 1.0, 
        # u'int_planetapproachsuite': 1.0,
        #  u'hpt_shieldbooster_size0_class1': 0.964773,
        #  u'int_stellarbodydiscoveryscanner_advanced': 0.9875,
        #  u'int_dockingcomputer_standard': 1.0, 
        # u'voicepack_verity': 1.0,
        #  u'decal_powerplay_mahon': 1.0,
        #  u'int_fueltank_size5_class3': 1.0,
        #  u'bobble_pilotmale': 1.0, 
        # u'nameplate_shipid_white': 1.0
        key_subsys = {}
        for internal_name in self.subsystems:
            if internal_name not in key_subsystems_lut:
                continue
            canonical_name = key_prefixes_lut[internal_name]
            key_subsys[canonical_name] = self.subsystems[internal_name]
        return key_subsys

    def __repr__(self):
        return str(self.__dict__)

    def reset(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = 100.0
        self.shield_health = 100.0
        self.shield_up = True
        self.subsystems = {}
        self.fight = {"value": False, "large": False, "timestamp": now}
        self.hardpoints_deployed = {"value": False, "timestamp": now}
        self._attacked = {"value": False, "timestamp": now}
        self.heat_damaged = {"value": False, "timestamp": now}
        self.in_danger = {"value": False, "timestamp": now}
    
    def destroy(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = 0.0

    def cockpit_breached(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        # TODO canopy is not canopy...
        self.subsystem_health("canopy", 0.0)

    def taking_hull_damage(self, remaining_health):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.hull_health = remaining_health

    def taking_heat_damage(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.heat_damaged = {"value": True, "timestamp": now}        

    def subsystem_health(self, subsystem, health):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        if subsystem is None:
            return
        self.subsystems[subsystem] = {"timestamp": now, "value": health * 100}

    def needs_large_landing_pad(self):
        return self.size in [EDVehicleSize.LARGE, EDVehicleSize.UNKNOWN]

    def supports_slf(self):
        return False

    def supports_srv(self):
        return True

    def attacked(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._attacked = {"value": True, "timestamp": now}

    def safe(self):
        now = EDTime.py_epoch_now()
        self._attacked = {"value": False, "timestamp": now}
        self.fight = {"value": False, "large": False, "timestamp": now}
        self.in_danger = {"value": False, "timestamp": now}
    
    def unsafe(self):
        now = EDTime.py_epoch_now()
        self.in_danger = {"value": True, "timestamp": now}

    def hardpoints(self, deployed):
        self.hardpoints_deployed = {"value": deployed, "timestamp": EDTime.py_epoch_now()}

    def shield_state(self, is_up):
        # TODO should we be trying to do some heuristics with that?
        self.shield_health = 0.0
        self.shield_up = is_up

    def skirmish(self):
        now = EDTime.py_epoch_now()
        self.fight = {"value": True, "large": False, "timestamp": now}

    def battle(self):
        now = EDTime.py_epoch_now()
        self.fight = {"value": True, "large": True, "timestamp": now}

    def in_a_fight(self):
        if self.fight["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self.fight["timestamp"]) and ((now - self.fight["timestamp"]) <= self.fight_staleness_threshold)
        return False

    def under_attack(self):
        # TODO have every inputs update a last attack timestamp instead of scouring around grabbing timestamps
        '''
        timestamps = []
        if self.fight["value"]:

        
        now = EDTime.py_epoch_now()
        return (now >= self.fight["timestamp"]) and ((now - self.fight["timestamp"]) <= self.fight_staleness_threshold)
        '''

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

class EDVulture(EDVehicle):
    def __init__(self):
        super(EDVulture, self).__init__()
        self.type = u'Vulture'
        self.size = EDVehicleSize.SMALL

class EDImperialClipper(EDVehicle):
    def __init__(self):
        super(EDImperialClipper, self).__init__()
        self.type = u'Imperial Clipper'
        self.size = EDVehicleSize.LARGE

class EDFederalDropship(EDVehicle):
    def __init__(self):
        super(EDFederalDropship, self).__init__()
        self.type = u'Federal Dropship'
        self.size = EDVehicleSize.MEDIUM

class EDOrca(EDVehicle):
    def __init__(self):
        super(EDOrca, self).__init__()
        self.type = u'Orca'
        self.size = EDVehicleSize.LARGE

class EDT9Heavy(EDVehicle):
    def __init__(self):
        super(EDT9Heavy, self).__init__()
        self.type = u'Type-9 Heavy'
        self.size = EDVehicleSize.LARGE

    def supports_slf(self):
        return True

class EDT10Defender(EDVehicle):
    def __init__(self):
        super(EDT10Defender, self).__init__()
        self.type = u'Type-10 Defender'
        self.size = EDVehicleSize.LARGE
    
    def supports_slf(self):
        return True

class EDPython(EDVehicle):
    def __init__(self):
        super(EDPython, self).__init__()
        self.type = u'Python'
        self.size = EDVehicleSize.MEDIUM
    
class EDBelugaLiner(EDVehicle):
    def __init__(self):
        super(EDBelugaLiner, self).__init__()
        self.type = u'Beluga Liner'
        self.size = EDVehicleSize.LARGE

    def supports_slf(self):
        return True

class EDFerDeLance(EDVehicle):
    def __init__(self):
        super(EDFerDeLance, self).__init__()
        self.type = u'Fer-de-Lance'
        self.size = EDVehicleSize.MEDIUM

class EDAnaconda(EDVehicle):
    def __init__(self):
        super(EDAnaconda, self).__init__()
        self.type = u'Anaconda'
        self.size = EDVehicleSize.LARGE

    def supports_slf(self):
        return True

class EDFederalCorvette(EDVehicle):
    def __init__(self):
        super(EDFederalCorvette, self).__init__()
        self.type = u'Federal Corvette'
        self.size = EDVehicleSize.LARGE
    
    def supports_slf(self):
        return True

class EDImperialCutter(EDVehicle):
    def __init__(self):
        super(EDImperialCutter, self).__init__()
        self.type = u'Imperial Cutter'
        self.size = EDVehicleSize.LARGE

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

class EDFederalGunship(EDVehicle):
    def __init__(self):
        super(EDFederalGunship, self).__init__()
        self.type = u'Federal Gunship'
        self.size = EDVehicleSize.MEDIUM

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

class EDKeelback(EDVehicle):
    def __init__(self):
        super(EDKeelback, self).__init__()
        self.type = u'Keelback'
        self.size = EDVehicleSize.MEDIUM

    def supports_slf(self):
        return True

class EDAspScout(EDVehicle):
    def __init__(self):
        super(EDAspScout, self).__init__()
        self.type = u'Asp Scout'
        self.size = EDVehicleSize.MEDIUM

class EDAllianceChieftain(EDVehicle):
    def __init__(self):
        super(EDAllianceChieftain, self).__init__()
        self.type = u'Alliance Chieftain'
        self.size = EDVehicleSize.MEDIUM

class EDAllianceCrusader(EDVehicle):
    def __init__(self):
        super(EDAllianceCrusader, self).__init__()
        self.type = u'Alliance Crusader'
        self.size = EDVehicleSize.MEDIUM

    def supports_slf(self):
        return True

class EDAllianceChallenger(EDVehicle):
    def __init__(self):
        super(EDAllianceChallenger, self).__init__()
        self.type = u'Alliance Challenger'
        self.size = EDVehicleSize.MEDIUM

class EDKraitMkII(EDVehicle):
    def __init__(self):
        super(EDKraitMkII, self).__init__()
        self.type = u'Krait Mk II'
        self.size = EDVehicleSize.MEDIUM

    def supports_slf(self):
        return True

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
                vehicle.subsystem_health(modules[module].get('Item', None), modules[module].get('Health', None))

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
