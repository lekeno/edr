from math import log10
import re

from edmodule import EDResistances # EDR_INTERNAL

class EDShieldBooster:
    """
    Shield booster module.
    """
    def __init__(self):
        # TODO make this a child of EDModule, reflect powerdraw etc.
        self.strength_bonus = 0
        self.resistances = EDResistances()
        self.enabled = True # TODO take into account actual state
    
    def update_from(self, module):
        """
        Update from module data.

        Args:
            module (dict): Module data.
        """
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        for m in modifiers:
            if m.get("Label", "") == "DefenceModifierShieldMultiplier" and "Value" in m:
                self.strength_bonus = m["Value"] / 100.0
                
            if m.get("Label", "") == "ThermicResistance" and "Value" in m:
                self.resistances.thermal = m["Value"] / 100.0

            if m.get("Label", "") == "KineticResistance" and "Value" in m:
                self.resistances.kinetic = m["Value"] / 100.0
            
            if m.get("Label", "") == "ExplosiveResistance" and "Value" in m:
                self.resistances.explosive = m["Value"] / 100.0

class EDShieldCellBank:
    """
    Shield cell bank module.
    """
    def __init__(self):
        # TODO make this a child of EDModule, reflect powerdraw etc.
        self.charges = 0
        self.duration = 0
        self.charge_rate = 0
        self.boot_time = 0
        self.spin_up = 5.0
        self.enabled = True # TODO take into account actual state
    
    def update_from(self, module):
        """
        Update from module data.

        Args:
            module (dict): Module data.
        """
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        for m in modifiers:
            if m.get("Label", "") == "BootTime" and "Value" in m:
                self.boot_time = m["Value"]
            
            if m.get("Label", "") == "ShieldBankSpinUp" and "Value" in m:
                self.spin_up = m["Value"]

            if m.get("Label", "") == "ShieldBankDuration" and "Value" in m:
                self.duration = m["Value"]
            
            if m.get("Label", "") == "ShieldBankReinforcement" and "Value" in m:
                self.charge_rate = m["Value"]

    def strength(self):
        """
        Returns:
            float: Strength per charge.
        """
        return self.duration * self.charge_rate

    def total_strength(self):
        """
        Returns:
            float: Total strength.
        """
        return self.charges * self.strength()

class EDGuardianShieldReinforcementPackage:
    """
    Guardian Shield Reinforcement Package.
    """
    def __init__(self):
        self.strength = 100
        self.enabled = True # TODO take into account actual state, although this might always be true?
    
    def update_from(self, module):
        """
        Update from module data.
        """
        # should not happen since these can't be modified
        pass

