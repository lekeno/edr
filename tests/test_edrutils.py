
from unittest import TestCase, main
from edr.utils.edrutils import pretty_print_number, simplified_body_name

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

    def test_compare_versions(self):
        from edr.utils.edrutils import compare_versions
        self.assertEqual(compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(compare_versions("1.0.1", "1.0.0"), 1)
        self.assertEqual(compare_versions("1.0.0", "1.0.1"), -1)
        self.assertEqual(compare_versions("1.1.0", "1.0.0"), 1)
        self.assertEqual(compare_versions("2.0.0", "1.0.0"), 1)
        self.assertEqual(compare_versions("1.0", "1.0.0"), 0)
        self.assertEqual(compare_versions("1.0.0", "1.0"), 0)
        self.assertEqual(compare_versions("1.0.0.1", "1.0.0"), 1)
        
    def test_is_valid_semver(self):
        from edr.utils.edrutils import is_valid_semver
        self.assertTrue(is_valid_semver("1.0.0"))
        self.assertTrue(is_valid_semver("0.1.0"))
        self.assertTrue(is_valid_semver("0.0.1"))
        self.assertTrue(is_valid_semver("10.20.30"))
        
        self.assertFalse(is_valid_semver("1.0"))
        self.assertFalse(is_valid_semver("1.0.0.0"))
        self.assertFalse(is_valid_semver("v1.0.0"))
        self.assertFalse(is_valid_semver("1.0.0-beta"))
        self.assertFalse(is_valid_semver("invalid"))

if __name__ == '__main__':
    main()
