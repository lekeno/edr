import os
import ConfigParser

class EDRConfig(object):
    def __init__(self, config_file='config/config.ini'):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(
        os.path.abspath(os.path.dirname(__file__)), config_file))

    def edr_version(self):
        return self.config.get('general', 'version')
    
    def edr_api_key(self):
        return self.config.get('edr', 'edr_api_key')

    def edr_endpoint(self):
        return self.config.get('edr', 'edr_endpoint')

    def inara_api_key(self):
        return self.config.get('inara', 'inara_api_key')

    def inara_endpoint(self):
        return self.config.get('inara', 'inara_endpoint')

    def system_novelty_threshold(self):
        return int(self.config.get('novelty', 'system_novelty_threshold'))

    def place_novelty_threshold(self):
        return int(self.config.get('novelty', 'place_novelty_threshold'))

    def ship_novelty_threshold(self):
        return int(self.config.get('novelty', 'ship_novelty_threshold'))

    def systems_max_age(self):
        return int(self.config.get('lrucaches', 'systems_max_age'))

    def cmdrs_max_age(self):
        return int(self.config.get('lrucaches', 'cmdrs_max_age'))

    def inara_max_age(self):
        return int(self.config.get('lrucaches', 'inara_max_age'))

    def blips_max_age(self):
        return int(self.config.get('lrucaches', 'blips_max_age'))

    def traffic_max_age(self):
        return int(self.config.get('lrucaches', 'traffic_max_age'))

    def friends_max_age(self):
        return int(self.config.get('lrucaches', 'friends_max_age'))

    def lru_max_size(self):
        return int(self.config.get('lrucaches', 'lru_max_size'))

    def logging_level(self):
        return self.config.get('general', 'logging_level')