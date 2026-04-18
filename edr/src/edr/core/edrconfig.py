import os
import configparser as cp
from .edropsec import EDROpsecConfig, EDROpsecConfigDefault
from edr.utils.edrpath import plugin_root


class EDRUserConfig:
    """
    Handles user-specific configuration options from config/user_config.ini.
    """

    def __init__(self, config_file='config/user_config.ini'):
        """
        Initialize EDRUserConfig.

        Args:
             config_file (str): Path to the user configuration file. Defaults to 'config/user_config.ini'.
        """
        self.config = cp.ConfigParser()
        edr_root = plugin_root()
        try:
            self.config.read(os.path.join(edr_root, config_file))
        except Exception:
            self.config = None

    def opsec_config(self):
        """
        Return the operational security configuration.

        Returns:
            EDROpsecConfig: The opsec configuration object or default if not found.
        """
        if self.config and self.config.has_section('opsec'):
            return EDROpsecConfig(self.config)
        return EDROpsecConfigDefault()

    def discord_webhook_for_comms(self, channel, incoming=True):
        """
        Return the Discord webhook URL for a specific communications channel.

        Args:
            channel (str): The channel name.
            incoming (bool): Whether it is for incoming messages. Defaults to True.

        Returns:
            str: Webhook URL or None.
        """
        if self.config:
            section = "discord_incoming" if incoming else "discord_outgoing"
            key = "{}_webhook".format(channel)
            try:
                return self.config.get(section, key)
            except (cp.NoSectionError, cp.NoOptionError):
                return None
        return None

    def discord_webhook_for_fc(self, kind):
        """
        Return the Discord webhook URL for fleet carrier updates.

        Args:
            kind (str): The kind of update.

        Returns:
            str: Webhook URL or None.
        """
        if self.config:
            section = "discord_fleetcarrier"
            key = "{}_webhook".format(kind)
            try:
                return self.config.get(section, key)
            except (cp.NoSectionError, cp.NoOptionError):
                return None
        return None


