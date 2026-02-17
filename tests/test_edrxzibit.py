
import unittest
from unittest.mock import MagicMock, patch, mock_open
from edr.models.edrxzibit import EDRXzibit

class TestEDRXzibit(unittest.TestCase):
    def setUp(self):
        self.log_patch = patch('edr.models.edrxzibit.EDR_LOG')
        self.mock_log = self.log_patch.start()
        
        self.i18n_patch = patch('edr.models.edrxzibit._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()
        
        # Mock open to prevent file access during load_power_data
        self.open_patch = patch('builtins.open', mock_open(read_data='{}'))
        self.mock_open = self.open_patch.start()

    def tearDown(self):
        self.log_patch.stop()
        self.i18n_patch.stop()
        self.open_patch.stop()

    def _create_mock_module(self, name, priority, power_draw, on=True, is_valid=True, is_shield=False):
        module = MagicMock()
        module.generic_name.return_value = name
        module.priority = priority
        module.power_draw = power_draw
        module.on = on
        module.is_valid.return_value = is_valid
        module.is_shield.return_value = is_shield
        return module

    def test_init_no_power(self):
        vehicle = MagicMock()
        vehicle.power_capacity = None
        vehicle.slots = {}
        
        xzibit = EDRXzibit(vehicle)
        self.assertIsNone(xzibit.power_capacity)
        
        assessment = xzibit.assess_power_priorities()
        self.assertIsNone(assessment)

    def test_init_with_modules(self):
        vehicle = MagicMock()
        vehicle.power_capacity = 30.0
        
        mod1 = self._create_mock_module("int_hyperdrive", 1, 2.0)
        mod2 = self._create_mock_module("int_engine", 2, 5.0)
        mod3 = self._create_mock_module("int_cargo", 5, 0.0, is_valid=False) # Invalid
        
        vehicle.slots = {"slot1": mod1, "slot2": mod2, "slot3": mod3}
        
        xzibit = EDRXzibit(vehicle)
        self.assertEqual(xzibit.power_capacity, 30.0)
        self.assertIn(mod1, xzibit.per_prio["1"]["modules"])
        self.assertIn(mod2, xzibit.per_prio["2"]["modules"])
        self.assertNotIn(mod3, xzibit.per_prio["5"]["modules"]) # Invalid shouldn't be added

    def test_assess_busted_pp(self):
        # Cap 10.0 MW. 20% = 2.0 MW.
        vehicle = MagicMock()
        vehicle.power_capacity = 10.0
        
        # FSD fits in 2.0 MW? 
        # FSD draw 1.5 MW (P1) -> OK
        fsd = self._create_mock_module("int_hyperdrive", 1, 1.5)
        # Thrusters draw 1.0 MW (P1) -> Total 2.5 MW -> Over 2.0 -> Neither might fit if processed together or in order
        # Code iterates priorities. 
        # P1 total = 2.5 > 2.0. So P1 is skipped?
        # _functional_at logic:
        # P1: power_draw starts 0. Add mod1 (1.5) -> 1.5 <= 2.0. ok.
        # Add mod2 (1.0) -> 2.5 > 2.0. The code says: "is over the cap => not adding anything from {tentative_within_modules}".
        # So NOTHING from P1 is added if the TOTAL of P1 exceeds cap?
        # Let's verify _functional_at logic:
        # for pri in keys:
        #   tentative = set()
        #   for module in modules: ... power_draw += module.power_draw ... tentative.add()
        #   if power_draw > threshold: break (and don't add tentative)
        # So yes, it's all-or-nothing per priority group.
        
        # We need FSD to fit in P1 for "Good job" grade.
        thrusters = self._create_mock_module("int_engine", 2, 1.0)
        
        vehicle.slots = {"fsd": fsd, "thrusters": thrusters}
        xzibit = EDRXzibit(vehicle)
        
        assessment = xzibit._assess_busted_powerplant()
        # FSD (1.5) is in P1. P1 total 1.5 < 2.0. OK.
        # Thrusters (1.0) is in P2. Total 2.5 > 2.0. P2 skipped.
        
        self.assertEqual(assessment["grade"], 1.0)
        self.assertIn("Good job", assessment["praise"])

    def test_assess_busted_pp_fail(self):
        vehicle = MagicMock()
        vehicle.power_capacity = 10.0
        
        # FSD draw 2.5 MW (P1) -> Exceeds 2.0 MW (20%)
        fsd = self._create_mock_module("int_hyperdrive", 1, 2.5)
        
        vehicle.slots = {"fsd": fsd}
        xzibit = EDRXzibit(vehicle)
        
        assessment = xzibit._assess_busted_powerplant()
        self.assertEqual(assessment["grade"], 0.0) # FSD not functional
        self.assertIn("Keep your FSD below", assessment.get("recommendation", ""))

    def test_assess_recovered_pp(self):
        # Cap 10.0. 50% = 5.0 MW.
        vehicle = MagicMock()
        vehicle.power_capacity = 10.0
        
        # We need FSD (1.5), Thrusters (1.5) and Shield (1.5)
        fsd = self._create_mock_module("int_hyperdrive", 1, 1.5)
        thrusters = self._create_mock_module("int_engine", 1, 1.5)
        shield = self._create_mock_module("int_shieldgenerator", 2, 1.5, is_shield=True)
        
        vehicle.slots = {"fsd": fsd, "thrusters": thrusters, "shield": shield}
        xzibit = EDRXzibit(vehicle)
        
        # P1: 3.0 <= 5.0. OK.
        # P2: 3.0 + 1.5 = 4.5 <= 5.0. OK.
        
        assessment = xzibit._assess_recovered_powerplant()
        self.assertEqual(assessment["grade"], 1.0)

    def test_assess_malfunctioning_pp(self):
        # Cap 10.0. 40% = 4.0 MW.
        vehicle = MagicMock()
        vehicle.power_capacity = 10.0
        
        fsd = self._create_mock_module("int_hyperdrive", 1, 1.5)
        thrusters = self._create_mock_module("int_engine", 1, 1.5)
        shield = self._create_mock_module("int_shieldgenerator", 2, 1.5, is_shield=True)
        
        vehicle.slots = {"fsd": fsd, "thrusters": thrusters, "shield": shield}
        xzibit = EDRXzibit(vehicle)
        
        # P1: 3.0 <= 4.0. OK.
        # P2: 3.0 + 1.5 = 4.5 > 4.0. Fail. Shield excluded.
        
        assessment = xzibit._assess_malfunctioning_powerplant()
        # Required: FSD, Engine, Shield (since we have one)
        # Present: FSD, Engine. Missing: Shield.
        # Grade should be partial.
        
        self.assertLess(assessment["grade"], 1.0)
        self.assertIn("shield", assessment["recommendation"])

    def test_assess_all(self):
        vehicle = MagicMock()
        vehicle.power_capacity = 10.0
        mod = self._create_mock_module("int_hyperdrive", 1, 1.0)
        vehicle.slots = {"mod": mod}
        
        xzibit = EDRXzibit(vehicle)
        assessment = xzibit.assess_power_priorities()
        
        self.assertIn("20", assessment)
        self.assertIn("40", assessment)
        self.assertIn("50", assessment)

    def test_off_modules(self):
        vehicle = MagicMock()
        vehicle.power_capacity = 10.0
        # Off module shouldn't count towards power draw unless required
        # But wait, code says:
        # if not ed_module.on and (required is None or ed_module.generic_name() not in required): continue
        # So if it IS required, it IS considered even if off?
        
        # Let's test non-required off module
        mod = self._create_mock_module("int_cargo", 1, 5.0, on=False) # 5.0 MW off
        # If it counted, it would take 5.0 MW. 
        # Let's try 20% (2.0 MW).
        
        required_mod = self._create_mock_module("int_hyperdrive", 1, 1.0, on=True)
        
        vehicle.slots = {"cargo": mod, "fsd": required_mod}
        xzibit = EDRXzibit(vehicle)
        
        assessment = xzibit._assess_busted_powerplant() # 2.0 MW limit
        # P1: Cargo is off and not required -> skipped.
        # P1: FSD is on -> added (1.0).
        # Total 1.0 <= 2.0. OK.
        
        self.assertEqual(assessment["grade"], 1.0)

if __name__ == '__main__':
    unittest.main()