class EDShieldGenerator:
    """
    Shield generator module.
    """
    RATING_BOOST_LUT = {"A": 1.3, "B": 1.225, "C": 1.15, "D": 1.075, "E": 1}
    RATING_MULTIPLIERS = {"A": [.7, 1.2, 1.7], "B": [.6, 1.1, 1.6], "C": [.5, 1.0, 1.5], "D": [.4, .9, 1.4], "E": [.3, .8, 1.3], "fast": [.4, .9, 1.4], "strong": [1.0, 1.5, 2.0]}
    
    def __init__(self):
        self.rating = "E"
        self.max_hull_mass = 0
        self.opt_hull_mass = 0
        self.min_hull_mass = 0
        self.min_multiplier = .3
        self.opt_multiplier = .8
        self.max_multiplier = 1.3
        self.shield_resistances = EDResistances(-0.2, 0.4, 0.5)
        self.enabled = True # TODO take into account actual state (powered, etc)

    def reset(self):
        """
        Reset internal state.
        """
        pass

    def configure(self, internal_name):
        """
        Configure based on internal name.
        
        Args:
            internal_name (str): Internal module name.
        """
        sg_regexp = r"^int_shieldgenerator_size[1-8]_class([1-5]).*$"
        m = re.match(sg_regexp, internal_name)
        if not m:
            return
        class_nb = int(m.group(1))
        if class_nb < 1 or class_nb > 5:
            return
        ratings = ["E", "D", "C", "B", "A"]
        self.rating = ratings[class_nb-1]
        multipliers = EDShieldGenerator.RATING_MULTIPLIERS.get(self.rating, [.3, .8, 1.3])
        if internal_name.endswith("strong"):
            multipliers = EDShieldGenerator.RATING_MULTIPLIERS["strong"]
        elif internal_name.endswith("fast"):
            multipliers = EDShieldGenerator.RATING_MULTIPLIERS["fast"]
        
        self.min_multiplier = multipliers[0]
        self.opt_multiplier = multipliers[1]
        self.max_multiplier = multipliers[2]

    def update_from(self, module):
        """
        Update from module data.
        
        Args:
            module (dict): Module data.
        """
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        for m in modifiers:
            if m.get("Label", "") == "ShieldGenStrength" and "Value" in m:
                new_opt_multiplier = m["Value"]/100.0
                ratio = new_opt_multiplier / self.opt_multiplier
                self.opt_multiplier = new_opt_multiplier
                self.min_multiplier  = self.min_multiplier * ratio
                self.max_multiplier  = self.max_multiplier * ratio
            
            if m.get("Label", "") == "ThermicResistance" and "Value" in m:
                self.shield_resistances.thermal = m["Value"] / 100.0
                
            if m.get("Label", "") == "KineticResistance" and "Value" in m:
                self.shield_resistances.kinetic = m["Value"] / 100.0
                
            if m.get("Label", "") == "ExplosiveResistance" and "Value" in m:
                self.shield_resistances.explosive = m["Value"] / 100.0
                
            if m.get("Label", "") == "ShieldGenOptimalMass" and "Value" in m:
                new_opt_hull_mass = m["Value"]
                ratio = new_opt_hull_mass / self.opt_hull_mass
                self.opt_hull_mass = new_opt_hull_mass
                self.min_hull_mass  = self.min_hull_mass * ratio
                
    def strength(self, hull_mass, base_strength):
        """
        Calculate shield strength.
        
        Args:
            hull_mass (float): Hull mass.
            base_strength (float): Base field strength.
            
        Returns:
            float: Calculated strength.
        """
        if base_strength == 0:
            return 0

        if self.max_hull_mass == 0 or self.min_hull_mass == 0 or self.opt_hull_mass == 0:
            return 0
        
        normalized_hull_mass = min(1.0, (self.max_hull_mass - hull_mass)/(self.max_hull_mass - self.min_hull_mass))
        exponent = log10((self.opt_multiplier - self.min_multiplier)/(self.max_multiplier - self.min_multiplier)) 
        exponent /= log10(min(1.0, (self.max_hull_mass - self.opt_hull_mass)/(self.max_hull_mass - self.min_hull_mass)))
        multiplier = self.min_multiplier + pow(normalized_hull_mass, exponent) * (self.max_multiplier - self.min_multiplier)
        shield_strength = base_strength * multiplier
        return shield_strength


class EDPowerDistributor:
    """
    Power distributor module.
    """
    def __init__(self):
        self.sys = 2
        self.eng = 2
        self.wep = 2

    def update(self, pips):
        """
        Update pip settings.
        
        Args:
            pips (list): List of pips [Sys, Eng, Weap].
            
        Returns:
            bool: True if changed.
        """
        if pips:
            sys = pips[0] / 2.0
            eng = pips[1] / 2.0
            wep = pips[2] / 2.0
            changed = self.sys != sys or self.eng != eng or self.wep != wep
            self.sys = sys
            self.eng = eng
            self.wep = wep
            return changed
        return False

    def reset(self):
        """
        Reset pips to default.
        """
        # TODO does Elite keep the pips as is or does it reset them, after a death/hangar in&out/... ?
        self.sys = 2
        self.eng = 2
        self.wep = 2

    def sys_resistance(self):
        """
        Calculate system resistance factor.
        
        Returns:
            float: Resistance factor.
        """
        return pow(self.sys, 0.85) * 0.6 / pow(4, 0.85)

class EDShieldBoosterE(EDShieldBooster):
    def __init__(self):
        super().__init__()
        self.strength_bonus = 0.04

class EDShieldBoosterD(EDShieldBooster):
    def __init__(self):
        super().__init__()
        self.strength_bonus = 0.08
        

class EDShieldBoosterC(EDShieldBooster):
    def __init__(self):
        super().__init__()
        self.strength_bonus = 0.12
        

