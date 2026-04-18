
import unittest
from unittest.mock import MagicMock, patch
from edr.core.edropsec import EDROpsecConfig, EDROpsecConfigDefault

class TestEDROpsecConfig(unittest.TestCase):
    def setUp(self):
        self.log_patch = patch('edr.core.edrlog.EDR_LOG')
        self.mock_log = self.log_patch.start()
        
        self.mock_user_config = MagicMock()
        # Default behavior: return True or empty keys if not specified
        self.mock_user_config.has_option.return_value = False
        self.mock_user_config.getboolean.return_value = True
        self.mock_user_config.get.return_value = ""

    def tearDown(self):
        self.log_patch.stop()

    def _setup_config(self, enabled=True, wing=True, crew=True, squadron=True, power=True, never_cmdrs="", never_powers=""):
        def getboolean_side_effect(section, option):
            if section != 'opsec': return None
            if option == 'enabled': return enabled
            if option == 'wing': return wing
            if option == 'crew': return crew
            if option == 'squadron': return squadron
            if option == 'power': return power
            return True
            
        def get_side_effect(section, option):
            if section != 'opsec': return None
            if option == 'never_report_cmdrs': return never_cmdrs
            if option == 'never_report_powers': return never_powers
            return ""
            
        self.mock_user_config.has_option.return_value = True
        self.mock_user_config.getboolean.side_effect = getboolean_side_effect
        self.mock_user_config.get.side_effect = get_side_effect
        
        return EDROpsecConfig(self.mock_user_config)

    def test_init_defaults(self):
        # Empty config -> defaults to True
        self.mock_user_config.has_option.return_value = False
        opsec = EDROpsecConfig(self.mock_user_config)
        self.assertTrue(opsec.opsec_enabled)
        self.assertTrue(opsec.wing)
        self.assertEqual(len(opsec.never_report_cmdrs), 0)

    def test_init_custom(self):
        opsec = self._setup_config(enabled=False, never_cmdrs="CmdrA, CmdrB")
        self.assertFalse(opsec.opsec_enabled)
        self.assertIn("CmdrA", opsec.never_report_cmdrs)
        self.assertIn("CmdrB", opsec.never_report_cmdrs)

    def test_is_protected_disabled(self):
        opsec = self._setup_config(enabled=False)
        self.assertFalse(opsec.is_protected(MagicMock(), MagicMock()))

    def test_is_protected_self(self):
        opsec = self._setup_config()
        player = MagicMock()
        player.name = "CmdrMe"
        profile = MagicMock()
        profile.name = "CmdrMe"
        
        # Self should not be "protected" in the sense of hiding interaction? 
        # Code says: if cmdr_profile.name == player.name: return False
        self.assertFalse(opsec.is_protected(profile, player))

    def test_is_protected_never_report(self):
        opsec = self._setup_config(never_cmdrs="CmdrSecret")
        player = MagicMock()
        player.name = "CmdrMe"
        profile = MagicMock()
        profile.name = "CmdrSecret"
        
        self.assertTrue(opsec.is_protected(profile, player))

    def test_is_protected_wing(self):
        opsec = self._setup_config(wing=True)
        player = MagicMock()
        player.name = "CmdrMe"
        player.is_wingmate.return_value = True
        player.is_crewmate.return_value = False
        player.power = None
        player.squadron = None
        
        profile = MagicMock()
        profile.name = "CmdrWingman"
        profile.squadron_id = None
        profile.powerplay = None
        
        self.assertTrue(opsec.is_protected(profile, player))
        
        # Test disabled
        opsec = self._setup_config(wing=False)
        self.assertFalse(opsec.is_protected(profile, player))

    def test_is_protected_squadron(self):
        opsec = self._setup_config(squadron=True)
        player = MagicMock()
        player.name = "CmdrMe"
        player.squadron.inara_id = 123
        player.is_wingmate.return_value = False
        player.is_crewmate.return_value = False
        player.power = None
        
        profile = MagicMock()
        profile.name = "CmdrSquad"
        profile.squadron_id = 123
        profile.powerplay = None
        
        self.assertTrue(opsec.is_protected(profile, player))
        
        # Test mismatch
        player.squadron.inara_id = 456
        self.assertFalse(opsec.is_protected(profile, player))

class TestEDROpsecConfigDefault(unittest.TestCase):
    def test_init(self):
        opsec = EDROpsecConfigDefault()
        self.assertTrue(opsec.opsec_enabled)
        self.assertTrue(opsec.wing)
        self.assertEqual(len(opsec.never_report_cmdrs), 0)

if __name__ == '__main__':
    unittest.main()
