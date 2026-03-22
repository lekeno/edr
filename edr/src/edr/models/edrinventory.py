import pickle
import os
import re
import json

from edr.core.edri18n import _ # EDR_INTERNAL
from edr.utils.edtime import EDTime # EDR_INTERNAL
from edr.utils.edrpath import edr_data_path, edr_cache_path # EDR_INTERNAL

#TODO anarchy only microresources...
ODYSSEY_MATS = json.loads(open(edr_data_path('odyssey_mats.json')).read())

HORIZONS_MATS = json.loads(open(edr_data_path('horizons_mats.json')).read())

MATERIALS_LUT = {
    "zinc": {"localized": _("Zinc"), "raw": "Zinc", "category": "raw", "grade": 2},
    "mercury": {"localized": _("Mercury"), "raw": "Mercury", "category": "raw", "grade": 3},
    "polonium": {"localized": _("Polonium"), "raw": "Polonium", "category": "raw", "grade": 4},
    "tellurium": {"localized": _("Tellurium"), "raw": "Tellurium", "category": "raw", "grade": 4},
    "yttrium": {"localized": _("Yttrium"), "raw": "Yttrium", "category": "raw", "grade": 4},
    "antimony": {"localized": _("Antimony"), "raw": "Antimony", "category": "raw", "grade": 4},
    "selenium": {"localized": _("Selenium"), "raw": "Selenium", "category": "raw", "grade": 4},
    "ruthenium": {"localized": _("Ruthenium"), "raw": "Ruthenium", "category": "raw", "grade": 4},
    "zirconium": {"localized": _("Zirconium"), "raw": "Zirconium", "category": "raw", "grade": 2},
    "vanadium": {"localized": _("Vanadium"), "raw": "Vanadium", "category": "raw", "grade": 2},
    "manganese": {"localized": _("Manganese"), "raw": "Manganese", "category": "raw", "grade": 2},
    "chromium": {"localized": _("Chromium"), "raw": "Chromium", "category": "raw", "grade": 2},
    "molybdenum": {"localized": _("Molybdenum"), "raw": "Molybdenum", "category": "raw", "grade": 3},
    "technetium": {"localized": _("Technetium"), "raw": "Technetium", "category": "raw", "grade": 4},
    "tin": {"localized": _("Tin"), "raw": "Tin", "category": "raw", "grade": 3},
    "arsenic": {"localized": _("Arsenic"), "raw": "Arsenic", "category": "raw", "grade": 2},
    "cadmium": {"localized": _("Cadmium"), "raw": "Cadmium", "category": "raw", "grade": 3},
    "iron": {"localized": _("Iron"), "raw": "Iron", "category": "raw", "grade": 1},
    "niobium": {"localized": _("Niobium"), "raw": "Niobium", "category": "raw", "grade": 3},
    "phosphorus": {"localized": _("Phosphorus"), "raw": "Phosphorus", "category": "raw", "grade": 1},
    "germanium": {"localized": _("Germanium"), "raw": "Germanium", "category": "raw", "grade": 2},
    "tungsten": {"localized": _("Tungsten"), "raw": "Tungsten", "category": "raw", "grade": 3},
    "sulphur": {"localized": _("Sulphur"), "raw": "Sulphur", "category": "raw", "grade": 1},
    "carbon": {"localized": _("Carbon"), "raw": "Carbon", "category": "raw", "grade": 1},
    "nickel": {"localized": _("Nickel"), "raw": "Nickel", "category": "raw", "grade": 1},
    "rhenium": {"localized": _("Rhenium"), "raw": "Rhenium", "category": "raw", "grade": 1},
    "boron": {"localized": _("Boron"), "raw": "Boron", "category": "raw", "grade": 3},
    "lead": {"localized": _("Lead"), "raw": "Lead", "category": "raw", "grade": 1},
    "focuscrystals": {"localized": _("Focus Crystals"), "raw": "Focus Crystals", "category": "manufactured", "grade": 3},
    "compoundshielding": {"localized": _("Compound Shielding"), "raw": "Compound Shielding", "category": "manufactured", "grade": 4},
    "galvanisingalloys": {"localized": _("Galvanising Alloys"), "raw": "Galvanising Alloys", "category": "manufactured", "grade": 2},
    "heatvanes": {"localized": _("Heat Vanes"), "raw": "Heat Vanes", "category": "manufactured", "grade": 4},
    "configurablecomponents": {"localized": _("Configurable Components"), "raw": "Configurable Components", "category": "manufactured", "grade": 4},
    "biotechconductors": {"localized": _("Biotech Conductors"), "raw": "Biotech Conductors", "category": "manufactured", "grade": 5},
    "chemicalmanipulators": {"localized": _("Chemical Manipulators"), "raw": "Chemical Manipulators", "category": "manufactured", "grade": 4},
    "mechanicalcomponents": {"localized": _("Mechanical Components"), "raw": "Mechanical Components", "category": "manufactured", "grade": 3},
    "fedproprietarycomposites": {"localized": _("Proprietary Composites"), "raw": "Proprietary Composites", "category": "manufactured", "grade": 4},
    "highdensitycomposites": {"localized": _("High Density Composites"), "raw": "High Density Composites", "category": "manufactured", "grade": 3},
    "protoradiolicalloys": {"localized": _("Proto Radiolic Alloys"), "raw": "Proto Radiolic Alloys", "category": "manufactured", "grade": 5},
    "chemicaldistillery": {"localized": _("Chemical Distillery"), "raw": "Chemical Distillery", "category": "manufactured", "grade": 3},
    "chemicalprocessors": {"localized": _("Chemical Processors"), "raw": "Chemical Processors", "category": "manufactured", "grade": 2},
    "imperialshielding": {"localized": _("Imperial Shielding"), "raw": "Imperial Shielding", "category": "manufactured", "grade": 5},
    "gridresistors": {"localized": _("Grid Resistors"), "raw": "Grid Resistors", "category": "manufactured", "grade": 1},
    "heatconductionwiring": {"localized": _("Heat Conduction Wiring"), "raw": "Heat Conduction Wiring", "category": "manufactured", "grade": 1},
    "militarygradealloys": {"localized": _("Military Grade Alloys"), "raw": "Military Grade Alloys", "category": "manufactured", "grade": 5},
    "hybridcapacitors": {"localized": _("Hybrid Capacitors"), "raw": "Hybrid Capacitors", "category": "manufactured", "grade": 2},
    "heatexchangers": {"localized": _("Heat Exchangers"), "raw": "Heat Exchangers", "category": "manufactured", "grade": 3},
    "conductivepolymers": {"localized": _("Conductive Polymers"), "raw": "Conductive Polymers", "category": "manufactured", "grade": 4},
    "shieldingsensors": {"localized": _("Shielding Sensors"), "raw": "Shielding Sensors", "category": "manufactured", "grade": 3},
    "heatdispersionplate": {"localized": _("Heat Dispersion Plate"), "raw": "Heat Dispersion Plate", "category": "manufactured", "grade": 2},
    "electrochemicalarrays": {"localized": _("Electrochemical Arrays"), "raw": "Electrochemical Arrays", "category": "manufactured", "grade": 1},
    "conductiveceramics": {"localized": _("Conductive Ceramics"), "raw": "Conductive Ceramics", "category": "manufactured", "grade": 3},
    "conductivecomponents": {"localized": _("Conductive Components"), "raw": "Conductive Components", "category": "manufactured", "grade": 2},
    "militarysupercapacitors": {"localized": _("Military Supercapacitors"), "raw": "Military Supercapacitors", "category": "manufactured", "grade": 5},
    "mechanicalequipment": {"localized": _("Mechanical Equipment"), "raw": "Mechanical Equipment", "category": "manufactured", "grade": 2},
    "phasealloys": {"localized": _("Phase Alloys"), "raw": "Phase Alloys", "category": "manufactured", "grade": 3},
    "pharmaceuticalisolators": {"localized": _("Pharmaceutical Isolators"), "raw": "Pharmaceutical Isolators", "category": "manufactured", "grade": 5},
    "fedcorecomposites": {"localized": _("Core Dynamics Composites"), "raw": "Core Dynamics Composites", "category": "manufactured", "grade": 5},
    "basicconductors": {"localized": _("Basic Conductors"), "raw": "Basic Conductors", "category": "manufactured", "grade": 1},
    "mechanicalscrap": {"localized": _("Mechanical Scrap"), "raw": "Mechanical Scrap", "category": "manufactured", "grade": 1},
    "salvagedalloys": {"localized": _("Salvaged Alloys"), "raw": "Salvaged Alloys", "category": "manufactured", "grade": 1},
    "protolightalloys": {"localized": _("Proto Light Alloys"), "raw": "Proto Light Alloys", "category": "manufactured", "grade": 4},
    "refinedfocuscrystals": {"localized": _("Refined Focus Crystals"), "raw": "Refined Focus Crystals", "category": "manufactured", "grade": 4},
    "shieldemitters": {"localized": _("Shield Emitters"), "raw": "Shield Emitters", "category": "manufactured", "grade": 1},
    "precipitatedalloys": {"localized": _("Precipitated Alloys"), "raw": "Precipitated Alloys", "category": "manufactured", "grade": 3},
    "wornshieldemitters": {"localized": _("Worn Shield Emitters"), "raw": "Worn Shield Emitters", "category": "manufactured", "grade": 1},
    "exquisitefocuscrystals": {"localized": _("Exquisite Focus Crystals"), "raw": "Exquisite Focus Crystals", "category": "manufactured", "grade": 5},
    "polymercapacitors": {"localized": _("Polymer Capacitors"), "raw": "Polymer Capacitors", "category": "manufactured", "grade": 4},
    "thermicalloys": {"localized": _("Thermic Alloys"), "raw": "Thermic Alloys", "category": "manufactured", "grade": 4},
    "improvisedcomponents": {"localized": _("Improvised Components"), "raw": "Improvised Components", "category": "manufactured", "grade": 5},
    "crystalshards": {"localized": _("Crystal Shards"), "raw": "Crystal Shards", "category": "manufactured", "grade": 1},
    "heatresistantceramics": {"localized": _("Heat Resistant Ceramics"), "raw": "Heat Resistant Ceramics", "category": "manufactured", "grade": 2},
    "temperedalloys": {"localized": _("Tempered Alloys"), "raw": "Tempered Alloys", "category": "manufactured", "grade": 1},
    "uncutfocuscrystals": {"localized": _("Flawed Focus Crystals"), "raw": "Flawed Focus Crystals", "category": "manufactured", "grade": 2},
    "filamentcomposites": {"localized": _("Filament Composites"), "raw": "Filament Composites", "category": "manufactured", "grade": 2},
    "compactcomposites": {"localized": _("Compact Composites"), "raw": "Compact Composites", "category": "manufactured", "grade": 1},
    "chemicalstorageunits": {"localized": _("Chemical Storage Units"), "raw": "Chemical Storage Units", "category": "manufactured", "grade": 1},
    "protoheatradiators": {"localized": _("Proto Heat Radiators"), "raw": "Proto Heat Radiators", "category": "manufactured", "grade": 5},
    "guardian_powerconduit": {"localized": _("Guardian Power Conduit"), "raw": "Guardian Power Conduit", "category": "manufactured", "grade": 2},
    "guardian_powercell": {"localized": _("Guardian Power Cell"), "raw": "Guardian Power Cell", "category": "manufactured", "grade": 1},
    "guardian_techcomponent": {"localized": _("Guardian Technology Component"), "raw": "Guardian Technology Component", "category": "manufactured", "grade": 3},
    "guardian_sentinel_wreckagecomponents": {"localized": _("Guardian Wreckage Components"), "raw": "Guardian Wreckage Components", "category": "manufactured", "grade": 1},
    "guardian_sentinel_weaponparts": {"localized": _("Guardian Sentinel Weapon Parts"), "raw": "Guardian Sentinel Weapon Parts", "category": "manufactured", "grade": 3},
    "classifiedscandata": {"localized": _("Classified Scan Fragment"), "raw": "Classified Scan Fragment", "category": "encoded", "grade": 5},
    "securityfirmware": {"localized": _("Security Firmware Patch"), "raw": "Security Firmware Patch", "category": "encoded", "grade": 4},
    "dataminedwake": {"localized": _("Datamined Wake Exceptions"), "raw": "Datamined Wake Exceptions", "category": "encoded", "grade": 5},
    "compactemissionsdata": {"localized": _("Abnormal Compact Emissions Data"), "raw": "Abnormal Compact Emissions Data", "category": "encoded", "grade": 5},
    "shieldpatternanalysis": {"localized": _("Aberrant Shield Pattern Analysis"), "raw": "Aberrant Shield Pattern Analysis", "category": "encoded", "grade": 4},
    "adaptiveencryptors": {"localized": _("Adaptive Encryptors Capture"), "raw": "Adaptive Encryptors Capture", "category": "encoded", "grade": 5},
    "emissiondata": {"localized": _("Unexpected Emission Data"), "raw": "Unexpected Emission Data", "category": "encoded", "grade": 3},
    "industrialfirmware": {"localized": _("Cracked Industrial Firmware"), "raw": "Cracked Industrial Firmware", "category": "encoded", "grade": 3},
    "scandatabanks": {"localized": _("Classified Scan Databanks"), "raw": "Classified Scan Databanks", "category": "encoded", "grade": 3},
    "legacyfirmware": {"localized": _("Specialised Legacy Firmware"), "raw": "Specialised Legacy Firmware", "category": "encoded", "grade": 1},
    "embeddedfirmware": {"localized": _("Modified Embedded Firmware"), "raw": "Modified Embedded Firmware", "category": "encoded", "grade": 5},
    "shieldcyclerecordings": {"localized": _("Distorted Shield Cycle Recordings"), "raw": "Distorted Shield Cycle Recordings", "category": "encoded", "grade": 1},
    "decodedemissiondata": {"localized": _("Decoded Emission Data"), "raw": "Decoded Emission Data", "category": "encoded", "grade": 4},
    "bulkscandata": {"localized": _("Anomalous Bulk Scan Data"), "raw": "Anomalous Bulk Scan Data", "category": "encoded", "grade": 1},
    "scanarchives": {"localized": _("Unidentified Scan Archives"), "raw": "Unidentified Scan Archives", "category": "encoded", "grade": 2},
    "shieldsoakanalysis": {"localized": _("Inconsistent Shield Soak Analysis"), "raw": "Inconsistent Shield Soak Analysis", "category": "encoded", "grade": 2},
    "encodedscandata": {"localized": _("Divergent Scan Data"), "raw": "Divergent Scan Data", "category": "encoded", "grade": 4},
    "shielddensityreports": {"localized": _("Untypical Shield Scans"), "raw": "Untypical Shield Scans", "category": "encoded", "grade": 3},
    "shieldfrequencydata": {"localized": _("Peculiar Shield Frequency Data"), "raw": "Peculiar Shield Frequency Data", "category": "encoded", "grade": 5},
    "encryptioncodes": {"localized": _("Tagged Encryption Codes"), "raw": "Tagged Encryption Codes", "category": "encoded", "grade": 2},
    "consumerfirmware": {"localized": _("Modified Consumer Firmware"), "raw": "Modified Consumer Firmware", "category": "encoded", "grade": 2},
    "archivedemissiondata": {"localized": _("Irregular Emission Data"), "raw": "Irregular Emission Data", "category": "encoded", "grade": 2},
    "symmetrickeys": {"localized": _("Open Symmetric Keys"), "raw": "Open Symmetric Keys", "category": "encoded", "grade": 3},
    "encryptedfiles": {"localized": _("Unusual Encrypted Files"), "raw": "Unusual Encrypted Files", "category": "encoded", "grade": 1},
    "scrambledemissiondata": {"localized": _("Exceptional Scrambled Emission Data"), "raw": "Exceptional Scrambled Emission Data", "category": "encoded", "grade": 1},
    "fsdtelemetry": {"localized": _("Anomalous FSD Telemetry"), "raw": "Anomalous FSD Telemetry", "category": "encoded", "grade": 2},
    "hyperspacetrajectories": {"localized": _("Eccentric Hyperspace Trajectories"), "raw": "Eccentric Hyperspace Trajectories", "category": "encoded", "grade": 4},
    "disruptedwakeechoes": {"localized": _("Atypical Disrupted Wake Echoes"), "raw": "Atypical Disrupted Wake Echoes", "category": "encoded", "grade": 1},
    "wakesolutions": {"localized": _("Strange Wake Solutions"), "raw": "Strange Wake Solutions", "category": "encoded", "grade": 3},
    "encryptionarchives": {"localized": _("Atypical Encryption Archives"), "raw": "Atypical Encryption Archives", "category": "encoded", "grade": 4},
    "ancientbiologicaldata": {"localized": _("Pattern Alpha Obelisk Data"), "raw": "Pattern Alpha Obelisk Data", "category": "encoded", "grade": 3},
    "ancienthistoricaldata": {"localized": _("Pattern Gamma Obelisk Data"), "raw": "Pattern Gamma Obelisk Data", "category": "encoded", "grade": 4},
    "guardian_moduleblueprint": {"localized": _("Guardian Module Blueprint Fragment"), "raw": "Guardian Module Blueprint Fragment", "category": "encoded", "grade": 5},
    "ancientculturaldata": {"localized": _("Pattern Beta Obelisk Data"), "raw": "Pattern Beta Obelisk Data", "category": "encoded", "grade": 2},
    "ancientlanguagedata": {"localized": _("Pattern Delta Obelisk Data"), "raw": "Pattern Delta Obelisk Data", "category": "encoded", "grade": 4},
    "guardian_vesselblueprint": {"localized": _("Guardian Starship Blueprint Fragment"), "raw": "Guardian Starship Blueprint Fragment", "category": "encoded", "grade": 5},
    "guardian_weaponblueprint": {"localized": _("Guardian Weapon Blueprint Fragment"), "raw": "Guardian Weapon Blueprint Fragment", "category": "encoded", "grade": 5},
    "ancienttechnologicaldata": {"localized": _("Pattern Epsilon Obelisk Data"), "raw": "Pattern Epsilon Obelisk Data", "category": "encoded", "grade": 5},
    "tg_shipsystemsdata": {"localized": _("Ship Systems Data"), "raw": "Ship Systems Data", "category": "encoded", "grade": 3},
    "tg_shipflightdata": {"localized": _("Ship Flight Data"), "raw": "Ship Flight Data", "category": "encoded", "grade": 3},
    "unknownshipsignature": {"localized": _("Thargoid Ship Signature"), "raw": "Thargoid Ship Signature", "category": "encoded", "grade": 3},
    "tg_structuraldata": {"localized": _("Thargoid Structural Data"), "raw": "Thargoid Structural Data", "category": "encoded", "grade": 2},
    "unknownwakedata": {"localized": _("Thargoid Wake Data"), "raw": "Thargoid Wake Data", "category": "encoded", "grade": 4},
    "tg_biomechanicalconduits": {"localized": _("Bio-Mechanical Conduits"), "raw": "Bio-Mechanical Conduits", "category": "manufactured", "grade": 3},
    "tg_propulsionelement": {"localized": _("Propulsion Elements"), "raw": "Propulsion Elements", "category": "manufactured", "grade": 3},
    "unknowncarapace": {"localized": _("Thargoid Carapace"), "raw": "Thargoid Carapace", "category": "manufactured", "grade": 2},
    "unknownenergycell": {"localized": _("Thargoid Energy Cell"), "raw": "Thargoid Energy Cell", "category": "manufactured", "grade": 3},
    "unknownorganiccircuitry": {"localized": _("Thargoid Organic Circuitry"), "raw": "Thargoid Organic Circuitry", "category": "manufactured", "grade": 5},
    "unknowntechnologycomponents": {"localized": _("Thargoid Technological Components"), "raw": "Thargoid Technological Components", "category": "manufactured", "grade": 4},
    "bypass": { "localized": _("E-Breach"), "category": "consumable", "raw": "E-Breach", "grade":0},
    "largecapacitypowerregulator": { "localized": _("Power Regulator"), "category": "item", "raw": "Power Regulator", "grade":0},
    "chemicalinventory": { "localized": _("Chemical Inventory"), "category": "data", "raw": "Chemical Inventory", "grade":0, "comments": _("Extra backpack")},
    "dutyrota": { "localized": _("Duty Rota"), "category": "data", "raw": "Duty Rota", "grade":0},
    "evacuationprotocols": { "localized": _("Evacuation Protocols"), "category": "data", "raw": "Evacuation Protocols", "grade":0, "comments": _("Combat movement")},
    "explorationjournals": { "localized": _("Exploration Journals"), "category": "data", "raw": "Exploration Journals", "grade":0},
    "factionnews": { "localized": _("Faction News"), "category": "data", "raw": "Faction News", "grade":0},
    "financialprojections": { "localized": _("Financial Projections"), "category": "data", "raw": "Financial Projections", "grade":0},
    "salesrecords": { "localized": _("Sales Records"), "category": "data", "raw": "Sales Records", "grade":0},
    "unionmembership": { "localized": _("Union Membership"), "category": "data", "raw": "Union Membership", "grade":0},
    "compactlibrary": { "localized": _("Compact Library"), "category": "item", "raw": "Compact Library", "grade":0},
    "infinity": { "localized": _("infinity"), "category": "item", "raw": "infinity", "grade":0},
    "insightentertainmentsuite": { "localized": _("Insight Entertainment Suite"), "category": "item", "raw": "Insight Entertainment Suite", "grade":0},
    "lazarus": { "localized": _("lazarus"), "category": "item", "raw": "lazarus", "grade":0},
    "energycell": { "localized": _("Energy Cell"), "category": "consumable", "raw": "Energy Cell", "grade":0},
    "healthpack": { "localized": _("Medkit"), "category": "consumable", "raw": "Medkit", "grade":0},
    "universaltranslator": { "localized": _("Universal Translator"), "category": "item", "raw": "Universal Translator", "grade":0},
    "biochemicalagent": { "localized": _("Biochemical Agent"), "category": "item", "raw": "Biochemical Agent", "grade":0},
    "degradedpowerregulator": { "localized": _("Degraded Power Regulator"), "category": "item", "raw": "Degraded Power Regulator", "grade":0},
    "hush": { "localized": _("Hush"), "category": "item", "raw": "Hush", "grade":0},
    "maintenancelogs": { "localized": _("Maintenance Logs"), "category": "data", "raw": "Maintenance Logs", "grade":0, "comments": _("Extra battery")},
    "patrolroutes": { "localized": _("Patrol Routes"), "category": "data", "raw": "Patrol Routes", "grade":0, "comments": _("Quieter footsteps, Audio masking")},
    "push": { "localized": _("push"), "category": "item", "raw": "push", "grade":0},
    "settlementdefenceplans": { "localized": _("Settlement Defence Plans"), "category": "data", "raw": "Settlement Defence Plans", "grade":0},
    "surveilleancelogs": { "localized": _("Surveillance Logs"), "category": "data", "raw": "Surveillance Logs", "grade":0, "comments": _("Night vision")},
    "syntheticpathogen": { "localized": _("Synthetic Pathogen"), "category": "item", "raw": "Synthetic Pathogen", "grade":0},
    "buildingschematic": { "localized": _("Building Schematic"), "category": "item", "raw": "Building Schematic", "grade":0},
    "operationalmanual": { "localized": _("Operational Manual"), "category": "data", "raw": "Operational Manual", "grade":0, "comments": _("Faster handling, Faster/Stowed reloading")},
    "blacklistdata": { "localized": _("Blacklist Data"), "category": "data", "raw": "Blacklist Data", "grade":0},
    "insight": { "localized": _("Insight"), "category": "item", "raw": "Insight", "grade":0},
    "airqualityreports": { "localized": _("Air Quality Reports"), "category": "data", "raw": "Air Quality Reports", "grade":0, "comments": _("Extra air")},
    "employeedirectory": { "localized": _("Employee Directory"), "category": "data", "raw": "Employee Directory", "grade":0},
    "factionassociates": { "localized": _("Faction Associates"), "category": "data", "raw": "Faction Associates", "grade":0},
    "meetingminutes": { "localized": _("Meeting Minutes"), "category": "data", "raw": "Meeting Minutes", "grade":0},
    "multimediaentertainment": { "localized": _("Multimedia Entertainment"), "category": "data", "raw": "Multimedia Entertainment", "grade":0},
    "networkaccesshistory": { "localized": _("Network Access History"), "category": "data", "raw": "Network Access History", "grade":0},
    "purchaserecords": { "localized": _("Purchase Records"), "category": "data", "raw": "Purchase Records", "grade":0},
    "radioactivitydata": { "localized": _("Radioactivity Data"), "category": "data", "raw": "Radioactivity Data", "grade":0, "comments": _("Night vision, TK hip fire")},
    "residentialdirectory": { "localized": _("Residential Directory"), "category": "data", "raw": "Residential Directory", "grade":0},
    "shareholderinformation": { "localized": _("Shareholder Information"), "category": "data", "raw": "Shareholder Information", "grade":0},
    "travelpermits": { "localized": _("Travel Permits"), "category": "data", "raw": "Travel Permits", "grade":0},
    "accidentlogs": { "localized": _("Accident Logs"), "category": "data", "raw": "Accident Logs", "grade":0},
    "campaignplans": { "localized": _("Campaign Plans"), "category": "data", "raw": "Campaign Plans", "grade":0},
    "combattrainingmaterial": { "localized": _("Combat Training Material"), "category": "data", "raw": "Combat Training Material", "grade":0, "comments": _("Faster handling/reload, Melee damage")},
    "internalcorrespondence": { "localized": _("Internal Correspondence"), "category": "data", "raw": "Internal Correspondence", "grade":0},
    "payrollinformation": { "localized": _("Payroll Information"), "category": "data", "raw": "Payroll Information", "grade":0},
    "personallogs": { "localized": _("Personal Logs"), "category": "data", "raw": "Personal Logs", "grade":0},
    "weaponinventory": { "localized": _("Weapon Inventory"), "category": "data", "raw": "Weapon Inventory", "grade":0, "comments": _("Extra backpack, Damage resistance")},
    "atmosphericdata": { "localized": _("Atmospheric Data"), "category": "data", "raw": "Atmospheric Data", "grade":0, "comments": _("Noise suppressor")},
    "topographicalsurveys": { "localized": _("Topographical Surveys"), "category": "data", "raw": "Topographical Surveys", "grade":0, "comments": _("Jump assist, Enhanced tracking, Karma range")},
    "literaryfiction": { "localized": _("Literary Fiction"), "category": "data", "raw": "Literary Fiction", "grade":0},
    "reactoroutputreview": { "localized": _("Reactor Output Review"), "category": "data", "raw": "Reactor Output Review", "grade":0, "comments": _("Battery capacity/consumption, Shield regen")},
    "nextofkinrecords": { "localized": _("Next of Kin Records"), "category": "data", "raw": "Next of Kin Records", "grade":0},
    "purchaserequests": { "localized": _("Purchase Requests"), "category": "data", "raw": "Purchase Requests", "grade":0},
    "taxrecords": { "localized": _("Tax Records"), "category": "data", "raw": "Tax Records", "grade":0},
    "visitorregister": { "localized": _("Visitor Register"), "category": "data", "raw": "Visitor Register", "grade":0},
    "pharmaceuticalpatents": { "localized": _("Pharmaceutical Patents"), "category": "data", "raw": "Pharmaceutical Patents", "grade":0, "comments": _("Extra air")},
    "vaccineresearch": { "localized": _("Vaccine Research"), "category": "data", "raw": "Vaccine Research", "grade":0},
    "virologydata": { "localized": _("Virology Data"), "category": "data", "raw": "Virology Data", "grade":0},
    "vaccinationrecords": { "localized": _("Vaccination Records"), "category": "data", "raw": "Vaccination Records", "grade":0},
    "censusdata": { "localized": _("Census Data"), "category": "data", "raw": "Census Data", "grade":0},
    "geographicaldata": { "localized": _("Geographical Data"), "category": "data", "raw": "Geographical Data", "grade":0},
    "mineralsurvey": { "localized": _("Mineral Survey"), "category": "data", "raw": "Mineral Survey", "grade":0, "comments": _("Manticore range")},
    "chemicalformulae": { "localized": _("Chemical Formulae"), "category": "data", "raw": "Chemical Formulae", "grade":0, "comments": _("Manticore range")},
    "amm_grenade_frag": { "localized": _("Frag Grenade"), "category": "consumable", "raw": "Frag Grenade", "grade":0},
    "amm_grenade_emp": { "localized": _("Shield Disruptor"), "category": "consumable", "raw": "Shield Disruptor", "grade":0},
    "amm_grenade_shield": { "localized": _("Shield Projector"), "category": "consumable", "raw": "Shield Projector", "grade":0},
    "chemicalexperimentdata": { "localized": _("Chemical Experiment Data"), "category": "data", "raw": "Chemical Experiment Data", "grade":0, "comments": _("Manticore headshot")},
    "chemicalpatents": { "localized": _("Chemical Patents"), "category": "data", "raw": "Chemical Patents", "grade":0, "comments": _("Manticore hip fire")},
    "productionreports": { "localized": _("Production Reports"), "category": "data", "raw": "Production Reports", "grade":0, "comments": _("Extra ammo, Faster reloading")},
    "productionschedule": { "localized": _("Production Schedule"), "category": "data", "raw": "Production Schedule", "grade":0, "comments": _("Stowed reloading")},
    "bloodtestresults": { "localized": _("Blood Test Results"), "category": "data", "raw": "Blood Test Results", "grade":0, "comments": _("Manticore headshot")},
    "combatantperformance": { "localized": _("Combatant Performance"), "category": "data", "raw": "Combatant Performance", "grade":0, "comments": _("Faster handling, Hip fire, Melee damage")},
    "troopdeploymentrecords": { "localized": _("Troop Deployment Records"), "category": "data", "raw": "Troop Deployment Records", "grade":0, "comments": _("Longer sprint")},
    "catmedia": { "localized": _("Cat Media"), "category": "data", "raw": "Cat Media", "grade":0},
    "employeegeneticdata": { "localized": _("Employee Genetic Data"), "category": "data", "raw": "Employee Genetic Data", "grade":0},
    "factiondonatorlist": { "localized": _("Faction Donator List"), "category": "data", "raw": "Faction Donator List", "grade":0},
    "nocdata": { "localized": _("NOC Data"), "category": "data", "raw": "NOC Data", "grade":0, "comments": _("Night vision")},
    "trueformfossil": { "localized": _("True Form Fossil"), "category": "item", "raw": "True Form Fossil", "grade":0},
    "healthmonitor": { "localized": _("Health Monitor"), "category": "item", "raw": "Health Monitor", "grade":0, "comments": _("Suits upgrades")},
    "nutritionalconcentrate": { "localized": _("Nutritional Concentrate"), "category": "item", "raw": "Nutritional Concentrate", "grade":0},
    "personaldocuments": { "localized": _("Personal Documents"), "category": "item", "raw": "Personal Documents", "grade":0},
    "chemicalsample": { "localized": _("Chemical Sample"), "category": "item", "raw": "Chemical Sample", "grade":0},
    "insightdatabank": { "localized": _("Insight Data Bank"), "category": "item", "raw": "Insight Data Bank", "grade":0},
    "ionisedgas": { "localized": _("Ionised Gas"), "category": "item", "raw": "Ionised Gas", "grade":0, "comments": _("Manticore/TK upgrades")},
    "personalcomputer": { "localized": _("Personal Computer"), "category": "item", "raw": "Personal Computer", "grade":0},
    "shipschematic": { "localized": _("Ship Schematic"), "category": "item", "raw": "Ship Schematic", "grade":0},
    "suitschematic": { "localized": _("Suit Schematic"), "category": "item", "raw": "Suit Schematic", "grade":0, "comments": _("Suits upgrades")},
    "vehicleschematic": { "localized": _("Vehicle Schematic"), "category": "item", "raw": "Vehicle Schematic", "grade":0},
    "weaponschematic": { "localized": _("Weapon Schematic"), "category": "item", "raw": "Weapon Schematic", "grade":0, "comments": _("Weapon upgrades")},
    "inertiacanister": { "localized": _("Inertia Canister"), "category": "item", "raw": "Inertia Canister", "grade":0},
    "surveillanceequipment": { "localized": _("Surveillance Equipment"), "category": "item", "raw": "Surveillance Equipment", "grade":0, "comments": _("Night vision")},
    "deepmantlesample": { "localized": _("Deep Mantle Sample"), "category": "item", "raw": "Deep Mantle Sample", "grade":0},
    "microbialinhibitor": { "localized": _("Microbial Inhibitor"), "category": "item", "raw": "Microbial Inhibitor", "grade":0},
    "castfossil": { "localized": _("Cast Fossil"), "category": "item", "raw": "Cast Fossil", "grade":0},
    "petrifiedfossil": { "localized": _("Petrified Fossil"), "category": "item", "raw": "Petrified Fossil", "grade":0},
    "agriculturalprocesssample": { "localized": _("Agricultural Process Sample"), "category": "item", "raw": "Agricultural Process Sample", "grade":0},
    "chemicalprocesssample": { "localized": _("Chemical Process Sample"), "category": "item", "raw": "Chemical Process Sample", "grade":0},
    "refinementprocesssample": { "localized": _("Refinement Process Sample"), "category": "item", "raw": "Refinement Process Sample", "grade":0},
    "microsupercapacitor": { "localized": _("Micro Supercapacitor"), "category": "component", "subcategory": "circuit", "raw": "Micro Supercapacitor", "grade":0, "comments": _("Extra battery, Manticore headshot")},
    "microtransformer": { "localized": _("Micro Transformer"), "category": "component", "subcategory": "circuit", "raw": "Micro Transformer", "grade":0, "comments": _("Shield regen, Battery consumption, TK range")},
    "chemicalsuperbase": { "localized": _("Chemical Superbase"), "category": "component", "subcategory": "chemical", "raw": "Chemical Superbase", "grade":0, "comments": _("Manticore upgrades")},
    "circuitswitch": { "localized": _("Circuit Switch"), "category": "component", "subcategory": "circuit", "raw": "Circuit Switch", "grade":0, "comments": _("Night vision")},
    "electricalwiring": { "localized": _("Electrical Wiring"), "category": "component", "subcategory": "circuit", "raw": "Electrical Wiring", "grade":0, "comments": _("Battery consumption, Extra battery, Shield regen, TK hip fire")},
    "encryptedmemorychip": { "localized": _("Encrypted Memory Chip"), "category": "component", "subcategory": "tech", "raw": "Encrypted Memory Chip", "grade":0, "comments": _("Stowed reloading")},
    "epoxyadhesive": { "localized": _("Epoxy Adhesive"), "category": "component", "subcategory": "chemical", "raw": "Epoxy Adhesive", "grade":0, "comments": _("Extra backpack, Damage resistance")},
    "memorychip": { "localized": _("Memory Chip"), "category": "component", "subcategory": "tech", "raw": "Memory Chip", "grade":0, "comments": _("Extra backpack")},
    "microhydraulics": { "localized": _("Micro Hydraulics"), "category": "component", "subcategory": "tech", "raw": "Micro Hydraulics", "grade":0, "comments": _("Quieter footsteps, Faster reload, Stability")},
    "opticalfibre": { "localized": _("Optical Fibre"), "category": "component", "subcategory": "circuit", "raw": "Optical Fibre", "grade":0, "comments": _("Scope, TK upgrades")},
    "titaniumplating": { "localized": _("Titanium Plating"), "category": "component", "subcategory": "tech", "raw": "Titanium Plating", "grade":0, "comments": _("Damage resistance, Dominator upgrades")},
    "phneutraliser": { "localized": _("pH Neutraliser"), "category": "component", "subcategory": "chemical", "raw": "pH Neutraliser", "grade":0, "comments": _("Extra air, Combat movement")},
    "metalcoil": { "localized": _("Metal Coil"), "category": "component", "subcategory": "circuit", "raw": "Metal Coil", "grade":0, "comments": _("Mag size, Karma range, TK & Manticore: hip fire")},
    "viscoelasticpolymer": { "localized": _("Viscoelastic Polymer"), "category": "component", "subcategory": "chemical", "raw": "Viscoelastic Polymer", "grade":0, "comments": _("Quieter footsteps, Noise suppressor, Faster handling, Stability, Karma hip fire")},
    "ionbattery": { "localized": _("Ion Battery"), "category": "component", "subcategory": "circuit", "raw": "Ion Battery", "grade":0, "comments": _("Shield regen, extra battery, TK & Manticore: headshot")},
    "chemicalcatalyst": { "localized": _("Chemical Catalyst"), "category": "component", "subcategory": "chemical", "raw": "Chemical Catalyst", "grade":0, "comments": _("Longer sprint, Karma headshot, Manticore hip fire")},
    "electricalfuse": { "localized": _("Electrical Fuse"), "category": "component", "subcategory": "circuit", "raw": "Electrical Fuse", "grade":0, "comments": _("Battery consumption, Manticore range")},
    "opticallens": { "localized": _("Optical Lens"), "category": "component", "subcategory": "tech", "raw": "Optical Lens", "grade":0, "comments": _("Scope, TK: hip fire / headshot / range")},
    "weaponcomponent": { "localized": _("Weapon Component"), "category": "component", "subcategory": "tech", "raw": "Weapon Component", "grade":0, "comments": _("Extra ammo, Mag size, Karma: Headshot / Range, TK & Manticore: Mag size, Noise suppressor")},
    "carbonfibreplating": { "localized": _("Carbon Fibre Plating"), "category": "component", "subcategory": "tech", "raw": "Carbon Fibre Plating", "grade":0, "comments": _("Damage resistance, Maverick upgrades")},
    "microthrusters": { "localized": _("Micro Thrusters"), "category": "component", "subcategory": "tech", "raw": "Micro Thrusters", "grade":0, "comments": _("Jump assist, Melee damage")},
    "oxygenicbacteria": { "localized": _("Oxygenic Bacteria"), "category": "component", "subcategory": "chemical", "raw": "Oxygenic Bacteria", "grade":0, "comments": _("Longer sprint, Extra air")},
    "circuitboard": { "localized": _("Circuit Board"), "category": "component", "subcategory": "circuit", "raw": "Circuit Board", "grade":0, "comments": _("Enhanced tracking, Audio masking, Stowed reloading, TK range")},
    "tungstencarbide": { "localized": _("Tungsten Carbide"), "category": "component", "subcategory": "tech", "raw": "Tungsten Carbide", "grade":0, "comments": _("Mag size, Karma upgrades")},
    "ballisticsdata": { "localized": _("Ballistics Data"), "category": "data", "raw": "Ballistics Data", "grade":0, "comments": _("Damage resistance, Karma range")},
    "politicalaffiliations": { "localized": _("Political Affiliations"), "category": "data", "raw": "Political Affiliations", "grade":0},
    "conflicthistory": { "localized": _("Conflict History"), "category": "data", "raw": "Conflict History", "grade":0},
    "riskassessments": { "localized": _("Risk Assessments"), "category": "data", "raw": "Risk Assessments", "grade":0, "comments": _("Stability, Greater range")},
    "stellaractivitylogs": { "localized": _("Stellar Activity Logs"), "category": "data", "raw": "Stellar Activity Logs", "grade":0, "comments": _("Enhanced tracking, TK range")},
    "manufacturinginstructions": { "localized": _("Manufacturing Instructions"), "category": "data", "raw": "Manufacturing Instructions", "grade":0, "comments": _("Suits & weapons upgrades")},
    "digitaldesigns": { "localized": _("Digital Designs"), "category": "data", "raw": "Digital Designs", "grade":0, "comments": _("Extra backpack, Stowed reloading")},
    "medicalrecords": { "localized": _("Medical Records"), "category": "data", "raw": "Medical Records", "grade":0, "comments": _("Karma headshot")},
    "employmenthistory": { "localized": _("Employment History"), "category": "data", "raw": "Employment History", "grade":0},
    "vipsecuritydetail": { "localized": _("VIP Security Detail"), "category": "data", "raw": "VIP Security Detail", "grade":0},
    "classicentertainment": { "localized": _("Classic Entertainment"), "category": "data", "raw": "Classic Entertainment", "grade":0},
    "photoalbums": { "localized": _("Photo Albums"), "category": "data", "raw": "Photo Albums", "grade":0},
    "biometricdata": { "localized": _("Biometric Data"), "category": "data", "raw": "Biometric Data", "grade":0, "comments": _("Hip fire, Scope, TK Headshot")},
    "extractionyielddata": { "localized": _("Extraction Yield Data"), "category": "data", "raw": "Extraction Yield Data", "grade":0, "comments": _("Karma hip fire")},
    "securityexpenses": { "localized": _("Security Expenses"), "category": "data", "raw": "Security Expenses", "grade":0, "comments": _("Mag size")},
    "culinaryrecipes": { "localized": _("Culinary Recipes"), "category": "data", "raw": "Culinary Recipes", "grade":0},
    "fleetregistry": { "localized": _("Fleet Registry"), "category": "data", "raw": "Fleet Registry", "grade":0},
    "influenceprojections": { "localized": _("Influence Projections"), "category": "data", "raw": "Influence Projections", "grade":0},
    "cocktailrecipes": { "localized": _("Cocktail Recipes"), "category": "data", "raw": "Cocktail Recipes", "grade":0},
    "employeeexpenses": { "localized": _("Employee Expenses"), "category": "data", "raw": "Employee Expenses", "grade":0},
    "interviewrecordings": { "localized": _("Interview Recordings"), "category": "data", "raw": "Interview Recordings", "grade":0},
    "recyclinglogs": { "localized": _("Recycling Logs"), "category": "data", "raw": "Recycling Logs", "grade":0, "comments": _("Extra ammo")},
    "jobapplications": { "localized": _("Job Applications"), "category": "data", "raw": "Job Applications", "grade":0},
    "californium": { "localized": _("Californium"), "category": "item", "raw": "Californium", "grade":0},
    "pyrolyticcatalyst": { "localized": _("Pyrolytic catalyst"), "category": "item", "raw": "Pyrolytic catalyst", "grade":0},
    "spyware": { "localized": _("Spyware"), "category": "data", "raw": "Spyware", "grade":0},
    "tacticalplans": { "localized": _("Tactical Plans"), "category": "data", "raw": "Tactical plans", "grade":0, "comments": _("Quieter footsteps")},
    "virus": { "localized": _("Virus"), "category": "data", "raw": "Virus", "grade":0},
    "aerogel": { "localized": _("Aerogel"), "category": "component", "subcategory": "chemical", "raw": "Aerogel", "grade":0, "comments": _("Artermis upgrades")},
    "geneticrepairmeds": { "localized": _("Genetic Repair Meds"), "category": "item", "raw": "Genetic Repair Meds", "grade":0},
    "cropyieldanalysis": { "localized": _("Crop Yield Analysis"), "category": "data", "raw": "Crop Yield Analysis", "grade":0},
    "kompromat": { "localized": _("Kompromat"), "category": "data", "raw": "Kompromat", "grade":0},
    "xenodefenceprotocols":  { "localized": _("Xeno Defence Protocols"), "category": "data", "raw": "Xeno Defence Protocols", "grade":0},
    "geologicaldata":  { "localized": _("Geological Data"), "category": "data", "raw": "Geological Data", "grade":0},
    "opinionpolls":  { "localized": _("Opinion Polls"), "category": "data", "raw": "Opinion Polls", "grade":0},
    "propaganda":  { "localized": _("Propaganda"), "category": "data", "raw": "Propaganda", "grade":0},
    "hydroponicdata": { "localized": _("Hydroponic Data"), "category": "data", "raw": "Hydroponic Data", "grade":0},
    "mininganalytics" :{ "localized": _("Mining Analytics"), "raw": "Mining Analytics", "category": "data", "grade": 0, "comments": _("Noise suppressor, Stability")},
    "compressionliquefiedgas" :{ "localized": _("Compression Liquefied Gas"), "raw": "Compression Liquefied Gas", "category": "item", "grade": 0, "comments": _("Karma upgrades")},
    "weapontestdata" :{ "localized": _("Weapon Test Data"), "raw": "Weapon Test Data", "category": "data", "grade": 0, "comments": _("Extra ammo, Mag size, Karma headshot")},
    "spectralanalysisdata" :{ "localized": _("Spectral Analysis Data"), "raw": "Spectral Analysis Data", "category": "data", "grade": 0, "comments": _("Enhanced tracking, Scope, TK headshot")},
    "audiologs" :{ "localized": _("Audiologs"), "raw": "Audiologs", "category": "data", "grade": 0, "comments": _("Audio masking")},
    "geneticresearch" :{ "localized": _("Genetic Research"), "raw": "Genetic Research", "category": "data", "grade": 0, "comments": _("Combat movement")},
    "clinicaltrialrecords" :{ "localized": _("Clinical Trial Records"), "raw": "Clinical Trial Records", "category": "data", "grade": 0, "comments": _("Longer sprint")},
    "medicaltrialrecords" :{ "localized": _("Clinical Trial Records"), "raw": "Clinical Trial Records", "category": "data", "grade": 0, "comments": _("Longer sprint")},
    "gmeds" :{ "localized": _("G-Meds"), "raw": "G-Meds", "category": "item", "grade": 0, "comments": _("Jump assist")},
    "genesequencingdata" :{ "localized": _("Gene Sequencing Data"), "raw": "Gene Sequencing Data", "category": "data", "grade": 0, "comments": _("Longer sprint")},
    "settlementassaultplans" :{ "localized": _("Settlement Assault Plans"), "raw": "Settlement Assault Plans", "category": "data", "grade": 0, "comments": _("Quieter footsteps")},
    "geneticsample" :{ "localized": _("Biological Sample"), "raw": "Biological Sample", "category": "data", "grade": 0},
    "biologicalsample" :{ "localized": _("Biological Sample"), "raw": "Biological Sample", "category": "goods", "grade": 0},
    "smearcampaignplans" :{ "localized": _("Smear Campaign Plans"), "raw": "Smear Campaign Plans", "category": "data", "grade": 0},
    "axcombatlogs" :{ "localized": _("Ax Combat Logs"), "raw": "Ax Combat Logs", "category": "data", "grade": 0},
    "biologicalweapondata" :{ "localized": _("Biological Weapon Data"), "raw": "Biological Weapon Data", "category": "data", "grade": 0},
    "chemicalweapondata" :{ "localized": _("Chemical Weapon Data"), "raw": "Chemical Weapon Data", "category": "data", "grade": 0},
    "criminalrecords" :{ "localized": _("Criminal Records"), "raw": "Criminal Records", "category": "data", "grade": 0},
    "enhancedinterrogationrecordings" :{ "localized": _("Enhanced Interrogation Recordings"), "raw": "Enhanced Interrogation Recordings", "category": "data", "grade": 0},
    "espionagematerial" :{ "localized": _("Espionage Material"), "raw": "Espionage Material", "category": "data", "grade": 0},
    "incidentlogs" :{ "localized": _("Incident Logs"), "raw": "Incident Logs", "category": "data", "grade": 0},
    "inorganiccontaminant" :{ "localized": _("Inorganic Contaminant"), "raw": "Inorganic Contaminant", "category": "item", "grade": 0},
    "interrogationrecordings" :{ "localized": _("Interrogation Recordings"), "raw": "Interrogation Recordings", "category": "data", "grade": 0},
    "mutageniccatalyst" :{ "localized": _("Mutagenic Catalyst"), "raw": "Mutagenic Catalyst", "category": "item", "grade": 0},
    "networksecurityprotocols" :{ "localized": _("Network Security Protocols"), "raw": "Network Security Protocols", "category": "data", "grade": 0},
    "patienthistory" :{ "localized": _("Patient History"), "raw": "Patient History", "category": "data", "grade": 0},
    "plantgrowthcharts" :{ "localized": _("Plant Growth Charts"), "raw": "Plant Growth Charts", "category": "data", "grade": 0},
    "prisonerlogs" :{ "localized": _("Prisoner Logs"), "raw": "Prisoner Logs", "category": "data", "grade": 0},
    "seedgeneaology" :{ "localized": _("Seed Geneaology"), "raw": "Seed Geneaology", "category": "data", "grade": 0},
    "slushfundlogs" :{ "localized": _("Slush Fund Logs"), "raw": "Slush Fund Logs", "category": "data", "grade": 0},
    "syntheticgenome" :{ "localized": _("Synthetic Genome"), "raw": "Synthetic Genome", "category": "item", "grade": 0},
    "epinephrine" :{ "localized": _("Epinephrine"), "raw": "Epinephrine", "category": "component", "subcategory": "chemical", "grade": 0, "comments": _("Melee damage, Combat movement")},
    "graphene" :{ "localized": _("Graphene"), "raw": "Graphene", "category": "component", "subcategory": "chemical", "grade": 0, "comments": _("Suits upgrades")},
    "rdx" :{ "localized": _("Rdx"), "raw": "Rdx", "category": "component", "subcategory": "chemical", "grade": 0, "comments": _("Karma: hip fire, headshot, range")},
    "electromagnet" :{ "localized": _("Electromagnet"), "raw": "Electromagnet", "category": "component", "subcategory": "circuit", "grade": 0, "comments": _("Faster reloading, Manticore: headshot, range, hip fire")},
    "microelectrode" :{ "localized": _("Microelectrode"), "raw": "Microelectrode", "category": "component", "subcategory": "circuit", "grade": 0, "comments": _("Suits upgrades")},
    "motor" :{ "localized": _("Motor"), "raw": "Motor", "category": "component", "subcategory": "circuit", "grade": 0, "comments": _("Jump assist, Manticore range")},
    "scrambler" :{ "localized": _("Scrambler"), "raw": "Scrambler", "category": "component", "subcategory": "tech", "grade": 0, "comments": _("Audio masking, TK headshot")},
    "transmitter" :{ "localized": _("Transmitter"), "raw": "Transmitter", "category": "component", "subcategory": "tech", "grade": 0, "comments": _("Enhanced tracking, Audio masking")},
}

