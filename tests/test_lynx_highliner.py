import unittest
from edr.models.edvehicles import EDVehicleFactory, EDLynxHighliner, EDVehicleSize

class TestLynxHighliner(unittest.TestCase):
    def test_factory_creation(self):
        ship = EDVehicleFactory.from_internal_name("mediumtransport01")
        self.assertIsInstance(ship, EDLynxHighliner)
        self.assertEqual(ship.type, "Lynx Highliner")
        self.assertEqual(ship.size, EDVehicleSize.MEDIUM)
        self.assertEqual(ship.seats, 2)
        self.assertEqual(ship.value, 69289470)
        self.assertEqual(ship.shield_base_strength, 228)
        self.assertEqual(ship.hull_mass, 260)
        self.assertEqual(ship.hull_hardness, 55)
        self.assertAlmostEqual(ship.hull_base_strength, 350.0)

    def test_canonicalize(self):
        self.assertEqual(EDVehicleFactory.canonicalize("mediumtransport01"), "Lynx Highliner")

if __name__ == '__main__':
    unittest.main()
