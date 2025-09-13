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

    def is_never_report_cmdr(self, cmdr_name):
        return cmdr_name in self.never_report_cmdrs

    def is_never_report_power(self, power_name):
        return power_name in self.never_report_powers
