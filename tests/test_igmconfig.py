
import unittest
from unittest.mock import MagicMock, patch
import configparser as cp
from edr.core.igmconfig import IGMConfig

class TestIGMConfig(unittest.TestCase):
    def setUp(self):
        # We can pass dummy paths because we will mock the internal config objects
        with patch('edr.core.igmconfig.cp.ConfigParser') as mock_cp:
            with patch('edr.core.igmconfig.os.path.exists'): # prevent file checks
                 self.igm = IGMConfig('dummy.ini', ['dummy_user.ini'])
        
        # Replace the mocks with verified MagicMocks for our tests
        self.igm.config = MagicMock(spec=cp.ConfigParser)
        self.igm.fallback_config = MagicMock(spec=cp.ConfigParser)

    def test_dimensions_defaults(self):
        # Setup defaults for helpers to trigger default values
        self.igm.config.getfloat.side_effect = cp.NoOptionError("section", "opt")
        self.igm.fallback_config.has_option.return_value = False
        
        self.assertEqual(self.igm.large_height(), 28)
        self.assertEqual(self.igm.normal_height(), 18)
        self.assertEqual(self.igm.large_width(), 14)
        self.assertEqual(self.igm.normal_width(), 8)

    def test_panel_enabled(self):
        # Case 1: Enabled in user config
        self.igm.config.getboolean.return_value = True
        self.assertTrue(self.igm.panel("mining"))
        self.igm.config.getboolean.assert_called_with('mining', 'panel')

        # Case 2: Disabled/Missing in user, check fallback
        self.igm.config.getboolean.side_effect = cp.NoSectionError("mining")
        self.igm.fallback_config.has_option.return_value = True
        self.igm.fallback_config.getboolean.return_value = True
        self.assertTrue(self.igm.panel("mining"))
        
        # Case 3: Missing in both -> Default False
        self.igm.fallback_config.has_option.return_value = False
        self.assertFalse(self.igm.panel("unknown"))

    def test_get_coordinates(self):
        self.igm.config.getint.return_value = 100
        self.assertEqual(self.igm.x("general", "body"), 100)
        self.igm.config.getint.assert_called_with('general', 'body_x')

    def test_rgb_and_fill(self):
        self.igm.config.get.return_value = "aabbcc"
        self.assertEqual(self.igm.rgb("general", "body"), "#aabbcc")
        self.assertEqual(self.igm.fill("general", "body"), "#aabbcc")

    def test_rgb_list(self):
        self.igm.config.get.return_value = "ffffff,000000"
        expected = ["#ffffff", "#000000"]
        self.assertEqual(self.igm.rgb_list("general", "body"), expected)
    
    def test_fill_list(self):
        self.igm.config.get.return_value = "ffffff,000000"
        expected = ["#ffffff", "#000000"]
        self.assertEqual(self.igm.fill_list("general", "body"), expected)

    def test_fallback_logic_get(self):
        # Trigger exception in main config
        self.igm.config.get.side_effect = Exception("Missing")
        
        # Setup fallback to have option
        self.igm.fallback_config.has_option.return_value = True
        self.igm.fallback_config.get.return_value = "FallbackValue"
        
        val = self.igm._get("sec", "opt", "Default")
        self.assertEqual(val, "FallbackValue")

    def test_fallback_logic_default(self):
        self.igm.config.get.side_effect = Exception("Missing")
        self.igm.fallback_config.has_option.return_value = False
        
        val = self.igm._get("sec", "opt", "Default")
        self.assertEqual(val, "Default")

if __name__ == '__main__':
    unittest.main()
