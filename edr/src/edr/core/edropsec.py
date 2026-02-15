class EDROpsecConfig:
    """
    Manages Operational Security (OpSec) configurations.

    Determines if player location/activity should be hidden based on wing/crew/power status.
    """

    def __init__(self, user_config):
        """
        Initializes EDROpsecConfig with user-specified settings.

        Args:
            user_config (configparser.ConfigParser): The user configuration object.
        """
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
        """
        Check if the interaction with the target commander is protected by OpSec rules.

        Args:
            cmdr_profile (EDRCmdrProfile): The profile of the commander being interacted with.
            player (EDPlayerOne): The current player object.

        Returns:
            bool: True if the interaction is protected by OpSec rules, False otherwise.
        """
        if not cmdr_profile:
            return False

        if not self.opsec_enabled:
            return False

        if cmdr_profile.name == player.name:
            return False

        from .edrlog import EDR_LOG  # EDR_INTERNAL
        if self._is_never_report_cmdr(cmdr_profile.name):
            EDR_LOG.debug(f"{cmdr_profile.name} is in never_report_cmdrs (OPSEC).")
            return True

        if self._is_never_report_power(cmdr_profile.powerplay):
            EDR_LOG.debug(f"{cmdr_profile.name} is in never_report_powers (OPSEC).")
            return True

        if self.power and cmdr_profile.powerplay and player.power and cmdr_profile.powerplay == player.power:
            EDR_LOG.debug(f"{cmdr_profile.name} is in the same power (OPSEC).")
            return True

        if self.squadron and cmdr_profile.squadron_id and player.squadron and cmdr_profile.squadron_id == player.squadron.inara_id:
            EDR_LOG.debug(f"{cmdr_profile.name} is in the same squadron (OPSEC).")
            return True

        if self.wing and player.is_wingmate(cmdr_profile.name):
            EDR_LOG.debug(f"{cmdr_profile.name} is in the same wing (OPSEC).")
            return True

        if self.crew and player.is_crewmate(cmdr_profile.name):
            EDR_LOG.debug(f"{cmdr_profile.name} is in the same crew (OPSEC).")
            return True

        return False

    def _is_never_report_cmdr(self, cmdr_name):
        """
        Check if a commander is in the 'never report' list.

        Args:
            cmdr_name (str): The name of the commander.

        Returns:
            bool: True if the commander should never be reported, False otherwise.
        """
        if cmdr_name is None:
            return False
        return cmdr_name in self.never_report_cmdrs

    def _is_never_report_power(self, power_name):
        """
        Check if a power is in the 'never report' list.

        Args:
            power_name (str): The name of the power.

        Returns:
            bool: True if the power should never be reported, False otherwise.
        """
        if power_name is None:
            return False
        return power_name in self.never_report_powers


class EDROpsecConfigDefault(EDROpsecConfig):
    """
    Default OpSec configuration (all protections enabled).
    """

    def __init__(self):
        """
        Initializes EDROpsecConfigDefault with all protections enabled.
        """
        self.opsec_enabled = True
        self.wing = True
        self.crew = True
        self.squadron = True
        self.power = True

        self.never_report_cmdrs = set()
        self.never_report_powers = set()
