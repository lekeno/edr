
class EDROpsecConfig(object):
    def __init__(self, user_config):
        self.opsec_enabled = user_config.getboolean('opsec', 'enabled') if user_config.has_option('opsec', 'enabled') else True
        self.wing = user_config.getboolean('opsec', 'wing') if user_config.has_option('opsec', 'wing') else True
        self.crew = user_config.getboolean('opsec', 'crew') if user_config.has_option('opsec', 'crew') else True
        self.squadron = user_config.getboolean('opsec', 'squadron') if user_config.has_option('opsec', 'squadron') else True
        self.power = user_config.getboolean('opsec', 'power') if user_config.has_option('opsec', 'power') else True

        never_report_cmdrs = user_config.get('opsec', 'never_report_cmdrs') if user_config.has_option('opsec', 'never_report_cmdrs') else ''
        self.never_report_cmdrs = set(val.strip() for val in never_report_cmdrs.split(',')) if never_report_cmdrs else set()

        never_report_powers = user_config.get('opsec', 'never_report_powers') if user_config.has_option('opsec', 'never_report_powers') else ''
        self.never_report_powers = set(val.strip() for val in never_report_powers.split(',')) if never_report_powers else set()

    def is_protected(self, cmdr_profile, player):
        if not cmdr_profile:
            return False

        if not self.opsec_enabled:
            return False
        
        if cmdr_profile.name == player.name:
            return False

        if self.__is_never_report_cmdr(cmdr_profile.name):
            return True

        if self.__is_never_report_power(cmdr_profile.powerplay):
            return True

        if self.power and cmdr_profile.powerplay and player.power and cmdr_profile.powerplay == player.power:
            return True

        if self.squadron and cmdr_profile.squadron_id and player.squadron and cmdr_profile.squadron_id == player.squadron.inara_id:
            return True

        if self.wing and player.is_wingmate(cmdr_profile.name):
            return True

        if self.crew and player.is_crewmate(cmdr_profile.name):
            return True

        return False

    def __is_never_report_cmdr(self, cmdr_name):
        if cmdr_name is None:
            return False
        
        return cmdr_name in self.never_report_cmdrs

    def __is_never_report_power(self, power_name):
        if power_name is None:
            return False
        
        return power_name in self.never_report_powers

class EDROpsecConfigDefault(EDROpsecConfig):
    def __init__(self):
        self.opsec_enabled = True
        self.wing = True
        self.crew = True
        self.squadron = True
        self.power = True

        self.never_report_cmdrs = set()
        self.never_report_powers = set()