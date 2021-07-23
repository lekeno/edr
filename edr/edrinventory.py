# coding= utf-8
from __future__ import absolute_import

import pickle
import os

from edri18n import _
import utils2to3

class EDRInventory(object):
    EDR_INVENTORY_ENCODED_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'encoded_mats.v1.p')
    EDR_INVENTORY_RAW_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'raw_mats.v1.p')
    EDR_INVENTORY_MANUFACTURED_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'manufactured_mats.v1.p')
    EDR_INVENTORY_COMPONENT_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'component_mats.v1.p')  
    EDR_INVENTORY_ITEM_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'item_mats.v1.p')  
    EDR_INVENTORY_CONSUMABLE_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'consumables.v1.p')
    EDR_INVENTORY_DATA_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'data_mats.v1.p')
    EDR_INVENTORY_BACKPACK_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'backpack.v1.p')

    MATERIALS_LUT = {
        "zinc": {"localized": _(u"Zinc"), "raw": "Zinc", "category": "raw", "grade": 2},
        "mercury": {"localized": _(u"Mercury"), "raw": "Mercury", "category": "raw", "grade": 3},
        "polonium": {"localized": _(u"Polonium"), "raw": "Polonium", "category": "raw", "grade": 4},
        "tellurium": {"localized": _(u"Tellurium"), "raw": "Tellurium", "category": "raw", "grade": 4},
        "yttrium": {"localized": _(u"Yttrium"), "raw": "Yttrium", "category": "raw", "grade": 4},
        "antimony": {"localized": _(u"Antimony"), "raw": "Antimony", "category": "raw", "grade": 4},
        "selenium": {"localized": _(u"Selenium"), "raw": "Selenium", "category": "raw", "grade": 4},
        "ruthenium": {"localized": _(u"Ruthenium"), "raw": "Ruthenium", "category": "raw", "grade": 4},
        "zirconium": {"localized": _(u"Zirconium"), "raw": "Zirconium", "category": "raw", "grade": 2},
        "vanadium": {"localized": _(u"Vanadium"), "raw": "Vanadium", "category": "raw", "grade": 2},
        "manganese": {"localized": _(u"Manganese"), "raw": "Manganese", "category": "raw", "grade": 2},
        "chromium": {"localized": _(u"Chromium"), "raw": "Chromium", "category": "raw", "grade": 2},
        "molybdenum": {"localized": _(u"Molybdenum"), "raw": "Molybdenum", "category": "raw", "grade": 3},
        "technetium": {"localized": _(u"Technetium"), "raw": "Technetium", "category": "raw", "grade": 4},
        "tin": {"localized": _(u"Tin"), "raw": "Tin", "category": "raw", "grade": 3},
        "arsenic": {"localized": _(u"Arsenic"), "raw": "Arsenic", "category": "raw", "grade": 2},
        "cadmium": {"localized": _(u"Cadmium"), "raw": "Cadmium", "category": "raw", "grade": 3},
        "iron": {"localized": _(u"Iron"), "raw": "Iron", "category": "raw", "grade": 1},
        "niobium": {"localized": _(u"Niobium"), "raw": "Niobium", "category": "raw", "grade": 3},
        "phosphorus": {"localized": _(u"Phosphorus"), "raw": "Phosphorus", "category": "raw", "grade": 1},
        "germanium": {"localized": _(u"Germanium"), "raw": "Germanium", "category": "raw", "grade": 2},
        "tungsten": {"localized": _(u"Tungsten"), "raw": "Tungsten", "category": "raw", "grade": 3},
        "sulphur": {"localized": _(u"Sulphur"), "raw": "Sulphur", "category": "raw", "grade": 1},
        "carbon": {"localized": _(u"Carbon"), "raw": "Carbon", "category": "raw", "grade": 1},
        "nickel": {"localized": _(u"Nickel"), "raw": "Nickel", "category": "raw", "grade": 1},
        "rhenium": {"localized": _(u"Rhenium"), "raw": "Rhenium", "category": "raw", "grade": 1},
        "boron": {"localized": _(u"Boron"), "raw": "Boron", "category": "raw", "grade": 3},
        "lead": {"localized": _(u"Lead"), "raw": "Lead", "category": "raw", "grade": 1},
        "focuscrystals": {"localized": _(u"Focus Crystals"), "raw": "Focus Crystals", "category": "manufactured", "grade": 3},
        "compoundshielding": {"localized": _(u"Compound Shielding"), "raw": "Compound Shielding", "category": "manufactured", "grade": 4},
        "galvanisingalloys": {"localized": _(u"Galvanising Alloys"), "raw": "Galvanising Alloys", "category": "manufactured", "grade": 2},
        "heatvanes": {"localized": _(u"Heat Vanes"), "raw": "Heat Vanes", "category": "manufactured", "grade": 4},
        "configurablecomponents": {"localized": _(u"Configurable Components"), "raw": "Configurable Components", "category": "manufactured", "grade": 4},
        "biotechconductors": {"localized": _(u"Biotech Conductors"), "raw": "Biotech Conductors", "category": "manufactured", "grade": 5},
        "chemicalmanipulators": {"localized": _(u"Chemical Manipulators"), "raw": "Chemical Manipulators", "category": "manufactured", "grade": 4},
        "mechanicalcomponents": {"localized": _(u"Mechanical Components"), "raw": "Mechanical Components", "category": "manufactured", "grade": 3},
        "fedproprietarycomposites": {"localized": _(u"Proprietary Composites"), "raw": "Proprietary Composites", "category": "manufactured", "grade": 4},
        "highdensitycomposites": {"localized": _(u"High Density Composites"), "raw": "High Density Composites", "category": "manufactured", "grade": 3},
        "protoradiolicalloys": {"localized": _(u"Proto Radiolic Alloys"), "raw": "Proto Radiolic Alloys", "category": "manufactured", "grade": 5},
        "chemicaldistillery": {"localized": _(u"Chemical Distillery"), "raw": "Chemical Distillery", "category": "manufactured", "grade": 3},
        "chemicalprocessors": {"localized": _(u"Chemical Processors"), "raw": "Chemical Processors", "category": "manufactured", "grade": 2},
        "imperialshielding": {"localized": _(u"Imperial Shielding"), "raw": "Imperial Shielding", "category": "manufactured", "grade": 5},
        "gridresistors": {"localized": _(u"Grid Resistors"), "raw": "Grid Resistors", "category": "manufactured", "grade": 1},
        "heatconductionwiring": {"localized": _(u"Heat Conduction Wiring"), "raw": "Heat Conduction Wiring", "category": "manufactured", "grade": 1},
        "militarygradealloys": {"localized": _(u"Military Grade Alloys"), "raw": "Military Grade Alloys", "category": "manufactured", "grade": 5},
        "hybridcapacitors": {"localized": _(u"Hybrid Capacitors"), "raw": "Hybrid Capacitors", "category": "manufactured", "grade": 2},
        "heatexchangers": {"localized": _(u"Heat Exchangers"), "raw": "Heat Exchangers", "category": "manufactured", "grade": 3},
        "conductivepolymers": {"localized": _(u"Conductive Polymers"), "raw": "Conductive Polymers", "category": "manufactured", "grade": 4},
        "shieldingsensors": {"localized": _(u"Shielding Sensors"), "raw": "Shielding Sensors", "category": "manufactured", "grade": 3},
        "heatdispersionplate": {"localized": _(u"Heat Dispersion Plate"), "raw": "Heat Dispersion Plate", "category": "manufactured", "grade": 2},
        "electrochemicalarrays": {"localized": _(u"Electrochemical Arrays"), "raw": "Electrochemical Arrays", "category": "manufactured", "grade": 1},
        "conductiveceramics": {"localized": _(u"Conductive Ceramics"), "raw": "Conductive Ceramics", "category": "manufactured", "grade": 3},
        "conductivecomponents": {"localized": _(u"Conductive Components"), "raw": "Conductive Components", "category": "manufactured", "grade": 2},
        "militarysupercapacitors": {"localized": _(u"Military Supercapacitors"), "raw": "Military Supercapacitors", "category": "manufactured", "grade": 5},
        "mechanicalequipment": {"localized": _(u"Mechanical Equipment"), "raw": "Mechanical Equipment", "category": "manufactured", "grade": 2},
        "phasealloys": {"localized": _(u"Phase Alloys"), "raw": "Phase Alloys", "category": "manufactured", "grade": 3},
        "pharmaceuticalisolators": {"localized": _(u"Pharmaceutical Isolators"), "raw": "Pharmaceutical Isolators", "category": "manufactured", "grade": 5},
        "fedcorecomposites": {"localized": _(u"Core Dynamics Composites"), "raw": "Core Dynamics Composites", "category": "manufactured", "grade": 5},
        "basicconductors": {"localized": _(u"Basic Conductors"), "raw": "Basic Conductors", "category": "manufactured", "grade": 1},
        "mechanicalscrap": {"localized": _(u"Mechanical Scrap"), "raw": "Mechanical Scrap", "category": "manufactured", "grade": 1},
        "salvagedalloys": {"localized": _(u"Salvaged Alloys"), "raw": "Salvaged Alloys", "category": "manufactured", "grade": 1},
        "protolightalloys": {"localized": _(u"Proto Light Alloys"), "raw": "Proto Light Alloys", "category": "manufactured", "grade": 4},
        "refinedfocuscrystals": {"localized": _(u"Refined Focus Crystals"), "raw": "Refined Focus Crystals", "category": "manufactured", "grade": 4},
        "shieldemitters": {"localized": _(u"Shield Emitters"), "raw": "Shield Emitters", "category": "manufactured", "grade": 1},
        "precipitatedalloys": {"localized": _(u"Precipitated Alloys"), "raw": "Precipitated Alloys", "category": "manufactured", "grade": 3},
        "wornshieldemitters": {"localized": _(u"Worn Shield Emitters"), "raw": "Worn Shield Emitters", "category": "manufactured", "grade": 1},
        "exquisitefocuscrystals": {"localized": _(u"Exquisite Focus Crystals"), "raw": "Exquisite Focus Crystals", "category": "manufactured", "grade": 5},
        "polymercapacitors": {"localized": _(u"Polymer Capacitors"), "raw": "Polymer Capacitors", "category": "manufactured", "grade": 4},
        "thermicalloys": {"localized": _(u"Thermic Alloys"), "raw": "Thermic Alloys", "category": "manufactured", "grade": 4},
        "improvisedcomponents": {"localized": _(u"Improvised Components"), "raw": "Improvised Components", "category": "manufactured", "grade": 5},
        "crystalshards": {"localized": _(u"Crystal Shards"), "raw": "Crystal Shards", "category": "manufactured", "grade": 1},
        "heatresistantceramics": {"localized": _(u"Heat Resistant Ceramics"), "raw": "Heat Resistant Ceramics", "category": "manufactured", "grade": 2},
        "temperedalloys": {"localized": _(u"Tempered Alloys"), "raw": "Tempered Alloys", "category": "manufactured", "grade": 1},
        "uncutfocuscrystals": {"localized": _(u"Flawed Focus Crystals"), "raw": "Flawed Focus Crystals", "category": "manufactured", "grade": 2},
        "filamentcomposites": {"localized": _(u"Filament Composites"), "raw": "Filament Composites", "category": "manufactured", "grade": 2},
        "compactcomposites": {"localized": _(u"Compact Composites"), "raw": "Compact Composites", "category": "manufactured", "grade": 1},
        "chemicalstorageunits": {"localized": _(u"Chemical Storage Units"), "raw": "Chemical Storage Units", "category": "manufactured", "grade": 1},
        "protoheatradiators": {"localized": _(u"Proto Heat Radiators"), "raw": "Proto Heat Radiators", "category": "manufactured", "grade": 5},
        "guardian_powerconduit": {"localized": _(u"Guardian Power Conduit"), "raw": "Guardian Power Conduit", "category": "manufactured", "grade": 2},
        "guardian_powercell": {"localized": _(u"Guardian Power Cell"), "raw": "Guardian Power Cell", "category": "manufactured", "grade": 1},
        "guardian_techcomponent": {"localized": _(u"Guardian Technology Component"), "raw": "Guardian Technology Component", "category": "manufactured", "grade": 3},
        "guardian_sentinel_wreckagecomponents": {"localized": _(u"Guardian Wreckage Components"), "raw": "Guardian Wreckage Components", "category": "manufactured", "grade": 1},
        "guardian_sentinel_weaponparts": {"localized": _(u"Guardian Sentinel Weapon Parts"), "raw": "Guardian Sentinel Weapon Parts", "category": "manufactured", "grade": 3},
        "classifiedscandata": {"localized": _(u"Classified Scan Fragment"), "raw": "Classified Scan Fragment", "category": "encoded", "grade": 5},
        "securityfirmware": {"localized": _(u"Security Firmware Patch"), "raw": "Security Firmware Patch", "category": "encoded", "grade": 4},
        "dataminedwake": {"localized": _(u"Datamined Wake Exceptions"), "raw": "Datamined Wake Exceptions", "category": "encoded", "grade": 5},
        "compactemissionsdata": {"localized": _(u"Abnormal Compact Emissions Data"), "raw": "Abnormal Compact Emissions Data", "category": "encoded", "grade": 5},
        "shieldpatternanalysis": {"localized": _(u"Aberrant Shield Pattern Analysis"), "raw": "Aberrant Shield Pattern Analysis", "category": "encoded", "grade": 4},
        "adaptiveencryptors": {"localized": _(u"Adaptive Encryptors Capture"), "raw": "Adaptive Encryptors Capture", "category": "encoded", "grade": 5},
        "emissiondata": {"localized": _(u"Unexpected Emission Data"), "raw": "Unexpected Emission Data", "category": "encoded", "grade": 3},
        "industrialfirmware": {"localized": _(u"Cracked Industrial Firmware"), "raw": "Cracked Industrial Firmware", "category": "encoded", "grade": 3},
        "scandatabanks": {"localized": _(u"Classified Scan Databanks"), "raw": "Classified Scan Databanks", "category": "encoded", "grade": 3},
        "legacyfirmware": {"localized": _(u"Specialised Legacy Firmware"), "raw": "Specialised Legacy Firmware", "category": "encoded", "grade": 1},
        "embeddedfirmware": {"localized": _(u"Modified Embedded Firmware"), "raw": "Modified Embedded Firmware", "category": "encoded", "grade": 5},
        "shieldcyclerecordings": {"localized": _(u"Distorted Shield Cycle Recordings"), "raw": "Distorted Shield Cycle Recordings", "category": "encoded", "grade": 1},
        "decodedemissiondata": {"localized": _(u"Decoded Emission Data"), "raw": "Decoded Emission Data", "category": "encoded", "grade": 4},
        "bulkscandata": {"localized": _(u"Anomalous Bulk Scan Data"), "raw": "Anomalous Bulk Scan Data", "category": "encoded", "grade": 1},
        "scanarchives": {"localized": _(u"Unidentified Scan Archives"), "raw": "Unidentified Scan Archives", "category": "encoded", "grade": 2},
        "shieldsoakanalysis": {"localized": _(u"Inconsistent Shield Soak Analysis"), "raw": "Inconsistent Shield Soak Analysis", "category": "encoded", "grade": 2},
        "encodedscandata": {"localized": _(u"Divergent Scan Data"), "raw": "Divergent Scan Data", "category": "encoded", "grade": 4},
        "shielddensityreports": {"localized": _(u"Untypical Shield Scans"), "raw": "Untypical Shield Scans", "category": "encoded", "grade": 3},
        "shieldfrequencydata": {"localized": _(u"Peculiar Shield Frequency Data"), "raw": "Peculiar Shield Frequency Data", "category": "encoded", "grade": 5},
        "encryptioncodes": {"localized": _(u"Tagged Encryption Codes"), "raw": "Tagged Encryption Codes", "category": "encoded", "grade": 2},
        "consumerfirmware": {"localized": _(u"Modified Consumer Firmware"), "raw": "Modified Consumer Firmware", "category": "encoded", "grade": 2},
        "archivedemissiondata": {"localized": _(u"Irregular Emission Data"), "raw": "Irregular Emission Data", "category": "encoded", "grade": 2},
        "symmetrickeys": {"localized": _(u"Open Symmetric Keys"), "raw": "Open Symmetric Keys", "category": "encoded", "grade": 3},
        "encryptedfiles": {"localized": _(u"Unusual Encrypted Files"), "raw": "Unusual Encrypted Files", "category": "encoded", "grade": 1},
        "scrambledemissiondata": {"localized": _(u"Exceptional Scrambled Emission Data"), "raw": "Exceptional Scrambled Emission Data", "category": "encoded", "grade": 1},
        "fsdtelemetry": {"localized": _(u"Anomalous FSD Telemetry"), "raw": "Anomalous FSD Telemetry", "category": "encoded", "grade": 2},
        "hyperspacetrajectories": {"localized": _(u"Eccentric Hyperspace Trajectories"), "raw": "Eccentric Hyperspace Trajectories", "category": "encoded", "grade": 4},
        "disruptedwakeechoes": {"localized": _(u"Atypical Disrupted Wake Echoes"), "raw": "Atypical Disrupted Wake Echoes", "category": "encoded", "grade": 1},
        "wakesolutions": {"localized": _(u"Strange Wake Solutions"), "raw": "Strange Wake Solutions", "category": "encoded", "grade": 3},
        "encryptionarchives": {"localized": _(u"Atypical Encryption Archives"), "raw": "Atypical Encryption Archives", "category": "encoded", "grade": 4},
        "ancientbiologicaldata": {"localized": _(u"Pattern Alpha Obelisk Data"), "raw": "Pattern Alpha Obelisk Data", "category": "encoded", "grade": 3},
        "ancienthistoricaldata": {"localized": _(u"Pattern Gamma Obelisk Data"), "raw": "Pattern Gamma Obelisk Data", "category": "encoded", "grade": 4},
        "guardian_moduleblueprint": {"localized": _(u"Guardian Module Blueprint Fragment"), "raw": "Guardian Module Blueprint Fragment", "category": "encoded", "grade": 5},
        "ancientculturaldata": {"localized": _(u"Pattern Beta Obelisk Data"), "raw": "Pattern Beta Obelisk Data", "category": "encoded", "grade": 2},
        "ancientlanguagedata": {"localized": _(u"Pattern Delta Obelisk Data"), "raw": "Pattern Delta Obelisk Data", "category": "encoded", "grade": 4},
        "guardian_vesselblueprint": {"localized": _(u"Guardian Starship Blueprint Fragment"), "raw": "Guardian Starship Blueprint Fragment", "category": "encoded", "grade": 5},
        "guardian_weaponblueprint": {"localized": _(u"Guardian Weapon Blueprint Fragment"), "raw": "Guardian Weapon Blueprint Fragment", "category": "encoded", "grade": 5},
        "ancienttechnologicaldata": {"localized": _(u"Pattern Epsilon Obelisk Data"), "raw": "Pattern Epsilon Obelisk Data", "category": "encoded", "grade": 5},
        "tg_shipsystemsdata": {"localized": _(u"Ship Systems Data"), "raw": "Ship Systems Data", "category": "encoded", "grade": 3},
        "tg_shipflightdata": {"localized": _(u"Ship Flight Data"), "raw": "Ship Flight Data", "category": "encoded", "grade": 3},
        "unknownshipsignature": {"localized": _(u"Thargoid Ship Signature"), "raw": "Thargoid Ship Signature", "category": "encoded", "grade": 3},
        "tg_structuraldata": {"localized": _(u"Thargoid Structural Data"), "raw": "Thargoid Structural Data", "category": "encoded", "grade": 2},
        "unknownwakedata": {"localized": _(u"Thargoid Wake Data"), "raw": "Thargoid Wake Data", "category": "encoded", "grade": 4},
        "tg_biomechanicalconduits": {"localized": _(u"Bio-Mechanical Conduits"), "raw": "Bio-Mechanical Conduits", "category": "manufactured", "grade": 3},
        "tg_propulsionelement": {"localized": _(u"Propulsion Elements"), "raw": "Propulsion Elements", "category": "manufactured", "grade": 3},
        "unknowncarapace": {"localized": _(u"Thargoid Carapace"), "raw": "Thargoid Carapace", "category": "manufactured", "grade": 2},
        "unknownenergycell": {"localized": _(u"Thargoid Energy Cell"), "raw": "Thargoid Energy Cell", "category": "manufactured", "grade": 3},
        "unknownorganiccircuitry": {"localized": _(u"Thargoid Organic Circuitry"), "raw": "Thargoid Organic Circuitry", "category": "manufactured", "grade": 5},
        "unknowntechnologycomponents": {"localized": _(u"Thargoid Technological Components"), "raw": "Thargoid Technological Components", "category": "manufactured", "grade": 4},
        "bypass": { "localized": _(u"E-Breach"), "category": "consumable", "raw": "E-Breach", "grade":0},
        "largecapacitypowerregulator": { "localized": _(u"Power Regulator"), "category": "item", "raw": "Power Regulator", "grade":0},
        "chemicalinventory": { "localized": _(u"Chemical Inventory"), "category": "data", "raw": "Chemical Inventory", "grade":0},
        "dutyrota": { "localized": _(u"Duty Rota"), "category": "data", "raw": "Duty Rota", "grade":0},
        "evacuationprotocols": { "localized": _(u"Evacuation Protocols"), "category": "data", "raw": "Evacuation Protocols", "grade":0},
        "explorationjournals": { "localized": _(u"Exploration Journals"), "category": "data", "raw": "Exploration Journals", "grade":0},
        "factionnews": { "localized": _(u"Faction News"), "category": "data", "raw": "Faction News", "grade":0},
        "financialprojections": { "localized": _(u"Financial Projections"), "category": "data", "raw": "Financial Projections", "grade":0},
        "salesrecords": { "localized": _(u"Sales Records"), "category": "data", "raw": "Sales Records", "grade":0},
        "unionmembership": { "localized": _(u"Union Membership"), "category": "data", "raw": "Union Membership", "grade":0},
        "compactlibrary": { "localized": _(u"Compact Library"), "category": "item", "raw": "Compact Library", "grade":0},
        "infinity": { "localized": _(u"infinity"), "category": "item", "raw": "infinity", "grade":0},
        "insightentertainmentsuite": { "localized": _(u"Insight Entertainment Suite"), "category": "item", "raw": "Insight Entertainment Suite", "grade":0},
        "lazarus": { "localized": _(u"lazarus"), "category": "item", "raw": "lazarus", "grade":0},
        "energycell": { "localized": _(u"Energy Cell"), "category": "consumable", "raw": "Energy Cell", "grade":0},
        "healthpack": { "localized": _(u"Medkit"), "category": "consumable", "raw": "Medkit", "grade":0},
        "universaltranslator": { "localized": _(u"Universal Translator"), "category": "item", "raw": "Universal Translator", "grade":0},
        "biochemicalagent": { "localized": _(u"Biochemical Agent"), "category": "item", "raw": "Biochemical Agent", "grade":0},
        "degradedpowerregulator": { "localized": _(u"Degraded Power Regulator"), "category": "item", "raw": "Degraded Power Regulator", "grade":0},
        "hush": { "localized": _(u"Hush"), "category": "item", "raw": "Hush", "grade":0},
        "maintenancelogs": { "localized": _(u"Maintenance Logs"), "category": "data", "raw": "Maintenance Logs", "grade":0},
        "patrolroutes": { "localized": _(u"Patrol Routes"), "category": "data", "raw": "Patrol Routes", "grade":0},
        "push": { "localized": _(u"push"), "category": "item", "raw": "push", "grade":0},
        "settlementdefenceplans": { "localized": _(u"Settlement Defence Plans"), "category": "data", "raw": "Settlement Defence Plans", "grade":0},
        "surveilleancelogs": { "localized": _(u"Surveillance Logs"), "category": "data", "raw": "Surveillance Logs", "grade":0},
        "syntheticpathogen": { "localized": _(u"Synthetic Pathogen"), "category": "item", "raw": "Synthetic Pathogen", "grade":0},
        "buildingschematic": { "localized": _(u"Building Schematic"), "category": "item", "raw": "Building Schematic", "grade":0},
        "operationalmanual": { "localized": _(u"Operational Manual"), "category": "data", "raw": "Operational Manual", "grade":0},
        "blacklistdata": { "localized": _(u"Blacklist Data"), "category": "data", "raw": "Blacklist Data", "grade":0},
        "insight": { "localized": _(u"insight"), "category": "item", "raw": "insight", "grade":0},
        "airqualityreports": { "localized": _(u"Air Quality Reports"), "category": "data", "raw": "Air Quality Reports", "grade":0},
        "employeedirectory": { "localized": _(u"Employee Directory"), "category": "data", "raw": "Employee Directory", "grade":0},
        "factionassociates": { "localized": _(u"Faction Associates"), "category": "data", "raw": "Faction Associates", "grade":0},
        "meetingminutes": { "localized": _(u"Meeting Minutes"), "category": "data", "raw": "Meeting Minutes", "grade":0},
        "multimediaentertainment": { "localized": _(u"Multimedia Entertainment"), "category": "data", "raw": "Multimedia Entertainment", "grade":0},
        "networkaccesshistory": { "localized": _(u"Network Access History"), "category": "data", "raw": "Network Access History", "grade":0},
        "purchaserecords": { "localized": _(u"Purchase Records"), "category": "data", "raw": "Purchase Records", "grade":0},
        "radioactivitydata": { "localized": _(u"Radioactivity Data"), "category": "data", "raw": "Radioactivity Data", "grade":0},
        "residentialdirectory": { "localized": _(u"Residential Directory"), "category": "data", "raw": "Residential Directory", "grade":0},
        "shareholderinformation": { "localized": _(u"Shareholder Information"), "category": "data", "raw": "Shareholder Information", "grade":0},
        "travelpermits": { "localized": _(u"Travel Permits"), "category": "data", "raw": "Travel Permits", "grade":0},
        "accidentlogs": { "localized": _(u"Accident Logs"), "category": "data", "raw": "Accident Logs", "grade":0},
        "campaignplans": { "localized": _(u"Campaign Plans"), "category": "data", "raw": "Campaign Plans", "grade":0},
        "combattrainingmaterial": { "localized": _(u"Combat Training Material"), "category": "data", "raw": "Combat Training Material", "grade":0},
        "internalcorrespondence": { "localized": _(u"Internal Correspondence"), "category": "data", "raw": "Internal Correspondence", "grade":0},
        "payrollinformation": { "localized": _(u"Payroll Information"), "category": "data", "raw": "Payroll Information", "grade":0},
        "personallogs": { "localized": _(u"Personal Logs"), "category": "data", "raw": "Personal Logs", "grade":0},
        "weaponinventory": { "localized": _(u"Weapon Inventory"), "category": "data", "raw": "Weapon Inventory", "grade":0},
        "atmosphericdata": { "localized": _(u"Atmospheric Data"), "category": "data", "raw": "Atmospheric Data", "grade":0},
        "topographicalsurveys": { "localized": _(u"Topographical Surveys"), "category": "data", "raw": "Topographical Surveys", "grade":0},
        "literaryfiction": { "localized": _(u"Literary Fiction"), "category": "data", "raw": "Literary Fiction", "grade":0},
        "reactoroutputreview": { "localized": _(u"Reactor Output Review"), "category": "data", "raw": "Reactor Output Review", "grade":0},
        "nextofkinrecords": { "localized": _(u"Next of Kin Records"), "category": "data", "raw": "Next of Kin Records", "grade":0},
        "purchaserequests": { "localized": _(u"Purchase Requests"), "category": "data", "raw": "Purchase Requests", "grade":0},
        "taxrecords": { "localized": _(u"Tax Records"), "category": "data", "raw": "Tax Records", "grade":0},
        "visitorregister": { "localized": _(u"Visitor Register"), "category": "data", "raw": "Visitor Register", "grade":0},
        "pharmaceuticalpatents": { "localized": _(u"Pharmaceutical Patents"), "category": "data", "raw": "Pharmaceutical Patents", "grade":0},
        "vaccineresearch": { "localized": _(u"Vaccine Research"), "category": "data", "raw": "Vaccine Research", "grade":0},
        "virologydata": { "localized": _(u"Virology Data"), "category": "data", "raw": "Virology Data", "grade":0},
        "vaccinationrecords": { "localized": _(u"Vaccination Records"), "category": "data", "raw": "Vaccination Records", "grade":0},
        "censusdata": { "localized": _(u"Census Data"), "category": "data", "raw": "Census Data", "grade":0},
        "geographicaldata": { "localized": _(u"Geographical Data"), "category": "data", "raw": "Geographical Data", "grade":0},
        "mineralsurvey": { "localized": _(u"Mineral Survey"), "category": "data", "raw": "Mineral Survey", "grade":0},
        "chemicalformulae": { "localized": _(u"Chemical Formulae"), "category": "data", "raw": "Chemical Formulae", "grade":0},
        "amm_grenade_frag": { "localized": _(u"Frag Grenade"), "category": "consumable", "raw": "Frag Grenade", "grade":0},
        "amm_grenade_emp": { "localized": _(u"Shield Disruptor"), "category": "consumable", "raw": "Shield Disruptor", "grade":0},
        "amm_grenade_shield": { "localized": _(u"Shield Projector"), "category": "consumable", "raw": "Shield Projector", "grade":0},
        "chemicalexperimentdata": { "localized": _(u"Chemical Experiment Data"), "category": "data", "raw": "Chemical Experiment Data", "grade":0},
        "chemicalpatents": { "localized": _(u"Chemical Patents"), "category": "data", "raw": "Chemical Patents", "grade":0},
        "productionreports": { "localized": _(u"Production Reports"), "category": "data", "raw": "Production Reports", "grade":0},
        "productionschedule": { "localized": _(u"Production Schedule"), "category": "data", "raw": "Production Schedule", "grade":0},
        "bloodtestresults": { "localized": _(u"Blood Test Results"), "category": "data", "raw": "Blood Test Results", "grade":0},
        "combatantperformance": { "localized": _(u"Combatant Performance"), "category": "data", "raw": "Combatant Performance", "grade":0},
        "troopdeploymentrecords": { "localized": _(u"Troop Deployment Records"), "category": "data", "raw": "Troop Deployment Records", "grade":0},
        "catmedia": { "localized": _(u"Cat Media"), "category": "data", "raw": "Cat Media", "grade":0},
        "employeegeneticdata": { "localized": _(u"Employee Genetic Data"), "category": "data", "raw": "Employee Genetic Data", "grade":0},
        "factiondonatorlist": { "localized": _(u"Faction Donator List"), "category": "data", "raw": "Faction Donator List", "grade":0},
        "nocdata": { "localized": _(u"NOC Data"), "category": "data", "raw": "NOC Data", "grade":0},
        "trueformfossil": { "localized": _(u"True Form Fossil"), "category": "item", "raw": "True Form Fossil", "grade":0},
        "healthmonitor": { "localized": _(u"Health Monitor"), "category": "item", "raw": "Health Monitor", "grade":0},
        "nutritionalconcentrate": { "localized": _(u"Nutritional Concentrate"), "category": "item", "raw": "Nutritional Concentrate", "grade":0},
        "personaldocuments": { "localized": _(u"Personal Documents"), "category": "item", "raw": "Personal Documents", "grade":0},
        "chemicalsample": { "localized": _(u"Chemical Sample"), "category": "item", "raw": "Chemical Sample", "grade":0},
        "insightdatabank": { "localized": _(u"Insight Data Bank"), "category": "item", "raw": "Insight Data Bank", "grade":0},
        "ionisedgas": { "localized": _(u"Ionised Gas"), "category": "item", "raw": "Ionised Gas", "grade":0},
        "personalcomputer": { "localized": _(u"Personal Computer"), "category": "item", "raw": "Personal Computer", "grade":0},
        "shipschematic": { "localized": _(u"Ship Schematic"), "category": "item", "raw": "Ship Schematic", "grade":0},
        "suitschematic": { "localized": _(u"Suit Schematic"), "category": "item", "raw": "Suit Schematic", "grade":0},
        "vehicleschematic": { "localized": _(u"Vehicle Schematic"), "category": "item", "raw": "Vehicle Schematic", "grade":0},
        "weaponschematic": { "localized": _(u"Weapon Schematic"), "category": "item", "raw": "Weapon Schematic", "grade":0},
        "inertiacanister": { "localized": _(u"Inertia Canister"), "category": "item", "raw": "Inertia Canister", "grade":0},
        "surveillanceequipment": { "localized": _(u"Surveillance Equipment"), "category": "item", "raw": "Surveillance Equipment", "grade":0},
        "deepmantlesample": { "localized": _(u"Deep Mantle Sample"), "category": "item", "raw": "Deep Mantle Sample", "grade":0},
        "microbialinhibitor": { "localized": _(u"Microbial Inhibitor"), "category": "item", "raw": "Microbial Inhibitor", "grade":0},
        "castfossil": { "localized": _(u"Cast Fossil"), "category": "item", "raw": "Cast Fossil", "grade":0},
        "petrifiedfossil": { "localized": _(u"Petrified Fossil"), "category": "item", "raw": "Petrified Fossil", "grade":0},
        "agriculturalprocesssample": { "localized": _(u"Agricultural Process Sample"), "category": "item", "raw": "Agricultural Process Sample", "grade":0},
        "chemicalprocesssample": { "localized": _(u"Chemical Process Sample"), "category": "item", "raw": "Chemical Process Sample", "grade":0},
        "refinementprocesssample": { "localized": _(u"Refinement Process Sample"), "category": "item", "raw": "Refinement Process Sample", "grade":0},
        "microsupercapacitor": { "localized": _(u"Micro Supercapacitor"), "category": "component", "raw": "Micro Supercapacitor", "grade":0},
        "microtransformer": { "localized": _(u"Micro Transformer"), "category": "component", "raw": "Micro Transformer", "grade":0},
        "chemicalsuperbase": { "localized": _(u"Chemical Superbase"), "category": "component", "raw": "Chemical Superbase", "grade":0},
        "circuitswitch": { "localized": _(u"Circuit Switch"), "category": "component", "raw": "Circuit Switch", "grade":0},
        "electricalwiring": { "localized": _(u"Electrical Wiring"), "category": "component", "raw": "Electrical Wiring", "grade":0},
        "encryptedmemorychip": { "localized": _(u"Encrypted Memory Chip"), "category": "component", "raw": "Encrypted Memory Chip", "grade":0},
        "epoxyadhesive": { "localized": _(u"Epoxy Adhesive"), "category": "component", "raw": "Epoxy Adhesive", "grade":0},
        "memorychip": { "localized": _(u"Memory Chip"), "category": "component", "raw": "Memory Chip", "grade":0},
        "microhydraulics": { "localized": _(u"Micro Hydraulics"), "category": "component", "raw": "Micro Hydraulics", "grade":0},
        "opticalfibre": { "localized": _(u"Optical Fibre"), "category": "component", "raw": "Optical Fibre", "grade":0},
        "titaniumplating": { "localized": _(u"Titanium Plating"), "category": "component", "raw": "Titanium Plating", "grade":0},
        "phneutraliser": { "localized": _(u"pH Neutraliser"), "category": "component", "raw": "pH Neutraliser", "grade":0},
        "metalcoil": { "localized": _(u"Metal Coil"), "category": "component", "raw": "Metal Coil", "grade":0},
        "viscoelasticpolymer": { "localized": _(u"Viscoelastic Polymer"), "category": "component", "raw": "Viscoelastic Polymer", "grade":0},
        "ionbattery": { "localized": _(u"Ion Battery"), "category": "component", "raw": "Ion Battery", "grade":0},
        "chemicalcatalyst": { "localized": _(u"Chemical Catalyst"), "category": "component", "raw": "Chemical Catalyst", "grade":0},
        "electricalfuse": { "localized": _(u"Electrical Fuse"), "category": "component", "raw": "Electrical Fuse", "grade":0},
        "opticallens": { "localized": _(u"Optical Lens"), "category": "component", "raw": "Optical Lens", "grade":0},
        "weaponcomponent": { "localized": _(u"Weapon Component"), "category": "component", "raw": "Weapon Component", "grade":0},
        "carbonfibreplating": { "localized": _(u"Carbon Fibre Plating"), "category": "component", "raw": "Carbon Fibre Plating", "grade":0},
        "microthrusters": { "localized": _(u"Micro Thrusters"), "category": "component", "raw": "Micro Thrusters", "grade":0},
        "oxygenicbacteria": { "localized": _(u"Oxygenic Bacteria"), "category": "component", "raw": "Oxygenic Bacteria", "grade":0},
        "circuitboard": { "localized": _(u"Circuit Board"), "category": "component", "raw": "Circuit Board", "grade":0},
        "tungstencarbide": { "localized": _(u"Tungsten Carbide"), "category": "component", "raw": "Tungsten Carbide", "grade":0},
        "ballisticsdata": { "localized": _(u"Ballistics Data"), "category": "data", "raw": "Ballistics Data", "grade":0},
        "politicalaffiliations": { "localized": _(u"Political Affiliations"), "category": "data", "raw": "Political Affiliations", "grade":0},
        "conflicthistory": { "localized": _(u"Conflict History"), "category": "data", "raw": "Conflict History", "grade":0},
        "riskassessments": { "localized": _(u"Risk Assessments"), "category": "data", "raw": "Risk Assessments", "grade":0},
        "stellaractivitylogs": { "localized": _(u"Stellar Activity Logs"), "category": "data", "raw": "Stellar Activity Logs", "grade":0},
        "manufacturinginstructions": { "localized": _(u"Manufacturing Instructions"), "category": "data", "raw": "Manufacturing Instructions", "grade":0},
        "digitaldesigns": { "localized": _(u"Digital Designs"), "category": "data", "raw": "Digital Designs", "grade":0},
        "medicalrecords": { "localized": _(u"Medical Records"), "category": "data", "raw": "Medical Records", "grade":0},
        "employmenthistory": { "localized": _(u"Employment History"), "category": "data", "raw": "Employment History", "grade":0},
        "vipsecuritydetail": { "localized": _(u"VIP Security Detail"), "category": "data", "raw": "VIP Security Detail", "grade":0},
        "classicentertainment": { "localized": _(u"Classic Entertainment"), "category": "data", "raw": "Classic Entertainment", "grade":0},
        "photoalbums": { "localized": _(u"Photo Albums"), "category": "data", "raw": "Photo Albums", "grade":0},
        "biometricdata": { "localized": _(u"Biometric Data"), "category": "data", "raw": "Biometric Data", "grade":0},
        "extractionyielddata": { "localized": _(u"Extraction Yield Data"), "category": "data", "raw": "Extraction Yield Data", "grade":0},
        "securityexpenses": { "localized": _(u"Security Expenses"), "category": "data", "raw": "Security Expenses", "grade":0},
        "culinaryrecipes": { "localized": _(u"Culinary Recipes"), "category": "data", "raw": "Culinary Recipes", "grade":0},
        "fleetregistry": { "localized": _(u"Fleet Registry"), "category": "data", "raw": "Fleet Registry", "grade":0},
        "influenceprojections": { "localized": _(u"Influence Projections"), "category": "data", "raw": "Influence Projections", "grade":0},
        "cocktailrecipes": { "localized": _(u"Cocktail Recipes"), "category": "data", "raw": "Cocktail Recipes", "grade":0},
        "employeeexpenses": { "localized": _(u"Employee Expenses"), "category": "data", "raw": "Employee Expenses", "grade":0},
        "interviewrecordings": { "localized": _(u"Interview Recordings"), "category": "data", "raw": "Interview Recordings", "grade":0},
        "recyclinglogs": { "localized": _(u"Recycling Logs"), "category": "data", "raw": "Recycling Logs", "grade":0},
        "jobapplications": { "localized": _(u"Job Applications"), "category": "data", "raw": "Job Applications", "grade":0},
        "californium": { "localized": _(u"Californium"), "category": "item", "raw": "Californium", "grade":0},
        "pyrolyticcatalyst": { "localized": _(u"Pyrolytic catalyst"), "category": "item", "raw": "Pyrolytic catalyst", "grade":0},
        "spyware": { "localized": _(u"Spyware"), "category": "data", "raw": "Spyware", "grade":0},
        "tacticalplans": { "localized": _(u"Tactical Plans"), "category": "data", "raw": "Tactical plans", "grade":0},
        "virus": { "localized": _(u"Virus"), "category": "data", "raw": "Virus", "grade":0},
        "aerogel": { "localized": _(u"Aerogel"), "category": "component", "raw": "Aerogel", "grade":0},
        "geneticrepairmeds": { "localized": _(u"Genetic Repair Meds"), "category": "item", "raw": "Genetic Repair Meds", "grade":0},
        "cropyieldanalysis": { "localized": _(u"Crop Yield Analysis"), "category": "data", "raw": "Crop Yield Analysis", "grade":0},
        "kompromat": { "localized": _(u"Kompromat"), "category": "data", "raw": "Kompromat", "grade":0},
        "xenodefenceprotocols":  { "localized": _(u"Xeno Defence Protocols"), "category": "data", "raw": "Xeno Defence Protocols", "grade":0},
        "geologicaldata":  { "localized": _(u"Geological Data"), "category": "data", "raw": "Geological Data", "grade":0},
        "opinionpolls":  { "localized": _(u"Opinion Polls"), "category": "data", "raw": "Opinion Polls", "grade":0},
        "propaganda":  { "localized": _(u"Propaganda"), "category": "data", "raw": "Propaganda", "grade":0},

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
        u'proto radiolic alloys': 'protoradiolicalloys', u'proto heat radiators': 'protoheatradiators', u'cadmium': 'cadmium', u'filament composites': 'filamentcomposites', u'exquisite focus crystals': 'exquisitefocuscrystals', u'electrochemical arrays': 'electrochemicalarrays', 
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

        try:
            with open(self.EDR_INVENTORY_COMPONENT_CACHE, 'rb') as handle:
                self.components = pickle.load(handle)
        except:
            self.components = {}

        try:
            with open(self.EDR_INVENTORY_ITEM_CACHE, 'rb') as handle:
                self.items = pickle.load(handle)
        except:
            self.items = {}

        try:
            with open(self.EDR_INVENTORY_CONSUMABLE_CACHE, 'rb') as handle:
                self.consumables = pickle.load(handle)
        except:
            self.consumables = {}

        try:
            with open(self.EDR_INVENTORY_DATA_CACHE, 'rb') as handle:
                self.data = pickle.load(handle)
        except:
            self.data = {}

        try:
            with open(self.EDR_INVENTORY_BACKPACK_CACHE, 'rb') as handle:
                self.backpack = pickle.load(handle)
        except:
            self.backpack = {}
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

        for thing in materials.get("Items", []):
            cname = self.__c_name(thing["Name"])
            self.items[cname] = thing["Count"]

        for thing in materials.get("Components", []):
            cname = self.__c_name(thing["Name"])
            self.components[cname] = thing["Count"]

        for thing in materials.get("Data", []):
            cname = self.__c_name(thing["Name"])
            self.data[cname] = thing["Count"]

        for thing in materials.get("Consumables", []):
            cname = self.__c_name(thing["Name"])
            self.consumables[cname] = thing["Count"]

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

        for thing in state.get("Component", {}):
            cname = self.__c_name(thing)
            self.components[cname] = state["Component"][thing]

        for thing in state.get("Item", {}):
            cname = self.__c_name(thing)
            self.items[cname] = state["Item"][thing]

        for thing in state.get("Consumable", {}):
            cname = self.__c_name(thing)
            self.consumables[cname] = state["Consumable"][thing]

        for thing in state.get("Data", {}):
            cname = self.__c_name(thing)
            self.data[cname] = state["Data"][thing]

        backpack = state.get("BackPack", {})
        for category in backpack:
            ccategory = category.lower()
            self.backpack[ccategory] = {}
            for thing in backpack[category]:
                cname = self.__c_name(thing)
                self.backpack[ccategory][cname] = backpack[category][thing]

        self.initialized = True
        self.inconsistencies = False

    def stale_or_incorrect(self):
        self.__check()
        return not self.initialized or self.inconsistencies

    def persist(self):
        with open(self.EDR_INVENTORY_ENCODED_CACHE, 'wb') as handle:
            pickle.dump(self.encoded, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_MANUFACTURED_CACHE, 'wb') as handle:
            pickle.dump(self.manufactured, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_RAW_CACHE, 'wb') as handle:
            pickle.dump(self.raw, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_CONSUMABLE_CACHE, 'wb') as handle:
            pickle.dump(self.consumables, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_ITEM_CACHE, 'wb') as handle:
            pickle.dump(self.items, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_DATA_CACHE, 'wb') as handle:
            pickle.dump(self.data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_COMPONENT_CACHE, 'wb') as handle:
            pickle.dump(self.components, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INVENTORY_BACKPACK_CACHE, 'wb') as handle:
            pickle.dump(self.backpack, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def all_in_locker(self):
        return {**self.items, **self.consumables, **self.data, **self.components}

    def all_in_backpack(self):
        return {**self.backpack.get("item",{}), **self.backpack.get("consumable",{}), **self.backpack.get("data",{}), **self.backpack.get("component",{})}

    def bought(self, info):
        self.add(info["Category"], info["Name"], info["Count"])

    def sold(self, info):
        if "MicroResources" not in info:
            self.substract(info["Category"], info["Name"], info["Count"])
            return

        for resource in info["MicroResources"]: 
            self.substract(resource["Category"], resource["Name"], resource["Count"])

    def transferred(self, info):
        if "Transfers" not in info:
            return

        for transfer in info["Transfers"]:
            self.set(transfer["Category"], transfer["Name"], transfer.get("NewCount", transfer.get("Count", 0)))
            self.adjust_backpack(transfer["Category"], transfer["Name"], transfer.get("OldCount", 0) - transfer.get("NewCount", 0))

    def backpack_change(self, info):
        if "Added" in info:
            for addition in info["Added"]:
                self.adjust_backpack(addition["Type"], addition["Name"], addition.get("Count", 0))
        
        if "Removed" in info:
            for removal in info["Removed"]:
                self.adjust_backpack(removal["Type"], removal["Name"], -removal.get("Count", 0))


    def traded(self, info):
        if "Offered" not in info:
            return

        for offer in info["Offered"]:
            self.substract(offer["Category"], offer["Name"], offer["Count"])

        self.add(info["Category"], info["Received"], info["Count"])
    
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
        elif category == "item":
            return self.items.get(cname, 0) + self.count_backpack(name)
        elif category == "component":
            return self.components.get(cname, 0) + self.count_backpack(name)
        elif category == "data":
            return self.data.get(cname, 0) + self.count_backpack(name)
        elif category == "consumables":
            return self.consumables.get(cname, 0) + self.count_backpack(name)
        return 0

    def count_backpack(self, name):
        cname = self.__c_name(name)
        category = self.category(cname)
        if category not in self.backpack:
            return 0
        return self.backpack[category].get(cname, 0)

    def oneliner(self, name, from_backpack):
        cname = self.__c_name(name)
        category = self.category(cname)
        entry = self.MATERIALS_LUT.get(cname, None)
        if not category or not entry:
            return name
        total_count = self.count(name)
        count = total_count
        if from_backpack:
            count = self.count_backpack(name)

        if category in ["encoded", "raw", "manufactured"]:
            grades = [u"?", u"Ⅰ", u"Ⅱ", u"Ⅲ", u"Ⅳ", u"Ⅴ"]
            slots = [u"?", u"300", u"250", u"200", u"150", u"100"]
            return u"{} (Grade {}; {}/{})".format(_(entry["raw"]), grades[entry["grade"]], total_count, slots[entry["grade"]])
        
        if from_backpack:
            return u"{} ({}/{})".format(_(entry["raw"]), count, total_count)
        return u"{} ({})".format(_(entry["raw"]), total_count)


    def __check(self):
        self.inconsistencies = False
        for collection in [self.encoded, self.raw, self.manufactured]:
            for thing in collection:
                self.__check_item(thing)
                if self.inconsistencies:
                    return False

        for collection in [self.items, self.data, self.components]:
            tally = 0
            for thing in collection:
                count = self.count(thing)
                if count < 0:
                    self.inconsistencies = True
                    break
                tally += count
            if tally > 1000:
                self.inconsistencies = True
                break

        return self.inconsistencies
    
    def __check_item(self, name):
        cname = self.__c_name(name)
        entry = self.MATERIALS_LUT.get(cname, None)
        if not entry:
            return False
        count = self.count(cname)
        if count < 0:
            self.inconsistencies = True
            return False
        
        if self.category(name) in ["raw", "manufactured", "encoded"]:
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
        self.add(received["Category"], received["Material"], received["Quantity"])

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
        elif ccategory == "data":
            self.data[cname] = min(self.data.get(cname, 0) + count, 1000)
        elif ccategory == "item":
            self.items[cname] = min(self.items.get(cname, 0) + count, 1000)
        elif ccategory == "component":
            self.components[cname] = min(self.components.get(cname, 0) + count, 1000)
        elif ccategory == "consumable":
            self.consumables[cname] = min(self.consumables.get(cname, 0) + count, 1000)

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
        elif ccategory == "data":
            self.data[cname] = max(self.data.get(cname, 0) - count, 0)
        elif ccategory == "item":
            self.items[cname] = max(self.items.get(cname, 0) - count, 0)
        elif ccategory == "component":
            self.components[cname] = max(self.components.get(cname, 0) - count, 0)
        elif ccategory == "consumable":
            self.consumables[cname] = max(self.consumables.get(cname, 0) - count, 0)


    def set(self, category, name, newcount):
        ccategory = self.__c_cat(category)
        cname = self.__c_name(name)
        if ccategory == "encoded":
            self.encoded[cname] = newcount
        elif ccategory == "raw":
            self.raw[cname] = newcount
        elif ccategory == "manufactured":
            self.manufactured[cname] = newcount
        elif ccategory == "data":
            self.data[cname] = newcount
        elif ccategory == "item":
            self.items[cname] = newcount
        elif ccategory == "component":
            self.components[cname] = newcount
        elif ccategory == "consumable":
            self.consumables[cname] = newcount

    def adjust_backpack(self, category, name, count):
        ccategory = category.lower()
        if ccategory not in self.backpack:
            self.backpack[ccategory] = {}
        self.backpack[ccategory][name] = max(self.backpack[ccategory].get(name, 0) + count, 0)

    def category(self, name):
        cname = self.__c_name(name)
        entry = self.MATERIALS_LUT.get(cname, None)
        return entry["category"] if entry else None

    @staticmethod
    def readable(name):
        cname = name.lower()
        if cname in EDRInventory.MATERIALS_LUT:
           return EDRInventory.MATERIALS_LUT[cname].get("localized", name)
        return name

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