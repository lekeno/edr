import unittest
from edr.utils.clippy import copy, paste

class TestClipboard(unittest.TestCase):
    def test_basic_copy_paste(self):
        copy("Safe 64-bit string")
        self.assertEqual(paste(), "Safe 64-bit string")

    def test_clippy_64bit_robustness(self):
        # A long-ish string with Unicode to test 64-bit allocation and UTF-16
        long_val = "EDR Journey to Beagle Point " + "🚀" * 50 
        copy(long_val)
        self.assertEqual(paste(), long_val)

if __name__ == '__main__':
    unittest.main()