class EDShieldBoosterB(EDShieldBooster):
    def __init__(self):
        super().__init__()
        self.strength_bonus = 0.16
        

class EDShieldBoosterA(EDShieldBooster):
    def __init__(self):
        super().__init__()
        self.strength_bonus = 0.20
        

class EDGsrp1E(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 44

class EDGsrp1D(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 61

class EDGsrp2E(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 83

class EDGsrp2D(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 105

class EDGsrp3E(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 127

class EDGsrp3D(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 143

class EDGsrp4E(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 165

class EDGsrp4D(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 182

class EDGsrp5E(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 198

class EDGsrp5D(EDGuardianShieldReinforcementPackage):
    def __init__(self):
        super().__init__()
        self.strength = 215
        
class EDShieldGenSize8(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 900
        self.opt_hull_mass = 1800
        self.max_hull_mass = 4500

class EDShieldGenSize7(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 530
        self.opt_hull_mass = 1060
        self.max_hull_mass = 2650

class EDShieldGenSize6(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 270	
        self.opt_hull_mass = 540
        self.max_hull_mass = 1350

class EDShieldGenSize5(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 203	
        self.opt_hull_mass = 405
        self.max_hull_mass = 1013

class EDShieldGenSize4(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 143
        self.opt_hull_mass = 285	
        self.max_hull_mass = 713

class EDShieldGenSize3(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 83
        self.opt_hull_mass = 165
        self.max_hull_mass = 413

class EDShieldGenSize2(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 28
        self.opt_hull_mass = 55
        self.max_hull_mass = 138

class EDShieldGenSize1(EDShieldGenerator):
    def __init__(self):
        super().__init__()
        self.min_hull_mass = 13
        self.opt_hull_mass = 25
        self.max_hull_mass = 63

class EDScbSize6A(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 8
        self.charge_rate = 46

class EDScbSize6B(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 6
        self.duration = 8
        self.charge_rate = 39

class EDScbSize6C(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 8
        self.charge_rate = 33

class EDScbSize6D(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 8
        self.charge_rate = 26

class EDScbSize6E(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 6
        self.duration = 8
        self.charge_rate = 20

class EDScbSize5A(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 5
        self.charge_rate = 48

class EDScbSize5B(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 5
        self.charge_rate = 41

class EDScbSize5C(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 5
        self.charge_rate = 35

class EDScbSize5D(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 3
        self.duration = 5
        self.charge_rate = 28

class EDScbSize5E(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 5
        self.charge_rate = 21

class EDScbSize4A(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 3
        self.charge_rate = 46

class EDScbSize4B(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 3
        self.charge_rate = 39

class EDScbSize4C(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 3
        self.charge_rate = 33

class EDScbSize4D(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 3
        self.duration = 3
        self.charge_rate = 26

class EDScbSize4E(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 3
        self.charge_rate = 12

class EDScbSize3A(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 2
        self.charge_rate = 41

class EDScbSize3B(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 2
        self.charge_rate = 35

class EDScbSize3C(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 2
        self.charge_rate = 29

class EDScbSize3D(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 3
        self.duration = 2
        self.charge_rate = 23

class EDScbSize3E(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 2
        self.charge_rate = 17

class EDScbSize2A(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 2
        self.charge_rate = 32

class EDScbSize2B(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 2
        self.charge_rate = 28

class EDScbSize2C(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 2
        self.charge_rate = 23

class EDScbSize2D(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 3
        self.duration = 2
        self.charge_rate = 18

class EDScbSize2E(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 5
        self.duration = 2
        self.charge_rate = 14

class EDScbSize1A(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 3
        self.duration = 1
        self.charge_rate = 28

class EDScbSize1B(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 1
        self.charge_rate = 24

class EDScbSize1C(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 3
        self.duration = 1
        self.charge_rate = 20

class EDScbSize1D(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 1
        self.duration = 1
        self.charge_rate = 12.5

class EDScbSize1E(EDShieldCellBank):
    def __init__(self):
        super().__init__()
        self.charges = 4
        self.duration = 1
        self.charge_rate = 12

class EDShieldingFactory:
    __module_classes = {
        "shieldbooster_size0_class1": EDShieldBoosterE,
        "shieldbooster_size0_class2": EDShieldBoosterD,
        "shieldbooster_size0_class3": EDShieldBoosterC,
        "shieldbooster_size0_class4": EDShieldBoosterB,
        "shieldbooster_size0_class5": EDShieldBoosterA,
        "guardianshieldreinforcement_size1_class1": EDGsrp1E,
        "guardianshieldreinforcement_size1_class2": EDGsrp1D,
        "guardianshieldreinforcement_size2_class1": EDGsrp2E,
        "guardianshieldreinforcement_size2_class2": EDGsrp2D,
        "guardianshieldreinforcement_size3_class1": EDGsrp3E,
        "guardianshieldreinforcement_size3_class2": EDGsrp3D,
        "guardianshieldreinforcement_size4_class1": EDGsrp4E,
        "guardianshieldreinforcement_size4_class2": EDGsrp4D,
        "guardianshieldreinforcement_size5_class1": EDGsrp5E,
        "guardianshieldreinforcement_size5_class2": EDGsrp5D,
        "shieldgenerator_size1_class5_strong": EDShieldGenSize1,
        "shieldgenerator_size2_class5_strong": EDShieldGenSize2,
        "shieldgenerator_size3_class5_strong": EDShieldGenSize3,
        "shieldgenerator_size4_class5_strong": EDShieldGenSize4,
        "shieldgenerator_size5_class5_strong": EDShieldGenSize5,
        "shieldgenerator_size6_class5_strong": EDShieldGenSize6,
        "shieldgenerator_size7_class5_strong": EDShieldGenSize7,
        "shieldgenerator_size8_class5_strong": EDShieldGenSize8,
        "shieldgenerator_size1_class5": EDShieldGenSize1, 
        "shieldgenerator_size2_class1": EDShieldGenSize2,
        "shieldgenerator_size2_class2": EDShieldGenSize2,
        "shieldgenerator_size2_class3": EDShieldGenSize2,
        "shieldgenerator_size2_class4": EDShieldGenSize2,
        "shieldgenerator_size2_class5": EDShieldGenSize2,
        "shieldgenerator_size3_class1": EDShieldGenSize3,
        "shieldgenerator_size3_class2": EDShieldGenSize3,
        "shieldgenerator_size3_class3": EDShieldGenSize3,
        "shieldgenerator_size3_class4": EDShieldGenSize3,
        "shieldgenerator_size3_class5": EDShieldGenSize3,
        "shieldgenerator_size4_class1": EDShieldGenSize4,
        "shieldgenerator_size4_class2": EDShieldGenSize4,
        "shieldgenerator_size4_class3": EDShieldGenSize4,
        "shieldgenerator_size4_class4": EDShieldGenSize4,
        "shieldgenerator_size4_class5": EDShieldGenSize4,
        "shieldgenerator_size5_class1": EDShieldGenSize5,
        "shieldgenerator_size5_class2": EDShieldGenSize5,
        "shieldgenerator_size5_class3": EDShieldGenSize5,
        "shieldgenerator_size5_class4": EDShieldGenSize5,
        "shieldgenerator_size5_class5": EDShieldGenSize5,
        "shieldgenerator_size6_class1": EDShieldGenSize6,
        "shieldgenerator_size6_class2": EDShieldGenSize6,
        "shieldgenerator_size6_class3": EDShieldGenSize6,
        "shieldgenerator_size6_class4": EDShieldGenSize6,
        "shieldgenerator_size6_class5": EDShieldGenSize6,
        "shieldgenerator_size7_class1": EDShieldGenSize7,
        "shieldgenerator_size7_class2": EDShieldGenSize7,
        "shieldgenerator_size7_class3": EDShieldGenSize7,
        "shieldgenerator_size7_class4": EDShieldGenSize7,
        "shieldgenerator_size7_class5": EDShieldGenSize7,
        "shieldgenerator_size8_class1": EDShieldGenSize8,
        "shieldgenerator_size8_class2": EDShieldGenSize8,
        "shieldgenerator_size8_class3": EDShieldGenSize8,
        "shieldgenerator_size8_class4": EDShieldGenSize8,
        "shieldgenerator_size8_class5": EDShieldGenSize8,
        "shieldgenerator_size1_class3_fast": EDShieldGenSize1,
        "shieldgenerator_size2_class3_fast": EDShieldGenSize2,
        "shieldgenerator_size3_class3_fast": EDShieldGenSize3,
        "shieldgenerator_size4_class3_fast": EDShieldGenSize4,
        "shieldgenerator_size5_class3_fast": EDShieldGenSize5,
        "shieldgenerator_size6_class3_fast": EDShieldGenSize6,
        "shieldgenerator_size7_class3_fast": EDShieldGenSize7,
        "shieldgenerator_size8_class3_fast": EDShieldGenSize8,
        "shieldcellbank_size6_class5": EDScbSize6A,
        "shieldcellbank_size6_class4": EDScbSize6B,
        "shieldcellbank_size6_class3": EDScbSize6C,
        "shieldcellbank_size6_class2": EDScbSize6D,
        "shieldcellbank_size6_class1": EDScbSize6E,
        "shieldcellbank_size5_class5": EDScbSize5A,
        "shieldcellbank_size5_class4": EDScbSize5B,
        "shieldcellbank_size5_class3": EDScbSize5C,
        "shieldcellbank_size5_class2": EDScbSize5D,
        "shieldcellbank_size5_class1": EDScbSize5E,
        "shieldcellbank_size4_class5": EDScbSize4A,
        "shieldcellbank_size4_class4": EDScbSize4B,
        "shieldcellbank_size4_class3": EDScbSize4C,
        "shieldcellbank_size4_class2": EDScbSize4D,
        "shieldcellbank_size4_class1": EDScbSize4E,
        "shieldcellbank_size3_class5": EDScbSize3A,
        "shieldcellbank_size3_class4": EDScbSize3B,
        "shieldcellbank_size3_class3": EDScbSize3C,
        "shieldcellbank_size3_class2": EDScbSize3D,
        "shieldcellbank_size3_class1": EDScbSize3E,
        "shieldcellbank_size2_class5": EDScbSize2A,
        "shieldcellbank_size2_class4": EDScbSize2B,
        "shieldcellbank_size2_class3": EDScbSize2C,
        "shieldcellbank_size2_class2": EDScbSize2D,
        "shieldcellbank_size2_class1": EDScbSize2E,
        "shieldcellbank_size1_class5": EDScbSize1A,
        "shieldcellbank_size1_class4": EDScbSize1B,
        "shieldcellbank_size1_class3": EDScbSize1C,
        "shieldcellbank_size1_class2": EDScbSize1D,
        "shieldcellbank_size1_class1": EDScbSize1E
    }

    @staticmethod
    def normalize_module_name(name):
        """
        Normalize module name.
        """
        normalized = name.lower()
        
        # suffix _name or _name; is not used in loadout or afmurepair events 
        if normalized.endswith("_name"):
            useless_suffix_length = len("_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith("_name;"):
            useless_suffix_length = len("_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith("$"):
            normalized = normalized[1:]

        # just get rid of prefixes because sometimes int_ becomes ext_ depending on the event
        if normalized.startswith(("int_", "ext_", "hpt_")):
            normalized = normalized[4:]
        return normalized

    @staticmethod
    def from_internal_name(internal_name):
        """
        Create module from internal name.

        Args:
            internal_name (str): Internal module name.

        Returns:
            object: Shielding module instance or None.
        """
        cname = EDShieldingFactory.normalize_module_name(internal_name)
        if cname in EDShieldingFactory.__module_classes:
            shielding = EDShieldingFactory.__module_classes[cname]()
            if internal_name.startswith("int_shieldgenerator"):
                shielding.configure(internal_name)
            return shielding
        return None

    @staticmethod
    def from_module(module):
        """
        Create module from module data.

        Args:
            module (dict): Module data.

        Returns:
            object: Shielding module instance or None.
        """
        internal_name = module.get("Item", "N/A")
        cname = EDShieldingFactory.normalize_module_name(internal_name)
        if cname in EDShieldingFactory.__module_classes:
            shielding = EDShieldingFactory.__module_classes[cname]()
            if internal_name.startswith("int_shieldgenerator"):
                shielding.configure(internal_name)
            shielding.update_from(module)
            return shielding
        return None