class EDRConfig:
    """
    Handles general EDR configuration from config/config.ini.
    """

    def __init__(self, config_file='config/config.ini'):
        """
        Initialize EDRConfig.

        Args:
            config_file (str): Path to the main configuration file. Defaults to 'config/config.ini'.
        """
        self.config = cp.ConfigParser()
        edr_root = plugin_root()
        self.config.read(os.path.join(edr_root, config_file))

    def edr_version(self):
        """
        Return the current EDR version.

        Returns:
            str: The current EDR version.
        """
        return self.config.get('general', 'version')

    def edr_api_key(self):
        """
        Return the EDR API Key.

        Returns:
            str: The EDR API Key.
        """
        return self.config.get('edr', 'edr_api_key')

    def edr_server(self):
        """
        Return the EDR server URL.

        Returns:
            str: The EDR server URL.
        """
        return self.config.get('edr', 'edr_server')

    def edr_server_functions(self):
        """
        Return the URL for EDR Cloud Functions.

        Returns:
             str: URL for EDR Cloud Functions.
        """
        return self.config.get('edr', 'edr_server_functions')

    def edr_needs_u_novelty_threshold(self):
        """
        Return threshold for considering a "needs " event novel.

        Returns:
             int: Threshold for considering a "needs " event novel.
        """
        return int(self.config.get('edr', 'edr_needs_u_novelty_threshold'))

    def edr_heartbeat(self):
        """
        Return heartbeat interval in seconds.

        Returns:
             int: Heartbeat interval in seconds.
        """
        return int(self.config.get('edr', 'edr_heartbeat'))

    def inara_api_key(self):
        """
        Return Inara API Key.

        Returns:
             str: Inara API Key.
        """
        return self.config.get('inara', 'inara_api_key')

    def inara_endpoint(self):
        """
        Return Inara API Endpoint.

        Returns:
             str: Inara API Endpoint.
        """
        return self.config.get('inara', 'inara_endpoint')

    def edsm_api_key(self):
        """
        Return EDSM API Key.

        Returns:
             str: EDSM API Key.
        """
        return self.config.get('edsm', 'edsm_api_key')

    def edsm_server(self):
        """
        Return EDSM Server URL.

        Returns:
             str: EDSM Server URL.
        """
        return self.config.get('edsm', 'edsm_server')

    def intel_even_if_clean(self):
        """
        Return whether to report intel even if the target is clean.

        Returns:
             bool: Whether to report intel even if the target is clean.
        """
        return self.config.getboolean('scans', 'intel_even_if_clean')

    def intel_bounty_threshold(self):
        """
        Return minimum bounty to trigger an intel report.

        Returns:
             int: Minimum bounty to trigger an intel report.
        """
        return self.config.getint('scans', 'intel_bounty_threshold')

    def legal_records_recent_threshold(self):
        """
        Return max age in seconds for a legal record to be considered recent.

        Returns:
             int: Max age in seconds for a legal record to be considered recent.
        """
        return int(self.config.get('scans', 'legal_records_recent_threshold'))

    def legal_records_check_interval(self):
        """
        Return interval in seconds between legal record checks.

        Returns:
             int: Interval in seconds between legal record checks.
        """
        return int(self.config.get('scans', 'legal_records_check_interval'))

    def legal_records_max_age(self):
        """
        Return max age in seconds for legal records cache.

        Returns:
             int: Max age in seconds for legal records cache.
        """
        return int(self.config.get('scans', 'legal_records_max_age'))

    def system_novelty_threshold(self):
        """
        Return threshold for system novelty.

        Returns:
             int: Threshold for system novelty.
        """
        return int(self.config.get('novelty', 'system_novelty_threshold'))

    def place_novelty_threshold(self):
        """
        Return threshold for place novelty.

        Returns:
             int: Threshold for place novelty.
        """
        return int(self.config.get('novelty', 'place_novelty_threshold'))

    def ship_novelty_threshold(self):
        """
        Return threshold for ship novelty.

        Returns:
             int: Threshold for ship novelty.
        """
        return int(self.config.get('novelty', 'ship_novelty_threshold'))

    def cognitive_novelty_threshold(self):
        """
        Return threshold for cognitive novelty.

        Returns:
             int: Threshold for cognitive novelty.
        """
        return int(self.config.get('novelty', 'cognitive_novelty_threshold'))

    def enemy_alerts_pledge_threshold(self):
        """
        Return pledge time threshold for enemy alerts.

        Returns:
             int: Pledge time threshold for enemy alerts.
        """
        return int(self.config.get('enemies', 'enemy_alerts_pledge_threshold'))

    def noteworthy_pledge_threshold(self):
        """
        Return pledge time threshold for being noteworthy.

        Returns:
             int: Pledge time threshold for being noteworthy.
        """
        return int(self.config.get('powerplay', 'noteworthy_pledge_threshold'))

    def systems_max_age(self):
        """
        Return max age for systems cache.

        Returns:
             int: Max age for systems cache.
        """
        return int(self.config.get('lrucaches', 'systems_max_age'))

    def cmdrs_max_age(self):
        """
        Return max age for commanders cache.

        Returns:
             int: Max age for commanders cache.
        """
        return int(self.config.get('lrucaches', 'cmdrs_max_age'))

    def cmdrsdex_max_age(self):
        """
        Return max age for commanders dex cache.

        Returns:
             int: Max age for commanders dex cache.
        """
        return int(self.config.get('lrucaches', 'cmdrsdex_max_age'))

    def sqdrdex_max_age(self):
        """
        Return max age for squadron dex cache.

        Returns:
             int: Max age for squadron dex cache.
        """
        return int(self.config.get('lrucaches', 'sqdrdex_max_age'))

    def inara_max_age(self):
        """
        Return max age for Inara cache.

        Returns:
             int: Max age for Inara cache.
        """
        return int(self.config.get('lrucaches', 'inara_max_age'))

    def blips_max_age(self):
        """
        Return max age for blips cache.

        Returns:
             int: Max age for blips cache.
        """
        return int(self.config.get('lrucaches', 'blips_max_age'))

    def scans_max_age(self):
        """
        Return max age for scans cache.

        Returns:
             int: Max age for scans cache.
        """
        return int(self.config.get('lrucaches', 'scans_max_age'))

    def traffic_max_age(self):
        """
        Return max age for traffic cache.

        Returns:
             int: Max age for traffic cache.
        """
        return int(self.config.get('lrucaches', 'traffic_max_age'))

    def crimes_max_age(self):
        """
        Return max age for crimes cache.

        Returns:
             int: Max age for crimes cache.
        """
        return int(self.config.get('lrucaches', 'crimes_max_age'))

    def alerts_max_age(self):
        """
        Return max age for alerts cache.

        Returns:
             int: Max age for alerts cache.
        """
        return int(self.config.get('lrucaches', 'alerts_max_age'))

    def fights_max_age(self):
        """
        Return max age for fights cache.

        Returns:
             int: Max age for fights cache.
        """
        return int(self.config.get('lrucaches', 'fights_max_age'))

    def materials_max_age(self):
        """
        Return max age for materials cache.

        Returns:
             int: Max age for materials cache.
        """
        return int(self.config.get('lrucaches', 'materials_max_age'))

    def factions_max_age(self):
        """
        Return max age for factions cache.

        Returns:
             int: Max age for factions cache.
        """
        return int(self.config.get('lrucaches', 'factions_max_age'))

    def edsm_systems_max_age(self):
        """
        Return max age for EDSM systems cache.

        Returns:
             int: Max age for EDSM systems cache.
        """
        return int(self.config.get('lrucaches', 'edsm_systems_max_age'))

    def edsm_bodies_max_age(self):
        """
        Return max age for EDSM bodies cache.

        Returns:
             int: Max age for EDSM bodies cache.
        """
        return int(self.config.get('lrucaches', 'edsm_bodies_max_age'))

    def edsm_stations_max_age(self):
        """
        Return max age for EDSM stations cache.

        Returns:
             int: Max age for EDSM stations cache.
        """
        return int(self.config.get('lrucaches', 'edsm_stations_max_age'))

    def edsm_factions_max_age(self):
        """
        Return max age for EDSM factions cache.

        Returns:
             int: Max age for EDSM factions cache.
        """
        return int(self.config.get('lrucaches', 'edsm_factions_max_age'))

    def edsm_markets_max_age(self):
        """
        Return max age for EDSM markets cache.

        Returns:
             int: Max age for EDSM markets cache.
        """
        return int(self.config.get('lrucaches', 'edsm_markets_max_age'))

    def edsm_shipyards_max_age(self):
        """
        Return max age for EDSM shipyards cache.

        Returns:
             int: Max age for EDSM shipyards cache.
        """
        return int(self.config.get('lrucaches', 'edsm_shipyards_max_age'))

    def edsm_outfitting_max_age(self):
        """
        Return max age for EDSM outfitting cache.

        Returns:
             int: Max age for EDSM outfitting cache.
        """
        return int(self.config.get('lrucaches', 'edsm_outfitting_max_age'))

    def edsm_traffic_max_age(self):
        """
        Return max age for EDSM traffic cache.

        Returns:
             int: Max age for EDSM traffic cache.
        """
        return int(self.config.get('lrucaches', 'edsm_traffic_max_age'))

    def edsm_deaths_max_age(self):
        """
        Return max age for EDSM deaths cache.

        Returns:
             int: Max age for EDSM deaths cache.
        """
        return int(self.config.get('lrucaches', 'edsm_deaths_max_age'))

    def lru_max_size(self):
        """
        Return max size for LRU caches.

        Returns:
             int: Max size for LRU caches.
        """
        return int(self.config.get('lrucaches', 'lru_max_size'))

    def edsm_within_radius_max_size(self):
        """
        Return max size for EDSM search within radius cache.

        Returns:
             int: Max size for EDSM search within radius cache.
        """
        return int(self.config.get('lrucaches', 'edsm_within_radius_max_size'))

    def opponents_max_age(self, kind):
        """
        Return max age for opponents cache of a given kind.

        Args:
            kind (str): Kind of opponent (e.g. 'interdictors', 'scanned').

        Returns:
             int: Max age for opponents cache of a given kind.
        """
        ckind = kind.lower()
        return int(self.config.get(ckind, '{}_max_age'.format(ckind)))

    def opponents_max_recents(self, kind):
        """
        Return max recent opponents to track.

        Args:
            kind (str): Kind of opponent.

        Returns:
             int: Max recent opponents to track.
        """
        ckind = kind.lower()
        return int(self.config.get(ckind, '{}_max_recents'.format(ckind)))

    def logging_level(self):
        """
        Return the logging level.

        Returns:
             str: The logging level.
        """
        return self.config.get('general', 'logging_level')

    def sitreps_timespan(self):
        """
        Return timespan in seconds for sitreps.

        Returns:
             int: Timespan in seconds for sitreps.
        """
        return int(self.config.get('sitreps', 'sitreps_timespan'))

    def notams_timespan(self):
        """
        Return timespan in seconds for NOTAMs.

        Returns:
             int: Timespan in seconds for NOTAMs.
        """
        return int(self.config.get('notams', 'notams_timespan'))

    def sitreps_max_age(self):
        """
        Return max age for sitreps cache.

        Returns:
             int: Max age for sitreps cache.
        """
        return int(self.config.get('sitreps', 'sitreps_max_age'))

    def reports_check_interval(self):
        """
        Return interval for checking reports.

        Returns:
             int: Interval for checking reports.
        """
        return int(self.config.get('sitreps', 'reports_check_interval'))

    def notams_check_interval(self):
        """
        Return interval for checking NOTAMs.

        Returns:
             int: Interval for checking NOTAMs.
        """
        return int(self.config.get('notams', 'notams_check_interval'))

    def notams_max_age(self):
        """
        Return max age for NOTAMs cache.

        Returns:
             int: Max age for NOTAMs cache.
        """
        return int(self.config.get('notams', 'notams_max_age'))

    def recon_recent_threshold(self):
        """
        Return threshold for considering recon data recent.

        Returns:
             int: Threshold for considering recon data recent.
        """
        return int(self.config.get('sitreps', 'recon_recent_threshold'))

    def opponents_recent_threshold(self, kind):
        """
        Return threshold for considering opponent contact recent.

        Args:
            kind (str): Kind of opponent.

        Returns:
             int: Threshold for considering opponent contact recent.
        """
        ckind = kind.lower()
        return int(self.config.get('sitreps', '{}_recent_threshold'.format(ckind)))

    def crimes_recent_threshold(self):
        """
        Return threshold for considering crimes recent.

        Returns:
             int: Threshold for considering crimes recent.
        """
        return int(self.config.get('sitreps', 'crimes_recent_threshold'))

    def traffic_recent_threshold(self):
        """
        Return threshold for considering traffic recent.

        Returns:
             int: Threshold for considering traffic recent.
        """
        return int(self.config.get('sitreps', 'traffic_recent_threshold'))

    def fc_reports_max_age(self):
        """
        Return max age for Fleet Carrier reports.

        Returns:
             int: Max age for Fleet Carrier reports.
        """
        return int(self.config.get('fc', 'fc_reports_max_age'))

    def fc_presence_max_age(self):
        """
        Return max age for Fleet Carrier presence data.

        Returns:
             int: Max age for Fleet Carrier presence data.
        """
        return int(self.config.get('fc', 'fc_presence_max_age'))

    def fc_materials_max_age(self):
        """
        Return max age for Fleet Carrier materials data.

        Returns:
             int: Max age for Fleet Carrier materials data.
        """
        return int(self.config.get('fc', 'fc_materials_max_age'))

    def fc_max_age(self):
        """
        Return max age for general Fleet Carrier data.

        Returns:
             int: Max age for general Fleet Carrier data.
        """
        return int(self.config.get('fc', 'fc_max_age'))

    def instance_fight_staleness_threshold(self):
        """
        Return threshold for fight staleness in instance.

        Returns:
             int: Threshold for fight staleness in instance.
        """
        return int(self.config.get('instance', 'fight_staleness_threshold'))

    def instance_danger_staleness_threshold(self):
        """
        Return threshold for danger staleness in instance.

        Returns:
             int: Threshold for danger staleness in instance.
        """
        return int(self.config.get('instance', 'danger_staleness_threshold'))

    def hpp_trend_span(self):
        """
        Return time span for HPP trend.

        Returns:
             int: Time span for HPP trend.
        """
        return int(self.config.get('hpp', 'trend_span'))

    def hpp_history_max_points(self):
        """
        Return max history points for HPP.

        Returns:
             int: Max history points for HPP.
        """
        return int(self.config.get('hpp', 'history_max_points'))

    def hpp_history_max_span(self):
        """
        Return max history span for HPP.

        Returns:
             int: Max history span for HPP.
        """
        return int(self.config.get('hpp', 'history_max_span'))

    def navroute_jumps_threshold_to_show(self):
        """
        Return jumps threshold to show nav route.

        Returns:
             int: Jumps threshold to show nav route.
        """
        return int(self.config.get('navroute', 'jumps_threshold_to_show'))

    def navroute_jumps_threshold_to_give_up(self):
        """
        Return jumps threshold to give up nav route.

        Returns:
             int: Jumps threshold to give up nav route.
        """
        return int(self.config.get('navroute', 'jumps_threshold_to_give_up'))


_edr_config_instance = None


def get_edr_config():
    """
    Get the global EDRConfig instance.

    Returns:
        EDRConfig: The configuration instance.
    """
    global _edr_config_instance
    if _edr_config_instance is None:
        _edr_config_instance = EDRConfig()
    return _edr_config_instance


EDR_CONFIG = get_edr_config()
__version__ = EDR_CONFIG.edr_version()
