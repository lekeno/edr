from __future__ import absolute_import

import json
import re
import os

from edrlog import EDRLog
import utils2to3

EDRLOG = EDRLog()
POWER_DATA = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'modules_power_data.json')).read())

class EDModule(object):
    def __init__(self, module):
        self.power_draw = EDModule.__get_power_draw(module)
        self.power_generation = EDModule.__get_power_gen(module) 
        self.priority = EDModule.__get_priority(module)
        self.cname = module["Item"].lower() if "Item" in module else None
        self.on = module.get("On", False)

    def update(self, module):
        prev_power_draw = self.power_draw
        prev_priority = self.priority
        prev_cname = self.cname
        prev_on = self.on

        EDRLOG.log(u"before: {}, {}, {}, {}".format(prev_cname, prev_power_draw, prev_priority, prev_on), "DEBUG")

        self.power_draw = module["Power"] if "Power" in module else EDModule.__get_power_draw(module)
        self.priority = EDModule.__get_priority(module)
        self.cname = module["Item"].lower() if "Item" in module else None
        self.on = module.get("On", True)

        updated = prev_power_draw != self.power_draw or prev_priority != self.priority or prev_cname != self.cname or prev_on != self.on
        if updated:
            EDRLOG.log(u"after: {}, {}, {}, {}".format(self.cname, self.power_draw, self.priority, self.on), "DEBUG")
        return updated


    def is_valid(self):
        return not (self.priority is None or self.power_draw is None or self.cname is None)

    def generic_name(self):
        match = re.search('([a-zA-Z_]*)_size[0-9]_class[0-9](_[a-zA-Z_]*)?', self.cname)
        if match:
            return match.group(1)
        return self.cname

    def size_and_class(self):
        match = re.search('[a-zA-Z_]*_size([0-9])_class([0-9])_[a-zA-Z_]*', self.cname)
        if match:
            return match.groups()
        return None

    def readable_name(self):
        lut = { 
            "int_hyperdrive": "FSD",
            "int_engine": "Thruster",
            "int_shieldgenerator": "Shield"
        }
        return lut.get(self.cname, self.cname)

    def is_shield(self):
        return self.cname.startswith('int_shieldgenerator')

    def is_prospector_drone_controller(self):
        return self.cname.startswith('int_dronecontrol_prospector')

    def is_drone_controller(self):
        return self.cname.startswith('int_dronecontrol')
    
    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def __get_power_draw(module):
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        power_draw = None
        item = module["Item"].lower() if "Item" in module else None
        if  item is None or item.startswith(('int_fueltank_', 'int_planetapproachsuite', 'int_passengercabin_', 'int_cargorack_', 'int_corrosionproof', 'int_hullreinforcement_', 'int_fueltank_', 'int_passengercabin_', 'int_metaalloyhullreinforcement_', 'int_modulereinforcement_', 'int_detailedsurfacescanner_')):
            power_draw = 0
        elif item in POWER_DATA:
            power_draw = POWER_DATA[item]["powerdraw"]
        elif item.startswith("modularcargobaydoor"):
            power_draw = 0.6
        else:
            EDRLOG.log(u"unknown item: {}".format(item), "DEBUG")
        for modifier in modifiers:
            if modifier.get("Label", "").lower() != "powerdraw":
                continue
            power_draw = modifier["Value"]
        return power_draw

    @staticmethod
    def __get_priority(module):
        if module["Item"].lower().startswith('int_guardian') and 'Priority' not in module:
            # Since the last patch in April, some?all? the Guardian modules have a fixed priority and are always on...
            # Both Priority and Powr draw are missing in modulesinfo.json. 
            return 1
        return module["Priority"] + 1 if "Priority" in module else None

    @staticmethod
    def __get_power_gen(module):
        power_generation = 0
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        item = module["Item"].lower() if "Item" in module else None
        power_generation = POWER_DATA[item]["powergen"] if item in POWER_DATA else None
        for modifier in modifiers:
            if modifier.get("Label", "").lower() != "powercapacity":
                continue
            power_generation = modifier["Value"]
        return power_generation