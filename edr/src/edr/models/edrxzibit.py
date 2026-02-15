import json
import os
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _


class EDRXzibit:
    """
    Assess ship module configuration and power priorities.
    """
    
    POWER_DATA = None

    @classmethod
    def load_power_data(cls):
        if cls.POWER_DATA is None:
            try:
                edr_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                data_path = os.path.join(edr_root, 'data', 'modules_power_data.json')
                with open(data_path, 'r') as f:
                    cls.POWER_DATA = json.load(f)
            except Exception as e:
                EDR_LOG.error(f"Failed to load power data: {e}")
                cls.POWER_DATA = {}

    def __init__(self, vehicle):
        self.load_power_data()
        EDR_LOG.debug("Xzibit is checking your ship")
        self.power_capacity = vehicle.power_capacity
        EDR_LOG.debug(f" Power cap: {self.power_capacity}")
        self.per_prio = {"1": {"modules": []}, "2": {"modules": []}, "3": {"modules": []}, "4": {"modules": []}, "5": {"modules": []}}
        for slot in vehicle.slots:
            ed_module = vehicle.slots[slot]
            EDR_LOG.debug(f" {slot}: {ed_module}")
            if ed_module.is_valid():
                prio = str(ed_module.priority)
                EDR_LOG.debug(f"  added to prio {prio}")
                if prio in self.per_prio:
                    self.per_prio[prio]["modules"].append(ed_module)

    def assess_power_priorities(self):
        """
        Assess power priorities for different failure states.
        """
        if not self.power_capacity:
            EDR_LOG.debug("A ship without any power?!")
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
        EDR_LOG.debug(f"Looking at what's functional within {threshold}MW")
        
        for pri in sorted(self.per_prio.keys()):
            EDR_LOG.debug(f" P{pri} is next. Power draw: {power_draw}MW so far")
            if power_draw > threshold:
                EDR_LOG.debug(f" {power_draw} is over the cap {threshold} => aborting")
                break
            
            tentative_within_modules = set()
            for ed_module in self.per_prio[pri]["modules"]:
                if not ed_module.on and (required is None or ed_module.generic_name() not in required):
                    EDR_LOG.debug(f" skipping {ed_module}")
                    continue
                tentative_within_modules.add(ed_module.generic_name())
                power_draw += ed_module.power_draw
                EDR_LOG.debug(f" adding {ed_module}. Power draw so far: {power_draw} vs. {threshold}")
                
            if power_draw > threshold:
                EDR_LOG.debug(f" {power_draw} is over the cap {threshold} => not adding anything from {tentative_within_modules}")
                break
            
            within_priorities.append(f"P{pri}")
            within_modules |= tentative_within_modules

        EDR_LOG.debug(f" within modules: {within_modules}")
        EDR_LOG.debug(f" within priorities: {within_priorities}")
        return {"modules": within_modules, "priorities": within_priorities}

    def _assess_busted_powerplant(self):
        required = {"int_hyperdrive"}
        functional = self._functional_at(.2, required)
        assessment = {
            "situation": _("Busted PP (20 pct for 5s; {0:.2f}MW)").format(self.power_capacity * .2),
            "annotation": ", ".join(functional["priorities"]),
            "grade": 0.0,
        }

        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
        else:
            assessment["grade"] = 0.2

        if 'int_hyperdrive' not in functional["modules"]:
            assessment["recommendation"] = _("Keep your FSD below the 20 pct line.")
        else:
            assessment["grade"] = 1.0
            assessment["praise"] = _("Good job on keeping your FSD below the 20 pct line.")

        return assessment

    def _assess_recovered_powerplant(self):
        required = {'int_hyperdrive', 'int_engine'}
        if self._has_shield():
            required.add('int_shieldgenerator')
        functional = self._functional_at(.5, required)
        assessment = {
            "situation": _("Recovered PP (50 pct after 5s; {0:.2f}MW)").format(self.power_capacity * .5),
            "annotation": ", ".join(functional["priorities"]),
            "grade": 0.0,
        }
        
        missing = [self._readable_name(module) for module in required - functional["modules"]]
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
            assessment["recommendation"] = _("Keep your {} below the 50 pct line.").format(', '.join(missing))
            return assessment

        if not required.issubset(functional["modules"]):
            present = [self._readable_name(module) for module in required.intersection(functional["modules"])]
            if present:
                assessment["grade"] = 1.0/len(required) * len(present)
                assessment["recommendation"] = _("Keep your {} below the 50 pct line.").format(', '.join(missing))
                assessment["praise"] = _("Good job with your {}.").format(', '.join(present))
            else:
                assessment["grade"] = 0.2
                assessment["recommendation"] = _("Keep your {} below the 50 pct line.").format(', '.join(missing))
        else:
            assessment["grade"] = 1.0
            assessment["praise"] = _("Good job on keeping your {} below 50 pct.").format(', '.join(missing))
            
        return assessment
    
    def _assess_malfunctioning_powerplant(self):
        required = {'int_hyperdrive', 'int_engine'}
        if self._has_shield():
            required.add('int_shieldgenerator')
        functional = self._functional_at(.4, required)
        assessment = {
            "situation": _("Malfunctioning PP (40 pct for 5s; {0:.2f}MW)").format(self.power_capacity * .4),
            "annotation": ", ".join(functional["priorities"]),
            "grade": 0.0,
        }
        
        missing = [self._readable_name(module) for module in required - functional["modules"]]
        if len(functional["modules"]) == 0:
            assessment["grade"] = 0
            assessment["recommendation"] = _("Keep your {} below the 40 pct line.").format(', '.join(missing))
            return assessment

        if not required.issubset(functional["modules"]):
            present = [self._readable_name(module) for module in required.intersection(functional["modules"])]
            if present:
                assessment["grade"] = 1.0/len(required) * len(present)
                assessment["recommendation"] = _("Keep your {} below the 40 pct line.").format(', '.join(missing))
                assessment["praise"] = _("Good job with your {}.").format(', '.join(present))
            else:
                assessment["grade"] = 0.2
                assessment["recommendation"] = _("Keep your {} below the 40 pct line.").format(', '.join(missing))
        else:
            assessment["grade"] = 1.0
            assessment["praise"] = _("Good job on keeping your {} below 40 pct.").format(', '.join(missing))
            
        return assessment

    @staticmethod
    def _readable_name(name):
        lut = { 
            "int_hyperdrive": _("FSD"),
            "int_engine": _("thruster"),
            "int_shieldgenerator": _("shield"),
            'int_dockingcomputer_standard': _("docking computer"),
            'int_dockingcomputer_advanced': _("docking computer"),
            'int_dockingcomputer': _("docking computer"),
            'hpt_cargoscanner': _("cargo scanner"),
            'int_fuelscoop': _("fuel scoop"),
            'hpt_crimescanner': _("bounty scanner"),
            'int_supercruiseassist': _("supercruise assist"),
            'int_detailedsurfacescanner_tiny': _("surface scanner"),
        }

        return lut.get(name, name)

    def _has_shield(self):
        for pri in self.per_prio:
            for module in self.per_prio[pri]["modules"]:
                if module.is_shield():
                    return True
        return False
