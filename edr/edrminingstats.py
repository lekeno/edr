from __future__ import absolute_import

from collections import deque
from edtime import EDTime

class EDRMiningStats(object):
    def __init__(self):
        self.of_interest = { "names": ["lowtemperaturediamond", "painite", "voidopal"], "types": ["$lowtemperaturediamond_name;", "$painite_name;", "$opal_name;"]}
        self.max = 0
        self.previous_max = 0
        self.min = 100.0
        self.previous_min = 0
        self.sum = 0
        self.distribution = {"last_index": 0, "bins": [0]*25}
        self.lmh = {"-": 0, "L": 0, "M": 0, "H": 0}
        self.prospected_nb = 0
        self.refined_nb = 0
        self.refinements = deque(maxlen=20)
        self.prospectements = deque(maxlen=20)
        self.efficiency = deque(maxlen=20)
        self.max_efficiency = 150
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        self.prospected_raw_history = deque(maxlen=8) # 8 max prospector drones
        self.last = {"timestamp": now, "proportion": None, "raw": None, "materials": None}
        self.depleted = False

    def reset(self):
        self.max = 0
        self.previous_max = 0
        self.min = 100.0
        self.previous_min = 0
        self.sum = 0
        self.distribution = {"last_index": 0, "bins": [0]*25}
        self.lmh = {"-": 0, "L": 0, "M": 0, "H": 0}
        self.prospected_nb = 0
        self.refined_nb = 0
        self.refinements = deque(maxlen=20)
        self.prospectements = deque(maxlen=20)
        self.efficiency = deque(maxlen=20)
        self.max_efficiency = 150
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        self.last = {"timestamp": now, "proportion": None, "raw": None, "materials": None}
        self.depleted = False

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
            "proportion": 0,
            "raw": key,
            "materials": len(materials)
        }
        
        was_a_dud = True
        for material in materials:
            if material.get("Name", "").lower() in self.of_interest["names"]:
                proportion = material.get("Proportion", 0.0)
                self.sum += proportion / 100.0
                self.previous_max = self.max
                self.previous_min = self.min
                self.max = max(self.max, proportion)
                self.min = min(self.min, proportion)
                index = int(round(proportion/100.0 * (len(self.distribution["bins"])-1), 0))
                self.distribution["last_index"] = index
                self.distribution["bins"][index] += 1
                self.prospectements.append((now, proportion))
                self.last["proportion"] = proportion
                was_a_dud = False
                break # TODO: assumption, an asteroid can't have multiple mineral of interest (at least for now, can't have both LTD and Painite or VO)
        if was_a_dud:
            self.distribution["last_index"] = 0
            self.distribution["bins"][0] += 1
            self.prospectements.append((now, 0.0))

    def __probably_previously_prospected(self, entry):
        b = entry.copy()
        b["timestamp"] = ""
        b["Remaining"] = ""
        matching_entry = None
        for previous in self.prospected_raw_history:
            a = previous.copy()
            a["timestamp"] = ""
            a["Remaining"] = ""
            if a == b:
                matching_entry = previous
                break 
            
        if matching_entry:
            max_age = 60*5
            a_time = EDTime().from_journal_timestamp(matching_entry["timestamp"])
            b_time = EDTime().from_journal_timestamp(entry["timestamp"])
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
        self.refinements.append((now, 1))
        self.__update_efficiency()

    def mineral_per_hour(self):
        now = EDTime.py_epoch_now()
        self.current = now
        elapsed_time = self.current - self.start
        if elapsed_time:
            return self.refined_nb / (elapsed_time / 3600.0)
        return 0
    
    def mineral_yield_average(self):
        return (self.sum / self.prospected_nb)*100.0 if self.prospected_nb else 0.0

    def __update_efficiency(self):
        now = EDTime.py_epoch_now()
        efficiency = self.mineral_per_hour()
        self.efficiency.append((now, efficiency))
        self.max_efficiency = max(self.max_efficiency, efficiency)


    def __repr__(self):
        return str(self.__dict__)