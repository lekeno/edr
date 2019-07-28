import json
import re
import os
import edrlog
EDRLOG = edrlog.EDRLog()
POWER_DATA = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/modules_power_data.json')).read())

class EDModule(object):
    def __init__(self, module):
        self.power_draw = EDModule.__get_power_draw(module)
        self.power_generation = EDModule.__get_power_gen(module) 
        self.priority = EDModule.__get_priority(module)
        self.cname = module["Item"].lower() if "Item" in module else None
        self.on = module.get("On", False)

    def update(self, module):
        self.power_draw = module["Power"] if "Power" in module else self.power_draw
        self.priority = EDModule.__get_priority(module)
        self.cname = module["Item"].lower() if "Item" in module else None
        self.on = module.get("On", True) #TODO unclear if modulesinfo contains that info in some sort

    def is_valid(self):
        return not (self.priority is None or self.power_draw is None or self.cname is None)

    def generic_name(self):
        match = re.search('([a-zA-Z_]*)_size[0-9]_class[0-9](_[a-zA-Z_].*)?', self.cname)
        if match:
            return match.group(1)
        return self.cname

    def readable_name(self):
        lut = { 
            "int_hyperdrive": "FSD",
            "int_engine": "Thruster",
            "int_shieldgenerator": "Shield"
        }
        return lut.get(self.cname, self.cname)

    def is_shield(self):
        return self.cname.startswith('int_shieldgenerator')

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