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
        self.power_capacity = vehicle.power_capacity
        
        self.per_prio = {"1": { "powerdraw": 0, "modules": []}, "2": { "powerdraw": 0, "modules": []}, "3": { "powerdraw": 0, "modules": []}, "4": { "powerdraw": 0, "modules": []}, "5": { "powerdraw": 0, "modules": []}}
        for slot in vehicle.slots:
            ed_module = vehicle.slots[slot]
            if ed_module.is_valid():
                prio = str(ed_module.priority)
                self.per_prio[prio]["powerdraw"] += ed_module.power_draw if ed_module.on else 0
                self.per_prio[prio]["modules"].append(ed_module)

    def assess_power_priorities(self):
        if not self.power_capacity:
            print "No power"
            return None

        yo_dawg = self._yo_dawg_meme()
        if yo_dawg:
            name = EDRXzibit.__readable_name(yo_dawg)
            return _(u"Yo dawg, I heard you like {} so I put more {} in your ship.").format(name, name)

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
        for pri in sorted(self.per_prio.keys()):
            power_draw += self.per_prio[pri]["powerdraw"]
            if power_draw > threshold:
                break
            
            tentative_within_modules = set()
            for ed_module in self.per_prio[pri]["modules"]:
                if not ed_module.on and not ed_module.generic_name() in required:
                    continue
                tentative_within_modules.add(ed_module.generic_name())
                if not ed_module.on:
                    power_draw += ed_module.power_draw
                
            if power_draw > threshold:
                break
            
            within_priorities.append(u"P{}".format(pri))
            within_modules |= tentative_within_modules

        return {"modules": within_modules, "priorities": within_priorities}

    def _assess_busted_powerplant(self):
        required = set(["int_hyperdrive"])
        functional = self._functional_at(.2, required)
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
        required = set(["int_hyperdrive"])
        functional = self._functional_at(.5, required)
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
        required = set(['int_hyperdrive', 'int_engine'])
        if self._has_shield():
            required.add('int_shieldgenerator')
        functional = self._functional_at(.4, required)
        assessment = {
            "situation": _(u"Malfunctioning PP (40% for 5s; {0:.2f}MW)").format(self.power_capacity * .4),
            "annotation": u", ".join(functional["priorities"]),
        }
        
        missing = [EDRXzibit.__readable_name(module) for module in required - functional["modules"]]
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
            assessment["recommendation"] = _(u"Keep your {} below the 40% line.").format(', '.join(missing))
            return assessment

        if not required.issubset(functional["modules"]):
            present = [EDRXzibit.__readable_name(module) for module in required.intersection(functional["modules"])]
            if present:
                assessment["grade"] = 1.0/len(required) * len(present)
                assessment["recommendation"] = _(u"Keep your {} below the 40% line.").format(', '.join(missing))
                assessment["praise"] = _(u"Good job with your {}.").format(', '.join(present))
            else:
                assessment["grade"] = 0.2
                assessment["recommendation"] = _(u"Keep your {} below the 40% line.").format(', '.join(missing))
        else:
            assessment["grade"] = 1.0,
            assessment["praise"] = _(u"Good job on keeping your {} below 40%.").format(', '.join(missing))
            
        return assessment

    def _yo_dawg_meme(self):
        pointless_dupes = {'int_dockingcomputer_standard': 0, 'int_dockingcomputer_advanced':0, 'hpt_cargoscanner':0, 'int_fuelscoop':0, 'hpt_crimescanner':0, 'int_supercruiseassist':0, 'int_detailedsurfacescanner_tiny':0}
        for pri in sorted(self.per_prio.keys()):
            for ed_module in self.per_prio[pri]["modules"]:
                gname = ed_module.generic_name()
                if gname not in pointless_dupes:
                    continue
                pointless_dupes[gname] +=1
                if pointless_dupes[gname] >= 2:
                    return gname
        
        if (pointless_dupes['int_dockingcomputer_standard'] + pointless_dupes['int_dockingcomputer_advanced']) >= 2:
            return 'int_dockingcomputer'

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
