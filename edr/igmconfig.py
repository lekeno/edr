import os
import ConfigParser

class IGMConfig(object):
    def __init__(self, config_file='config/igm_config.ini'):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), config_file))

    def large_height(self):
        return self.config.getfloat('general', 'large_height')

    def normal_height(self):
        return self.config.getfloat('general', 'normal_height')

    def large_width(self):
        return self.config.getfloat('general', 'large_width')

    def normal_width(self):
        return self.config.getfloat('general', 'normal_width')

    def x(self, kind, part):
        return self.config.getint(kind, '{}_x'.format(part))

    def y(self, kind, part):
        return self.config.getint(kind, '{}_y'.format(part))

    def ttl(self, kind, part):
        return self.config.getint(kind, '{}_ttl'.format(part))

    def rgb(self, kind, part):
        return "#{}".format(self.config.get(kind, '{}_rgb'.format(part)))

    def size(self, kind, part):
        return self.config.get(kind, '{}_size'.format(part))

    def len(self, kind, part):
        return self.config.getint(kind, '{}_len'.format(part))

    def align(self, kind, part):
        return self.config.get(kind, '{}_align'.format(part))

    def body_rows(self, kind):
        return self.config.getint(kind, 'body_rows')
