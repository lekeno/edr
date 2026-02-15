
from unittest import TestCase, main
from unittest.mock import MagicMock
from edr.core.edropsec import EDROpsecConfig

class TestEDROpsecConfig(TestCase):
    def test_init_defaults(self):
        # Mock user config with no options (simulating defaults)
        user_config = MagicMock()
        user_config.has_option.return_value = False
        
        opsec = EDROpsecConfig(user_config)
        self.assertTrue(opsec.opsec_enabled)
        self.assertTrue(opsec.wing)
        self.assertTrue(opsec.crew)
        self.assertTrue(opsec.squadron)
        self.assertTrue(opsec.power)
        self.assertEqual(opsec.never_report_cmdrs, set())
        self.assertEqual(opsec.never_report_powers, set())

    def test_init_custom(self):
        user_config = MagicMock()
        user_config.has_option.side_effect = lambda section, option: True
        
        def getboolean_side_effect(section, option):
            if section == 'opsec':
                if option == 'enabled': return True
                if option == 'wing': return False
                return True
            return False

        user_config.getboolean.side_effect = getboolean_side_effect
        user_config.get.side_effect = lambda section, option: "Cmdr1, Cmdr2" if option == 'never_report_cmdrs' else "Power1"

        opsec = EDROpsecConfig(user_config)
        self.assertTrue(opsec.opsec_enabled)
        self.assertFalse(opsec.wing)
        self.assertEqual(opsec.never_report_cmdrs, {"Cmdr1", "Cmdr2"})
        self.assertEqual(opsec.never_report_powers, {"Power1"})

    def test_is_protected_general(self):
        # Setup basic enabled opsec
        user_config = MagicMock()
        user_config.has_option.return_value = False # Defaults to True
        opsec = EDROpsecConfig(user_config)
        
        cmdr = MagicMock()
        cmdr.name = "Target"
        player = MagicMock()
        
        # Base case: no relation
        player.is_wingmate.return_value = False
        player.is_crewmate.return_value = False
        cmdr.powerplay = "PowerA"
        player.power = "PowerB"
        cmdr.squadron_id = "Sq1"
        player.squadron.inara_id = "Sq2"
        
        self.assertFalse(opsec.is_protected(cmdr, player))
        
        # Disabled globally
        opsec.opsec_enabled = False
        self.assertFalse(opsec.is_protected(cmdr, player))

    def test_is_protected_blocklists(self):
        user_config = MagicMock()
        user_config.has_option.return_value = False
        opsec = EDROpsecConfig(user_config)
        opsec.never_report_cmdrs = {"BlockedCmdr"}
        opsec.never_report_powers = {"BlockedPower"}
        
        cmdr = MagicMock()
        player = MagicMock()
        player.is_wingmate.return_value = False
        player.is_crewmate.return_value = False
        player.power = None
        player.squadron.inara_id = None
        
        # Blocked CMDR
        cmdr.name = "BlockedCmdr"
        self.assertTrue(opsec.is_protected(cmdr, player))
        
        # Blocked Power
        cmdr.name = "Random"
        cmdr.powerplay = "BlockedPower"
        self.assertTrue(opsec.is_protected(cmdr, player))
        
        # Not blocked
        cmdr.powerplay = "CleanPower"
        self.assertFalse(opsec.is_protected(cmdr, player))

    def test_is_protected_relations(self):
        user_config = MagicMock()
        user_config.has_option.return_value = False
        opsec = EDROpsecConfig(user_config)
        
        cmdr = MagicMock()
        player = MagicMock()
        
        # Wing
        player.is_wingmate.return_value = True
        cmdr.name = "Wingmate"
        self.assertTrue(opsec.is_protected(cmdr, player))
        player.is_wingmate.return_value = False
        
        # Crew
        player.is_crewmate.return_value = True
        cmdr.name = "Crewmate"
        self.assertTrue(opsec.is_protected(cmdr, player))
        player.is_crewmate.return_value = False
        
        # Power
        cmdr.powerplay = "SamePower"
        player.power = "SamePower"
        self.assertTrue(opsec.is_protected(cmdr, player))
        player.power = "OtherPower"
        self.assertFalse(opsec.is_protected(cmdr, player))
        
        # Squadron
        cmdr.squadron_id = 123
        player.squadron.inara_id = 123
        self.assertTrue(opsec.is_protected(cmdr, player))
        player.squadron.inara_id = 456
        self.assertFalse(opsec.is_protected(cmdr, player))


if __name__ == '__main__':
    main()
