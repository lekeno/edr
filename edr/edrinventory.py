# coding= utf-8
import pickle
import os
from edri18n import _

class EDRInventory(object):
    EDR_INVENTORY_ENCODED_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/encoded_mats.v1.p')
    EDR_INVENTORY_RAW_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/raw_mats.v1.p')
    EDR_INVENTORY_MANUFACTURED_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/manufactured_mats.v1.p')    

    MATERIALS_LUT = {
        "zinc": {"localized": _(u"Zinc"), "category": "raw", "grade": 2},
        "mercury": {"localized": _(u"Mercury"), "category": "raw", "grade": 3},
        "polonium": {"localized": _(u"Polonium"), "category": "raw", "grade": 4},
        "tellurium": {"localized": _(u"Tellurium"), "category": "raw", "grade": 4},
        "yttrium": {"localized": _(u"Yttrium"), "category": "raw", "grade": 4},
        "antimony": {"localized": _(u"Antimony"), "category": "raw", "grade": 4},
        "selenium": {"localized": _(u"Selenium"), "category": "raw", "grade": 4},
        "ruthenium": {"localized": _(u"Ruthenium"), "category": "raw", "grade": 4},
        "zirconium": {"localized": _(u"Zirconium"), "category": "raw", "grade": 2},
        "vanadium": {"localized": _(u"Vanadium"), "category": "raw", "grade": 2},
        "manganese": {"localized": _(u"Manganese"), "category": "raw", "grade": 2},
        "chromium": {"localized": _(u"Chromium"), "category": "raw", "grade": 2},
        "molybdenum": {"localized": _(u"Molybdenum"), "category": "raw", "grade": 3},
        "technetium": {"localized": _(u"Technetium"), "category": "raw", "grade": 3},
        "tin": {"localized": _(u"Tin"), "category": "raw", "grade": 3},
        "arsenic": {"localized": _(u"Arsenic"), "category": "raw", "grade": 2},
        "cadmium": {"localized": _(u"Cadmium"), "category": "raw", "grade": 3},
        "iron": {"localized": _(u"Iron"), "category": "raw", "grade": 1},
        "niobium": {"localized": _(u"Niobium"), "category": "raw", "grade": 3},
        "phosphorus": {"localized": _(u"Phosphorus"), "category": "raw", "grade": 1},
        "germanium": {"localized": _(u"Germanium"), "category": "raw", "grade": 2},
        "tungsten": {"localized": _(u"Tungsten"), "category": "raw", "grade": 3},
        "sulphur": {"localized": _(u"Sulphur"), "category": "raw", "grade": 1},
        "carbon": {"localized": _(u"Carbon"), "category": "raw", "grade": 1},
        "nickel": {"localized": _(u"Nickel"), "category": "raw", "grade": 1},
        "rhenium": {"localized": _(u"Rhenium"), "category": "raw", "grade": 1},
        "boron": {"localized": _(u"Boron"), "category": "raw", "grade": 3},
        "lead": {"localized": _(u"Lead"), "category": "raw", "grade": 1},
        "focuscrystals": {"localized": _(u"Focus Crystals"), "category": "manufactured", "grade": 3},
        "compoundshielding": {"localized": _(u"Compound Shielding"), "category": "manufactured", "grade": 4},
        "galvanisingalloys": {"localized": _(u"Galvanising Alloys"), "category": "manufactured", "grade": 2},
        "heatvanes": {"localized": _(u"Heat Vanes"), "category": "manufactured", "grade": 4},
        "configurablecomponents": {"localized": _(u"Configurable Components"), "category": "manufactured", "grade": 4},
        "biotechconductors": {"localized": _(u"Biotech Conductors"), "category": "manufactured", "grade": 5},
        "chemicalmanipulators": {"localized": _(u"Chemical Manipulators"), "category": "manufactured", "grade": 4},
        "mechanicalcomponents": {"localized": _(u"Mechanical Components"), "category": "manufactured", "grade": 3},
        "fedproprietarycomposites": {"localized": _(u"Proprietary Composites"), "category": "manufactured", "grade": 4},
        "highdensitycomposites": {"localized": _(u"High Density Composites"), "category": "manufactured", "grade": 3},
        "protoradiolicalloys": {"localized": _(u"Proto Radiolic Alloys"), "category": "manufactured", "grade": 5},
        "chemicaldistillery": {"localized": _(u"Chemical Distillery"), "category": "manufactured", "grade": 3},
        "chemicalprocessors": {"localized": _(u"Chemical Processors"), "category": "manufactured", "grade": 2},
        "imperialshielding": {"localized": _(u"Imperial Shielding"), "category": "manufactured", "grade": 5},
        "gridresistors": {"localized": _(u"Grid Resistors"), "category": "manufactured", "grade": 1},
        "heatconductionwiring": {"localized": _(u"Heat Conduction Wiring"), "category": "manufactured", "grade": 1},
        "militarygradealloys": {"localized": _(u"Military Grade Alloys"), "category": "manufactured", "grade": 5},
        "hybridcapacitors": {"localized": _(u"Hybrid Capacitors"), "category": "manufactured", "grade": 2},
        "heatexchangers": {"localized": _(u"Heat Exchangers"), "category": "manufactured", "grade": 3},
        "conductivepolymers": {"localized": _(u"Conductive Polymers"), "category": "manufactured", "grade": 4},
        "shieldingsensors": {"localized": _(u"Shielding Sensors"), "category": "manufactured", "grade": 3},
        "heatdispersionplate": {"localized": _(u"Heat Dispersion Plate"), "category": "manufactured", "grade": 2},
        "electrochemicalarrays": {"localized": _(u"Electrochemical Arrays"), "category": "manufactured", "grade": 1},
        "conductiveceramics": {"localized": _(u"Conductive Ceramics"), "category": "manufactured", "grade": 3},
        "conductivecomponents": {"localized": _(u"Conductive Components"), "category": "manufactured", "grade": 2},
        "militarysupercapacitors": {"localized": _(u"Military Supercapacitors"), "category": "manufactured", "grade": 5},
        "mechanicalequipment": {"localized": _(u"Mechanical Equipment"), "category": "manufactured", "grade": 2},
        "phasealloys": {"localized": _(u"Phase Alloys"), "category": "manufactured", "grade": 3},
        "pharmaceuticalisolators": {"localized": _(u"Pharmaceutical Isolators"), "category": "manufactured", "grade": 5},
        "fedcorecomposites": {"localized": _(u"Core Dynamics Composites"), "category": "manufactured", "grade": 5},
        "basicconductors": {"localized": _(u"Basic Conductors"), "category": "manufactured", "grade": 1},
        "mechanicalscrap": {"localized": _(u"Mechanical Scrap"), "category": "manufactured", "grade": 1},
        "salvagedalloys": {"localized": _(u"Salvaged Alloys"), "category": "manufactured", "grade": 1},
        "protolightalloys": {"localized": _(u"Proto Light Alloys"), "category": "manufactured", "grade": 4},
        "refinedfocuscrystals": {"localized": _(u"Refined Focus Crystals"), "category": "manufactured", "grade": 4},
        "shieldemitters": {"localized": _(u"Shield Emitters"), "category": "manufactured", "grade": 1},
        "precipitatedalloys": {"localized": _(u"Precipitated Alloys"), "category": "manufactured", "grade": 3},
        "wornshieldemitters": {"localized": _(u"Worn Shield Emitters"), "category": "manufactured", "grade": 1},
        "exquisitefocuscrystals": {"localized": _(u"Exquisite Focus Crystals"), "category": "manufactured", "grade": 5},
        "polymercapacitors": {"localized": _(u"Polymer Capacitors"), "category": "manufactured", "grade": 4},
        "thermicalloys": {"localized": _(u"Thermic Alloys"), "category": "manufactured", "grade": 4},
        "improvisedcomponents": {"localized": _(u"Improvised Components"), "category": "manufactured", "grade": 5},
        "crystalshards": {"localized": _(u"Crystal Shards"), "category": "manufactured", "grade": 1},
        "heatresistantceramics": {"localized": _(u"Heat Resistant Ceramics"), "category": "manufactured", "grade": 2},
        "temperedalloys": {"localized": _(u"Tempered Alloys"), "category": "manufactured", "grade": 1},
        "uncutfocuscrystals": {"localized": _(u"Flawed Focus Crystals"), "category": "manufactured", "grade": 2},
        "filamentcomposites": {"localized": _(u"Filament Composites"), "category": "manufactured", "grade": 2},
        "compactcomposites": {"localized": _(u"Compact Composites"), "category": "manufactured", "grade": 1},
        "chemicalstorageunits": {"localized": _(u"Chemical Storage Units"), "category": "manufactured", "grade": 1},
        "protoheatradiator": {"localized": _(u"Proto Heat Radiators"), "category": "manufactured", "grade": 5},
        "guardian_powerconduit": {"localized": _(u"Guardian Power Conduit"), "category": "manufactured", "grade": 2},
        "guardian_powercell": {"localized": _(u"Guardian Power Cell"), "category": "manufactured", "grade": 1},
        "guardian_techcomponent": {"localized": _(u"Guardian Technology Component"), "category": "manufactured", "grade": 3},
        "guardian_sentinel_wreckagecomponents": {"localized": _(u"Guardian Wreckage Components"), "category": "manufactured", "grade": 1},
        "guardian_sentinel_weaponparts": {"localized": _(u"Guardian Sentinel Weapon Parts"), "category": "manufactured", "grade": 3},
        "classifiedscandata": {"localized": _(u"Classified Scan Fragment"), "category": "encoded", "grade": 5},
        "securityfirmware": {"localized": _(u"Security Firmware Patch"), "category": "encoded", "grade": 4},
        "dataminedwake": {"localized": _(u"Datamined Wake Exceptions"), "category": "encoded", "grade": 5},
        "compactemissionsdata": {"localized": _(u"Abnormal Compact Emissions Data"), "category": "encoded", "grade": 5},
        "shieldpatternanalysis": {"localized": _(u"Aberrant Shield Pattern Analysis"), "category": "encoded", "grade": 4},
        "adaptiveencryptors": {"localized": _(u"Adaptive Encryptors Capture"), "category": "encoded", "grade": 5},
        "emissiondata": {"localized": _(u"Unexpected Emission Data"), "category": "encoded", "grade": 3},
        "industrialfirmware": {"localized": _(u"Cracked Industrial Firmware"), "category": "encoded", "grade": 3},
        "scandatabanks": {"localized": _(u"Classified Scan Databanks"), "category": "encoded", "grade": 3},
        "legacyfirmware": {"localized": _(u"Specialised Legacy Firmware"), "category": "encoded", "grade": 1},
        "embeddedfirmware": {"localized": _(u"Modified Embedded Firmware"), "category": "encoded", "grade": 5},
        "shieldcyclerecordings": {"localized": _(u"Distorted Shield Cycle Recordings"), "category": "encoded", "grade": 1},
        "decodedemissiondata": {"localized": _(u"Decoded Emission Data"), "category": "encoded", "grade": 4},
        "bulkscandata": {"localized": _(u"Anomalous Bulk Scan Data"), "category": "encoded", "grade": 1},
        "scanarchives": {"localized": _(u"Unidentified Scan Archives"), "category": "encoded", "grade": 2},
        "shieldsoakanalysis": {"localized": _(u"Inconsistent Shield Soak Analysis"), "category": "encoded", "grade": 2},
        "encodedscandata": {"localized": _(u"Divergent Scan Data"), "category": "encoded", "grade": 4},
        "shielddensityreports": {"localized": _(u"Untypical Shield Scans"), "category": "encoded", "grade": 3},
        "shieldfrequencydata": {"localized": _(u"Peculiar Shield Frequency Data"), "category": "encoded", "grade": 5},
        "encryptioncodes": {"localized": _(u"Tagged Encryption Codes"), "category": "encoded", "grade": 2},
        "consumerfirmware": {"localized": _(u"Modified Consumer Firmware"), "category": "encoded", "grade": 2},
        "archivedemissiondata": {"localized": _(u"Irregular Emission Data"), "category": "encoded", "grade": 2},
        "symmetrickeys": {"localized": _(u"Open Symmetric Keys"), "category": "encoded", "grade": 3},
        "encryptedfiles": {"localized": _(u"Unusual Encrypted Files"), "category": "encoded", "grade": 1},
        "scrambledemissiondata": {"localized": _(u"Exceptional Scrambled Emission Data"), "category": "encoded", "grade": 1},
        "fsdtelemetry": {"localized": _(u"Anomalous FSD Telemetry"), "category": "encoded", "grade": 2},
        "hyperspacetrajectories": {"localized": _(u"Eccentric Hyperspace Trajectories"), "category": "encoded", "grade": 4},
        "disruptedwakeechoes": {"localized": _(u"Atypical Disrupted Wake Echoes"), "category": "encoded", "grade": 1},
        "wakesolutions": {"localized": _(u"Strange Wake Solutions"), "category": "encoded", "grade": 3},
        "encryptionarchives": {"localized": _(u"Atypical Encryption Archives"), "category": "encoded", "grade": 4},
        "ancientbiologicaldata": {"localized": _(u"Pattern Alpha Obelisk Data"), "category": "encoded", "grade": 3},
        "ancienthistoricaldata": {"localized": _(u"Pattern Gamma Obelisk Data"), "category": "encoded", "grade": 4},
        "guardian_moduleblueprint": {"localized": _(u"Guardian Module Blueprint Fragment"), "category": "encoded", "grade": 5},
        "ancientculturaldata": {"localized": _(u"Pattern Beta Obelisk Data"), "category": "encoded", "grade": 2},
        "ancientlanguagedata": {"localized": _(u"Pattern Delta Obelisk Data"), "category": "encoded", "grade": 4},
        "guardian_vesselblueprint": {"localized": _(u"Guardian Starship Blueprint Fragment"), "category": "encoded", "grade": 5},
        "guardian_weaponblueprint": {"localized": _(u"Guardian Weapon Blueprint Fragment"), "category": "encoded", "grade": 5},
        "ancienttechnologicaldata": {"localized": _(u"Pattern Epsilon Obelisk Data"), "category": "encoded", "grade": 5},
        "tg_shipsystemsdata": {"localized": _(u"Ship Systems Data"), "category": "encoded", "grade": 3},
        "tg_shipflightdata": {"localized": _(u"Ship Flight Data"), "category": "encoded", "grade": 3},
        "unknownshipsignature": {"localized": _(u"Thargoid Ship Signature"), "category": "encoded", "grade": 3},
        "tg_structuraldata": {"localized": _(u"Thargoid Structural Data"), "category": "encoded", "grade": 2},
        "unknownwakedata": {"localized": _(u"Thargoid Wake Data"), "category": "encoded", "grade": 4},
        "tg_biomechanicalconduits": {"localized": _(u"Bio-Mechanical Conduits"), "category": "manufactured", "grade": 3},
        "tg_propulsionelement": {"localized": _(u"Propulsion Elements"), "category": "manufactured", "grade": 3},
        "unknowncarapace": {"localized": _(u"Thargoid Carapace"), "category": "manufactured", "grade": 2},
        "unknownenergycell": {"localized": _(u"Thargoid Energy Cell"), "category": "manufactured", "grade": 3},
        "unknownorganiccircuitry": {"localized": _(u"Thargoid Organic Circuitry"), "category": "manufactured", "grade": 5},
        "unknowntechnologycomponents": {"localized": _(u"Thargoid Technological Components"), "category": "manufactured", "grade": 4}
    }

    INTERNAL_NAMES_LUT = { u'classified scan databanks': 'scandatabanks', u'conductive components': 'conductivecomponents', u'abnormal compact emissions data': 'compactemissionsdata', u'germanium': 'germanium',
        u'atypical disrupted wake echoes': 'disruptedwakeechoes', u'crystal shards': 'crystalshards', u'selenium': 'selenium', u'technetium': 'technetium', u'galvanising alloys': 'galvanisingalloys',
        u'improvised components': 'improvisedcomponents', u'cracked industrial firmware': 'industrialfirmware', u'guardian technology component': 'guardian_techcomponent', u'heat resistant ceramics': 'heatresistantceramics',
        u'unexpected emission data': 'emissiondata', u'tungsten': 'tungsten', u'exceptional scrambled emission data': 'scrambledemissiondata', u'thermic alloys': 'thermicalloys', u'molybdenum': 'molybdenum',
        u'atypical encryption archives': 'encryptionarchives', u'salvaged alloys': 'salvagedalloys', u'pharmaceutical isolators': 'pharmaceuticalisolators', u'divergent scan data': 'encodedscandata',
        u'anomalous fsd telemetry': 'fsdtelemetry', u'pattern delta obelisk data': 'ancientlanguagedata', u'worn shield emitters': 'wornshieldemitters', u'strange wake solutions': 'wakesolutions',
        u'tempered alloys': 'temperedalloys', u'zinc': 'zinc', u'mechanical equipment': 'mechanicalequipment', u'eccentric hyperspace trajectories': 'hyperspacetrajectories', u'grid resistors': 'gridresistors', 
        u'unusual encrypted files': 'encryptedfiles', u'peculiar shield frequency data': 'shieldfrequencydata', u'specialised legacy firmware': 'legacyfirmware', u'flawed focus crystals': 'uncutfocuscrystals', 
        u'pattern beta obelisk data': 'ancientculturaldata', u'antimony': 'antimony', u'untypical shield scans': 'shielddensityreports', u'focus crystals': 'focuscrystals', u'lead': 'lead', 
        u'heat dispersion plate': 'heatdispersionplate', u'irregular emission data': 'archivedemissiondata', u'guardian module blueprint fragment': 'guardian_moduleblueprint', u'yttrium': 'yttrium', 
        u'mechanical scrap': 'mechanicalscrap', u'biotech conductors': 'biotechconductors', u'military grade alloys': 'militarygradealloys', u'basic conductors': 'basicconductors', u'boron': 'boron', u'carbon': 'carbon', 
        u'unidentified scan archives': 'scanarchives', u'imperial shielding': 'imperialshielding', u'chemical distillery': 'chemicaldistillery', u'guardian wreckage components': 'guardian_sentinel_wreckagecomponents', 
        u'proto radiolic alloys': 'protoradiolicalloys', u'cadmium': 'cadmium', u'filament composites': 'filamentcomposites', u'exquisite focus crystals': 'exquisitefocuscrystals', u'electrochemical arrays': 'electrochemicalarrays', 
        u'mechanical components': 'mechanicalcomponents', u'pattern alpha obelisk data': 'ancientbiologicaldata', u'arsenic': 'arsenic', u'chromium': 'chromium', u'conductive ceramics': 'conductiveceramics', u'mercury': 'mercury', 
        u'chemical processors': 'chemicalprocessors', u'pattern gamma obelisk data': 'ancienthistoricaldata', u'proprietary composites': 'fedproprietarycomposites', u'proto light alloys': 'protolightalloys', 
        u'datamined wake exceptions': 'dataminedwake', u'adaptive encryptors capture': 'adaptiveencryptors', u'open symmetric keys': 'symmetrickeys', u'nickel': 'nickel', u'ruthenium': 'ruthenium', 
        u'guardian sentinel weapon parts': 'guardian_sentinel_weaponparts', u'decoded emission data': 'decodedemissiondata', u'guardian power cell': 'guardian_powercell', u'chemical storage units': 'chemicalstorageunits', 
        u'sulphur': 'sulphur', u'anomalous bulk scan data': 'bulkscandata', u'refined focus crystals': 'refinedfocuscrystals', u'zirconium': 'zirconium', u'heat vanes': 'heatvanes', u'niobium': 'niobium', u'iron': 'iron', 
        u'conductive polymers': 'conductivepolymers', u'configurable components': 'configurablecomponents', u'rhenium': 'rhenium', u'security firmware patch': 'securityfirmware', u'aberrant shield pattern analysis': 'shieldpatternanalysis',
        u'modified consumer firmware': 'consumerfirmware', u'military supercapacitors': 'militarysupercapacitors', u'heat conduction wiring': 'heatconductionwiring', u'inconsistent shield soak analysis': 'shieldsoakanalysis',
        u'distorted shield cycle recordings': 'shieldcyclerecordings', u'shield emitters': 'shieldemitters', u'tin': 'tin', u'chemical manipulators': 'chemicalmanipulators', u'hybrid capacitors': 'hybridcapacitors',
        u'tagged encryption codes': 'encryptioncodes', u'classified scan fragment': 'classifiedscandata', u'polymer capacitors': 'polymercapacitors', u'precipitated alloys': 'precipitatedalloys', 
        u'heat exchangers': 'heatexchangers', u'polonium': 'polonium', u'core dynamics composites': 'fedcorecomposites', u'high density composites': 'highdensitycomposites', u'modified embedded firmware': 'embeddedfirmware',
        u'phosphorus': 'phosphorus', u'guardian power conduit': 'guardian_powerconduit', u'vanadium': 'vanadium', u'shielding sensors': 'shieldingsensors', u'compound shielding': 'compoundshielding', 
        u'manganese': 'manganese', u'compact composites': 'compactcomposites', u'tellurium': 'tellurium', u'phase alloys': 'phasealloys', u'thargoid organic circuitry': u'unknownorganiccircuitry', 
        u'thargoid energy cell': u'unknownenergycell', u'thargoid structural data': u'tg_structuraldata', u'thargoid ship signature': u'unknownshipsignature', u'thargoid carapace': u'unknowncarapace', 
        u'propulsion elements': u'tg_propulsionelement', u'guardian weapon blueprint fragment': u'guardian_weaponblueprint', u'guardian starship blueprint fragment': u'guardian_vesselblueprint', 
        u'pattern epsilon obelisk data': u'ancienttechnologicaldata', u'bio-mechanical conduits': u'tg_biomechanicalconduits', u'ship flight data': u'tg_shipflightdata', u'thargoid wake data': u'unknownwakedata', 
        u'thargoid technological components': u'unknowntechnologycomponents', u'ship systems data': u'tg_shipsystemsdata'}

    def __init__(self):
        self.initialized = False
        self.inconsistencies = False
        try:
            with open(self.EDR_INVENTORY_ENCODED_CACHE, 'rb') as handle:
                self.encoded = pickle.load(handle)
        except:
            self.encoded = {}

        try:
            with open(self.EDR_INVENTORY_RAW_CACHE, 'rb') as handle:
                self.raw = pickle.load(handle)
        except:
            self.raw = {}

        try:
            with open(self.EDR_INVENTORY_MANUFACTURED_CACHE, 'rb') as handle:
                self.manufactured = pickle.load(handle)
        except:
            self.manufactured = {}
        self.__check()

    def initialize(self, materials):
        for thing in materials.get("Encoded", []):
            cname = self.__c_name(thing["Name"])
            self.encoded[cname] = thing["Count"]

        for thing in materials.get("Raw", []):
            cname = self.__c_name(thing["Name"])
            self.raw[cname] = thing["Count"]

        for thing in materials.get("Manufactured", []):
            cname = self.__c_name(thing["Name"])
            self.manufactured[cname] = thing["Count"]
        self.initialized = True
        self.inconsistencies = False

    def initialize_with_edmc(self, state):
        for thing in state.get("Encoded", {}):
            cname = self.__c_name(thing)
            self.encoded[cname] = state["Encoded"][thing]

        for thing in state.get("Raw", {}):
            cname = self.__c_name(thing)
            self.raw[cname] = state["Raw"][thing]

        for thing in state.get("Manufactured", {}):
            cname = self.__c_name(thing)
            self.manufactured[cname] = state["Manufactured"][thing]
        self.initialized = True
        self.inconsistencies = False

    def stale_or_incorrect(self):
        return not self.initialized or self.inconsistencies

    def persist(self):
        with open(self.EDR_INVENTORY_ENCODED_CACHE, 'wb') as handle:
            pickle.dump(self.encoded, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_MANUFACTURED_CACHE, 'wb') as handle:
            pickle.dump(self.manufactured, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_RAW_CACHE, 'wb') as handle:
            pickle.dump(self.raw, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def collected(self, info):
        self.add(info["Category"], info["Name"], info["Count"])

    def discarded(self, info):
        self.substract(info["Category"], info["Name"], info["Count"])

    def count(self, name):
        cname = self.__c_name(name)
        category = self.category(cname)
        if category == "encoded":
            return self.encoded.get(cname, 0)
        elif category == "raw":
            return self.raw.get(cname, 0)
        elif category == "manufactured":
            return self.manufactured.get(cname, 0)
        return 0

    def oneliner(self, name):
        cname = self.__c_name(name)
        category = self.category(cname)
        entry = self.MATERIALS_LUT.get(cname, None)
        if not category or not entry:
            return name
        count = self.count(cname)
        grades = [u"?", u"Ⅰ", u"Ⅱ", u"Ⅲ", u"Ⅳ", u"Ⅴ"]
        slots = [u"?", u"300", u"250", u"200", u"150", u"100"]
        return u"{} (Grade {}; {}/{})".format(entry["localized"], grades[entry["grade"]], count or u"?", slots[entry["grade"]])

    def __check(self):
        self.inconsistencies = False
        for collection in [self.encoded, self.raw, self.manufactured]:
            for thing in collection:
                self.__check_item(thing)
                if self.inconsistencies:
                    return False
        return True
    
    def __check_item(self, name):
        cname = self.__c_name(name)
        entry = self.MATERIALS_LUT.get(cname, None)
        if not entry:
            return False
        count = self.count(cname)
        if count < 0:
            self.inconsistencies = True
            return False
        max_for_slot = self.slots(name)
        if count > max_for_slot:
            self.inconsistencies = True
            return False
        return True

    def donated_engineer(self, info):
        if info["Type"] != "Material":
            return
        category = self.category(info["Name"])
        if category:
            self.substract(category, info["Name"], info["Quantity"])

    def donated_science(self, info):
        self.substract(info["Category"], info["Name"], info["Count"])

    def consumed(self, ingredients):
        for ingredient in ingredients:
            category = ingredient.get("Category", self.category(ingredient["Name"]))
            if category:
                self.substract(category, ingredient["Name"], ingredient["Count"])

    def traded(self, info):
        paid = info["Paid"]
        self.substract(paid["Category"], paid["Material"], paid["Quantity"])
        received = info["Received"]
        self.substract(received["Category"], received["Material"], received["Quantity"])

    def rewarded(self, info):
        # TODO Does Search And Rescue give material rewards??
        if "MaterialsReward" not in info:
            return
        for reward in info["MaterialsReward"]:
            self.add(reward["Category"], reward["Name"], reward["Count"])

    def add(self, category, name, count):
        ccategory = self.__c_cat(category)
        cname = self.__c_name(name)
        if ccategory == "encoded":
            self.encoded[cname] = min(self.encoded.get(cname, 0) + count, self.slots(name))
        elif ccategory == "raw":
            self.raw[cname] = min(self.raw.get(cname, 0) + count, self.slots(name))
        elif ccategory == "manufactured":
            self.manufactured[cname] = min(self.manufactured.get(cname, 0) + count, self.slots(name))

    def slots(self, name):
        cname = self.__c_name(name)
        entry = self.MATERIALS_LUT.get(cname, None)
        if not entry:
            return 100
        slots = [100, 300, 250, 200, 150, 100]
        return slots[entry["grade"]]

    def substract(self, category, name, count):
        ccategory = self.__c_cat(category)
        cname = self.__c_name(name)
        if ccategory == "encoded":
            self.encoded[cname] = max(self.encoded.get(cname, 0) - count, 0)
        elif ccategory == "raw":
            self.raw[cname] = max(self.raw.get(cname, 0) - count, 0)
        elif ccategory == "manufactured":
            self.manufactured[cname] = max(self.manufactured.get(cname, 0) - count, 0)

    def category(self, name):
        cname = self.__c_name(name)
        entry = self.MATERIALS_LUT.get(cname, None)
        return entry["category"] if entry else None

    def __c_cat(self, category):
        ccat = category.lower()
        if ccat.endswith(u";"):
            ccat = ccat[:-1]
        if ccat.startswith(u"$MICRORESOURCE_CATEGORY_"):
            useless_prefix_length = len(u"$MICRORESOURCE_CATEGORY_")
            ccat = ccat[useless_prefix_length:]
        return ccat

    def __c_name(self, name):
        cname = name.lower()
        if cname in self.MATERIALS_LUT:
            return cname
        return self.INTERNAL_NAMES_LUT.get(cname, cname)