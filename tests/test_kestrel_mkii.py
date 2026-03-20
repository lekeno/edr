import unittest
from edr.models.edvehicles import EDVehicleFactory, EDKestrelMkII, EDVehicleSize

class TestKestrelMkII(unittest.TestCase):
    def test_factory_creation(self):
        ship = EDVehicleFactory.from_internal_name("kestrel_mkii")
        self.assertIsInstance(ship, EDKestrelMkII)
        self.assertEqual(ship.type, "Kestrel Mk II")
        self.assertEqual(ship.size, EDVehicleSize.SMALL)
        self.assertEqual(ship.seats, 1)
        self.assertEqual(ship.value, 14273820)
        self.assertEqual(ship.shield_base_strength, 293)
        self.assertEqual(ship.hull_mass, 190)
        self.assertEqual(ship.hull_hardness, 55)
        self.assertAlmostEqual(ship.hull_base_strength, 70.0)

    def test_canonicalize(self):
        self.assertEqual(EDVehicleFactory.canonicalize("kestrel_mkii"), "Kestrel Mk II")

if __name__ == '__main__':
    unittest.main()
