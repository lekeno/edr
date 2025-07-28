from __future__ import absolute_import

from collections import deque
from time import time
from edtime import EDTime
from edri18n import _
import json
import utils2to3

class EDRMineralStats(object):
    def __init__(self, name, internal_name, symbol):
        self.name = name
        self.internal_name = internal_name
        self.symbol = symbol
        self.previous_min = 0.0
        self.min = 100.0
        self.previous_max = 0.0
        self.max = 0.0
        self.distribution = {"last_index": 0, "bins": [0]*25}
        self.sum = 0
        self.refined_nb = 0
        self.refinements = deque(maxlen=20)
        self.prospectements = deque(maxlen=20)
        self.efficiency = deque(maxlen=20)
        now = EDTime.py_epoch_now()
        self.last = {"timestamp": now, "proportion": None}

    def prospected(self, proportion, now):
        if proportion:
            self.sum += proportion / 100.0
            self.previous_max = self.max
            self.previous_min = self.min
            self.max = max(self.max, proportion)
            self.min = min(self.min, proportion)
            self.last["proportion"] = proportion
        index = int(round(proportion/100.0 * (len(self.distribution["bins"])-1), 0))
        self.distribution["last_index"] = index
        self.distribution["bins"][index] += 1
        self.prospectements.append((now, proportion))

    def refined(self, now):
        self.refined_nb += 1
        self.refinements.append((now, 1))

    def yield_average(self, overall_prospected_nb):
        if overall_prospected_nb <= 0:
            return 0.0
        return (self.sum / overall_prospected_nb)*100.0


