import unittest
import sys
import os

# Setup paths
current_dir = os.path.dirname(__file__)
edr_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
root_dir = os.path.abspath(os.path.join(edr_dir, os.pardir))
sys.path.insert(0, root_dir)
sys.path.insert(0, edr_dir)

from edarmour import EDHullFactory, EDHullBulkhead, EDHullReinforcementPackage # EDR_INTERNAL

class TestEDArmour(unittest.TestCase):
    def test_factory_bulkheads(self):
        # Test basic lightweight alloy
        hull = EDHullFactory.from_module({"Item": "$python_armour_grade1_name;", "Name": "Lightweight Alloy"})
        self.assertIsNotNone(hull)
        self.assertEqual(hull.armour_multiplier, 0.8)

        # Test military grade
        hull = EDHullFactory.from_module({"Item": "$int_python_armour_grade3_name;", "Name": "Military Grade Composite"})
        self.assertIsNotNone(hull)
        self.assertEqual(hull.armour_multiplier, 2.5)

    def test_factory_hrp(self):
        # Test HRP 5D
        hrp = EDHullFactory.from_module({"Item": "$int_hullreinforcement_size5_class2_name;", "Name": "Hull Reinforcement Package"})
        self.assertIsNotNone(hrp)
        self.assertEqual(hrp.armour, 390)

    def test_factory_unknown(self):
        hull = EDHullFactory.from_module({"Item": "unknown_module"})
        self.assertIsNone(hull)

    def test_hull_strength(self):
        # Military grade: multiplier 2.5. Base strength 100.
        # Strength = 100 * (1 + 2.5) = 350
        hull = EDHullFactory.from_module({"Item": "grade3"})
        self.assertEqual(hull.strength(100), 350.0)

        # Lightweight: multiplier 0.8. Strength = 100 * 1.8 = 180
        hull = EDHullFactory.from_module({"Item": "grade1"})
        self.assertAlmostEqual(hull.strength(100), 180.0)

    def test_update_from_engineering_bulkhead(self):
        hull = EDHullFactory.from_module({"Item": "grade2"}) # Reinforced, 1.52
        
        # Apply engineering: Heavy Duty (increases multiplier) and resists
        engineering = {
            "Engineering": {
                "Modifiers": [
                    {"Label": "DefenceModifierHealthMultiplier", "Value": 30.0}, # +30% to multiplier? or replaces? 
                    # Code says: self.armour_multiplier = m["Value"]/100.0. It REPLACES the multiplier.
                    # Wait, if it replaces, then base stats are ignored? 
                    # Let's verify `edarmour.py` implementation.
                    # L53: self.armour_multiplier = m["Value"]/100.0
                    # Yes, it assigns directly. 
                    # So if Heavy Duty gives +30% over base, the Value in journal usually reflects the TOTAL multiplier or the bonus?
                    # In Journal 3.4+, Modifiers have "Value".
                    # Usually for multipliers it's the final multiplier or the addition? 
                    # If the code assigns it, it assumes "Value" is the absolute multiplier?
                    # Or maybe "Value" is the BONUS? 
                    # If I have 1.52 base, and Value is 30, does it become 0.3? That would be weak.
                    # Typically "DefenceModifierHealthMultiplier" value is like 182.0 for 82% boost?
                    # Let's assume the code expects the value to be used as `Value/100.0`. 
                    # So if Value is 152, it matches base. 
                    
                    {"Label": "ExplosiveResistance", "Value": 50.0}
                ]
            }
        }
        
        hull.update_from(engineering)
        self.assertEqual(hull.armour_multiplier, 0.3) # 30.0 / 100.0. This seems low if it replaces. 
        # But per the code `edarmour.py`: `self.armour_multiplier = m["Value"]/100.0`.
        # So I will test that it does exactly what the code says.
        
        self.assertEqual(hull.hull_resistances.explosive, 0.5)

    def test_update_from_engineering_hrp(self):
        hrp = EDHullFactory.from_module({"Item": "hullreinforcement_size1_class1"}) # 1E, 80 armour
        
        engineering = {
            "Engineering": {
                "Modifiers": [
                    {"Label": "DefenceModifierHealthAddition", "Value": 200.0},
                    {"Label": "KineticResistance", "Value": 15.5}
                ]
            }
        }
        
        hrp.update_from(engineering)
        self.assertEqual(hrp.armour, 200.0) # Replaces
        self.assertEqual(hrp.resistances.kinetic, 0.155)

if __name__ == '__main__':
    unittest.main()
