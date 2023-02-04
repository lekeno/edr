from math import log10
import re

import edrlog
from edmodule import EDResistances

EDRLOG = edrlog.EDRLog()

class EDHullReinforcementPackage(object):
    def __init__(self):
        # TODO make this a child of EDModule, reflect powerdraw etc.
        self.armour = 0
        self.resistances = EDResistances()
        self.enabled = True
    
    def update_from(self, module):
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        for m in modifiers:
            if m.get("Label", "") == "DefenceModifierHealthAddition" and "Value" in m:
                self.armour = m["Value"]
            
            if m.get("Label", "") == "ThermicResistance" and "Value" in m:
                self.resistances.thermal = m["Value"] / 100.0

            if m.get("Label", "") == "KineticResistance" and "Value" in m:
                self.resistances.kinetic = m["Value"] / 100.0
            
            if m.get("Label", "") == "ExplosiveResistance" and "Value" in m:
                self.resistances.explosive = m["Value"] / 100.0

class EDGuardianHullReinforcementPackage(object):
    def __init__(self):
        self.armour = 0
        self.resistances = EDResistances(0.02, 0.0, 0.0, 0.05)
        self.enabled = True # TODO take into account actual state, although this might always be true?

class EDMetaAlloyHullReinforcementPackage(object):
    def __init__(self):
        self.armour = 0
        self.resistances = EDResistances(0.0, 0.0, 0.0, 0.03)
        self.enabled = True

class EDHullBulkhead(object):
    def __init__(self):
        self.armour = 0
        self.armour_multiplier = 1.0
        self.hull_resistances = EDResistances()
        
    def update_from(self, module):
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        for m in modifiers:
            # TODO
            if m.get("Label", "") == "DefenceModifierHealthMultiplier" and "Value" in m:
                self.armour_multiplier = m["Value"]/100.0
                
            if m.get("Label", "") == "ThermicResistance" and "Value" in m:
                self.hull_resistances.thermal = m["Value"] / 100.0
                
            if m.get("Label", "") == "KineticResistance" and "Value" in m:
                self.hull_resistances.kinetic = m["Value"] / 100.0
                
            if m.get("Label", "") == "ExplosiveResistance" and "Value" in m:
                self.hull_resistances.explosive = m["Value"] / 100.0
                
    def strength(self, base_strength):
        if base_strength == 0:
            return 0

        hull_strength = base_strength * (1.0 + self.armour_multiplier)
        return hull_strength


class EDHrp5D(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp5D, self).__init__()
        self.armour = 390
        self.resistances = EDResistances(0.025, 0.025, 0.025)

class EDHrp5E(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp5E, self).__init__()
        self.armour = 360
        self.resistances = EDResistances(0.025, 0.025, 0.025)

class EDHrp4D(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp4D, self).__init__()
        self.armour = 330
        self.resistances = EDResistances(0.02, 0.02, 0.02)

class EDHrp4E(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp4E, self).__init__()
        self.armour = 300
        self.resistances = EDResistances(0.02, 0.02, 0.02)
    
class EDHrp3D(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp3D, self).__init__()
        self.armour = 260
        self.resistances = EDResistances(0.015, 0.015, 0.015)

class EDHrp3E(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp3E, self).__init__()
        self.armour = 230
        self.resistances = EDResistances(0.015, 0.015, 0.015)

class EDHrp2D(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp2D, self).__init__()
        self.armour = 190
        self.resistances = EDResistances(0.01, 0.01, 0.01)

class EDHrp2E(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp2E, self).__init__()
        self.armour = 150
        self.resistances = EDResistances(0.01, 0.01, 0.01)

class EDHrp1D(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp1D, self).__init__()
        self.armour = 110
        self.resistances = EDResistances(0.005, 0.005, 0.005)

class EDHrp1E(EDHullReinforcementPackage):
    def __init__(self):
        super(EDHrp1E, self).__init__()
        self.armour = 80
        self.resistances = EDResistances(0.005, 0.005, 0.005)

class EDGhrp5D(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp5D, self).__init__()
        self.armour = 488

class EDGhrp5E(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp5E, self).__init__()
        self.armour = 450

class EDGhrp4D(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp4D, self).__init__()
        self.armour = 413

class EDGhrp4E(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp4E, self).__init__()
        self.armour = 375

class EDGhrp3D(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp3D, self).__init__()
        self.armour = 325

class EDGhrp3E(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp3E, self).__init__()
        self.armour = 288

class EDGhrp2D(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp2D, self).__init__()
        self.armour = 238

class EDGhrp2E(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp2E, self).__init__()
        self.armour = 188

