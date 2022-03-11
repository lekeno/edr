from __future__ import absolute_import

import os
try:
    # for Python2
    import ConfigParser as cp
except ImportError:
    # for Python3
    import configparser as cp


import utils2to3

class EDRUserConfig(object):
    def __init__(self, config_file='config/user_config.ini'):
        self.config = cp.ConfigParser()
        try:
            self.config.read(utils2to3.abspathmaker(__file__, config_file))
        except:
            self.config = None

    def discord_webhook(self, channel, incoming=True):
        if self.config:
            section = "discord_incoming" if incoming else "discord_outgoing"
            key = "{}_webhook".format(channel)
            try:
                return self.config.get(section, key)
            except:
                return None
        return None


class EDRConfig(object):
    def __init__(self, config_file='config/config.ini'):
        self.config = cp.ConfigParser()
        self.config.read(utils2to3.abspathmaker(__file__, config_file))

    def edr_version(self):
        return self.config.get('general', 'version')

    def edr_api_key(self):
        return self.config.get('edr', 'edr_api_key')

    def edr_server(self):
        return self.config.get('edr', 'edr_server')

    def edr_needs_u_novelty_threshold(self):
        return int(self.config.get('edr', 'edr_needs_u_novelty_threshold'))

    def edr_heartbeat(self):
        return int(self.config.get('edr', 'edr_heartbeat'))

    def inara_api_key(self):
        return self.config.get('inara', 'inara_api_key')

    def inara_endpoint(self):
        return self.config.get('inara', 'inara_endpoint')

    def edsm_api_key(self):
        return self.config.get('edsm', 'edsm_api_key')

    def edsm_server(self):
        return self.config.get('edsm', 'edsm_server')

    def intel_even_if_clean(self):
        return self.config.getboolean('scans', 'intel_even_if_clean')

    def intel_bounty_threshold(self):
        return self.config.getint('scans', 'intel_bounty_threshold')

    def legal_records_recent_threshold(self):
        return int(self.config.get('scans', 'legal_records_recent_threshold'))
    
    def legal_records_check_interval(self):
        return int(self.config.get('scans', 'legal_records_check_interval'))

    def legal_records_max_age(self):
        return int(self.config.get('scans', 'legal_records_max_age'))

    def system_novelty_threshold(self):
        return int(self.config.get('novelty', 'system_novelty_threshold'))

    def place_novelty_threshold(self):
        return int(self.config.get('novelty', 'place_novelty_threshold'))

    def ship_novelty_threshold(self):
        return int(self.config.get('novelty', 'ship_novelty_threshold'))

    def cognitive_novelty_threshold(self):
        return int(self.config.get('novelty', 'cognitive_novelty_threshold'))

    def enemy_alerts_pledge_threshold(self):
        return int(self.config.get('enemies', 'enemy_alerts_pledge_threshold'))

    def noteworthy_pledge_threshold(self):
        return int(self.config.get('powerplay', 'noteworthy_pledge_threshold'))

    def systems_max_age(self):
        return int(self.config.get('lrucaches', 'systems_max_age'))

    def cmdrs_max_age(self):
        return int(self.config.get('lrucaches', 'cmdrs_max_age'))

    def cmdrsdex_max_age(self):
        return int(self.config.get('lrucaches', 'cmdrsdex_max_age'))

    def sqdrdex_max_age(self):
        return int(self.config.get('lrucaches', 'sqdrdex_max_age'))

    def inara_max_age(self):
        return int(self.config.get('lrucaches', 'inara_max_age'))

    def blips_max_age(self):
        return int(self.config.get('lrucaches', 'blips_max_age'))

    def scans_max_age(self):
        return int(self.config.get('lrucaches', 'scans_max_age'))

    def traffic_max_age(self):
        return int(self.config.get('lrucaches', 'traffic_max_age'))

    def crimes_max_age(self):
        return int(self.config.get('lrucaches', 'crimes_max_age'))

    def alerts_max_age(self):
        return int(self.config.get('lrucaches', 'alerts_max_age'))

    def fights_max_age(self):
        return int(self.config.get('lrucaches', 'fights_max_age'))

    def materials_max_age(self):
        return int(self.config.get('lrucaches', 'materials_max_age'))

    def factions_max_age(self):
        return int(self.config.get('lrucaches', 'factions_max_age'))

    def edsm_systems_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_systems_max_age'))

    def edsm_bodies_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_bodies_max_age'))

    def edsm_stations_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_stations_max_age'))

    def edsm_factions_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_factions_max_age'))

    def edsm_markets_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_markets_max_age'))

    def edsm_shipyards_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_shipyards_max_age'))

    def edsm_outfitting_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_outfitting_max_age'))
    
    def edsm_traffic_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_traffic_max_age'))

    def edsm_deaths_max_age(self):
        return int(self.config.get('lrucaches', 'edsm_deaths_max_age'))

    def lru_max_size(self):
        return int(self.config.get('lrucaches', 'lru_max_size'))

    def edsm_within_radius_max_size(self):
        return int(self.config.get('lrucaches', 'edsm_within_radius_max_size'))

    def opponents_max_age(self, kind):
        ckind = kind.lower()
        return int(self.config.get(ckind, '{}_max_age'.format(ckind)))

    def opponents_max_recents(self, kind):
        ckind = kind.lower()
        return int(self.config.get(ckind, '{}_max_recents'.format(ckind)))

    def logging_level(self):
        return self.config.get('general', 'logging_level')

    def sitreps_timespan(self):
        return int(self.config.get('sitreps', 'sitreps_timespan'))

    def notams_timespan(self):
        return int(self.config.get('notams', 'notams_timespan'))

    def sitreps_max_age(self):
        return int(self.config.get('sitreps', 'sitreps_max_age'))

    def reports_check_interval(self):
        return int(self.config.get('sitreps', 'reports_check_interval'))

    def notams_check_interval(self):
        return int(self.config.get('notams', 'notams_check_interval'))

    def notams_max_age(self):
        return int(self.config.get('notams', 'notams_max_age'))

    def recon_recent_threshold(self):
        return int(self.config.get('sitreps', 'recon_recent_threshold'))

    def opponents_recent_threshold(self, kind):
        ckind = kind.lower()
        return int(self.config.get('sitreps', '{}_recent_threshold'.format(ckind)))

    def crimes_recent_threshold(self):
        return int(self.config.get('sitreps', 'crimes_recent_threshold'))

    def traffic_recent_threshold(self):
        return int(self.config.get('sitreps', 'traffic_recent_threshold'))

    def fc_reports_max_age(self):
        return int(self.config.get('fc', 'fc_reports_max_age'))

    def fc_presence_max_age(self):
        return int(self.config.get('fc', 'fc_presence_max_age'))

    def instance_fight_staleness_threshold(self):
        return int(self.config.get('instance', 'fight_staleness_threshold'))

    def instance_danger_staleness_threshold(self):
        return int(self.config.get('instance', 'danger_staleness_threshold'))

    def hpp_trend_span(self):
        return int(self.config.get('hpp', 'trend_span'))

    def hpp_history_max_points(self):
        return int(self.config.get('hpp', 'history_max_points'))
    
    def hpp_history_max_span(self):
        return int(self.config.get('hpp', 'history_max_span'))

EDR_CONFIG = EDRConfig()