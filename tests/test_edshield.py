
import unittest
from edr.models.edshield import EDShieldingFactory, EDShieldGenerator, EDShieldBooster, EDPowerDistributor, EDShieldCellBank

class TestEDShieldingFactory(unittest.TestCase):
    def test_normalize_module_name(self):
        self.assertEqual(EDShieldingFactory.normalize_module_name("int_shieldgenerator_size3_class3"), "shieldgenerator_size3_class3")
        self.assertEqual(EDShieldingFactory.normalize_module_name("$int_shieldgenerator_size3_class3_name;"), "shieldgenerator_size3_class3")

    def test_from_internal_name_generator(self):
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class3")
        self.assertIsInstance(sg, EDShieldGenerator)
        self.assertEqual(sg.rating, "C")

    def test_from_internal_name_booster(self):
        sb = EDShieldingFactory.from_internal_name("hpt_shieldbooster_size0_class5")
        self.assertIsInstance(sb, EDShieldBooster)
        self.assertAlmostEqual(sb.strength_bonus, 0.20)

    def test_from_module_generator(self):
        module = {
            "Item": "int_shieldgenerator_size3_class3",
            "Engineering": {
                "Modifiers": [
                    {"Label": "ShieldGenStrength", "Value": 110.0} # +10% opt multiplier
                ]
            }
        }
        sg = EDShieldingFactory.from_module(module)
        self.assertIsInstance(sg, EDShieldGenerator)
        # Base C rated opt multiplier is 1.0. With 1.1 multiplier in engineering...
        # Wait, the code says new_opt_multiplier = Value / 100.0. So 110/100 = 1.1.
        self.assertAlmostEqual(sg.opt_multiplier, 1.1)

class TestEDShieldGenerator(unittest.TestCase):
    def test_strength_calculation_standard(self):
        # Size 3 Class C
        # Min Mass: 83, Opt Mass: 165, Max Mass: 413
        # Min Mult: 0.5, Opt Mult: 1.0, Max Mult: 1.5
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class3")
        
        # Test at optimal mass
        hull_mass = 165
        base_strength = 100
        strength = sg.strength(hull_mass, base_strength)
        self.assertAlmostEqual(strength, 100 * 1.0)

    def test_strength_calculation_max_mass(self):
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class3")
        hull_mass = 413
        base_strength = 100
        strength = sg.strength(hull_mass, base_strength)
        self.assertAlmostEqual(strength, 100 * 0.5)

    def test_strength_calculation_min_mass(self):
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class3")
        hull_mass = 83
        base_strength = 100
        strength = sg.strength(hull_mass, base_strength)
        self.assertAlmostEqual(strength, 100 * 1.5)

class TestEDShieldBooster(unittest.TestCase):
    def test_update_from_engineering(self):
        sb = EDShieldBooster()
        module = {
            "Item": "hpt_shieldbooster_size0_class5",
            "Engineering": {
                "Modifiers": [
                    {"Label": "DefenceModifierShieldMultiplier", "Value": 25.0},
                    {"Label": "ThermicResistance", "Value": 15.0}
                ]
            }
        }
        sb.update_from(module)
        self.assertAlmostEqual(sb.strength_bonus, 0.25)
        self.assertAlmostEqual(sb.resistances.thermal, 0.15)

class TestEDPowerDistributor(unittest.TestCase):
    def test_update_pips(self):
        pd = EDPowerDistributor()
        # Initial: 2, 2, 2
        self.assertEqual(pd.sys, 2)
        
        changed = pd.update([4, 0, 8]) # Pips are usually half-points in game but passed as integers to update? 
        # The update method divides by 2.0. So [4, 2, 2] -> 2.0, 1.0, 1.0? 
        # Standard pips are 4, 4, 4 max? No, 8 total. 
        # Let's assume input is standard ranks (0-8 per capacitor) or something.
        # update([4, 0, 8]) -> sys=2.0, eng=0.0, wep=4.0
        
        self.assertTrue(changed)
        self.assertEqual(pd.sys, 2.0)
        self.assertEqual(pd.eng, 0.0)
        self.assertEqual(pd.wep, 4.0)

    def test_sys_resistance(self):
        pd = EDPowerDistributor()
        pd.sys = 4.0 # 4 pips
        # pow(4, 0.85) * 0.6 / pow(4, 0.85) = 0.6
        self.assertAlmostEqual(pd.sys_resistance(), 0.6)
        
        pd.sys = 0.0
        self.assertEqual(pd.sys_resistance(), 0.0)

class TestEDShieldCellBank(unittest.TestCase):
    def test_strength(self):
        # EDScbSize6A: duration=8, charge_rate=46, charges=5
        scb = EDShieldingFactory.from_internal_name("shieldcellbank_size6_class5")
        self.assertIsInstance(scb, EDShieldCellBank)
        self.assertEqual(scb.strength(), 8 * 46)
        self.assertEqual(scb.total_strength(), 5 * 8 * 46)

if __name__ == '__main__':
    unittest.main()
