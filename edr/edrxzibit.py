import json
import re
import os
import edrlog
from edri18n import _
EDRLOG = edrlog.EDRLog()

class EDRXzibit(object):
    POWER_DATA = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/modules_power_data.json')).read())

    def __init__(self, modules):
        self.power_capacity = EDRXzibit.__get_power_capacity(modules)
        
        self.per_prio = {"1": { "powerdraw": 0, "modules": []}, "2": { "powerdraw": 0, "modules": []}, "3": { "powerdraw": 0, "modules": []}, "4": { "powerdraw": 0, "modules": []}, "5": { "powerdraw": 0, "modules": []}}
        for module in modules:
            prio = EDRXzibit.__get_power_priority(module)
            draw = EDRXzibit.__get_power_draw(module)
            cname = module.get("Item", None)
            if not (prio is None or draw is None or cname is None):
                self.per_prio[str(prio)]["powerdraw"] += draw
                self.per_prio[str(prio)]["modules"].append(cname.lower())

    def assess_power_priorities(self):
        if not self.power_capacity:
            return None

        assessment = {}
        assessment["20"] = self._assess_busted_powerplant()
        assessment["50"] = self._assess_recovered_powerplant()
        assessment["40"] = self._assess_malfunctioning_powerplant()
        return assessment

    def _functional_at(self, percent):
        power_draw = 0
        threshold = self.power_capacity * percent
        within_modules = set()
        within_priorities = []
        for pri in sorted(self.per_prio.keys()):
            power_draw += self.per_prio[pri]["powerdraw"]
            if power_draw > threshold:
                break
            within_priorities.append(u"P{}".format(pri))
            
            for module in self.per_prio[pri]["modules"]:
                within_modules.add(EDRXzibit.__generic_name(module))

        return {"modules": within_modules, "priorities": within_priorities}

    def _assess_overall_priorities(self):
        functional = self._functional_at(1.0)
        #TODO priorities and modules with/without hardpoints deployed

    def _assess_busted_powerplant(self):
        functional = self._functional_at(.2)
        assessment = {
            "situation": _(u"Busted PP (20% for 5s; {0:.2f}MW)").format(self.power_capacity * .2),
            "annotation": u", ".join(functional["priorities"]),
        }

        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
        else:
            assessment["grade"] = 0.2

        if 'int_hyperdrive' not in functional["modules"]:
            assessment["recommendation"] = _(u"Keep your FSD below the 20% line.")
        else:
            assessment["grade"] = 1.0
            assessment["praise"] = _(u"Good job on keeping your FSD below the 20% line.")

        return assessment

    def _assess_recovered_powerplant(self):
        functional = self._functional_at(.5)
        assessment = {
            "situation": _(u"Recovered PP (50% after 5s; {0:.2f}MW)").format(self.power_capacity * .5),
            "annotation": u", ".join(functional["priorities"]),
        }
        
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
        else:
            assessment["grade"] = 0.2

        if 'int_hyperdrive' not in functional["modules"]:
            assessment["grade"] = 0
            assessment["recommendation"] = _(u"Keep your FSD below the 50% line.")
        else:
            assessment["grade"] = 1.0
            assessment["praise"] = _(u"Good job on keeping your FSD below the 50% line.")

        return assessment
    
    def _assess_malfunctioning_powerplant(self):
        functional = self._functional_at(.4)
        assessment = {
            "situation": _(u"Malfunctioning PP (40% for 5s; {0:.2f}MW)").format(self.power_capacity * .4),
            "annotation": u", ".join(functional["priorities"]),
        }
        
        critical_set = set(['int_hyperdrive', 'int_engine'])
        if self._has_shield():
            critical_set.add('int_shieldgenerator')
        missing = [EDRXzibit.__readable_name(module) for module in critical_set - functional["modules"]]
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
            assessment["recommendation"] = _(u"Keep your {} below the 40% line.").format(', '.join(missing))
            return assessment

        if not critical_set.issubset(functional["modules"]):
            present = [EDRXzibit.__readable_name(module) for module in critical_set.intersection(functional["modules"])]
            if present:
                assessment["grade"] = 1.0/len(critical_set) * len(present)
                assessment["recommendation"] = _(u"Keep your {} below the 40% line.").format(', '.join(missing))
                assessment["praise"] = _(u"Good job with your {}.").format(', '.join(present))
            else:
                assessment["grade"] = 0.2
                assessment["recommendation"] = _(u"Keep your {} below the 40% line.").format(', '.join(missing))
        else:
            assessment["grade"] = 1.0,
            assessment["praise"] = _(u"Good job on keeping your {} below 40%.").format(', '.join(missing))
            
        return assessment


    @staticmethod
    def __get_power_capacity(modules):
        power_capacity = None
        for module in modules:
            if module.get("Slot", "").lower() != "powerplant":
                continue

            engineering = module.get("Engineering", {})
            modifiers = engineering.get("Modifiers", [])
            item = module.get("Item", None)
            power_capacity = EDRXzibit.POWER_DATA[item]["powergen"] if item in EDRXzibit.POWER_DATA else None
            for modifier in modifiers:
                if modifier.get("Label", "").lower() != "powercapacity":
                    continue
                power_capacity = modifier["Value"]
        return power_capacity

    @staticmethod
    def __get_power_draw(module):
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        power_draw = None
        item = module["Item"].lower() if "Item" in module else None
        if  item is None or item.startswith(('int_fueltank_', 'int_planetapproachsuite', 'int_passengercabin_', 'int_cargorack_', 'int_corrosionproof', 'int_hullreinforcement_', 'int_fueltank_', 'int_passengercabin_', 'int_metaalloyhullreinforcement_', 'int_modulereinforcement_', 'int_detailedsurfacescanner_')):
            power_draw = 0
        elif item in EDRXzibit.POWER_DATA:
            power_draw = EDRXzibit.POWER_DATA[item]["powerdraw"]
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
    def __get_power_priority(module):
        return module["Priority"] + 1 if "Priority" in module else None

    @staticmethod
    def __generic_name(name):
        match = re.search('([a-zA-Z_]*)_size[0-9]_class[0-9](_[a-zA-Z_].*)?', name)
        if match:
            name = match.group(1)
        return name

    @staticmethod
    def __readable_name(name):
        lut = { 
            "int_hyperdrive": "FSD",
            "int_engine": "Thruster",
            "int_shieldgenerator": "Shield"
        }

        return lut.get(name, name)

    def _has_shield(self):
        for pri in self.per_prio:
            for module in self.per_prio[pri]["modules"]:
                if module.startswith('int_shieldgenerator'):
                    return True
        return False
