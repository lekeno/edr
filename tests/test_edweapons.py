import unittest
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edweapons import EDWeaponFactory, EDWeapon, EDDamageFractions # EDR_INTERNAL

class TestEDWeapon(unittest.TestCase):
    def test_factory_plasma(self):
        # hpt_plasmaaccelerator_fixed_huge -> EDPlasmaAcc4A
        pa = EDWeaponFactory.from_internal_name("hpt_plasmaaccelerator_fixed_huge")
        self.assertIsNotNone(pa)
        self.assertEqual(pa.damage, 125.2)
        # Fractions: 60% absolute, 20% thermal, 20% kinetic
        self.assertEqual(pa.fractions.absolute, 0.6)
        self.assertEqual(pa.fractions.thermal, 0.2)
        self.assertEqual(pa.fractions.kinetic, 0.2)
        self.assertEqual(pa.fractions.explosive, 0.0)

    def test_factory_railgun(self):
        # hpt_railgun_fixed_medium -> EDRailGun2B
        rg = EDWeaponFactory.from_internal_name("hpt_railgun_fixed_medium")
        self.assertIsNotNone(rg)
        self.assertEqual(rg.damage, 41.5)
        # Fractions: 33/66 kinetic/thermal? Code says: 1.0/3.0 kinetic, 2.0/3.0 thermal
        self.assertAlmostEqual(rg.fractions.kinetic, 1.0/3.0)
        self.assertAlmostEqual(rg.fractions.thermal, 2.0/3.0)

    def test_damage_fractions_apply(self):
        fractions = EDDamageFractions(absolute=0.5, thermal=0.5)
        damage = 100
        applied = fractions.apply(damage)
        self.assertEqual(applied["absolute"], 50.0)
        self.assertEqual(applied["thermal"], 50.0)
        self.assertEqual(applied["kinetic"], 0.0)

    def test_damage_calculation_basic(self):
        pa = EDWeaponFactory.from_internal_name("hpt_plasmaaccelerator_fixed_huge")
        result = pa.damage_per_shot()
        # 125.2 distributed
        self.assertAlmostEqual(result["absolute"], 125.2 * 0.6)

    def test_damage_calculation_premium_ammo(self):
        pa = EDWeaponFactory.from_internal_name("hpt_plasmaaccelerator_fixed_huge")
        pa.premium_ammo() # +30% of base damage
        
        # Expected: 125.2 + (125.2 * 0.3) = 162.76
        result = pa.damage_per_shot()
        total_damage = sum(result.values())
        self.assertAlmostEqual(total_damage, 125.2 * 1.3)

    def test_damage_calculation_engineering(self):
        pa = EDWeaponFactory.from_internal_name("hpt_plasmaaccelerator_fixed_huge")
        
        # Engineering: Damage Mod (+10%)
        engineering = {
            "Engineering": {
                "Modifiers": [
                    {"Label": "Damage", "Value": 137.72, "OriginalValue": 125.2}
                ]
            }
        }
        pa.update_from(engineering)
        
        result = pa.damage_per_shot()
        total_damage = sum(result.values())
        self.assertAlmostEqual(total_damage, 137.72)

    def test_damage_calculation_thermal_conduit(self):
        pa = EDWeaponFactory.from_internal_name("hpt_plasmaaccelerator_fixed_huge")
        # Add special effect
        engineering = {
            "Engineering": {
                "Modifiers": [
                    {"ExperimentalEffect": "special_thermal_conduit"} # Sets temp_multiplier to 0.6
                ]
            }
        }
        pa.update_from(engineering)
        
        # No temp -> no bonus
        pa.temperature_percent(0.0)
        result = pa.damage_per_shot()
        self.assertAlmostEqual(sum(result.values()), 125.2)

        # Max temp (>150%) -> +60% bonus
        pa.temperature_percent(1.6)
        result = pa.damage_per_shot()
        self.assertAlmostEqual(sum(result.values()), 125.2 * 1.6)
        
        # Partial temp (120%) 
        # Scale: (1.2 - 0.9) / (1.5 - 0.9) = 0.3 / 0.6 = 0.5
        # Bonus: 0.5 * 0.6 = 0.3 (30%)
        pa.temperature_percent(1.2)
        result = pa.damage_per_shot()
        self.assertAlmostEqual(sum(result.values()), 125.2 * 1.3)

if __name__ == '__main__':
    unittest.main()
