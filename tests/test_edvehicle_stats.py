import unittest
import sys
import os

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Also add edr directory itself to resolve imports like 'edrconfig' if they are top-level
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../edr')))

from edr.edmodule import EDModule, EDResistances
from edr.edvehicles import EDSidewinder, EDAnaconda
from edr.edshield import EDShieldGenerator, EDShieldBooster, EDGuardianShieldReinforcementPackage
from edr.edarmour import EDHullReinforcementPackage

class TestEDVehicleStats(unittest.TestCase):
    def test_shield_strength_no_boosters(self):
        ship = EDSidewinder()
        ship.shield_base_strength = 100.0
        ship.hull_mass = 100.0 # Match opt_hull_mass
        # For simple test, let's mock/setup generator stats
        ship.shield_gen = EDShieldGenerator()
        ship.shield_gen.min_hull_mass = 1
        ship.shield_gen.opt_hull_mass = 100
        ship.shield_gen.max_hull_mass = 1000
        ship.shield_gen.min_multiplier = 0.7
        ship.shield_gen.opt_multiplier = 1.2
        ship.shield_gen.max_multiplier = 1.7
        
        # 100 MJ base, 1.2 multiplier at opt mass -> 120 MJ
        self.assertAlmostEqual(ship.shield_strength(), 120.0)

    def test_shield_strength_with_boosters(self):
        ship = EDSidewinder()
        ship.shield_base_strength = 100.0
        ship.hull_mass = 50.0
        ship.shield_gen = EDShieldGenerator()
        ship.shield_gen.min_hull_mass = 1
        ship.shield_gen.opt_hull_mass = 50
        ship.shield_gen.max_hull_mass = 1000
        ship.shield_gen.min_multiplier = 0.7
        ship.shield_gen.opt_multiplier = 1.2
        ship.shield_gen.max_multiplier = 1.7
        
        # 100 MJ base, 1.2 multiplier at opt mass -> 120 MJ
        # Add 20% booster -> 120 * 1.2 = 144 MJ
        booster = EDShieldBooster()
        booster.strength_bonus = 0.20
        booster.enabled = True
        ship.boosters.append(booster)
        
        self.assertAlmostEqual(ship.shield_strength(), 144.0)

    def test_shield_strength_with_gsrp(self):
        ship = EDSidewinder()
        ship.shield_base_strength = 100.0
        ship.hull_mass = 50.0
        ship.shield_gen = EDShieldGenerator()
        ship.shield_gen.min_hull_mass = 1
        ship.shield_gen.opt_hull_mass = 50
        ship.shield_gen.max_hull_mass = 1000
        ship.shield_gen.min_multiplier = 0.7
        ship.shield_gen.opt_multiplier = 1.2
        ship.shield_gen.max_multiplier = 1.7
        
        # Add GSRP (flat MJ bonus)
        gsrp = EDGuardianShieldReinforcementPackage()
        gsrp.strength = 50.0
        gsrp.enabled = True
        ship.gsrps.append(gsrp)
        
        # 100 * 1.2 + 50 = 170 MJ
        self.assertAlmostEqual(ship.shield_strength(), 170.0)

    def test_shield_pip_independence(self):
        """Verify that SYS pips do NOT reduce shield strength MJ value."""
        ship = EDSidewinder()
        ship.shield_base_strength = 100.0
        ship.hull_mass = 50.0
        ship.shield_gen = EDShieldGenerator()
        ship.shield_gen.min_hull_mass = 1
        ship.shield_gen.opt_hull_mass = 50
        ship.shield_gen.max_hull_mass = 1000
        ship.shield_gen.min_multiplier = 0.7
        ship.shield_gen.opt_multiplier = 1.2
        ship.shield_gen.max_multiplier = 1.7
        
        # 4 Pips in SYS (div by 2.0 in update -> 2.0. Dividing 8 half-pips -> 4.0)
        # Journal: Update Pips [8, 4, 0]
        ship.distro.update([8, 0, 0]) # 4 pips SYS
        
        # BEFORE FIX: strength *= (1.0 - sys_resistance)
        # sys_res at 4 pips is ~0.6. So strength became 120 * 0.4 = 48 MJ.
        # AFTER FIX: strength remains 120 MJ.
        self.assertAlmostEqual(ship.shield_strength(), 120.0)

    def test_effective_shield_strength_pips(self):
        """Verify that effective_shield_strength increases with SYS pips."""
        ship = EDSidewinder()
        ship.shield_base_strength = 100.0
        ship.hull_mass = 100.0
        ship.shield_gen = EDShieldGenerator()
        ship.shield_gen.min_hull_mass = 1
        ship.shield_gen.opt_hull_mass = 100
        ship.shield_gen.max_hull_mass = 1000
        ship.shield_gen.min_multiplier = 0.7
        ship.shield_gen.opt_multiplier = 1.2
        ship.shield_gen.max_multiplier = 1.7
        
        # 4 Pips in SYS -> approx 60% mitigation
        ship.distro.update([8, 0, 0])
        raw_mj = 120.0
        pip_res = ship.distro.sys_resistance() # approx 0.6
        expected_eff = raw_mj / (1.0 - pip_res)
        
        self.assertAlmostEqual(ship.effective_shield_strength("absolute"), expected_eff)
        self.assertTrue(expected_eff > raw_mj)

    def test_effective_shield_strength_resistances(self):
        """Verify that effective_shield_strength accounts for both pips and module resistances."""
        ship = EDSidewinder()
        ship.shield_base_strength = 100.0
        ship.hull_mass = 100.0
        ship.shield_gen = EDShieldGenerator()
        ship.shield_gen.min_hull_mass = 1
        ship.shield_gen.opt_hull_mass = 100
        ship.shield_gen.max_hull_mass = 1000
        ship.shield_gen.min_multiplier = 0.7
        ship.shield_gen.opt_multiplier = 1.2
        ship.shield_gen.max_multiplier = 1.7
        ship.shield_gen.shield_resistances = EDResistances(0, 0, 0)
        
        # Add a booster with thermal resistance
        booster = EDShieldBooster()
        booster.resistances.thermal = 0.1 # 10%
        booster.enabled = True
        ship.boosters.append(booster)
        
        # 0 Pips in SYS -> 0% mitigation
        ship.distro.update([0, 4, 4])
        
        # Verify Raw MJ first
        raw_mj = ship.shield_strength()
        self.assertAlmostEqual(raw_mj, 120.0)
        
        thermal_res = 0.1
        expected_eff = raw_mj / (1.0 - thermal_res)
        
        self.assertAlmostEqual(ship.effective_shield_strength("thermal"), expected_eff)

    def test_hull_strength_with_hrp(self):
        ship = EDSidewinder()
        ship.hull_base_strength = 100.0
        ship.armour.armour_multiplier = 0.5 # 50% extra from bulkheads
        
        # Base + Bulkhead = 100 * (1 + 0.5) = 150
        
        hrp = EDHullReinforcementPackage()
        hrp.armour = 100.0
        hrp.enabled = True
        ship.hrps.append(hrp)
        
        # 150 + 100 = 250
        self.assertAlmostEqual(ship.hull_strength(), 250.0)

if __name__ == '__main__':
    unittest.main()