class EDGhrp1D(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp1D, self).__init__()
        self.armour = 138

class EDGhrp1E(EDGuardianHullReinforcementPackage):
    def __init__(self):
        super(EDGhrp1E, self).__init__()
        self.armour = 100


class EDMhrp5D(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp5D, self).__init__()
        self.armour = 351

class EDMhrp5E(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp5E, self).__init__()
        self.armour = 324

class EDMhrp4D(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp4D, self).__init__()
        self.armour = 297

class EDMhrp4E(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp4E, self).__init__()
        self.armour = 270

class EDMhrp3D(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp3D, self).__init__()
        self.armour = 234

class EDMhrp3E(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp3E, self).__init__()
        self.armour = 207

class EDMhrp2D(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp2D, self).__init__()
        self.armour = 171

class EDMhrp2E(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp2E, self).__init__()
        self.armour = 135

class EDMhrp1D(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp1D, self).__init__()
        self.armour = 99

class EDMhrp1E(EDMetaAlloyHullReinforcementPackage):
    def __init__(self):
        super(EDMhrp1E, self).__init__()
        self.armour = 72

class EDLightweightAlloyHull(EDHullBulkhead):
    def __init__(self):
        super(EDLightweightAlloyHull, self).__init__()
        self.armour_multiplier = 0.8
        self.resistances = EDResistances(0, -0.2, -0.4)

class EDReinforcedAlloyHull(EDHullBulkhead):
    def __init__(self):
        super(EDReinforcedAlloyHull, self).__init__()
        self.armour_multiplier = 1.52
        self.resistances = EDResistances(0, -0.2, -0.4)

class EDMilitaryGradeCompositeHull(EDHullBulkhead):
    def __init__(self):
        super(EDMilitaryGradeCompositeHull, self).__init__()
        self.armour_multiplier = 2.5
        self.resistances = EDResistances(0, -0.2, -0.4)

class EDMirroredSurfaceCompositeHull(EDHullBulkhead):
    def __init__(self):
        super(EDMirroredSurfaceCompositeHull, self).__init__()
        self.armour_multiplier = 2.5
        self.resistances = EDResistances(0.5, -0.75, -0.5)
    
class EDReactiveSurfaceCompositeHull(EDHullBulkhead):
    def __init__(self):
        super(EDReactiveSurfaceCompositeHull, self).__init__()
        self.armour_multiplier = 2.5
        # TODO
        self.resistances = EDResistances(-0.4, 0.2, 0.25)

class EDHullFactory(object):
    __module_classes = {
        "grade1": EDLightweightAlloyHull,
        "grade2": EDReinforcedAlloyHull,
        "grade3": EDMilitaryGradeCompositeHull,
        "mirrored": EDMirroredSurfaceCompositeHull,
        "reactive": EDReactiveSurfaceCompositeHull,
        "hullreinforcement_size5_class1": EDHrp5E,
        "hullreinforcement_size5_class2": EDHrp5D,
        "hullreinforcement_size4_class1": EDHrp4E,
        "hullreinforcement_size4_class2": EDHrp4D,
        "hullreinforcement_size3_class1": EDHrp3E,
        "hullreinforcement_size3_class2": EDHrp3D,
        "hullreinforcement_size2_class1": EDHrp2E,
        "hullreinforcement_size2_class2": EDHrp2D,
        "hullreinforcement_size1_class1": EDHrp1E,
        "hullreinforcement_size1_class2": EDHrp1D,
    }

    @staticmethod
    def normalize_module_name(name):
        normalized = name.lower()
        
        # suffix _name or _name; is not used in loadout or afmurepair events 
        if normalized.endswith(u"_name"):
            useless_suffix_length = len(u"_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith(u"_name;"):
            useless_suffix_length = len(u"_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith(u"$"):
            normalized = normalized[1:]
        
        if normalized.startswith(u"int_"):
            normalized = normalized[4:]

        m = re.match(r'^.*_armour_(.*)$', normalized)
        if m:
            normalized = m.group(1)
        
        return normalized

    @staticmethod
    def from_internal_name(internal_name):
        cname = EDHullFactory.normalize_module_name(internal_name)
        if cname in EDHullFactory.__module_classes:
            hull = EDHullFactory.__module_classes[cname]()
            return hull
        return None

    @staticmethod
    def default_armour():
        return EDLightweightAlloyHull()
        
    @staticmethod
    def from_module(module):
        internal_name = module.get("Item", "N/A")
        cname = EDHullFactory.normalize_module_name(internal_name)
        if cname in EDHullFactory.__module_classes:
            hull = EDHullFactory.__module_classes[cname]()
            hull.update_from(module)
            return hull
        return None