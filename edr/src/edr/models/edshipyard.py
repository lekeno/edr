import json
import re
from edr.core.edrlog import EDR_LOG
from edr.utils.edtime import EDTime
from edr.utils.edrpath import edr_data_path
from .edvehicles import EDVehicleSize, EDVehicle, EDTaxi, EDShipLaunchedFighter, EDSurfaceVehicle, EDUnknownVehicle, EDCrewUnknownVehicle, EDCaptainUnknownVehicle

class EDSidewinder(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Sidewinder'
        self.size = EDVehicleSize.SMALL
        self.value = 31000
        self.shield_base_strength = 40
        self.hull_mass = 25
        self.hull_hardness = 35
        self.hull_base_strength = 108 / 1.8

class EDHauler(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Hauler'
        self.size = EDVehicleSize.SMALL
        self.value = 51720
        self.shield_base_strength = 50
        self.hull_mass = 14
        self.hull_hardness = 20
        self.hull_base_strength = 180 / 1.8

class EDEagle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Eagle'
        self.size = EDVehicleSize.SMALL
        self.value = 43800
        self.shield_base_strength = 60
        self.hull_mass = 50
        self.hull_hardness = 20
        self.hull_base_strength = 72 / 1.8

class EDAdder(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Adder'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 86472
        self.shield_base_strength = 60
        self.hull_mass = 35
        self.hull_hardness = 35
        self.hull_base_strength = 162 / 1.8

class EDAdderApex(EDTaxi):
    def __init__(self):
        super().__init__()
        self.type = 'Adder Apex'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 86472
        self.shield_base_strength = 60
        self.hull_mass = 35
        self.hull_hardness = 35
        self.hull_base_strength = 162 / 1.8
    

class EDViperMkIII(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Viper Mk III'
        self.size = EDVehicleSize.SMALL
        self.value = 141592
        self.shield_base_strength = 105
        self.hull_mass = 50
        self.hull_hardness = 35
        self.hull_base_strength = 126 / 1.8

class EDCobraMkIII(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Cobra Mk III'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 346634
        self.shield_base_strength = 80
        self.hull_mass = 180
        self.hull_hardness = 35
        self.hull_base_strength = 216 / 1.8

class EDT6Transporter(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Type-6 Transporter'
        self.size = EDVehicleSize.MEDIUM
        self.value = 1044612
        self.shield_base_strength = 90
        self.hull_mass = 155
        self.hull_hardness = 35
        self.hull_base_strength = 324 / 1.8

class EDDolphin(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Dolphin'
        self.size = EDVehicleSize.SMALL
        self.value = 1334244
        self.shield_base_strength = 110
        self.hull_mass = 140
        self.hull_hardness = 35
        self.hull_base_strength = 198 / 1.8

class EDT7Transporter(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Type-7 Transporter'
        self.size = EDVehicleSize.LARGE
        self.value = 17469174
        self.shield_base_strength = 155
        self.hull_mass = 350
        self.hull_hardness = 54
        self.hull_base_strength = 612 / 1.8

class EDT8Transporter(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Type-8 Transporter'
        self.size = EDVehicleSize.MEDIUM
        self.value = 0 # TODO
        self.shield_base_strength = 122
        self.hull_mass = 400
        self.hull_hardness = 54 # TODO
        self.hull_base_strength = 792 / 1.8

class EDAspExplorer(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Asp Explorer'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 6650520
        self.shield_base_strength = 140
        self.hull_mass = 280
        self.hull_hardness = 52
        self.hull_base_strength = 378 / 1.8

class EDCaspianExplorer(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Caspian Explorer'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 189989758
        self.shield_base_strength = 196 # TODO reconfirm
        self.hull_mass = 950 # TODO reconfirm
        self.hull_hardness = 60 # TODO reconfirm
        self.hull_base_strength = 621 / 1.8 # TODO reconfirm

    def supports_slf(self):
        return True

class EDVulture(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Vulture'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 4922534
        self.shield_base_strength = 240
        self.hull_mass = 230
        self.hull_hardness = 55
        self.hull_base_strength = 288 / 1.8
    
class EDVultureFrontlines(EDTaxi):
    def __init__(self):
        super().__init__()
        self.type = 'Vulture Frontlines'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 4922534
        self.shield_base_strength = 240
        self.hull_mass = 230
        self.hull_hardness = 55
        self.hull_base_strength = 288 / 1.8

class EDImperialClipper(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Imperial Clipper'
        self.size = EDVehicleSize.LARGE
        self.seats = 2
        self.value = 22256248
        self.shield_base_strength = 180
        self.hull_mass = 400
        self.hull_hardness = 60
        self.hull_base_strength = 486 / 1.8

class EDFederalDropship(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Federal Dropship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 14273598
        self.shield_base_strength = 200
        self.hull_mass = 580
        self.hull_hardness = 60
        self.hull_base_strength = 540 / 1.8

class EDOrca(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Orca'
        self.size = EDVehicleSize.LARGE
        self.seats = 2
        self.value = 48529270
        self.shield_base_strength = 220
        self.hull_mass = 290
        self.hull_hardness = 55
        self.hull_base_strength = 396 / 1.8

class EDT9Heavy(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Type-9 Heavy'
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
        super().__init__()
        self.type = 'Type-10 Defender'
        self.size = EDVehicleSize.LARGE
        self.seats = 3
        self.value = 124874411
        self.shield_base_strength = 320
        self.hull_mass = 1200
        self.hull_hardness = 75
        self.hull_base_strength = 1044 / 1.8
    
    def supports_slf(self):
        return True

class EDT11Prospector(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Type-11 Prospector'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 3
        self.value = 67861850
        self.shield_base_strength = 271
        self.hull_mass = 320
        self.hull_hardness = 75  # TODO
        self.hull_base_strength = 1044 / 1.8  # TODO
    
    def supports_slf(self):
        return True

class EDPantherClipperMkII(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Panther Clipper Mk II'
        self.size = EDVehicleSize.LARGE
        self.seats = 4
        self.value = 301348586
        self.shield_base_strength = 350
        self.hull_mass = 1200
        self.hull_hardness = 70
        self.hull_base_strength = 1116 / 1.8
    
    def supports_slf(self):
        return True

class EDPython(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Python'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 56824391
        self.shield_base_strength = 260
        self.hull_mass = 350
        self.hull_hardness = 65
        self.hull_base_strength = 468 / 1.8

class EDPythonMkII(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Python Mk II'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 68906009
        self.shield_base_strength = 335
        self.hull_mass = 450
        self.hull_hardness = 70
        self.hull_base_strength = 504 / 1.8
    
class EDBelugaLiner(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Beluga Liner'
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
        super().__init__()
        self.type = 'Fer-de-Lance'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 51556410
        self.shield_base_strength = 300
        self.hull_mass = 250
        self.hull_hardness = 70
        self.hull_base_strength = 405 / 1.8

class EDAnaconda(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Anaconda'
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
        super().__init__()
        self.type = 'Federal Corvette'
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
        super().__init__()
        self.type = 'Imperial Cutter'
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
        super().__init__()
        self.type = 'Diamondback Scout'
        self.size = EDVehicleSize.SMALL
        self.value = 561244
        self.shield_base_strength = 120
        self.hull_mass = 170
        self.hull_hardness = 40
        self.hull_base_strength = 216 / 1.8

class EDImperialCourier(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Imperial Courier'
        self.size = EDVehicleSize.SMALL
        self.value = 2539844
        self.shield_base_strength = 200
        self.hull_mass = 35
        self.hull_hardness = 30
        self.hull_base_strength = 144 / 1.8

class EDDiamondbackExplorer(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Diamondback Explorer'
        self.size = EDVehicleSize.SMALL
        self.value = 1891674
        self.shield_base_strength = 150
        self.hull_mass = 260
        self.hull_hardness = 42
        self.hull_base_strength = 270 / 1.8

class EDImperialEagle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Imperial Eagle'
        self.size = EDVehicleSize.SMALL
        self.value = 109492
        self.shield_base_strength = 80
        self.hull_mass = 50
        self.hull_hardness = 28
        self.hull_base_strength = 108 / 1.8

class EDFederalAssaultShip(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Federal Assault Ship'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 19774598
        self.shield_base_strength = 200
        self.hull_mass = 480
        self.hull_hardness = 60
        self.hull_base_strength = 540 / 1.8

class EDFederalGunship(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Federal Gunship'
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
        super().__init__()
        self.type = 'Viper Mk IV'
        self.size = EDVehicleSize.SMALL
        self.value = 434844
        self.shield_base_strength = 150
        self.hull_mass = 190
        self.hull_hardness = 35
        self.hull_base_strength = 270 / 1.8

class EDCobraMkIV(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Cobra Mk IV'
        self.size = EDVehicleSize.SMALL
        self.seats = 2
        self.value = 744574
        self.shield_base_strength = 120
        self.hull_mass = 210
        self.hull_hardness = 35
        self.hull_base_strength = 216 / 1.8

class EDCobraMkV(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Cobra Mk V'
        self.size = EDVehicleSize.SMALL
        self.seats = 3
        self.value = 1989460
        self.shield_base_strength = 160
        self.hull_mass = 150
        self.hull_hardness = 40
        self.hull_base_strength = 324 / 1.8

class EDCorsair(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Corsair'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 79291731
        self.shield_base_strength = 264
        self.hull_mass = 265
        self.hull_hardness = 65
        self.hull_base_strength = 486 / 1.8

class EDKeelback(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Keelback'
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
        super().__init__()
        self.type = 'Asp Scout'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 3959064
        self.shield_base_strength = 120
        self.hull_mass = 150
        self.hull_hardness = 52
        self.hull_base_strength = 324 / 1.8

class EDAllianceChieftain(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Alliance Chieftain'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 18952161
        self.shield_base_strength = 200
        self.hull_mass = 400
        self.hull_hardness = 65
        self.hull_base_strength = 504 / 1.8

class EDAllianceChallenger(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Alliance Challenger'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 30540973
        self.shield_base_strength = 220
        self.hull_mass = 450
        self.hull_hardness = 65
        self.hull_base_strength = 540 / 1.8


class EDAllianceCrusader(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Alliance Crusader'
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
        super().__init__()
        self.type = 'Krait Mk II'
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
        super().__init__()
        self.type = 'Krait Phantom'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 44139676
        self.shield_base_strength = 200
        self.hull_mass = 270
        self.hull_hardness = 60
        self.hull_base_strength = 324 / 1.8

class EDMamba(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Mamba'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 56289969
        self.shield_base_strength = 270
        self.hull_mass = 250
        self.hull_hardness = 70
        self.hull_base_strength = 414 / 1.8

class EDMandalay(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Mandalay'
        self.size = EDVehicleSize.MEDIUM
        self.seats = 2
        self.value = 15614644
        self.shield_base_strength = 220
        self.hull_mass = 230
        self.hull_hardness = 55
        self.hull_base_strength = 414 / 1.8

class EDKestrelMkII(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Kestrel Mk II'
        self.size = EDVehicleSize.SMALL
        self.seats = 1
        self.value = 14273820
        self.shield_base_strength = 293
        self.hull_mass = 190
        self.hull_hardness = 55
        self.hull_base_strength = 126 / 1.8

class EDImperialFighter(EDShipLaunchedFighter):
    def __init__(self):
        super().__init__()
        self.type = 'Imperial Fighter'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 15
        self.hull_mass = 10
        self.hull_base_strength = 15 / 1.8
        # Hull of 15, Shield of 15

class EDF63Condor(EDShipLaunchedFighter):
    def __init__(self):
        super().__init__()
        self.type = 'F63 Condor'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 20
        self.hull_base_strength = 25 / 1.8
        # 50 total: Hull of 25, Shield of 25

class EDTaipanFighter(EDShipLaunchedFighter):
    def __init__(self):
        super().__init__()
        self.type = 'Taipan Fighter'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 22
        self.hull_base_strength = 45 / 1.8
        # Hull of 45, Shield of 30

class EDTrident(EDShipLaunchedFighter):
    def __init__(self):
        super().__init__()
        self.type = 'Trident'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 20
        self.hull_base_strength = 10 / 1.8

class EDJavelin(EDShipLaunchedFighter):
    def __init__(self):
        super().__init__()
        self.type = 'Javelin'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 20
        self.hull_base_strength = 10 / 1.8

class EDLance(EDShipLaunchedFighter):
    def __init__(self):
        super().__init__()
        self.type = 'Lance'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 30
        self.hull_mass = 20
        self.hull_base_strength = 10 / 1.8

class EDSRVScorpion(EDSurfaceVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'SRV Scorpion'
        self.size = EDVehicleSize.UNKNOWN
        self.seats = 2
        self.shield_base_strength = 130
        self.hull_mass = 30
        self.hull_base_strength = 162 / 1.8

class EDSRVScarab(EDSurfaceVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'SRV Scarab'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 4
        self.hull_base_strength = 108 / 1.8

class EDVehicleFactory:
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
        "explorer_nx": EDCaspianExplorer,
        "vulture": EDVulture,
        "vulture_taxi": EDVultureFrontlines,
        "empire_trader": EDImperialClipper,
        "federation_dropship": EDFederalDropship,
        "orca": EDOrca,
        "type9": EDT9Heavy,
        "type9_military": EDT10Defender,
        "lakonminer": EDT11Prospector,
        "panthermkii": EDPantherClipperMkII,
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
        "cobramkv": EDCobraMkV,
        "corsair": EDCorsair,
        "independant_trader": EDKeelback,
        "asp_scout": EDAspScout,
        "typex": EDAllianceChieftain,
        "typex_2": EDAllianceCrusader,
        "typex_3": EDAllianceChallenger,
        "krait_mkii": EDKraitMkII,
        "krait_light": EDKraitPhantom, 
        "mamba": EDMamba,
        "mandalay": EDMandalay,
        "kestrel_mkii": EDKestrelMkII,
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

    CANONICAL_SHIP_NAMES = json.loads(open(edr_data_path('shipnames.json')).read())
    CANONICAL_MODULE_NAMES = json.loads(open(edr_data_path('modulenames.json'), encoding="utf-8", errors='ignore').read())

    @staticmethod
    def canonicalize(name):
        """
        Canonicalize ship name.

        Args:
            name (str): Ship name.

        Returns:
            str: Canonical name.
        """
        if name is None:
            return "Unknown" # Note: this shouldn't be translated

        if name in EDVehicleFactory.CANONICAL_SHIP_NAMES.values():
            return name # Already canonical

        if name.lower() in EDVehicleFactory.CANONICAL_SHIP_NAMES:
            return EDVehicleFactory.CANONICAL_SHIP_NAMES[name.lower()]

        return name.lower()

    @staticmethod
    def normalize_module_name(name):
        """
        Normalize module name.

        Args:
            name (str): Module name.

        Returns:
            str: Normalized name.
        """
        normalized = name.lower()
        
        # suffix _name or _name; is not used in loadout or afmurepair events 
        if normalized.endswith("_name"):
            useless_suffix_length = len("_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith("_name;"):
            useless_suffix_length = len("_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith("$"):
            normalized = normalized[1:]

        # just get rid of prefixes because sometimes int_ becomes ext_ depending on the event
        if normalized.startswith(("int_", "ext_", "hpt_")):
            normalized = normalized[4:]
        return normalized

    @staticmethod
    def readable_module_names(name):
        """
        Get readable module names.

        Args:
            name (str): Module name.

        Returns:
            tuple: (Readable name, Short name).
        """
        if name is None:
            return "Unknown" # Note: this shouldn't be translated

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
                synthetic_name = "{} {} ({}{})".format(match.group(1), match.group(4), match.group(2), class_letter)
            else:
                synthetic_name = "{} ({}{})".format(match.group(1), match.group(2), class_letter)
            return (synthetic_name, synthetic_name)
        return (normalized.lower(), normalized.lower())

    @staticmethod
    def module_tags(name):
        """
        Get module tags.

        Args:
            name (str): Module name.

        Returns:
            dict: Module tags.
        """
        if name is None:
            return {}

        normalized = EDVehicleFactory.normalize_module_name(name)
        if normalized not in EDVehicleFactory.CANONICAL_MODULE_NAMES:
            return {}
        return EDVehicleFactory.CANONICAL_MODULE_NAMES[normalized].get("tags", {})

    @staticmethod
    def from_edmc_state(state):
        """
        Create vehicle from EDMC state.

        Args:
            state (dict): EDMC state.

        Returns:
            EDVehicle: Vehicle instance.
        """
        name = state.get('ShipType', None)

        if name is None:
            name = 'unknown'

        vehicle_class = EDVehicleFactory.__vehicle_classes.get(name.lower(), None)
        if vehicle_class is None:
            EDR_LOG.error("The requested vehicle has not been implemented: {}".format(name))
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
        """
        Create vehicle from internal name.

        Args:
            internal_name (str): Internal name.

        Returns:
            EDVehicle: Vehicle instance.
        """
        return EDVehicleFactory.__vehicle_classes.get(internal_name.lower(), EDUnknownVehicle)()

    
    @staticmethod
    def from_loadgame_or_loadout_event(event):
        """
        Create vehicle from LoadGame or Loadout event.

        Args:
            event (dict): Journal event.

        Returns:
            EDVehicle: Vehicle instance.
        """
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
        """
        Create vehicle from LoadGame event.

        Args:
            event (dict): LoadGame event.

        Returns:
            EDVehicle: Vehicle instance.
        """
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
        """
        Create vehicle from Loadout event.

        Args:
            event (dict): Loadout event.

        Returns:
            EDVehicle: Vehicle instance.
        """
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
        """
        Create vehicle from stored ship info.

        Args:
            ship_info (dict): Stored ship info.

        Returns:
            EDVehicle: Vehicle instance.
        """
        vehicle = EDVehicleFactory.from_internal_name(ship_info.get("ShipType", 'unknown'))
        vehicle.id = ship_info.get('ShipID', None)
        vehicle.name = ship_info.get('Name', None)
        vehicle.value = ship_info.get('Value', None)
        vehicle.hot = ship_info.get('Hot', None)
        return vehicle

    @staticmethod
    def is_ship_launched_fighter(vehicle):
        """
        Check if vehicle is SLF.
        """
        return isinstance(vehicle, EDShipLaunchedFighter)

    @staticmethod
    def is_surface_vehicle(vehicle):
        """
        Check if vehicle is SRV.
        """
        return isinstance(vehicle, EDSurfaceVehicle)

    @staticmethod
    def unknown_vehicle():
        """
        Returns:
            EDUnknownVehicle: Unknown vehicle.
        """
        return EDUnknownVehicle()

    @staticmethod
    def unknown_taxi():
        """
        Returns:
            EDTaxi: Unknown taxi.
        """
        return EDTaxi()
    
    @staticmethod
    def unknown_crew_vehicle():
        """
        Returns:
            EDCrewUnknownVehicle: Unknown crew vehicle.
        """
        return EDCrewUnknownVehicle()

    @staticmethod
    def default_srv():
        """
        Returns:
            EDSRVScarab: Default SRV (Scarab).
        """
        return EDSRVScarab()

    @staticmethod
    def unknown_slf():
        """
        Returns:
            EDShipLaunchedFighter: Unknown SLF.
        """
        return EDShipLaunchedFighter()

    @staticmethod
    def apex_taxi(entry=None):
        """
        Create Apex Taxi vehicle.

        Args:
            entry (dict): Optional entry for destination.
        """
        vehicle = EDAdderApex()
        if entry and entry.get("event", None) == "BookTaxi":
            vehicle.bound_for(entry.get("DestinationSystem", None), entry.get("DestinationLocation", None))
        return vehicle

    @staticmethod
    def frontlines_dropship(entry=None):
        """
        Create Frontlines Dropship vehicle.

        Args:
            entry (dict): Optional entry for destination.
        """
        vehicle = EDVultureFrontlines()
        if entry and entry.get("event", None) == "BookDropship":
            vehicle.bound_for(entry.get("DestinationSystem", None), entry.get("DestinationLocation", None))
        return vehicle


