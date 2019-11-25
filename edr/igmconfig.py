from __future__ import absolute_import

import os
from six.moves.configparser import ConfigParser
from .edrlog import EDRLog

class IGMConfig(object):
    def __init__(self, config_file='config/igm_config.v2.ini', user_config_file='config/user_igm_config.v2.ini'):
        self.config = ConfigParser.ConfigParser()
        self.fallback_config = ConfigParser.ConfigParser()
        self.fallback_config.read(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), config_file))
        user_cfg_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), user_config_file)
        if os.path.exists(user_cfg_path):
            EDRLog().log(u"Using user defined layout at {}.".format(user_config_file), "INFO")
            self.config.read(user_cfg_path)
        else:
            EDRLog().log(u"No user defined layout at {}, using {} instead.".format(user_config_file, config_file), "INFO")
            self.config = self.fallback_config

    def large_height(self):
        return self._getfloat('general', 'large_height')

    def normal_height(self):
        return self._getfloat('general', 'normal_height')

    def large_width(self):
        return self._getfloat('general', 'large_width')

    def normal_width(self):
        return self._getfloat('general', 'normal_width')

    def panel(self, kind):
        return self._getboolean(kind, 'panel')

    def x(self, kind, part):
        return self._getint(kind, '{}_x'.format(part))

    def y(self, kind, part):
        return self._getint(kind, '{}_y'.format(part))

    def x2(self, kind, part):
        return self._getint(kind, '{}_x2'.format(part))

    def y2(self, kind, part):
        return self._getint(kind, '{}_y2'.format(part))

    def ttl(self, kind, part):
        return self._getint(kind, '{}_ttl'.format(part))

    def rgb(self, kind, part):
        return "#{}".format(self._get(kind, '{}_rgb'.format(part)))

    def fill(self, kind, part):
        return "#{}".format(self._get(kind, '{}_fill'.format(part)))

    def size(self, kind, part):
        return self._get(kind, '{}_size'.format(part))

    def len(self, kind, part):
        return self._getint(kind, '{}_len'.format(part))

    def align(self, kind, part):
        return self._get(kind, '{}_align'.format(part))

    def body_rows(self, kind):
        return self._getint(kind, 'body_rows')

    def _get(self, category, variable):
        try:
            return self.config.get(category, variable)
        except:
            return self.fallback_config.get(category, variable)
    
    def _getfloat(self, category, variable):
        try:
            return self.config.getfloat(category, variable)
        except:
            return self.fallback_config.getfloat(category, variable)

    def _getboolean(self, category, variable):
        try:
            return self.config.getboolean(category, variable)
        except:
            return self.fallback_config.getboolean(category, variable)

    def _getint(self, category, variable):
        try:
            return self.config.getint(category, variable)
        except:
            return self.fallback_config.getint(category, variable)
