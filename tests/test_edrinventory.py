import config_tests
from unittest import TestCase, main
from edrinventory import EDRInventory

class TestEDRInventory(TestCase):
    def test_initialize(self):
        inventory = EDRInventory()
        event = { "timestamp":"2019-01-02T11:03:33Z", "event":"Materials", "Raw":[ { "Name":"zinc", "Count":52 }, { "Name":"mercury", "Count":54 }, { "Name":"polonium", "Count":33 }, { "Name":"tellurium", "Count":47 }, { "Name":"yttrium", "Count":43 }, { "Name":"antimony", "Count":51 }, { "Name":"selenium", "Count":21 }, { "Name":"ruthenium", "Count":49 }, { "Name":"zirconium", "Count":50 }, { "Name":"vanadium", "Count":66 }, { "Name":"manganese", "Count":83 }, { "Name":"chromium", "Count":26 }, { "Name":"molybdenum", "Count":44 }, { "Name":"technetium", "Count":22 }, { "Name":"tin", "Count":15 }, { "Name":"arsenic", "Count":44 }, { "Name":"cadmium", "Count":42 }, { "Name":"iron", "Count":54 }, { "Name":"niobium", "Count":29 }, { "Name":"phosphorus", "Count":48 }, { "Name":"germanium", "Count":37 }, { "Name":"tungsten", "Count":24 }, { "Name":"sulphur", "Count":32 }, { "Name":"carbon", "Count":67 }, { "Name":"nickel", "Count":78 }, { "Name":"rhenium", "Count":52 }, { "Name":"boron", "Count":36 }, { "Name":"lead", "Count":52 } ], "Manufactured":[ { "Name":"focuscrystals", "Name_Localised":"Focus Crystals", "Count":87 }, { "Name":"compoundshielding", "Name_Localised":"Compound Shielding", "Count":55 }, { "Name":"galvanisingalloys", "Name_Localised":"Galvanising Alloys", "Count":85 }, { "Name":"heatvanes", "Name_Localised":"Heat Vanes", "Count":34 }, { "Name":"configurablecomponents", "Name_Localised":"Configurable Components", "Count":26 }, { "Name":"biotechconductors", "Name_Localised":"Biotech Conductors", "Count":53 }, { "Name":"chemicalmanipulators", "Name_Localised":"Chemical Manipulators", "Count":77 }, { "Name":"mechanicalcomponents", "Name_Localised":"Mechanical Components", "Count":24 }, { "Name":"fedproprietarycomposites", "Name_Localised":"Proprietary Composites", "Count":46 }, { "Name":"highdensitycomposites", "Name_Localised":"High Density Composites", "Count":60 }, { "Name":"protoradiolicalloys", "Name_Localised":"Proto Radiolic Alloys", "Count":25 }, { "Name":"chemicaldistillery", "Name_Localised":"Chemical Distillery", "Count":76 }, { "Name":"chemicalprocessors", "Name_Localised":"Chemical Processors", "Count":131 }, { "Name":"imperialshielding", "Name_Localised":"Imperial Shielding", "Count":76 }, { "Name":"gridresistors", "Name_Localised":"Grid Resistors", "Count":59 }, { "Name":"heatconductionwiring", "Name_Localised":"Heat Conduction Wiring", "Count":94 }, { "Name":"militarygradealloys", "Name_Localised":"Military Grade Alloys", "Count":87 }, { "Name":"hybridcapacitors", "Name_Localised":"Hybrid Capacitors", "Count":99 }, { "Name":"heatexchangers", "Name_Localised":"Heat Exchangers", "Count":50 }, { "Name":"conductivepolymers", "Name_Localised":"Conductive Polymers", "Count":43 }, { "Name":"shieldingsensors", "Name_Localised":"Shielding Sensors", "Count":88 }, { "Name":"heatdispersionplate", "Name_Localised":"Heat Dispersion Plate", "Count":100 }, { "Name":"electrochemicalarrays", "Name_Localised":"Electrochemical Arrays", "Count":52 }, { "Name":"conductiveceramics", "Name_Localised":"Conductive Ceramics", "Count":46 }, { "Name":"conductivecomponents", "Name_Localised":"Conductive Components", "Count":87 }, { "Name":"militarysupercapacitors", "Name_Localised":"Military Supercapacitors", "Count":75 }, { "Name":"mechanicalequipment", "Name_Localised":"Mechanical Equipment", "Count":93 }, { "Name":"phasealloys", "Name_Localised":"Phase Alloys", "Count":47 }, { "Name":"pharmaceuticalisolators", "Name_Localised":"Pharmaceutical Isolators", "Count":34 }, { "Name":"fedcorecomposites", "Name_Localised":"Core Dynamics Composites", "Count":25 }, { "Name":"basicconductors", "Name_Localised":"Basic Conductors", "Count":70 }, { "Name":"mechanicalscrap", "Name_Localised":"Mechanical Scrap", "Count":93 }, { "Name":"salvagedalloys", "Name_Localised":"Salvaged Alloys", "Count":90 }, { "Name":"protolightalloys", "Name_Localised":"Proto Light Alloys", "Count":60 }, { "Name":"refinedfocuscrystals", "Name_Localised":"Refined Focus Crystals", "Count":79 }, { "Name":"shieldemitters", "Name_Localised":"Shield Emitters", "Count":105 }, { "Name":"precipitatedalloys", "Name_Localised":"Precipitated Alloys", "Count":5 }, { "Name":"wornshieldemitters", "Name_Localised":"Worn Shield Emitters", "Count":89 }, { "Name":"exquisitefocuscrystals", "Name_Localised":"Exquisite Focus Crystals", "Count":21 }, { "Name":"polymercapacitors", "Name_Localised":"Polymer Capacitors", "Count":60 }, { "Name":"thermicalloys", "Name_Localised":"Thermic Alloys", "Count":42 }, { "Name":"improvisedcomponents", "Name_Localised":"Improvised Components", "Count":27 }, { "Name":"protoheatradiators", "Name_Localised":"Proto Heat Radiators", "Count":12 }, { "Name":"crystalshards", "Name_Localised":"Crystal Shards", "Count":87 }, { "Name":"heatresistantceramics", "Name_Localised":"Heat Resistant Ceramics", "Count":33 }, { "Name":"temperedalloys", "Name_Localised":"Tempered Alloys", "Count":34 }, { "Name":"uncutfocuscrystals", "Name_Localised":"Flawed Focus Crystals", "Count":93 }, { "Name":"filamentcomposites", "Name_Localised":"Filament Composites", "Count":23 }, { "Name":"compactcomposites", "Name_Localised":"Compact Composites", "Count":10 }, { "Name":"chemicalstorageunits", "Name_Localised":"Chemical Storage Units", "Count":43 }, { "Name":"guardian_powerconduit", "Name_Localised":"Guardian Power Conduit", "Count":148 }, { "Name":"guardian_powercell", "Name_Localised":"Guardian Power Cell", "Count":163 }, { "Name":"guardian_techcomponent", "Name_Localised":"Guardian Technology Component", "Count":25 }, { "Name":"guardian_sentinel_wreckagecomponents", "Name_Localised":"Guardian Wreckage Components", "Count":3 }, { "Name":"guardian_sentinel_weaponparts", "Name_Localised":"Guardian Sentinel Weapon Parts", "Count":57 } ], "Encoded":[ { "Name":"classifiedscandata", "Name_Localised":"Classified Scan Fragment", "Count":63 }, { "Name":"securityfirmware", "Name_Localised":"Security Firmware Patch", "Count":78 }, { "Name":"dataminedwake", "Name_Localised":"Datamined Wake Exceptions", "Count":31 }, { "Name":"compactemissionsdata", "Name_Localised":"Abnormal Compact Emissions Data", "Count":53 }, { "Name":"shieldpatternanalysis", "Name_Localised":"Aberrant Shield Pattern Analysis", "Count":81 }, { "Name":"adaptiveencryptors", "Name_Localised":"Adaptive Encryptors Capture", "Count":32 }, { "Name":"emissiondata", "Name_Localised":"Unexpected Emission Data", "Count":88 }, { "Name":"industrialfirmware", "Name_Localised":"Cracked Industrial Firmware", "Count":92 }, { "Name":"scandatabanks", "Name_Localised":"Classified Scan Databanks", "Count":106 }, { "Name":"legacyfirmware", "Name_Localised":"Specialised Legacy Firmware", "Count":100 }, { "Name":"embeddedfirmware", "Name_Localised":"Modified Embedded Firmware", "Count":33 }, { "Name":"shieldcyclerecordings", "Name_Localised":"Distorted Shield Cycle Recordings", "Count":102 }, { "Name":"decodedemissiondata", "Name_Localised":"Decoded Emission Data", "Count":110 }, { "Name":"bulkscandata", "Name_Localised":"Anomalous Bulk Scan Data", "Count":120 }, { "Name":"scanarchives", "Name_Localised":"Unidentified Scan Archives", "Count":98 }, { "Name":"shieldsoakanalysis", "Name_Localised":"Inconsistent Shield Soak Analysis", "Count":92 }, { "Name":"encodedscandata", "Name_Localised":"Divergent Scan Data", "Count":55 }, { "Name":"shielddensityreports", "Name_Localised":"Untypical Shield Scans ", "Count":87 }, { "Name":"shieldfrequencydata", "Name_Localised":"Peculiar Shield Frequency Data", "Count":45 }, { "Name":"encryptioncodes", "Name_Localised":"Tagged Encryption Codes", "Count":85 }, { "Name":"consumerfirmware", "Name_Localised":"Modified Consumer Firmware", "Count":67 }, { "Name":"archivedemissiondata", "Name_Localised":"Irregular Emission Data", "Count":24 }, { "Name":"symmetrickeys", "Name_Localised":"Open Symmetric Keys", "Count":93 }, { "Name":"encryptedfiles", "Name_Localised":"Unusual Encrypted Files", "Count":93 }, { "Name":"scrambledemissiondata", "Name_Localised":"Exceptional Scrambled Emission Data", "Count":18 }, { "Name":"fsdtelemetry", "Name_Localised":"Anomalous FSD Telemetry", "Count":69 }, { "Name":"hyperspacetrajectories", "Name_Localised":"Eccentric Hyperspace Trajectories", "Count":28 }, { "Name":"disruptedwakeechoes", "Name_Localised":"Atypical Disrupted Wake Echoes", "Count":17 }, { "Name":"wakesolutions", "Name_Localised":"Strange Wake Solutions", "Count":16 }, { "Name":"encryptionarchives", "Name_Localised":"Atypical Encryption Archives", "Count":47 }, { "Name":"ancientbiologicaldata", "Name_Localised":"Pattern Alpha Obelisk Data", "Count":144 }, { "Name":"ancienthistoricaldata", "Name_Localised":"Pattern Gamma Obelisk Data", "Count":147 }, { "Name":"guardian_moduleblueprint", "Name_Localised":"Guardian Module Blueprint Fragment", "Count":1 }, { "Name":"ancientculturaldata", "Name_Localised":"Pattern Beta Obelisk Data", "Count":132 }, { "Name":"ancientlanguagedata", "Name_Localised":"Pattern Delta Obelisk Data", "Count":42 } ] }
        inventory.initialize(event)
        self.assertEqual(inventory.count("zinc"), 52)
        self.assertEqual(inventory.count("Zinc"), 52)
        self.assertEqual(inventory.count("compoundshielding"), 55)
        self.assertEqual(inventory.count("Compound Shielding"), 55)
        self.assertEqual(inventory.count("guardian_moduleblueprint"), 1)
        self.assertEqual(inventory.count("Guardian Module Blueprint Fragment"), 1)
        self.assertEqual(inventory.count("doesnotexist"), 0)

    def test_collected(self):
        inventory = EDRInventory()
        self.assertEqual(inventory.count("zinc"), 0)
        info = {"Category": "raw", "Name": "zinc", "Count": 3}
        inventory.collected(info)
        self.assertEqual(inventory.count("zinc"), 3)
        info = {"Category": "raw", "Name": "zinc", "Count": 5}
        inventory.collected(info)
        self.assertEqual(inventory.count("zinc"), 8)

        info = {"Category": "raw", "Name": "polonium", "Count": 3}
        inventory.collected(info)
        self.assertEqual(inventory.count("zinc"), 8)
        self.assertEqual(inventory.count("polonium"), 3)

        info = {"Category": "manufactured", "Name": "highdensitycomposites", "Count": 3}
        inventory.collected(info)
        info = {"Category": "encoded", "Name": "shieldcyclerecordings", "Count": 3}
        inventory.collected(info)
        self.assertEqual(inventory.count("highdensitycomposites"), 3)
        self.assertEqual(inventory.count("shieldcyclerecordings"), 3)

        info = { "timestamp":"2018-10-31T04:03:19Z", "event":"MaterialCollected", "Category":"Manufactured", "Name":"tg_propulsionelement", "Name_Localised":"Propulsion Elements", "Count":3 }
        inventory.collected(info)
        self.assertEqual(inventory.count("tg_propulsionelement"), 3)
        self.assertEqual(inventory.count("Propulsion Elements"), 3)


    def test_discarded(self):
        inventory = EDRInventory()
        info = { "timestamp":"2019-01-02T11:03:33Z", "event":"Materials", "Raw":[ { "Name":"zinc", "Count":52 }, { "Name":"mercury", "Count":54 } ], "Manufactured":[ { "Name":"focuscrystals", "Name_Localised":"Focus Crystals", "Count":87 }, { "Name":"compoundshielding", "Name_Localised":"Compound Shielding", "Count":55 } ], "Encoded":[ { "Name":"classifiedscandata", "Name_Localised":"Classified Scan Fragment", "Count":63 }, { "Name":"securityfirmware", "Name_Localised":"Security Firmware Patch", "Count":78 } ] }
        inventory.initialize(info)
        info = {"Category": "raw", "Name": "zinc", "Count": 3}
        inventory.discarded(info)
        self.assertEqual(inventory.count("zinc"), 49)
        info = {"Category": "raw", "Name": "zinc", "Count": 52}
        inventory.discarded(info)
        self.assertEqual(inventory.count("zinc"), 0)
        info = {"Category": "raw", "Name": "zinc", "Count": 1}
        inventory.discarded(info)
        self.assertEqual(inventory.count("zinc"), 0)
        self.assertEqual(inventory.count("mercury"), 54)

        info = {"Category": "manufactured", "Name": "focuscrystals", "Count": 3}
        inventory.discarded(info)
        self.assertEqual(inventory.count("focuscrystals"), 84)
        info = {"Category": "manufactured", "Name": "focuscrystals", "Count": 84}
        inventory.discarded(info)
        self.assertEqual(inventory.count("focuscrystals"), 0)
        info = {"Category": "manufactured", "Name": "focuscrystals", "Count": 1}
        inventory.discarded(info)
        self.assertEqual(inventory.count("focuscrystals"), 0)
        self.assertEqual(inventory.count("compoundshielding"), 55)

        info = {"Category": "encoded", "Name": "classifiedscandata", "Count": 3}
        inventory.discarded(info)
        self.assertEqual(inventory.count("classifiedscandata"), 60)
        info = {"Category": "encoded", "Name": "classifiedscandata", "Count": 60}
        inventory.discarded(info)
        self.assertEqual(inventory.count("focuscrystals"), 0)
        info = {"Category": "encoded", "Name": "classifiedscandata", "Count": 1}
        inventory.discarded(info)
        self.assertEqual(inventory.count("classifiedscandata"), 0)
        self.assertEqual(inventory.count("securityfirmware"), 78)

    def test_slots(self):
        inventory = EDRInventory()
        self.assertEqual(inventory.slots("electrochemicalarrays"), 300)
        self.assertEqual(inventory.slots("niobium"), 200)
        self.assertEqual(inventory.slots("decodedemissiondata"), 150)
        self.assertEqual(inventory.slots("ancienttechnologicaldata"), 100)
        

    def test_consumed(self):
        inventory = EDRInventory()
        inventory.add("manufactured", "heatconductionwiring", 2)
        inventory.add("manufactured", "conductivecomponents", 3)
        event = { "timestamp":"2018-11-08T05:15:17Z", "event":"EngineerCraft", "Slot":"PowerPlant", "Module":"int_powerplant_size6_class3", "Ingredients":[ { "Name":"heatconductionwiring", "Name_Localised":"Heat Conduction Wiring", "Count":1 }, { "Name":"conductivecomponents", "Name_Localised":"Conductive Components", "Count":1 } ], "Engineer":"Hera Tani", "EngineerID":300090, "BlueprintID":128673766, "BlueprintName":"PowerPlant_Boosted", "Level":2, "Quality":0.852900, "Modifiers":[ { "Label":"Integrity", "Value":101.699997, "OriginalValue":113.000000, "LessIsGood":0 }, { "Label":"PowerCapacity", "Value":24.773701, "OriginalValue":21.000000, "LessIsGood":0 }, { "Label":"HeatEfficiency", "Value":0.550000, "OriginalValue":0.500000, "LessIsGood":1 } ] }
        inventory.consumed(event["Ingredients"])
        self.assertEqual(inventory.count("heatconductionwiring"), 1)
        self.assertEqual(inventory.count("conductivecomponents"), 2)

        event = { "timestamp":"2018-10-31T04:02:03Z", "event":"Synthesis", "Name":"Limpet Basic", "Materials":[ { "Name":"iron", "Count":10 }, { "Name":"nickel", "Count":10 } ] }
        inventory = EDRInventory()
        inventory.add("raw", "nickel", 11)
        inventory.add("raw", "iron", 13)
        inventory.consumed(event["Materials"])
        self.assertEqual(inventory.count("nickel"), 1)
        self.assertEqual(inventory.count("iron"), 3)

        
    
if __name__ == '__main__':
    main()