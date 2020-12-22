from __future__ import absolute_import

from collections import deque
from edtime import EDTime
from edri18n import _

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

    def prospected(self, proportion):
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
        now = EDTime.py_epoch_now()
        self.prospectements.append((now, proportion))

    def refined(self):
        self.refined_nb += 1
        now = EDTime.py_epoch_now()
        self.refinements.append((now, 1))

    def yield_average(self, overall_prospected_nb):
        if overall_prospected_nb <= 0:
            return 0.0
        return (self.sum / overall_prospected_nb)*100.0


class EDRMiningStats(object):
    MINERALS_LUT = { 
        "platinum": {"name": "platinum", "type": "$platinum_name;", "symbol": _("Pt")},
        "monazite": {"name": "monazite", "type": "$monazite_name;", "symbol": _("MNZT")},
        "musgravite": {"name": "musgravite", "type": "$musgravite_name;", "symbol": _("MGRV")},
        "low temperature diamond": { "name": "lowtemperaturediamond", "type": "$lowtemperaturediamond_name;", "symbol": _("LTD")},
        "painite": { "name": "painite", "type": "$painite_name;", "symbol": _("PAIN")},
        "void opal": { "name": "voidopal", "type": "$opal_name;", "symbol": _("V.O.")},
    }

    MINERAL_TYPES_LUT = { 
        "$platinum_name;": "platinum",
        "$monazite_name;": "monazite",
        "$musgravite_name;": "musgravite",
        "$lowtemperaturediamond_name;": "lowtemperaturediamond",
        "$painite_name;": "painite",
        "$opal_name;": "voidopal",
    }
    ## musgravite, monazite and maybe Grandidierite Alexandrite Benitoite
    ## can have multiple of these... 

    def __init__(self):
        self.lmh = {"-": 0, "L": 0, "M": 0, "H": 0}
        self.prospected_nb = 0
        self.max_efficiency = 150
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        self.last = {"timestamp": now, "raw": None, "materials": None, "minerals_stats": []}
        self.depleted = False
        self.of_interest = { "names": set(), "types": set()}
        self.stats = {}
        self.refined_nb = 0
        self.prospected_raw_history = deque(maxlen=8) # 8 max prospector drones
        self.efficiency = deque(maxlen=20)
        for mineral in self.MINERALS_LUT:
            name = self.MINERALS_LUT[mineral]["name"]
            internal_name = self.MINERALS_LUT[mineral]["type"]
            symbol = self.MINERALS_LUT[mineral]["symbol"]
            self.of_interest["names"].add(name)
            self.of_interest["types"].add(internal_name)
            self.stats[mineral] = EDRMineralStats(name, internal_name, symbol)

    def reset(self):
        self.lmh = {"-": 0, "L": 0, "M": 0, "H": 0}
        self.prospected_nb = 0
        self.max_efficiency = 150
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        self.refined_nb = 0
        self.last = {"timestamp": now, "raw": None, "materials": None, "minerals_stats": []}
        self.depleted = False
        self.of_interest = { "names": set(), "types": set()}
        self.stats = {}
        self.prospected_raw_history = deque(maxlen=8) # 8 max prospector drones
        for mineral in self.MINERALS_LUT:
            name = self.MINERALS_LUT[mineral]["name"]
            internal_name = self.MINERALS_LUT[mineral]["type"]
            symbol = self.MINERALS_LUT[mineral]["symbol"]
            self.of_interest["names"].add(name)
            self.of_interest["types"].add(internal_name)
            self.stats[mineral] = EDRMineralStats(name, internal_name, symbol)

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
        now = EDTime.py_epoch_now()
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
            "minerals_stats": []
        }
        
        for material in materials:
            cname = material.get("Name", "").lower()
            if cname in self.of_interest["names"]:
                proportion = material.get("Proportion", 0.0)
                self.stats[cname].prospected(proportion)
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
        now = EDTime.py_epoch_now()
        self.current = now
        if entry.get("Type", "").lower() not in self.of_interest["types"]:
            return

        self.refined_nb += 1
        self.__update_efficiency()
        cinternal_name = entry.get("Type", "").lower()
        if cinternal_name in self.of_interest["types"]:
            cname = self.MINERAL_TYPES_LUT[cinternal_name]
            self.stats[cname].refined()

    def last_max():
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
        efficiency = self.mineral_per_hour()
        self.efficiency.append((now, efficiency))
        self.max_efficiency = max(self.max_efficiency, efficiency)


    def __repr__(self):
        return str(self.__dict__)