INTERNAL_NAMES_LUT = { 'classified scan databanks': 'scandatabanks', 'conductive components': 'conductivecomponents', 'abnormal compact emissions data': 'compactemissionsdata', 'germanium': 'germanium',
    'atypical disrupted wake echoes': 'disruptedwakeechoes', 'crystal shards': 'crystalshards', 'selenium': 'selenium', 'technetium': 'technetium', 'galvanising alloys': 'galvanisingalloys',
    'improvised components': 'improvisedcomponents', 'cracked industrial firmware': 'industrialfirmware', 'guardian technology component': 'guardian_techcomponent', 'heat resistant ceramics': 'heatresistantceramics',
    'unexpected emission data': 'emissiondata', 'tungsten': 'tungsten', 'exceptional scrambled emission data': 'scrambledemissiondata', 'thermic alloys': 'thermicalloys', 'molybdenum': 'molybdenum',
    'atypical encryption archives': 'encryptionarchives', 'salvaged alloys': 'salvagedalloys', 'pharmaceutical isolators': 'pharmaceuticalisolators', 'divergent scan data': 'encodedscandata',
    'anomalous fsd telemetry': 'fsdtelemetry', 'pattern delta obelisk data': 'ancientlanguagedata', 'worn shield emitters': 'wornshieldemitters', 'strange wake solutions': 'wakesolutions',
    'tempered alloys': 'temperedalloys', 'zinc': 'zinc', 'mechanical equipment': 'mechanicalequipment', 'eccentric hyperspace trajectories': 'hyperspacetrajectories', 'grid resistors': 'gridresistors', 
    'unusual encrypted files': 'encryptedfiles', 'peculiar shield frequency data': 'shieldfrequencydata', 'specialised legacy firmware': 'legacyfirmware', 'flawed focus crystals': 'uncutfocuscrystals', 
    'pattern beta obelisk data': 'ancientculturaldata', 'antimony': 'antimony', 'untypical shield scans': 'shielddensityreports', 'focus crystals': 'focuscrystals', 'lead': 'lead', 
    'heat dispersion plate': 'heatdispersionplate', 'irregular emission data': 'archivedemissiondata', 'guardian module blueprint fragment': 'guardian_moduleblueprint', 'yttrium': 'yttrium', 
    'mechanical scrap': 'mechanicalscrap', 'biotech conductors': 'biotechconductors', 'military grade alloys': 'militarygradealloys', 'basic conductors': 'basicconductors', 'boron': 'boron', 'carbon': 'carbon', 
    'unidentified scan archives': 'scanarchives', 'imperial shielding': 'imperialshielding', 'chemical distillery': 'chemicaldistillery', 'guardian wreckage components': 'guardian_sentinel_wreckagecomponents', 
    'proto radiolic alloys': 'protoradiolicalloys', 'proto heat radiators': 'protoheatradiators', 'cadmium': 'cadmium', 'filament composites': 'filamentcomposites', 'exquisite focus crystals': 'exquisitefocuscrystals', 'electrochemical arrays': 'electrochemicalarrays', 
    'mechanical components': 'mechanicalcomponents', 'pattern alpha obelisk data': 'ancientbiologicaldata', 'arsenic': 'arsenic', 'chromium': 'chromium', 'conductive ceramics': 'conductiveceramics', 'mercury': 'mercury', 
    'chemical processors': 'chemicalprocessors', 'pattern gamma obelisk data': 'ancienthistoricaldata', 'proprietary composites': 'fedproprietarycomposites', 'proto light alloys': 'protolightalloys', 
    'datamined wake exceptions': 'dataminedwake', 'adaptive encryptors capture': 'adaptiveencryptors', 'open symmetric keys': 'symmetrickeys', 'nickel': 'nickel', 'ruthenium': 'ruthenium', 
    'guardian sentinel weapon parts': 'guardian_sentinel_weaponparts', 'decoded emission data': 'decodedemissiondata', 'guardian power cell': 'guardian_powercell', 'chemical storage units': 'chemicalstorageunits', 
    'sulphur': 'sulphur', 'anomalous bulk scan data': 'bulkscandata', 'refined focus crystals': 'refinedfocuscrystals', 'zirconium': 'zirconium', 'heat vanes': 'heatvanes', 'niobium': 'niobium', 'iron': 'iron', 
    'conductive polymers': 'conductivepolymers', 'configurable components': 'configurablecomponents', 'rhenium': 'rhenium', 'security firmware patch': 'securityfirmware', 'aberrant shield pattern analysis': 'shieldpatternanalysis',
    'modified consumer firmware': 'consumerfirmware', 'military supercapacitors': 'militarysupercapacitors', 'heat conduction wiring': 'heatconductionwiring', 'inconsistent shield soak analysis': 'shieldsoakanalysis',
    'distorted shield cycle recordings': 'shieldcyclerecordings', 'shield emitters': 'shieldemitters', 'tin': 'tin', 'chemical manipulators': 'chemicalmanipulators', 'hybrid capacitors': 'hybridcapacitors',
    'tagged encryption codes': 'encryptioncodes', 'classified scan fragment': 'classifiedscandata', 'polymer capacitors': 'polymercapacitors', 'precipitated alloys': 'precipitatedalloys', 
    'heat exchangers': 'heatexchangers', 'polonium': 'polonium', 'core dynamics composites': 'fedcorecomposites', 'high density composites': 'highdensitycomposites', 'modified embedded firmware': 'embeddedfirmware',
    'phosphorus': 'phosphorus', 'guardian power conduit': 'guardian_powerconduit', 'vanadium': 'vanadium', 'shielding sensors': 'shieldingsensors', 'compound shielding': 'compoundshielding', 
    'manganese': 'manganese', 'compact composites': 'compactcomposites', 'tellurium': 'tellurium', 'phase alloys': 'phasealloys', 'thargoid organic circuitry': 'unknownorganiccircuitry', 
    'thargoid energy cell': 'unknownenergycell', 'thargoid structural data': 'tg_structuraldata', 'thargoid ship signature': 'unknownshipsignature', 'thargoid carapace': 'unknowncarapace', 
    'propulsion elements': 'tg_propulsionelement', 'guardian weapon blueprint fragment': 'guardian_weaponblueprint', 'guardian starship blueprint fragment': 'guardian_vesselblueprint', 
    'pattern epsilon obelisk data': 'ancienttechnologicaldata', 'bio-mechanical conduits': 'tg_biomechanicalconduits', 'ship flight data': 'tg_shipflightdata', 'thargoid wake data': 'unknownwakedata', 
    'thargoid technological components': 'unknowntechnologycomponents', 'ship systems data': 'tg_shipsystemsdata', 'power regulator': 'largecapacitypowerregulator',
    'surveillance logs': 'surveilleancelogs', 'surveillance log': 'surveilleancelogs'}

