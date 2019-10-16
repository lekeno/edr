import json
import re
import os
import edrlog
import edmodule
from edri18n import _
EDRLOG = edrlog.EDRLog()
POWER_DATA = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/modules_power_data.json')).read())


class EDRXzibit(object):
 
    def __init__(self, vehicle):
        EDRLOG.log(u"Xzibit is checking your ship", "DEBUG")
        self.power_capacity = vehicle.power_capacity
        EDRLOG.log(u" Power cap: {}".format(self.power_capacity), "DEBUG")
        self.per_prio = {"1": { "modules": []}, "2": { "modules": []}, "3": { "modules": []}, "4": { "modules": []}, "5": { "modules": []}}
        for slot in vehicle.slots:
            ed_module = vehicle.slots[slot]
            EDRLOG.log(u" {}: {}".format(slot, ed_module), "DEBUG")
            if ed_module.is_valid():
                prio = str(ed_module.priority)
                EDRLOG.log(u"  added to prio {}".format(prio), "DEBUG")
                self.per_prio[prio]["modules"].append(ed_module)

    def assess_power_priorities(self):
        if not self.power_capacity:
            EDRLOG.log(u"A ship without any power?!", "DEBUG")
            return None

        assessment = {}
        assessment["20"] = self._assess_busted_powerplant()
        assessment["50"] = self._assess_recovered_powerplant()
        assessment["40"] = self._assess_malfunctioning_powerplant()
        return assessment

    def _functional_at(self, percent, required=None):
        power_draw = 0
        threshold = self.power_capacity * percent
        within_modules = set()
        within_priorities = []
        EDRLOG.log(u"Looking at what's functional within {}MW".format(threshold), "DEBUG")
        for pri in sorted(self.per_prio.keys()):
            EDRLOG.log(u" P{} is next. Power draw: {}MW so far".format(pri, power_draw), "DEBUG")
            if power_draw > threshold:
                EDRLOG.log(u" {} is over the cap {} => aborting".format(power_draw, threshold), "DEBUG")
                break
            
            tentative_within_modules = set()
            for ed_module in self.per_prio[pri]["modules"]:
                if not ed_module.on and not ed_module.generic_name() in required:
                    EDRLOG.log(u" skipping {}".format(ed_module), "DEBUG")
                    continue
                tentative_within_modules.add(ed_module.generic_name())
                power_draw += ed_module.power_draw
                EDRLOG.log(u" adding {}. Power draw so far: {} vs. {}".format(ed_module, power_draw, threshold), "DEBUG")
                
            if power_draw > threshold:
                EDRLOG.log(u" {} is over the cap {} => not adding anything from {}".format(power_draw, threshold, tentative_within_modules), "DEBUG")
                break
            
            within_priorities.append(u"P{}".format(pri))
            within_modules |= tentative_within_modules

        EDRLOG.log(u" within modules: {}".format(within_modules), "DEBUG")
        EDRLOG.log(u" within priorities: {}".format(within_priorities), "DEBUG")
        return {"modules": within_modules, "priorities": within_priorities}

    def _assess_busted_powerplant(self):
        required = set(["int_hyperdrive"])
        functional = self._functional_at(.2, required)
        assessment = {
            "situation": _(u"Busted PP (20 pct for 5s; {0:.2f}MW)").format(self.power_capacity * .2),
            "annotation": u", ".join(functional["priorities"]),
            "grade": 0.0,
        }

        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
        else:
            assessment["grade"] = 0.2

        if 'int_hyperdrive' not in functional["modules"]:
            assessment["recommendation"] = _(u"Keep your FSD below the 20 pct line.")
        else:
            assessment["grade"] = 1.0
            assessment["praise"] = _(u"Good job on keeping your FSD below the 20 pct line.")

        return assessment


    def _assess_recovered_powerplant(self):
        required = set(['int_hyperdrive', 'int_engine'])
        if self._has_shield():
            required.add('int_shieldgenerator')
        functional = self._functional_at(.5, required)
        assessment = {
            "situation": _(u"Recovered PP (50 pct after 5s; {0:.2f}MW)").format(self.power_capacity * .5),
            "annotation": u", ".join(functional["priorities"]),
            "grade": 0.0,
        }
        
        missing = [EDRXzibit.__readable_name(module) for module in required - functional["modules"]]
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
            assessment["recommendation"] = _(u"Keep your {} below the 50 pct line.").format(', '.join(missing))
            return assessment

        if not required.issubset(functional["modules"]):
            present = [EDRXzibit.__readable_name(module) for module in required.intersection(functional["modules"])]
            if present:
                assessment["grade"] = 1.0/len(required) * len(present)
                assessment["recommendation"] = _(u"Keep your {} below the 50 pct line.").format(', '.join(missing))
                assessment["praise"] = _(u"Good job with your {}.").format(', '.join(present))
            else:
                assessment["grade"] = 0.2
                assessment["recommendation"] = _(u"Keep your {} below the 50 pct line.").format(', '.join(missing))
        else:
            assessment["grade"] = 1.0,
            assessment["praise"] = _(u"Good job on keeping your {} below 50 pct.").format(', '.join(missing))
            
        return assessment
    
    def _assess_malfunctioning_powerplant(self):
        required = set(['int_hyperdrive', 'int_engine'])
        if self._has_shield():
            required.add('int_shieldgenerator')
        functional = self._functional_at(.4, required)
        assessment = {
            "situation": _(u"Malfunctioning PP (40 pct for 5s; {0:.2f}MW)").format(self.power_capacity * .4),
            "annotation": u", ".join(functional["priorities"]),
            "grade": 0.0,
        }
        
        missing = [EDRXzibit.__readable_name(module) for module in required - functional["modules"]]
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
            assessment["recommendation"] = _(u"Keep your {} below the 40 pct line.").format(', '.join(missing))
            return assessment

        if not required.issubset(functional["modules"]):
            present = [EDRXzibit.__readable_name(module) for module in required.intersection(functional["modules"])]
            if present:
                assessment["grade"] = 1.0/len(required) * len(present)
                assessment["recommendation"] = _(u"Keep your {} below the 40 pct line.").format(', '.join(missing))
                assessment["praise"] = _(u"Good job with your {}.").format(', '.join(present))
            else:
                assessment["grade"] = 0.2
                assessment["recommendation"] = _(u"Keep your {} below the 40 pct line.").format(', '.join(missing))
        else:
            assessment["grade"] = 1.0,
            assessment["praise"] = _(u"Good job on keeping your {} below 40 pct.").format(', '.join(missing))
            
        return assessment

    @staticmethod
    def __readable_name(name):
        lut = { 
            "int_hyperdrive": _(u"FSD"),
            "int_engine": _(u"thruster"),
            "int_shieldgenerator": _(u"shield"),
            'int_dockingcomputer_standard': _(u"docking computer"),
            'int_dockingcomputer_advanced': _(u"docking computer"),
            'int_dockingcomputer': _(u"docking computer"),
            'hpt_cargoscanner': _(u"cargo scanner"),
            'int_fuelscoop': _(u"fuel scoop"),
            'hpt_crimescanner': _(u"bounty scanner"),
            'int_supercruiseassist': _(u"supercruise assist"),
            'int_detailedsurfacescanner_tiny': _(u"surface scanner"),
        }

        return lut.get(name, name)

    def _has_shield(self):
        for pri in self.per_prio:
            for module in self.per_prio[pri]["modules"]:
                if module.is_shield():
                    return True
        return False
