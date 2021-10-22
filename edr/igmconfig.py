from __future__ import absolute_import

import os
try:
    # for Python2
    import ConfigParser as cp
except ImportError:
    # for Python3
    import configparser as cp

from edrlog import EDRLog
import utils2to3

class IGMConfig(object):
    def __init__(self, config_file, user_config_file):
        self.config = cp.ConfigParser()
        self.fallback_config = cp.ConfigParser()
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
        return self._getfloat('general', 'large_height', 28)

    def normal_height(self):
        return self._getfloat('general', 'normal_height', 18)

    def large_width(self):
        return self._getfloat('general', 'large_width', 14)

    def normal_width(self):
        return self._getfloat('general', 'normal_width', 8)

    def panel(self, kind):
        return self._getboolean(kind, 'panel', False)

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
        return self._getint(kind, '{}_ttl'.format(part), 5)

    def rgb(self, kind, part):
        return "#{}".format(self._get(kind, '{}_rgb'.format(part)), "ffffff")

    def rgb_list(self, kind, part):
        rgbs = self._get(kind, '{}_rgb'.format(part), "ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff")
        return [ "#{}".format(rgb) for rgb in rgbs.split(",") ]

    def fill_list(self, kind, part):
        fills = self._get(kind, '{}_fill'.format(part), "5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801")
        return [ "#{}".format(fill) for fill in fills.split(",") ]

    def fill(self, kind, part):
        return "#{}".format(self._get(kind, '{}_fill'.format(part), "5B260801"))

    def size(self, kind, part):
        return self._get(kind, '{}_size'.format(part), "normal")

    def len(self, kind, part):
        return self._getint(kind, '{}_len'.format(part), 150)

    def align(self, kind, part):
        return self._get(kind, '{}_align'.format(part), "left")

    def body_rows(self, kind):
        return self._getint(kind, 'body_rows', 5)

    def _get(self, category, variable, default=""):
        try:
            return self.config.get(category, variable)
        except:
            if self.fallback_config.has_option(category, variable):
                return self.fallback_config.get(category, variable)
            else:
                return default
    
    def _getfloat(self, category, variable, default=0.0):
        try:
            return self.config.getfloat(category, variable)
        except:
            if self.fallback_config.has_option(category, variable):
                return self.fallback_config.getfloat(category, variable)
            else:
                return default

    def _getboolean(self, category, variable, default=False):
        try:
            return self.config.getboolean(category, variable)
        except:
            if self.fallback_config.has_option(category, variable):
                return self.fallback_config.getboolean(category, variable)
            else:
                return default

    def _getint(self, category, variable, default=0):
        try:
            return self.config.getint(category, variable)
        except:
            if self.fallback_config.has_option(category, variable):
                return self.fallback_config.getint(category, variable)
            else:
                return default

class IGMConfigOnFoot(IGMConfig):
    def __init__(self, config_file='config/igm_config_spacelegs.v7.ini', user_config_file=['config/user_igm_config_spacelegs.v7.ini']):
        super(IGMConfigOnFoot, self).__init__(config_file, user_config_file)
        
class IGMConfigInShip(IGMConfig):
    def __init__(self, config_file='config/igm_config.v7.ini', user_config_file=['config/user_igm_config.v7.ini', 'config/user_igm_config.v6.ini']):
        super(IGMConfigInShip, self).__init__(config_file, user_config_file)
