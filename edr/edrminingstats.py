from __future__ import absolute_import

from collections import deque
from edtime import EDTime

# TODO consider doing more than just LTD? configurable? automatic?
# TODO keep ~0% LTD in distribution and show it?
class EDRMiningStats(object):
    def __init__(self):
        self.name = "lowtemperaturediamond"
        self.type = "$lowtemperaturediamond_name;"
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

    def prospected(self, entry):
        if entry.get("event", None) != "ProspectedAsteroid":
            return False
        if entry.get("Remaining", 0) <= 0:
            return False
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
        
        had_no_ltd = True
        for material in materials:
            if material.get("Name", "").lower() == self.name:
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
                had_no_ltd = False
                break
        if had_no_ltd:
            self.distribution["last_index"] = 0
            self.distribution["bins"][0] += 1
            self.prospectements.append((now, 0.0))

    def refined(self, entry):
        if entry.get("event", None) != "MiningRefined":
            return
        now = EDTime.py_epoch_now()
        self.current = now
        if entry.get("Type", "").lower() != self.type:
            return
        self.refined_nb += 1
        self.refinements.append((now, 1))
        self.__update_efficiency()

    def ltd_per_hour(self):
        now = EDTime.py_epoch_now()
        self.current = now
        elapsed_time = self.current - self.start
        if elapsed_time:
            return self.refined_nb / (elapsed_time / 3600.0)
        return 0
    
    def ltd_yield_average(self):
        return (self.sum / self.prospected_nb)*100.0 if self.prospected_nb else 0.0

    def __update_efficiency(self):
        now = EDTime.py_epoch_now()
        efficiency = self.ltd_per_hour()
        self.efficiency.append((now, efficiency))
        self.max_efficiency = max(self.max_efficiency, efficiency)


    def __repr__(self):
        return str(self.__dict__)