import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from edr.models.edvehicles import EDUnknownVehicle, EDVehicle
from edr.models.edshipyard import EDVehicleFactory, EDSidewinder, EDAnaconda, EDDiamondbackExplorer
import json
import os

class TestEDVehicles(unittest.TestCase):
    def setUp(self):
        self.vehicle = EDVehicle()
        self.vehicle.type = "Sidewinder"
        self.vehicle.size = 2 # SMALL

    def test_canonicalize_missing(self):
        result = EDVehicleFactory.canonicalize(None)
        self.assertEqual(result, u"Unknown")

        result = EDVehicleFactory.canonicalize(u"")
        self.assertEqual(result, u"")

    def test_canonicalize_non_official(self):
        result = EDVehicleFactory.canonicalize(u"Panther X")
        self.assertEqual(result, u"panther x")

    def test_from_internal_name(self):
        result = EDVehicleFactory.from_internal_name(u"sidewinder")
        self.assertIsInstance(result, EDSidewinder)

        result = EDVehicleFactory.from_internal_name(u"Anaconda")
        self.assertIsInstance(result, EDAnaconda)

        result = EDVehicleFactory.from_internal_name(u"doesnotexist")
        self.assertIsInstance(result, EDUnknownVehicle)

    def test_hull_strength_basic(self):
        self.vehicle.hull_base_strength = 200
        # Default armour has no bonus? Need to check default_armour in EDHullFactory which we probably should have mocked but let's see.
        # Assuming lightweight alloy, no bonus.
        
        strength = self.vehicle.hull_strength()
        # Default armour multiplier is usually ~1.0 or depending on alloy. 
        # Let's check EDHullFactory.default_armour() behavior or mock it.
        # Since we didn't mock EDHullFactory, we rely on its default.
        # If it's Lightweight Alloy, multiplier is usually 0.8? Or 1.0?
        # Actually in edarmour.py Lightweight Alloy might have multiplier 1.0 or 0.8?
        # Let's rely on loose check or mock self.vehicle.armour
        
        self.vehicle.armour = MagicMock()
        self.vehicle.armour.strength.return_value = 200 # Mocking the computation
        
        self.assertEqual(self.vehicle.hull_strength(), 200)

    def test_hull_strength_with_hrp(self):
        self.vehicle.hull_base_strength = 200
        self.vehicle.armour = MagicMock()
        self.vehicle.armour.strength.return_value = 200
        
        hrp = MagicMock()
        hrp.enabled = True
        hrp.armour = 100
        self.vehicle.hrps = [hrp]
        
        self.assertEqual(self.vehicle.hull_strength(), 300)

    def test_shield_strength_basic(self):
        self.vehicle.hull_mass = 100
        self.vehicle.shield_base_strength = 200
        self.vehicle.shield_gen = MagicMock()
        self.vehicle.shield_gen.strength.return_value = 200
        
        self.assertEqual(self.vehicle.shield_strength(), 200)

    def test_shield_strength_with_boosters(self):
        self.vehicle.hull_mass = 100
        self.vehicle.shield_base_strength = 200
        self.vehicle.shield_gen = MagicMock()
        self.vehicle.shield_gen.strength.return_value = 200
        
        booster = MagicMock()
        booster.enabled = True
        booster.strength_bonus = 0.2 # +20%
        self.vehicle.boosters = [booster]
        
        # 200 * (1 + 0.2) = 240
        self.assertAlmostEqual(self.vehicle.shield_strength(), 240.0)

    def test_subsystem_health(self):
        with patch('edr.models.edvehicles.EDTime') as mock_time:
            # Patch readable_module_names to avoid dependency on external JSON files
            with patch('edr.models.edshipyard.EDVehicleFactory.readable_module_names', return_value=("Power Plant", "PP")):
                self.vehicle.subsystem_health("PowerPlant", 80.0)
                
                details = self.vehicle.subsystem_details("PowerPlant")
                self.assertIsNotNone(details)
                self.assertEqual(details["name"], "Power Plant")
                self.assertEqual(details["stats"].last_value(), 80.0)

    def test_update_from_modules_dict(self):
        modules = [
            {"Slot": "PowerPlant", "Item": "Int_PowerPlant_Size2_Class1", "Health": 1.0},
            {"Slot": "MediumHardpoint1", "Item": "Hpt_MultiCannon_Fixed_Medium", "Health": 1.0},
            {"Slot": "Slot01_Size2", "Item": "Int_HullReinforcement_Size1_Class1", "Health": 1.0}
        ]
        
        # Mock EDWeaponFactory to ensure a weapon is created
        with patch('edr.models.edvehicles.EDWeaponFactory.from_module') as mock_weapon_factory:
            mock_weapon = MagicMock()
            mock_weapon_factory.return_value = mock_weapon
            
            self.vehicle.update_from_modules_dict(modules)
            
            self.assertIn("PowerPlant", self.vehicle.slots)
            self.assertEqual(len(self.vehicle.weapons), 1)
            self.assertEqual(len(self.vehicle.hrps), 1)

    def test_json_status(self):
        # Mock hull/shield health
        self.vehicle.hull_health = 100.0
        self.vehicle.shield_health = 100.0
        self.vehicle.timestamp = 1000
        
        # Ensure shield_default logic (whole_loadout and has_shield_generator)
        self.vehicle.whole_loadout = True
        
        # Mock has_shield_generator to return True
        with patch.object(self.vehicle, 'has_shield_generator', return_value=True):
            status = self.vehicle.json()
            
            self.assertEqual(status["type"], "Sidewinder")
            self.assertEqual(status["hullHealth"]["value"], 100.0)
            self.assertEqual(status["shieldHealth"]["value"], 100.0)

    def test_needs_landing_pads(self):
        self.vehicle.size = 2 # SMALL
        self.assertFalse(self.vehicle.needs_medium_landing_pad())
        
        self.vehicle.size = 3 # MEDIUM
        self.assertTrue(self.vehicle.needs_medium_landing_pad())
        self.assertFalse(self.vehicle.needs_large_landing_pad())
        
        self.vehicle.size = 4 # LARGE
        self.assertFalse(self.vehicle.needs_medium_landing_pad()) # This logic might be tricky. Is Large > Medium? 
        # Code says: return self.size in [EDVehicleSize.MEDIUM, EDVehicleSize.UNKNOWN]
        # So Large does NOT need Medium pad (it needs Large). 
        # Wait, usually a Large ship needs a Large pad. A Medium pad is too small. 
        # A Small ship CAN use Medium pad.
        # But the function is `needs_medium_landing_pad`.
        # If it returns True, it implies it requires AT LEAST Medium? Or EXACTLY Medium?
        # The code: `return self.size in [EDVehicleSize.MEDIUM, EDVehicleSize.UNKNOWN]`
        # So it returns True if it IS Medium.
        # Let's check usage. If I have a Large ship, needs_medium is False. needs_large is True.
        
        self.assertTrue(self.vehicle.needs_large_landing_pad())

    def test_unsafe(self):
        with patch('edr.models.edvehicles.EDTime') as mock_time:
            mock_time.py_epoch_now.return_value = 1000
            self.vehicle.unsafe()
            
            # Check in_danger
            self.assertTrue(self.vehicle.in_danger())
            
            # Advance time beyond threshold
            mock_time.py_epoch_now.return_value = 1000 + self.vehicle.danger_staleness_threshold + 1
            self.assertFalse(self.vehicle.in_danger())

if __name__ == '__main__':
    unittest.main()