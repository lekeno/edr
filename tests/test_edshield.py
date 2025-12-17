import unittest
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edr.edshield import EDShieldingFactory, EDShieldGenerator, EDShieldBooster, EDPowerDistributor, EDShieldCellBank

class TestEDShield(unittest.TestCase):
    def test_factory_generator(self):
        # Test basic generator creation
        # int_shieldgenerator_size3_class3 -> 3C -> Bi-Weave usually? 
        # Standard: class1=E, class2=D, class3=C, class4=B, class5=A
        # Bi-weave is usually C-rated but has "fast" suffix?
        
        # Test 3A Shield Generator
        # int_shieldgenerator_size3_class5
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class5")
        self.assertIsNotNone(sg)
        self.assertIsInstance(sg, EDShieldGenerator)
        self.assertEqual(sg.rating, "A")
        # Multipliers for A: min:0.7, opt:1.2, max:1.7
        self.assertAlmostEqual(sg.opt_multiplier, 1.2)

    def test_factory_biweave(self):
         # Bi-Weave is C rated (class 3) with fast suffix
         # int_shieldgenerator_size3_class3_fast
         sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class3_fast")
         self.assertIsNotNone(sg)
         self.assertEqual(sg.rating, "C")
         # Fast multipliers: min:0.4, opt:0.9, max:1.4
         self.assertAlmostEqual(sg.opt_multiplier, 0.9)

    def test_factory_booster(self):
        # Booster 0A: shieldbooster_size0_class5
        sb = EDShieldingFactory.from_internal_name("shieldbooster_size0_class5")
        self.assertIsNotNone(sb)
        self.assertIsInstance(sb, EDShieldBooster)
        self.assertEqual(sb.strength_bonus, 0.20)

    def test_factory_scb(self):
        # SCB 6A: shieldcellbank_size6_class5
        scb = EDShieldingFactory.from_internal_name("shieldcellbank_size6_class5")
        self.assertIsNotNone(scb)
        self.assertIsInstance(scb, EDShieldCellBank)
        self.assertEqual(scb.duration, 8)
        self.assertEqual(scb.charges, 5)

    def test_generator_strength(self):
        # 3A Shield
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class5")
        # 3A Stats: opt mass 165
        # Multiplier: 1.2
        
        # Exact optimal mass match -> strength = base * opt_multiplier
        base_strength = 100.0
        strength = sg.strength(165, base_strength)
        self.assertAlmostEqual(strength, 120.0)

        # Lower mass than optional -> higher multiplier
        strength_light = sg.strength(100, base_strength)
        self.assertTrue(strength_light > 120.0)

        # Higher mass -> lower multiplier
        strength_heavy = sg.strength(200, base_strength)
        self.assertTrue(strength_heavy < 120.0)

    def test_distributor_pips(self):
        pd = EDPowerDistributor()
        # Default 2-2-2
        self.assertEqual(pd.sys, 2)
        
        # Update pips (values are out of 8?) 
        # Code divides by 2?
        # Typically pips are 0-4 per system, sum 6. 
        # In journal: "Pips": [4, 8, 0] -> SYS 2, ENG 4, WEP 0 ?
        # Code: sys = pips[0] / 2.0
        # If journal says 4 -> 2.0. So journal values are doubled? 
        # Yes, journal uses half-pips integer.
        
        pd.update([4, 8, 0])
        self.assertEqual(pd.sys, 2.0)
        self.assertEqual(pd.eng, 4.0)
        self.assertEqual(pd.wep, 0.0)
        
    def test_generator_engineering(self):
        sg = EDShieldingFactory.from_internal_name("int_shieldgenerator_size3_class5")
        # Apply Reinforced: +Strength, +Resistances
        engineering = {
            "Engineering": {
                "Modifiers": [
                    {"Label": "ShieldGenStrength", "Value": 150.0}, # +50% opt mult?
                    # Code: self.opt_multiplier = m["Value"]/100.0
                    # So 1.5. Old was 1.2.
                    # It also scales min/max by ratio.
                    
                    {"Label": "ExplosiveResistance", "Value": 60.0}
                ]
            }
        }
        
        sg.update_from(engineering)
        self.assertEqual(sg.opt_multiplier, 1.5)
        # Ratio: 1.5 / 1.2 = 1.25
        # Min was 0.7 -> 0.7 * 1.25 = 0.875
        self.assertAlmostEqual(sg.min_multiplier, 0.875)
        
        self.assertEqual(sg.shield_resistances.explosive, 0.6)

if __name__ == '__main__':
    unittest.main()
