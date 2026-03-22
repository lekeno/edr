import os
import configparser as cp

from .edrlog import EDR_LOG  # EDR_INTERNAL
from edr.utils.edrpath import plugin_root # EDR_INTERNAL


class IGMConfig:
    """
    Configuration handler for In-Game Message (IGM) layouts.
    """

    def __init__(self, config_file, user_config_file):
        """
        Initialize IGMConfig.

        Args:
            config_file (str): Path to the default configuration file.
            user_config_file (list): List of paths to user configuration files (priority order).
        """
        self.config = cp.ConfigParser()
        self.fallback_config = cp.ConfigParser()
        root = plugin_root()
        self.fallback_config.read(os.path.join(root, config_file))
        # TODO assumes that there is always 2 user config options...
        user_cfg_path = os.path.join(root, user_config_file[0])
        if os.path.exists(user_cfg_path):
            EDR_LOG.info(u"Using user defined layout at {}.".format(user_config_file[0]))
            self.config.read(user_cfg_path)
        else:
            EDR_LOG.info(u"No user defined layout at {}, using {} instead.".format(user_config_file[0], user_config_file[1]))
            user_cfg_path = os.path.join(root, user_config_file[1])
            if os.path.exists(user_cfg_path):
                EDR_LOG.info(u"Using user defined layout at {}.".format(user_config_file[1]))
                self.config.read(user_cfg_path)
            else:
                EDR_LOG.info(u"No user defined layout at {} or {}, using {} instead.".format(user_config_file[0], user_config_file[1], config_file))
                self.config = self.fallback_config

    def large_height(self):
        """
        Get the height for large display setting.

        Returns:
            float: Height value.
        """
        return self._getfloat('general', 'large_height', 28)

    def normal_height(self):
        """
        Get the height for normal display setting.

        Returns:
            float: Height value.
        """
        return self._getfloat('general', 'normal_height', 18)

    def large_width(self):
        """
        Get the width for large display setting.

        Returns:
            float: Width value.
        """
        return self._getfloat('general', 'large_width', 14)

    def normal_width(self):
        """
        Get the width for normal display setting.

        Returns:
            float: Width value.
        """
        return self._getfloat('general', 'normal_width', 8)

    def panel(self, kind):
        """
        Check if a panel type is enabled.

        Args:
            kind (str): The panel type.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self._getboolean(kind, 'panel', False)

    def getint(self, kind, part, variable, default=0):
        """
        Get an integer value from config.

        Args:
            kind (str): The category/kind.
            part (str): The part prefix.
            variable (str): The variable suffix.
            default (int): Default value if not found.

        Returns:
            int: The configuration value.
        """
        return self._getint(kind, '{}_{}'.format(part, variable), default)

    def x(self, kind, part):
        """
        Get X coordinate.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: X coordinate.
        """
        return self._getint(kind, '{}_x'.format(part))

    def y(self, kind, part):
        """
        Get Y coordinate.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: Y coordinate.
        """
        return self._getint(kind, '{}_y'.format(part))

    def x2(self, kind, part):
        """
        Get X2 coordinate.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: X2 coordinate.
        """
        return self._getint(kind, '{}_x2'.format(part))

    def y2(self, kind, part):
        """
        Get Y2 coordinate.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: Y2 coordinate.
        """
        return self._getint(kind, '{}_y2'.format(part))

    def h(self, kind, part):
        """
        Get Height.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: Height.
        """
        return self._getint(kind, '{}_h'.format(part))

    def w(self, kind, part):
        """
        Get Width.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: Width.
        """
        return self._getint(kind, '{}_w'.format(part))

    def s(self, kind, part):
        """
        Get spacing/size.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: Spacing/Size.
        """
        return self._getint(kind, '{}_s'.format(part))

    def ttl(self, kind, part):
        """
        Get Time-To-Live.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: TTL in seconds.
        """
        return self._getint(kind, '{}_ttl'.format(part), 5)

    def rgb(self, kind, part):
        """
        Get RGB color string.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            str: RGB string (e.g., "#ffffff").
        """
        return "#{}".format(self._get(kind, '{}_rgb'.format(part), "ffffff"))

    def rgb_list(self, kind, part):
        """
        Get list of RGB color strings.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            list: List of RGB strings.
        """
        rgbs = self._get(kind, '{}_rgb'.format(part), "ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff,ffffff")
        return ["#{}".format(rgb) for rgb in rgbs.split(",")]

    def fill_list(self, kind, part):
        """
        Get list of fill color strings.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            list: List of fill color strings.
        """
        fills = self._get(kind, '{}_fill'.format(part), "5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801,5B260801")
        return ["#{}".format(fill) for fill in fills.split(",")]

    def fill(self, kind, part):
        """
        Get fill color string.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            str: Fill color string.
        """
        return "#{}".format(self._get(kind, '{}_fill'.format(part), "5B260801"))

    def string_list(self, kind, part, name, fallback):
        """
        Get a list of strings split by comma.

        Args:
            kind (str): Category.
            part (str): Part name.
            name (str): Variable name.
            fallback (list): Fallback value.

        Returns:
            list: List of strings.
        """
        strings = self._get(kind, '{}_{}'.format(part, name), None)
        if strings:
            return strings.split(",")
        return fallback

    def size(self, kind, part):
        """
        Get size string.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            str: Size string (e.g. "normal").
        """
        return self._get(kind, '{}_size'.format(part), "normal")

    def len(self, kind, part):
        """
        Get length.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            int: Length.
        """
        return self._getint(kind, '{}_len'.format(part), 150)

    def align(self, kind, part):
        """
        Get alignment.

        Args:
            kind (str): Category.
            part (str): Part name.

        Returns:
            str: Alignment (e.g. "left").
        """
        return self._get(kind, '{}_align'.format(part), "left")

    def body_rows(self, kind):
        """
        Get number of body rows.

        Args:
            kind (str): Category.

        Returns:
            int: Number of rows.
        """
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
    def __init__(self, config_file='config/igm_config_spacelegs.v8.ini', user_config_file=['config/user_igm_config_spacelegs.v8.ini', 'config/igm_config_spacelegs.v7.ini', 'config/igm_config_spacelegs.v6.ini']):
        super().__init__(config_file, user_config_file)


class IGMConfigInShip(IGMConfig):
    def __init__(self, config_file='config/igm_config.v9.ini', user_config_file=['config/user_igm_config.v9.ini', 'config/user_igm_config.v8.ini', 'config/user_igm_config.v7.ini']):
        super().__init__(config_file, user_config_file)
