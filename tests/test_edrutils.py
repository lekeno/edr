
from unittest import TestCase, main
from edr.utils.edrutils import pretty_print_number, simplified_body_name # EDR_INTERNAL

class TestEDRUtils(TestCase):
    def test_pretty_print_number(self):
        self.assertEqual(pretty_print_number(100), "100")
        self.assertEqual(pretty_print_number(999), "999")
        self.assertEqual(pretty_print_number(1000), "1 k")
        self.assertEqual(pretty_print_number(1500), "1.5 k")
        self.assertEqual(pretty_print_number(9999), "10 k")
        self.assertEqual(pretty_print_number(10000), "10 k")
        self.assertEqual(pretty_print_number(15000), "15 k")
        self.assertEqual(pretty_print_number(999999), "999 k")
        self.assertEqual(pretty_print_number(1000000), "1 m")
        
        self.assertEqual(pretty_print_number(None), "N/A")

    def test_simplified_body_name(self):
        # Case 1: Prefix match
        self.assertEqual(simplified_body_name("Pleione", "Pleione A 1 A"), "a 1 a")
        
        # Case 2: Case insensitivity
        self.assertEqual(simplified_body_name("pleione", "PLEIONE A 1 A"), "a 1 a")
        
        # Case 3: No prefix match
        self.assertEqual(simplified_body_name("Sol", "Earth"), "earth")
        
        # Case 4: Prefix match but result empty (system name equals body name)
        # implementation returns original body_name (Preserving case) if simplified is empty and no override
        self.assertEqual(simplified_body_name("Pleione", "Pleione"), "Pleione")
        self.assertEqual(simplified_body_name("Pleione", "Pleione", "Star"), "Star")

        self.assertIsNone(simplified_body_name(None, "Body"))
        self.assertIsNone(simplified_body_name("System", None))

if __name__ == '__main__':
    main()
