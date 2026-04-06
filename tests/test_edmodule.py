import unittest
from unittest.mock import patch
from edr.models.edmodule import EDModule, EDResistances

class TestEDModule(unittest.TestCase):
    def setUp(self):
        # Mock POWER_DATA to be deterministic and independent of file
        self.mock_power_data = {
            "int_powerplant_size2_class1": {"powergen": 6.4, "powerdraw": 0.0},
            "int_hyperdrive_size2_class1": {"powergen": 0.0, "powerdraw": 0.15}
        }
        self.patcher = patch.dict('edr.models.edmodule.POWER_DATA', self.mock_power_data, clear=True)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_init_generic(self):
        module_data = {
            "Item": "int_hyperdrive_size2_class1",
            "Slot": "FrameShiftDrive",
            "On": True,
            "Priority": 1
        }
        module = EDModule(module_data)
        self.assertEqual(module.cname, "int_hyperdrive_size2_class1")
        self.assertEqual(module.power_draw, 0.15)
        self.assertEqual(module.priority, 2) # edmodule adds 1 to priority
        self.assertTrue(module.on)

    def test_is_shield(self):
        module = EDModule({"Item": "int_shieldgenerator_size2_class1", "Priority": 1})
        self.assertTrue(module.is_shield())
        
        module = EDModule({"Item": "int_engine_size2_class1", "Priority": 1})
        self.assertFalse(module.is_shield())

    def test_readable_name(self):
        # readable_name uses a LUT that keys off the full cname if normalization fails to match a pattern?
        # Actually, let's look at edmodule.py: generic_name attempts to extract the base name.
        # But readable_name does `lut.get(self.cname, self.cname)`. 
        # The LUT has "int_hyperdrive".
        # So we should test with "int_hyperdrive" if we want "FSD".
        module = EDModule({"Item": "int_hyperdrive", "Priority": 1})
        self.assertEqual(module.readable_name(), "FSD") # Lookup in internal LUT

    def test_resistances_class(self):
        res = EDResistances(0.1, 0.2, 0.3, 0.4)
        self.assertEqual(res.thermal, 0.1)
        self.assertEqual(res.kinetic, 0.2)
        self.assertEqual(res.explosive, 0.3)
        self.assertEqual(res.caustic, 0.4)

    def test_update(self):
        module_data = {"Item": "test_module", "On": False, "Priority": 1}
        module = EDModule(module_data)
        self.assertFalse(module.on)
        
        update_data = {"Item": "test_module", "On": True, "Priority": 1}
        updated = module.update(update_data)
        self.assertTrue(updated)
        self.assertTrue(module.on)

if __name__ == '__main__':
    unittest.main()
