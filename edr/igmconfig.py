from __future__ import absolute_import

import os
from ConfigParser import ConfigParser
from edrlog import EDRLog
import utils2to3

class IGMConfig(object):
    def __init__(self, config_file='config/igm_config.v5.ini', user_config_file=['config/user_igm_config.v5.ini', 'config/user_igm_config.v4.ini']):
        self.config = ConfigParser()
        self.fallback_config = ConfigParser()
        self.fallback_config.read(utils2to3.abspathmaker(__file__, config_file))
        user_cfg_path = utils2to3.abspathmaker(__file__, user_config_file[0])
        if os.path.exists(user_cfg_path):
            EDRLog().log(u"Using user defined layout at {}.".format(user_config_file[0]), "INFO")
            self.config.read(user_cfg_path)
        else:
            EDRLog().log(u"No user defined layout at {}, using {} instead.".format(user_config_file[0], user_config_file[1]), "INFO")
            user_cfg_path = utils2to3.abspathmaker(__file__, user_config_file[1])
            if os.path.exists(user_cfg_path):
                EDRLog().log(u"Using user defined layout at {}.".format(user_config_file[1]), "INFO")
                self.config.read(user_cfg_path)
            else:
                EDRLog().log(u"No user defined layout at {} or {}, using {} instead.".format(user_config_file[0], user_config_file[1], config_file), "INFO")
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

    def h(self, kind, part):
        return self._getint(kind, '{}_h'.format(part))

    def w(self, kind, part):
        return self._getint(kind, '{}_w'.format(part))

    def s(self, kind, part):
        return self._getint(kind, '{}_s'.format(part))

    def ttl(self, kind, part):
        return self._getint(kind, '{}_ttl'.format(part))

    def rgb(self, kind, part):
        return "#{}".format(self._get(kind, '{}_rgb'.format(part)))

    def rgb_list(self, kind, part):
        rgbs = self._get(kind, '{}_rgb'.format(part))
        return [ "#{}".format(rgb) for rgb in rgbs.split(",") ]

    def fill_list(self, kind, part):
        fills = self._get(kind, '{}_fill'.format(part))
        return [ "#{}".format(fill) for fill in fills.split(",") ]

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