class EDRMiningStats(object):
    MINERALS_LUT = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'mining.json')).read())

    def __init__(self):
        self.lmh = {"-": 0, "L": 0, "M": 0, "H": 0}
        self.prospected_nb = 0
        self.max_efficiency = 150
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        self.last = {"timestamp": now, "raw": None, "materials": None, "minerals_stats": [], "proportion": None}
        self.depleted = False
        self.of_interest = { "names": set(), "types": set()}
        self.stats = {}
        self.refined_nb = 0
        self.prospected_raw_history = deque(maxlen=8) # 8 max prospector drones
        self.efficiency = deque(maxlen=20)
        self.mineral_types_lut = {}
        for mineral in self.MINERALS_LUT:
            name = self.MINERALS_LUT[mineral]["name"]
            internal_name = self.MINERALS_LUT[mineral]["type"]
            self.mineral_types_lut[internal_name] = name
            symbol = self.MINERALS_LUT[mineral]["symbol"]
            self.of_interest["names"].add(name)
            self.of_interest["types"].add(internal_name)
            self.stats[name] = EDRMineralStats(name, internal_name, symbol)

    def reset(self):
        self.lmh = {"-": 0, "L": 0, "M": 0, "H": 0}
        self.prospected_nb = 0
        self.max_efficiency = 150
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        self.refined_nb = 0
        self.last = {"timestamp": now, "raw": None, "materials": None, "minerals_stats": [], "proportion": None}
        self.depleted = False
        self.of_interest = { "names": set(), "types": set()}
        self.stats = {}
        self.prospected_raw_history = deque(maxlen=8) # 8 max prospector drones
        self.mineral_types_lut = {}
        for mineral in self.MINERALS_LUT:
            name = self.MINERALS_LUT[mineral]["name"]
            internal_name = self.MINERALS_LUT[mineral]["type"]
            self.mineral_types_lut[internal_name] = name
            symbol = self.MINERALS_LUT[mineral]["symbol"]
            self.of_interest["names"].add(name)
            self.of_interest["types"].add(internal_name)
            self.stats[name] = EDRMineralStats(name, internal_name, symbol)

    def dummify(self):
        self.reset()
        
        events = [
            { "delta":0, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":32.171711 }, { "Name":"Indite", "Proportion":3.015685 }, { "Name":"Silver", "Proportion":7.020900 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":5, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":22.635149 }, { "Name":"Indite", "Proportion":12.600220 }, { "Name":"Painite", "Proportion":12.419773 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":26, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":26.404419 }, { "Name":"Samarium", "Proportion":17.613367 }, { "Name":"Praseodymium", "Proportion":7.239036 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":22, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Bertrandite", "Proportion":30.968697 }, { "Name":"Painite", "Proportion":7.976030 }, { "Name":"Samarium", "Proportion":3.769541 } ], "Content":"$AsteroidMaterialContent_Low;", "Content_Localised":"Material Content: Low", "Remaining":100.000000 },
            { "delta":28, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Painite", "Proportion":34.572594 }, { "Name":"Bertrandite", "Proportion":12.292540 }, { "Name":"Indite", "Proportion":8.305000 } ], "Content":"$AsteroidMaterialContent_Low;", "Content_Localised":"Material Content: Low", "Remaining":100.000000 },
            { "delta":46, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":6, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":5, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":6, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":5, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":5, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":5, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":60, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Praseodymium", "Proportion":35.965885 }, { "Name":"Painite", "Proportion":9.763608 }, { "Name":"Indite", "Proportion":6.561393 } ], "Content":"$AsteroidMaterialContent_Low;", "Content_Localised":"Material Content: Low", "Remaining":100.000000 },
            { "delta":26, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Indite", "Proportion":28.778957 }, { "Name":"Gold", "Proportion":14.339796 }, { "Name":"Praseodymium", "Proportion":5.365635 } ], "Content":"$AsteroidMaterialContent_Low;", "Content_Localised":"Material Content: Low", "Remaining":100.000000 },
            { "delta":5, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":30.249086 }, { "Name":"Indite", "Proportion":10.113951 }, { "Name":"Silver", "Proportion":11.140014 } ], "Content":"$AsteroidMaterialContent_High;", "Content_Localised":"Material Content: High", "Remaining":100.000000 },
            { "delta":18, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":31.419930 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":22, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Palladium", "Proportion":25.370291 }, { "Name":"Praseodymium", "Proportion":24.505444 }, { "Name":"Indite", "Proportion":4.841553 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":16, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":20.945780 }, { "Name":"Painite", "Proportion":15.845593 }, { "Name":"Indite", "Proportion":8.426105 } ], "Content":"$AsteroidMaterialContent_Low;", "Content_Localised":"Material Content: Low", "Remaining":100.000000 },
            { "delta":18, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":33.340839 }, { "Name":"Palladium", "Proportion":20.186563 }, { "Name":"Samarium", "Proportion":5.996222 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":27, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Painite", "Proportion":40.854160 }, { "Name":"Indite", "Proportion":10.070118 } ], "Content":"$AsteroidMaterialContent_Low;", "Content_Localised":"Material Content: Low", "Remaining":100.000000 },
            { "delta":17, "event":"ProspectedAsteroid", "Materials":[ { "Name":"Gallite", "Proportion":22.635149 }, { "Name":"Indite", "Proportion":12.600220 }, { "Name":"Painite", "Proportion":12.419773 } ], "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 },
            { "delta":19, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":4, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":5, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":28, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":11, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":4, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":4, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" },
            { "delta":9, "event":"MiningRefined", "Type":"$painite_name;", "Type_Localised":"Painite" }
        ]

        faketime = EDTime()
        faketime.rewind(8*60)
        self.start -= 8*60
        for entry in events:
            faketime.advance(entry["delta"])
            entry["timestamp"] = faketime.as_journal_timestamp()
            if entry.get("event", None) == "ProspectedAsteroid":
                self.prospected(entry)
            elif entry.get("event", None) == "MiningRefined":
                self.refined(entry)

    def prospected(self, entry):
        if entry.get("event", None) != "ProspectedAsteroid":
            return False
        if entry.get("Remaining", 0) <= 0:
            self.depleted = True
            return False

        self.depleted = False
        if self.__probably_previously_prospected(entry):
            return False
        
        self.prospected_raw_history.append(entry)
        timestamp = EDTime()
        timestamp.from_journal_timestamp(entry["timestamp"])
        now = timestamp.as_py_epoch()
        self.current = now
        self.prospected_nb += 1
        self.__update_efficiency()
        
        lut_content = {
            "n/a": "-",
            "$AsteroidMaterialContent_Low;": "L",
            "$AsteroidMaterialContent_Medium;": "M",
            "$AsteroidMaterialContent_High;": "H"
        }

        key = lut_content.get(entry.get("Content", "-"), "-")
        self.lmh[key] += 1
        materials = entry.get("Materials", [])
        self.last = {
            "timestamp": now,
            "raw": key,
            "materials": len(materials),
            "minerals_stats": [],
            "proportion": None
        }
        
        for material in materials:
            cname = material.get("Name", "").lower().replace(" ", "")
            if cname in self.of_interest["names"]:
                proportion = material.get("Proportion", 0.0)
                self.stats[cname].prospected(proportion, now)
                self.last["minerals_stats"].append(self.stats[cname])
                

    def __probably_previously_prospected(self, entry):
        b = entry.copy()
        b["timestamp"] = ""
        b["Remaining"] = ""
        matching_entry = None
        for previous in self.prospected_raw_history:
            a = previous.copy()
            a["timestamp"] = ""
            a["Remaining"] = ""
            if a == b and previous["Remaining"] >= entry["Remaining"]:
                matching_entry = previous
                break 
            
        if matching_entry:
            max_age = 60*5
            a_time = EDTime()
            a_time.from_journal_timestamp(matching_entry["timestamp"])
            b_time = EDTime()
            b_time.from_journal_timestamp(entry["timestamp"])
            return (b_time.as_py_epoch() - a_time.as_py_epoch()) <= max_age
        return False
    
    def refined(self, entry):
        if entry.get("event", None) != "MiningRefined":
            return
        timestamp = EDTime()
        timestamp.from_journal_timestamp(entry["timestamp"])
        now = timestamp.as_py_epoch()
        self.current = now
        if entry.get("Type", "").lower() not in self.of_interest["types"]:
            return

        self.refined_nb += 1
        self.__update_efficiency()
        cinternal_name = entry.get("Type", "").lower()
        if cinternal_name in self.of_interest["types"]:
            cname = self.mineral_types_lut[cinternal_name]
            self.stats[cname].refined(now)

    def last_max(self):
        if not self.last["minerals_stats"]:
            return self.max
        return self.last["mineral_stats"][0].max

    def item_per_hour(self):
        now = EDTime.py_epoch_now()
        self.current = now
        elapsed_time = self.current - self.start
        if elapsed_time:
            return self.refined_nb / (elapsed_time / 3600.0)
        return 0
    
    def last_yield_average(self):
        if self.prospected_nb <= 0:
            return 0.0

        if not self.last["minerals_stats"]:
            return (self.sum / self.prospected_nb)*100.0
        return self.last["minerals_stats"][0].yield_average(self.prospected_nb)

    def __update_efficiency(self):
        now = EDTime.py_epoch_now()
        efficiency = self.item_per_hour()
        self.efficiency.append((now, efficiency))
        self.max_efficiency = max(self.max_efficiency, efficiency)


    def __repr__(self):
        return str(self.__dict__)