class EDRInventory:
    EDR_INVENTORY_ENCODED_CACHE = edr_cache_path('encoded_mats.v1.p')
    EDR_INVENTORY_RAW_CACHE = edr_cache_path('raw_mats.v1.p')
    EDR_INVENTORY_MANUFACTURED_CACHE = edr_cache_path('manufactured_mats.v1.p')
    EDR_INVENTORY_COMPONENT_CACHE = edr_cache_path('component_mats.v1.p')
    EDR_INVENTORY_ITEM_CACHE = edr_cache_path('item_mats.v1.p')
    EDR_INVENTORY_CONSUMABLE_CACHE = edr_cache_path('consumables.v1.p')
    EDR_INVENTORY_DATA_CACHE = edr_cache_path('data_mats.v1.p')
    EDR_INVENTORY_BACKPACK_CACHE = edr_cache_path('backpack.v2.p')

    def __init__(self):
        self.initialized = False
        self.inconsistencies = False
        self.locker_timestamp = None
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

    def initialize(self, entry):
        if entry.get("event", "") in ["ShipLocker", "Materials", "ShipLockerMaterials"]:
            self.initialize_locker(entry)
        elif entry.get("event", "") == "Backpack":
            self.initialize_backpack(entry)

    def initialize_backpack(self, materials):
        if "Encoded" in materials:
            self.backpack["encoded"] = {}
        for thing in materials.get("Encoded", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["encoded"][cname] = thing["Count"]

        if "Raw" in materials:
            self.backpack["raw"] = {}
        for thing in materials.get("Raw", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["raw"][cname] = thing["Count"]

        if "Manufactured" in materials:
            self.backpack["manufactured"] = {}
        for thing in materials.get("Manufactured", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["manufactured"][cname] = thing["Count"]

        if "Items" in materials:
            self.backpack["item"] = {}
        for thing in materials.get("Items", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["item"][cname] = thing["Count"]

        if "Components" in materials:
            self.backpack["component"] = {}
        for thing in materials.get("Components", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["component"][cname] = thing["Count"]

        if "Data" in materials:
            self.backpack["data"] = {}
        for thing in materials.get("Data", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["data"][cname] = thing["Count"]

        if "Consumables" in materials:
            self.backpack["consumable"] = {}
        for thing in materials.get("Consumables", []):
            cname = self.__c_name(thing["Name"])
            self.backpack["consumable"][cname] = thing["Count"]

        self.initialized = True
        self.inconsistencies = False

    def initialize_locker(self, materials):
        self.locker_timestamp = EDTime.py_epoch_now()
        if "Encoded" in materials:
            self.encoded = {}
        for thing in materials.get("Encoded", []):
            cname = self.__c_name(thing["Name"])
            self.encoded[cname] = thing["Count"]

        if "Raw" in materials:
            self.raw = {}
        for thing in materials.get("Raw", []):
            cname = self.__c_name(thing["Name"])
            self.raw[cname] = thing["Count"]

        if "Manufactured" in materials:
            self.manufactured = {}
        for thing in materials.get("Manufactured", []):
            cname = self.__c_name(thing["Name"])
            self.manufactured[cname] = thing["Count"]

        if "Items" in materials:
            self.items = {}
        for thing in materials.get("Items", []):
            cname = self.__c_name(thing["Name"])
            self.items[cname] = thing["Count"]

        if "Components" in materials:
            self.components = {}
        for thing in materials.get("Components", []):
            cname = self.__c_name(thing["Name"])
            self.components[cname] = thing["Count"]

        if "Data" in materials:
            self.data = {}
        for thing in materials.get("Data", []):
            cname = self.__c_name(thing["Name"])
            self.data[cname] = thing["Count"]

        if "Consumables" in materials:
            self.consumables = {}
        for thing in materials.get("Consumables", []):
            cname = self.__c_name(thing["Name"])
            self.consumables[cname] = thing["Count"]

        self.initialized = True
        self.inconsistencies = False

    def initialize_with_edmc(self, state):
        self.encoded = {} if "Encoded" in state else self.encoded
        for thing in state.get("Encoded", {}):
            cname = self.__c_name(thing)
            self.encoded[cname] = state["Encoded"][thing]

        self.raw = {} if "Raw" in state else self.raw
        for thing in state.get("Raw", {}):
            cname = self.__c_name(thing)
            self.raw[cname] = state["Raw"][thing]

        self.manufactured = {} if "Manufactured" in state else self.manufactured
        for thing in state.get("Manufactured", {}):
            cname = self.__c_name(thing)
            self.manufactured[cname] = state["Manufactured"][thing]

        self.components = {} if "Component" in state else self.components
        for thing in state.get("Component", {}):
            cname = self.__c_name(thing)
            self.components[cname] = state["Component"][thing]

        self.items = {} if "Item" in state else self.items
        for thing in state.get("Item", {}):
            cname = self.__c_name(thing)
            self.items[cname] = state["Item"][thing]

        self.consumables = {} if "Consumable" in state else self.consumables
        for thing in state.get("Consumable", {}):
            cname = self.__c_name(thing)
            self.consumables[cname] = state["Consumable"][thing]

        self.data = {} if "Data" in state else self.data
        for thing in state.get("Data", {}):
            cname = self.__c_name(thing)
            self.data[cname] = state["Data"][thing]

        self.backpack = {} if "BackPack" in state else self.backpack
        for category in state["BackPack"]:
            ccategory = category.lower()
            self.backpack[ccategory] = {}
            things = state["BackPack"].get(category, {})
            for thing in things:
                cname = self.__c_name(thing)
                self.backpack[ccategory][cname] = things[thing]

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
        if "MicroResources" not in info:
            self.add(info["Category"], info["Name"], info["Count"])
            return

        for resource in info["MicroResources"]: 
            self.add(resource["Category"], resource["Name"], resource["Count"])

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

    def collected(self, info):
        self.add(info["Category"], info["Name"], info["Count"])

    def discarded(self, info):
        self.substract(info["Category"], info["Name"], info["Count"])

    
    def count(self, name, from_backpack=True, from_locker=True):
        total = 0
        if from_backpack:
            total += self.count_backpack(name)
        if from_locker:
            total += self.count_locker(name)
        return total

    def count_locker(self, name):
        cname = self.__c_name(name)
        category = self.category(cname)
        if category == "encoded":
            return self.encoded.get(cname, 0)
        elif category == "raw":
            return self.raw.get(cname, 0)
        elif category == "manufactured":
            return self.manufactured.get(cname, 0)
        elif category == "item":
            return self.items.get(cname, 0)
        elif category == "component":
            return self.components.get(cname, 0)
        elif category == "data":
            return self.data.get(cname, 0)
        elif category == "consumables":
            return self.consumables.get(cname, 0)
        return 0

    def count_backpack(self, name):
        cname = self.__c_name(name)
        category = self.category(cname)
        if category not in self.backpack:
            return 0
        return self.backpack[category].get(cname, 0)

    def oneliner(self, name, from_backpack=False, fallback=True):
        cname = self.__c_name(name)
        category = self.category(cname)
        entry = MATERIALS_LUT.get(cname, None)
        if not category or not entry:
            return name if fallback else None
        total_count = self.count(name)
        count = total_count
        if from_backpack:
            count = self.count_backpack(name)

        if category in ["encoded", "raw", "manufactured"]:
            grades = ["?", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ"]
            slots = ["?", "300", "250", "200", "150", "100"]
            return "{} (Grade {}; {}/{})".format(_(entry["raw"]), grades[entry["grade"]], total_count, slots[entry["grade"]])

        
        shorthands = {"data": _("DATA"), "component": _("ASSET"), "item": _("GOODS"), "consumable": _("CONSUMABLE"), "tech": _("TECH"), "chemical": _("CHEMICALS"), "circuit": _("CIRCUITS") }
        shorthand = shorthands.get(category, category[0:min(3,len(category))])
        if category == "component":
            subcategory = self.subcategory(cname)
            shorthand = shorthands.get(subcategory, shorthand)

        if from_backpack:
            if entry.get("comments", False):
                return "{} [{}]: (Backpack: {}; Locker:{}); For: {}".format(_(entry["raw"]), shorthand, count, (total_count - count) or 0, entry["comments"])
            else:
                return "{} [{}]: (Backpack: {}; Locker:{})".format(_(entry["raw"]), shorthand, count, (total_count - count) or 0)
        return "{} [{}]: {}".format(_(entry["raw"]), shorthand, total_count)

    def readable_name(self, name, fallback=True):
        cname = self.__c_name(name)
        entry = MATERIALS_LUT.get(cname, None)
        if not entry:
            return name if fallback else None
        return entry["raw"]


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
        entry = MATERIALS_LUT.get(cname, None)
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
        if info.get("event", None) == "MaterialTrade":
            paid = info["Paid"]
            self.substract(paid["Category"], paid["Material"], paid["Quantity"])
            received = info["Received"]
            self.add(received["Category"], received["Material"], received["Quantity"])
        elif info.get("event", None) == "TradeMicroResources":
            offered = info["Offered"]
            for offer in offered:
                self.substract(offer["Category"], offer["Name"], offer["Count"])
            self.add(info["Category"], info["Received"], info["Count"])


    def rewarded(self, info):
        # TODO Does Search And Rescue give material rewards??
        if "MaterialsReward" not in info:
            return
        now = EDTime.py_epoch_now()
        if self.locker_timestamp and (now - self.locker_timestamp) < 5:
            # skip manual operation since we likely got a shiplocker event already containing the change
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
        entry = MATERIALS_LUT.get(cname, None)
        if not entry:
            return 100
        slots = [100, 300, 250, 200, 150, 100]
        return slots[entry["grade"]]

    def substract(self, category, name, count):
        ccategory = self.__c_cat(category)
        cname = self.__c_name(name)
        if ccategory == "encoded":
            newcount = max(self.encoded.get(cname, 0) - count, 0)
            if newcount > 0:
                self.encoded[cname] = newcount
            else:
                self.encoded.pop(cname, None)
        elif ccategory == "raw":
            newcount = max(self.raw.get(cname, 0) - count, 0)
            if newcount > 0:
                self.raw[cname]  = newcount
            else:
                self.raw.pop(cname, None)
        elif ccategory == "manufactured":
            newcount = max(self.manufactured.get(cname, 0) - count, 0)
            if newcount > 0:
                self.manufactured[cname]  = newcount
            else:
                self.manufactured.pop(cname, None)
        elif ccategory == "data":
            newcount = max(self.data.get(cname, 0) - count, 0)
            if newcount > 0:
                self.data[cname] = newcount
            else:
                self.data.pop(cname, None)
        elif ccategory == "item":
            newcount = max(self.items.get(cname, 0) - count, 0)
            if newcount > 0:
                self.items[cname] = newcount
            else:
                self.items.pop(cname, None)
        elif ccategory == "component":
            newcount = max(self.components.get(cname, 0) - count, 0)
            if newcount > 0:
                self.components[cname] = newcount
            else:
                self.components.pop(cname, None)
        elif ccategory == "consumable":
            newcount = max(self.consumables.get(cname, 0) - count, 0)
            if newcount > 0:
                self.consumables[cname] = newcount
            else:
                self.consumables.pop(cname, None)


    def set(self, category, name, newcount):
        ccategory = self.__c_cat(category)
        cname = self.__c_name(name)
        if newcount == 0:
            self.remove(category, name)
            return

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

    def remove(self, category, name):
        ccategory = self.__c_cat(category)
        cname = self.__c_name(name)
        
        if ccategory == "encoded":
            self.encoded.pop(cname, None)
        elif ccategory == "raw":
            self.raw.pop(cname, None)
        elif ccategory == "manufactured":
            self.manufactured.pop(cname, None)
        elif ccategory == "data":
            self.data.pop(cname, None)
        elif ccategory == "item":
            self.items.pop(cname, None)
        elif ccategory == "component":
            self.components.pop(cname, None)
        elif ccategory == "consumable":
            self.consumables.pop(cname, None)

    def adjust_backpack(self, category, name, count):
        ccategory = category.lower()
        if ccategory not in self.backpack:
            self.backpack[ccategory] = {}
        newcount = max(self.backpack[ccategory].get(name, 0) + count, 0)
        if newcount > 0:
            self.backpack[ccategory][name] = newcount
        else:
            self.backpack[ccategory].pop(name, None)

    def category(self, name):
        cname = self.__c_name(name)
        entry = MATERIALS_LUT.get(cname, None)
        return entry["category"] if entry else None

    def subcategory(self, name):
        cname = self.__c_name(name)
        entry = MATERIALS_LUT.get(cname, None)
        return entry.get("subcategory", None) if entry else None
        

    @staticmethod
    def readable(name):
        cname = name.lower()
        if cname in MATERIALS_LUT:
           return MATERIALS_LUT[cname].get("localized", name)
        return name

    def __c_cat(self, category):
        ccat = category.lower()
        if ccat.endswith(";"):
            ccat = ccat[:-1]
        if ccat.startswith("$microresource_category_"):
            useless_prefix_length = len("$microresource_category_")
            ccat = ccat[useless_prefix_length:]
        return ccat

    def __c_name(self, name):
        cname = name.lower()
        if cname in MATERIALS_LUT:
            return cname

        adj_cname = cname.rstrip(";")
        if adj_cname.startswith("$"):
            adj_cname = adj_cname[1:]
        if adj_cname.endswith("_name"):
            adj_cname = adj_cname[:-5]
        adj_cname = re.sub("[ -_]", "", adj_cname)
        
        if adj_cname in MATERIALS_LUT:
            return adj_cname

        if adj_cname.endswith("s") and adj_cname[:-1] in MATERIALS_LUT:
            return adj_cname[:-1]
        elif adj_cname + "s" in MATERIALS_LUT:
            return adj_cname + "s"
        
        return INTERNAL_NAMES_LUT.get(cname, cname)

class EDRRemlokHelmet:  
    MISC_LUT = {
        "healthpack": ["TODO: healthpack; some useful info about it"],
        "ammgrenadeshieldname": ["TODO: grenade shield; some useful info about it"],
       
        "interactiveconsoleapu": ["todo: interactiveconsoleapu; some useful info about it"],
        "interactiverechargepoint": ["todo: recharge point; some useful info about it"],        
        "interactivepanellifesupportcutting01": ["todo: panel life support cutting01; some useful info about it"],
        "interactivelifesupportdoor": ["todo: life support door; some useful info about it"],
        "interactivecontaineritem": ["todo: container item; some useful info about it"],
        "interactivelocker": ["todo: locker; some useful info about it"],
        "interactivegrenadecontainer": ["todo: grenade container; some useful info about it"],
        "interactivemedkitcontainer": ["todo: medkit container; some useful info about it"],
        "interactivedropboxreactor": ["todo: dropbox reactor; some useful info about it"],
        "interactiveenergycontainer": ["todo: energy container; some useful info about it"],
        "interactivesuitcharge": ["that's useful to recharge your space suit batteries. [placeholder]"],
        "interactivedataportgeneric": ["download/upload data from here. [placeholder]"],
        "interactiveammocachesmall01": ["todo: ammunition small 01"],
        "interactivemillockera11x1maglock": ["todo: mil locker a1_1x1 maglock"],
        "interactivepanelsmallcutting01_": ["a small panel which can be cut. [placeholder]"],
        "interactiveindustdropbox": ["todo: interactiveindustdropbox; some useful info about it"],
        "interactiveconsoleindustdropbox": ["todo: console industdropbox; some useful info about it"],
        "interactiveconsoleautho": ["todo: console authorization; some useful info about it"],
        "interactiveconsolealarms": ["todo: console alarms; some useful info about it"],
        "interactivedataportindustrial": ["todo: dapaport industrial; some useful info about it"],
        "interactivelockerindustrial": ["todo: locker industrial; some useful info about it"],
        "interactiveconsolepdefence": ["todo: console pdefence; some useful info about it"],
        "interactiverechargepoint2": ["todo: rechargepoint2; some useful info about it"],
        "interactiveconsoleapturret": ["todo: console ap turret; some useful info about it"],
        "interactivepanelturretcutting01_": ["todo: panel turret cutting01; some useful info about it"],
        "interactivedataportpoi": ["dataport poi. [placeholder]"],
        "interactivedataportextraction": ["dataport extraction. [placeholder]"],
        "interactivelockerresearch'": ["locker research. [placeholder]"],
        "interactivelockermedical": ["locker medical. [placeholder]"],
        "interactivedataportpower": ["dataport power. [placeholder]"],
        "interactiveconsolereactor": ["console reactor. [placeholder]"],
        "interactiveconsolesampledropbox": ["console sample dropbox. [placeholder]"],
        "interactiveconsoleagridropbox": ["console agriculture dropbox. [placeholder]"],
        "interactivelockeragricultural": ["locker agriculture. [placeholder]"],
        "interactivedataportagricultural":  ["dataport agriculture. [placeholder]"],
        "interactivedataportsecurity": ["todo: dataport"],
        "interactivelockercomputer": ["todo: locker computer"],
        "interactivelockerpowerroom": ["todo: locker power room"],
        "interactivelockerresearch": ["todo: locker research"],
        "interactivesampledropbox":  ["todo: Sample dropbox"],
        
        "guiinteractiveterminalgen": ["that's a terminal. you can access stuff from it. [placeholder]"],
        "guiinteractiveshipyardterminalstandinggen_01": ["that's a shipyard terminal. you can manage your ships from there. [placeholder]"],
        
        "humanoidcorridorroomname": ["todo: corridor room"],
        "humanoidpowerplantroomname": ["todo: powerplant room"],
        "humanoidbarroomname": ["todo: bar room"],
        "humanoidfoyerroomname": ["todo: foyer room"],
        "humanoidhabitatbldlongname": ["todo: habitat building"],
        "humanoidcabinroomname": ["todo: cabin room"],
        "humanoidleisurebldlongname": ["todo: leisure building"],
        "humanoidpowercentrebldlongname": ["todo: power building"],
        "humanoidaccesswaya_bldlongname": ["todo: accessway a building"],
        "humanoidproductionindbldlongname": ["todo: industrial production building"],
        "humanoidprocessingroomname": ["todo: processing room"],
        "humanoidproductionagribldlongname": ["todo: agricultural production building"],
        "humanoidwarehousebldlongname": ["todo: warehouse building"],
        "humanoidcommandcenterbldlongname": ["todo: command center building"],
        "humanoidhudunknownhumanoidname":  ["todo: not yet scanned humanoid"],
        "humanoidresearchbldlongname":  ["todo: Research building"],
        "humanoidmedbayroomname": ["todo: medbay room"],
        "humanoidlaboratoryroomname": ["todo: laboratory room"],
        
        "energycell": ["energy cell. [todo]"],
        
        "skimmerdrone":  ["that's a skimmer drone, yep. [placeholder]"],
        "bombskimmerdrone":  ["that's a bomb skimmer drone, yep. [placeholder]"],
        
        "higenauthorisationpanel": ["moultipass? [placeholder]"],
        "higenkeypad": ["that's a higen keypad. [placeholder]"],
        
        "psairlock6mstr02": ["that's an airlock 6mstr 02. [placeholder]"],
        "psturretbasemedium6m": ["that's a 6m medium turret. [placeholder]"],
        "psturretbasemedium026m": ["that's a 6m medium turret 02. [placeholder]"],
        "psturretbasesmall3m": ["that's a 3m small turret. [placeholder]"],
        "psdoorwaywidelux01": ["that's a wide luxury door 01. [placeholder]"],
        "psdoorwaywide01": ["that's a wide door 01. [placeholder]"],
        "psdoorwaywidetech01": ["todo: Door way wide tech 01 building"],
        "psdoorwaywidegen01": ["that's a wide door gen 01. [placeholder]"],
        
        "poiturretplatforma": ["that's a turret platform. [placeholder]"],
        "poisalvagelootsmall": ["salvage loot small. [placeholder]"],
    }

    # TODO add timer for console sample, power, etc, using one of the gesture to trigger it and clear it.
    # TODO add SRV, clap your hand to enable/disable lights, same for ships
    
    def __init__(self):
        self.unknown_things = []

    def pointing_at(self, pointing_event):
        emote_regex = r"^\$HumanoidEmote_TargetMessage:#player=\$cmdr_decorate:#name=(.+);:#targetedAction=\$HumanoidEmote_point_Action_Targeted;:#target=\$(.+);( [0-9]+)?[;]+$"
        m = re.match(emote_regex, pointing_event.get("Message", ""))
        target = None
        if m:
            target = m.group(2)
    
        if target is None:
            return None
        target = target.rstrip(";")
        return target

    def describe_item(self, item, inventory):
        c_item = item.lower()
        if c_item in INTERNAL_NAMES_LUT:
            c_item = INTERNAL_NAMES_LUT[c_item]
        else:
            c_item = c_item.rstrip(";")
            if c_item.startswith("$"):
                c_item = c_item[1:]
            if c_item.endswith("_name"):
                c_item = c_item[:-5]
            if c_item.startswith("microresource_of:#content=$"):
                c_item = c_item[len("microresource_of:#content=$"):]
            c_item = re.sub(r"[ -_]", "", c_item)
        
        if c_item in ODYSSEY_MATS:
            return self.__describe_odyssey_material(c_item, inventory)
        elif c_item in HORIZONS_MATS:
            return self.__describe_horizons_material(c_item, inventory)
        elif c_item in self.MISC_LUT:
            return self.__describe_misc(c_item)

        if c_item.endswith("s"):
            c_item = c_item[:-1]
        else:
            c_item = c_item + "s"

        if c_item in ODYSSEY_MATS:
            return self.__describe_odyssey_material(c_item, inventory)
        elif c_item in HORIZONS_MATS:
            return self.__describe_horizons_material(c_item, inventory)
        elif c_item in self.MISC_LUT:
            return self.__describe_misc(c_item)


        if item not in self.unknown_things:
            self.unknown_things.append(item)
        return None

    def __describe_odyssey_material(self, internal_name, inventory):
        if internal_name not in ODYSSEY_MATS:
            return None
        
        descriptor = ODYSSEY_MATS[internal_name]
        entry = MATERIALS_LUT.get(internal_name, {})
        
        details = []
        inventory_descr = inventory.oneliner(internal_name)
        if inventory_descr:
            details.append(inventory_descr)

        if descriptor.get("useless", False):
            details.append(_("Useless material"))
            
        if descriptor.get("value", False):
            if descriptor.get("cost", False):
                details.append(_("Bar exchange: worth {}, cost {}").format(descriptor["value"], descriptor["cost"]))
            else:
                details.append(_("Bar exchange: worth {}").format(descriptor["value"]))
        
        if entry.get("comments", False):
            details.append(_("Used for: {}").format(entry["comments"]))
        else:
            if descriptor.get("blueprints", False):
                if descriptor.get("upgrades", False):
                    details.append(_("Used in {} blueprints, {} upgrades").format(descriptor["blueprints"], descriptor["upgrades"]))
                else:
                    details.append(_("Used in {} blueprints").format(descriptor["blueprints"]))
            elif descriptor.get("upgrades", False):
                details.append(_("Used in {} upgrades").format(descriptor["upgrades"]))

        if descriptor.get("referer", False) and descriptor.get("refer", False):
            details.append(_("Required by {} to refer {}").format(descriptor["referer"], descriptor["refer"]))
        
        if descriptor.get("unlock", False):
            details.append(_("Required by {}").format(descriptor["unlock"]))

        if descriptor.get("locations", False):
            details.append(_("Found in: {}").format("; ".join(descriptor["locations"])))

        return details

    def describe_odyssey_material_short(self, internal_name, inventory, ignore_eng_unlocks=False):
        if internal_name not in ODYSSEY_MATS:
            return None
        
        cname = self.__c_name(internal_name)
        entry = MATERIALS_LUT.get(cname, {})
        has_comments = entry.get("comments", False)
        values = self.worthiness_odyssey_material(internal_name, ignore_eng_unlocks, ignore_upgrades_and_mods=has_comments)
        owned = inventory.count(internal_name)
        
        if owned:
            if has_comments:
                return "{} ({} => {}) [S{}]".format(entry.get("raw", internal_name), values, entry["comments"], owned) 
            else:
                return "{} ({}) [S{}]".format(entry.get("raw", internal_name), values, owned) 
        if has_comments:
            return "{} ({} => {})".format(entry.get("raw", internal_name), values, entry["comments"])
        return "{} ({})".format(entry.get("raw", internal_name), values)

    def worthiness_odyssey_material(self, internal_name, ignore_eng_unlocks=False, ignore_upgrades_and_mods=False):
        if internal_name not in ODYSSEY_MATS:
            return None
        
        descriptor = ODYSSEY_MATS[internal_name]
        values  = []
        if descriptor.get("useless", False):
            values.append(_("0"))
        
        if descriptor.get("blueprints", False) and not ignore_upgrades_and_mods:
            values.append(_("B{}").format(descriptor["blueprints"]))
        
        if descriptor.get("upgrades", False) and not ignore_upgrades_and_mods:
            values.append(_("U{}").format(descriptor["upgrades"]))

        if descriptor.get("value", False):
            values.append(_("X{}").format(descriptor["value"]))
        
        if not ignore_eng_unlocks:
            value = 0
            if descriptor.get("referer", False) and descriptor.get("refer", False):
                value +=1
            
            if descriptor.get("unlock", False):
                value +=1
            
            if value:
                values.append(_("E{}").format(value))
        
        return "/".join(values)
    
    def __describe_horizons_material(self, internal_name, inventory):
        if internal_name not in HORIZONS_MATS:
            return None

        descriptor = HORIZONS_MATS[internal_name]
        details = []

        inventory_descr = inventory.oneliner(internal_name)
        if inventory_descr:
            details.append(inventory_descr)
        
        if descriptor.get("useless", False):
            details.append(_("Useless material"))
        
        recipe_categories = ["blueprints", "synthesis", "experimentals", "techbroker"]
        prefixes = {"blueprints": _("blueprints"), "synthesis": _("synthesis") , "experimentals": _("experimental effects"), "techbroker": _("tech broker items")}
        all_recipes = []
        for category in recipe_categories:
            if descriptor.get(category, False):
                all_recipes.append(_("{} {}").format(descriptor[category], prefixes[category]))
        details.append(_("Used in: {}").format("; ".join(all_recipes)))

        if descriptor.get("unlock", False):
            details.append(_("Required by {}").format(descriptor["unlock"]))

        return details

    def is_data(self, name):
        cname = self.__c_name(name)
        entry = MATERIALS_LUT.get(cname, None)
        return entry["category"] == "data" if entry else False
    
    def is_assets(self, name):
        cname = self.__c_name(name)
        entry = MATERIALS_LUT.get(cname, None)
        return entry["category"] == "component" if entry else False

    def is_goods(self, name):
        cname = self.__c_name(name)
        entry = MATERIALS_LUT.get(cname, None)
        return entry["category"] == "item" if entry else False

    def is_odyssey_mat(self, name):
        cname = self.__c_name(name)
        return cname in ODYSSEY_MATS
        

    def __c_name(self, name):
        cname = name.lower()
        if cname in MATERIALS_LUT:
            return cname

        adj_cname = cname.rstrip(";")
        if adj_cname.startswith("$"):
            adj_cname = adj_cname[1:]
        if adj_cname.endswith("_name"):
            adj_cname = adj_cname[:-5]
        adj_cname = re.sub("[ -_]", "", adj_cname)
        
        if adj_cname in MATERIALS_LUT:
            return adj_cname

        if adj_cname.endswith("s") and adj_cname[:-1] in MATERIALS_LUT:
            return adj_cname[:-1]
        elif adj_cname + "s" in MATERIALS_LUT:
            return adj_cname + "s"
        
        return INTERNAL_NAMES_LUT.get(cname, cname)

    def how_useful(self, item):
        c_item = item.lower()
        if c_item in INTERNAL_NAMES_LUT:
            c_item = INTERNAL_NAMES_LUT[c_item]
        else:
            c_item = c_item.rstrip(";")
            if c_item.startswith("$"):
                c_item = c_item[1:]
            if c_item.endswith("_name"):
                c_item = c_item[:-5]
            if c_item.startswith("microresource_of:#content=$"):
                c_item = c_item[len("microresource_of:#content=$"):]
            c_item = re.sub(r"[ -_]", "", c_item)
        
        if c_item in ODYSSEY_MATS:
            return self.__how_useful_odyssey_material(c_item)
        elif c_item in HORIZONS_MATS:
            # TODO not expected yet
            return 0
        elif c_item in self.MISC_LUT:
            return 0
        return 0

    def __how_useful_odyssey_material(self, internal_name):
        score = {"engineering": 0, "unlocks": 0}
        if internal_name not in ODYSSEY_MATS:
            return score["engineering"]
        
        descriptor = ODYSSEY_MATS[internal_name]
        if descriptor.get("useless", False):
            return score["engineering"]
            
        # 4 is the median trading value for odyssey mats.
        # So, this adds up 1 point if "mid of the pack" stuff, 2 points for the highest known value.
        score["engineering"] += descriptor.get("value", 0) / 4

        score["engineering"] += descriptor.get("blueprints", 0)
        score["engineering"] += descriptor.get("upgrades", 0)
        
        if descriptor.get("referer", False) and descriptor.get("refer", False):
            score["unlocks"] += 1
        
        if descriptor.get("unlock", False):
            score["unlocks"] += 1

        return score["engineering"]


    def __describe_misc(self, internal_name):
        #if internal_name not in self.MISC_LUT:
        #    return None
        #
        #return self.MISC_LUT[internal_name]
        return None
