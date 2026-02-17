
import unittest
from edr.models.edweapons import EDDamageFractions, EDWeapon, EDWeaponFactory, EDPlasmaAcc4A

class TestEDDamageFractions(unittest.TestCase):
    def test_apply(self):
        # absolute, explosive, kinetic, thermal, caustic
        fractions = EDDamageFractions(absolute=0.1, explosive=0.2, kinetic=0.3, thermal=0.4, caustic=0.0)
        
        damage_dist = fractions.apply(100.0)
        self.assertAlmostEqual(damage_dist["absolute"], 10.0)
        self.assertAlmostEqual(damage_dist["explosive"], 20.0)
        self.assertAlmostEqual(damage_dist["kinetic"], 30.0)
        self.assertAlmostEqual(damage_dist["thermal"], 40.0)
        self.assertAlmostEqual(damage_dist["caustic"], 0.0)

class TestEDWeapon(unittest.TestCase):
    def test_update_from_engineering(self):
        weapon = EDWeapon()
        weapon.damage = 10.0
        
        module = {
            "Engineering": {
                "Modifiers": [
                    {"Label": "Damage", "OriginalValue": 10.0, "Value": 15.0},
                    {"Label": "DamagePerSecond", "OriginalValue": 5.0, "Value": 7.5}
                ]
            }
        }
        
        weapon.update_from(module)
        self.assertEqual(weapon.damage, 10.0)
        self.assertEqual(weapon.enhanced_damage, 15.0)
        self.assertEqual(weapon.dps, 5.0)
        self.assertEqual(weapon.enhanced_dps, 7.5)

    def test_update_from_experimental(self):
        weapon = EDWeapon()
        module = {
            "Engineering": {
                "Modifiers": [
                    {"ExperimentalEffect": "special_thermal_conduit"}
                ]
            }
        }
        weapon.update_from(module)
        self.assertEqual(weapon.temp_multiplier, 0.6)

    def test_damage_calc_basic(self):
        weapon = EDWeapon()
        weapon.damage = 100.0
        weapon.fractions = EDDamageFractions(absolute=1.0)
        
        result = weapon.damage_per_shot()
        self.assertAlmostEqual(result["absolute"], 100.0)

    def test_damage_calc_premium_ammo(self):
        weapon = EDWeapon()
        weapon.damage = 100.0
        weapon.fractions = EDDamageFractions(absolute=1.0)
        weapon.premium_ammo() # +30%
        
        result = weapon.damage_per_shot()
        # 100 + (100 * 0.3) = 130
        self.assertAlmostEqual(result["absolute"], 130.0)

    def test_damage_calc_thermal_conduit(self):
        weapon = EDWeapon()
        weapon.damage = 100.0
        weapon.fractions = EDDamageFractions(absolute=1.0)
        weapon.temp_multiplier = 0.6 # 60% max bonus
        
        # Temp < 90% -> No bonus
        weapon.temperature_percent(0.8)
        result = weapon.damage_per_shot()
        self.assertAlmostEqual(result["absolute"], 100.0)
        
        # Temp > 150% -> Max bonus
        weapon.temperature_percent(1.6)
        # 100 * (1.0 + 0.6) = 160
        result = weapon.damage_per_shot()
        self.assertAlmostEqual(result["absolute"], 160.0)
        
        # Temp 120% -> Half bonus (0.3)
        # scaled: (1.2 - 0.9) / (1.5 - 0.9) = 0.3 / 0.6 = 0.5 ratio
        # multiplier = 0.5 * 0.6 = 0.3
        weapon.temperature_percent(1.2)
        result = weapon.damage_per_shot()
        self.assertAlmostEqual(result["absolute"], 130.0)

class TestEDWeaponFactory(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(EDWeaponFactory.normalize_module_name("$int_plasmaaccelerator_fixed_huge_name;"), "plasmaaccelerator_fixed_huge")
        self.assertEqual(EDWeaponFactory.normalize_module_name("hpt_railgun_fixed_medium"), "railgun_fixed_medium")

    def test_from_internal_name(self):
        weapon = EDWeaponFactory.from_internal_name("$int_plasmaaccelerator_fixed_huge_name;")
        self.assertIsInstance(weapon, EDPlasmaAcc4A)
        self.assertEqual(weapon.damage, 125.2)

    def test_from_module(self):
        module = {
            "Item": "$int_plasmaaccelerator_fixed_huge_name;",
            "Engineering": {
                "Modifiers": [{"Label": "Damage", "OriginalValue": 125.2, "Value": 200.0}]
            }
        }
        weapon = EDWeaponFactory.from_module(module)
        self.assertIsInstance(weapon, EDPlasmaAcc4A)
        self.assertEqual(weapon.enhanced_damage, 200.0)

if __name__ == '__main__':
    unittest.main()
