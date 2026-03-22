import os
import sys
import configparser as cp

from edr.core.edrlog import EDR_LOG
from edr.utils.edrpath import plugin_root, edr_sound_path


class SFXConfig:
    """
    Manages Sound Effects (SFX) configuration.
    Reads from default config and optionally a user overrides file.
    """

    def __init__(self, config_file, user_config_file):
        """
        Initialize the SFX configuration.

        Args:
            config_file (str): Path to the default configuration file.
            user_config_file (str): Path to the user override configuration file.
        """
        self.config = cp.ConfigParser()
        self.fallback_config = cp.ConfigParser()
        base_dir = plugin_root()
        self.fallback_config.read(os.path.join(base_dir, config_file))

        user_cfg_path = os.path.join(base_dir, user_config_file)
        if os.path.exists(user_cfg_path):
            EDR_LOG.info(f"Using user defined SFX at {user_config_file}.")
            self.config.read(user_cfg_path)
        else:
            EDR_LOG.info(f"No user defined SFX at {user_config_file}, using {config_file} instead.")
            self.config = self.fallback_config

    def snd(self, kind, loud=True):
        """
        Get the filename for a sound effect kind and loudness.

        Args:
            kind (str): The type of sound effect.
            loud (bool): Whether to retrieve the loud version.

        Returns:
            str: The filename of the sound effect, or None.
        """
        suffix = "" if loud else "_SOFT"
        return self._get(f"SFX{suffix}", kind, None)

    def _get(self, category, variable, default=""):
        """
        Get a configuration value safely.

        Args:
            category (str): The config section.
            variable (str): The config key.
            default (str): Default value if not found.

        Returns:
            str: The configuration value or default.
        """
        try:
            return self.config.get(category, variable)
        except (cp.NoSectionError, cp.NoOptionError):
            if self.fallback_config.has_option(category, variable):
                return self.fallback_config.get(category, variable)
            return default


# Platform-specific AudioFeedback implementation
if sys.platform == 'darwin':
    from AppKit import NSSound

    class AudioFeedback:
        """
        Audio feedback handler for macOS (Darwin).
        """
        def __init__(self, audio_filename):
            """
            Initialize audio feedback for macOS.

            Args:
                audio_filename (str): The filename of the audio file in the sounds directory.
            """
            self.snd = None
            if not audio_filename:
                return
            audio_file_path = edr_sound_path(audio_filename)
            if os.path.exists(audio_file_path):
                self.snd = NSSound.alloc().initWithContentsOfFile_byReference_(audio_file_path, False)

        def play(self):
            """Play the sound effect."""
            if self.snd:
                self.snd.play()

elif sys.platform == 'win32':
    import winsound

    class AudioFeedback:
        """
        Audio feedback handler for Windows.
        """
        def __init__(self, audio_filename):
            """
            Initialize audio feedback for Windows.

            Args:
                audio_filename (str): The filename of the audio file in the sounds directory.
            """
            self.snd = None
            if not audio_filename:
                return
            audio_file_path = edr_sound_path(audio_filename)
            if os.path.exists(audio_file_path):
                self.snd = audio_file_path

        def play(self):
            """Play the sound effect asynchronously."""
            if self.snd:
                winsound.PlaySound(self.snd, winsound.SND_ASYNC)

elif sys.platform.startswith('linux'):
    from playsound import playsound

    class AudioFeedback:
        """
        Audio feedback handler for Linux.
        """
        def __init__(self, audio_filename):
            """
            Initialize audio feedback for Linux.

            Args:
                audio_filename (str): The filename of the audio file in the sounds directory.
            """
            self.snd = None
            if not audio_filename:
                return
            audio_file_path = edr_sound_path(audio_filename)
            if os.path.exists(audio_file_path):
                self.snd = audio_file_path

        def play(self):
            """Play the sound effect."""
            if self.snd:
                try:
                    playsound(self.snd)
                except Exception:
                    pass  # Fail silently on Linux if playsound has issues

else:
    class AudioFeedback:
        """Dummy implementation for unsupported platforms."""
        def __init__(self, audio_filename):
            pass

        def play(self):
            pass


class EDRSoundEffects:
    """
    High-level interface for playing EDR sound effects.
    """

    def __init__(self, loud=True):
        """
        Initialize the sound effects interface.

        Args:
            loud (bool): Initialize with loud sound profile if True.
        """
        self.sfx_config = SFXConfig(config_file='config/sfx_config.v1.ini', user_config_file='config/user_sfx_config.v1.ini')
        self.kinds = [
            "startup", "intel", "warning", "sitrep", "notify", "help",
            "navigation", "docking", "mining", "bounty-hunting", "target",
            "searching", "failed", "jammed", "biology"
        ]
        self.sounds = {}
        self._load_sounds(loud)

    def _load_sounds(self, loud=True):
        """
        Load sound effects based on loudness setting.

        Args:
            loud (bool): Load loud versions if True.
        """
        self.sounds = {}
        for kind in self.kinds:
            audio_filename = self.sfx_config.snd(kind, loud)
            self.sounds[kind] = AudioFeedback(audio_filename)

    def loud(self):
        """Switch to loud sound effects."""
        self._load_sounds(loud=True)

    def soft(self):
        """Switch to soft sound effects."""
        self._load_sounds(loud=False)

    def startup(self):
        """Play startup sound."""
        self.__sfx("startup")

    def intel(self):
        """Play intel sound."""
        self.__sfx("intel")

    def warning(self):
        """Play warning sound."""
        self.__sfx("warning")

    def sitrep(self):
        """Play situation report sound."""
        self.__sfx("sitrep")

    def notify(self):
        """Play notification sound."""
        self.__sfx("notify")

    def help(self):
        """Play help sound."""
        self.__sfx("help")

    def navigation(self):
        """Play navigation sound."""
        self.__sfx("navigation")

    def biology(self):
        """Play biology sound."""
        self.__sfx("biology")

    def docking(self):
        """Play docking sound."""
        self.__sfx("docking")

    def mining(self):
        """Play mining sound."""
        self.__sfx("mining")

    def bounty_hunting(self):
        """Play bounty hunting sound."""
        self.__sfx("bounty-hunting")

    def target(self):
        """Play target sound."""
        self.__sfx("target")

    def failed(self):
        """Play failed sound."""
        self.__sfx("failed")

    def jammed(self):
        """Play jammed sound."""
        self.__sfx("jammed")

    def searching(self):
        """Play searching sound."""
        self.__sfx("searching")

    def __sfx(self, kind):
        """
        Internal method to play a sound by kind.

        Args:
            kind (str): The kind of sound to play.
        """
        sound = self.sounds.get(kind, None)
        if sound:
            sound.play()
