
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edrxzibit import EDRXzibit # EDR_INTERNAL

class TestEDRXzibit(unittest.TestCase):
    def setUp(self):
        self.vehicle = MagicMock()
        self.vehicle.power_capacity = 30.0
        self.vehicle.slots = {}
        
        # Mock Power Data loading
        patcher = patch.object(EDRXzibit, 'load_power_data')
        self.mock_load = patcher.start()
        self.addCleanup(patcher.stop)
        EDRXzibit.POWER_DATA = {"int_hyperdrive": {"power": 2.0}, "int_shieldgenerator": {"power": 5.0}}

    def test_init(self):
        xzibit = EDRXzibit(self.vehicle)
        self.assertEqual(xzibit.power_capacity, 30.0)

    def test_assess_power_priorities_busted(self):
        # Setup modules
        fsd = MagicMock()
        fsd.is_valid.return_value = True
        fsd.priority = 1
        fsd.power_draw = 5.0 # < 20% of 30 (6.0)
        fsd.on = True
        fsd.generic_name.return_value = "int_hyperdrive"
        
        self.vehicle.slots = {"slot1": fsd}
        
        xzibit = EDRXzibit(self.vehicle)
        assessment = xzibit.assess_power_priorities()
        
        busted = assessment["20"]
        self.assertEqual(busted["grade"], 1.0) # FSD is operational below 20%

    def test_assess_power_priorities_busted_fail(self):
        # Setup modules
        fsd = MagicMock()
        fsd.is_valid.return_value = True
        fsd.priority = 1
        fsd.power_draw = 10.0 # > 20% of 30 (6.0)
        fsd.on = True
        fsd.generic_name.return_value = "int_hyperdrive"
        
        self.vehicle.slots = {"slot1": fsd}
        
        xzibit = EDRXzibit(self.vehicle)
        assessment = xzibit.assess_power_priorities()
        
        busted = assessment["20"]
        self.assertEqual(busted["grade"], 0) # FSD not powered, nothing functional

    def test_readable_name(self):
        self.assertEqual(EDRXzibit._readable_name("int_hyperdrive"), "FSD")
        self.assertEqual(EDRXzibit._readable_name("unknown_module"), "unknown_module")

if __name__ == '__main__':
    unittest.main()
