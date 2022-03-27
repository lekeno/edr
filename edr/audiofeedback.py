from __future__ import absolute_import

from sys import platform
import os.path

import utils2to3
import os
import configparser as cp

from edrlog import EDRLog

class EDRSoundEffects(object):
    def __init__(self, loud=True):
        self.sfx_config = SFXConfig(config_file='config/sfx_config.v1.ini', user_config_file='config/user_sfx_config.v1.ini')
        self.kinds = ["startup", "intel", "warning", "sitrep", "notify", "help", "navigation", "docking", "mining", "bounty-hunting", "target", "searching", "failed", "jammed"]
        self.sounds = {}
        for kind in self.kinds:
            audio_filename = self.sfx_config.snd(kind, loud)
            self.sounds[kind] = AudioFeedback(audio_filename)
    
    def loud(self):
        self.sounds = {}
        for kind in self.kinds:
            audio_filename = self.sfx_config.snd(kind, loud=True)
            self.sounds[kind] = AudioFeedback(audio_filename)

    def soft(self):
        self.sounds = {}
        for kind in self.kinds:
            audio_filename = self.sfx_config.snd(kind, loud=False)
            self.sounds[kind] = AudioFeedback(audio_filename)

    def startup(self):
        self.__sfx("startup")

    def intel(self):
        self.__sfx("intel")

    def warning(self):
        self.__sfx("warning")

    def sitrep(self):
        self.__sfx("sitrep")

    def notify(self):
        self.__sfx("notify")

    def help(self):
        self.__sfx("help")

    def navigation(self):
        self.__sfx("navigation")

    def docking(self):
        self.__sfx("docking")

    def mining(self):
        self.__sfx("mining")

    def bounty_hunting(self):
        self.__sfx("bounty-hunting")

    def target(self):
        self.__sfx("target")

    def failed(self):
        self.__sfx("failed")

    def jammed(self):
        self.__sfx("jammed")

    def searching(self):
        self.__sfx("searching")

    def __sfx(self, kind):
        sound = self.sounds.get(kind, None)
        if sound:
            sound.play()


class SFXConfig(object):
    def __init__(self, config_file, user_config_file):
        self.config = cp.ConfigParser()
        self.fallback_config = cp.ConfigParser()
        self.fallback_config.read(utils2to3.abspathmaker(__file__, config_file))
        user_cfg_path = utils2to3.abspathmaker(__file__, user_config_file)
        if os.path.exists(user_cfg_path):
            EDRLog().log(u"Using user defined SFX at {}.".format(user_config_file), "INFO")
            self.config.read(user_cfg_path)
        else:
            EDRLog().log(u"No user defined SFX at {}, using {} instead.".format(user_config_file, config_file), "INFO")
            self.config = self.fallback_config

    def snd(self, kind, loud=True):
        suffix = "" if loud else "_SOFT"
        return self._get("SFX{}".format(suffix), kind, None)

    def _get(self, category, variable, default=""):
        try:
            return self.config.get(category, variable)
        except:
            if self.fallback_config.has_option(category, variable):
                return self.fallback_config.get(category, variable)
            else:
                return default


if platform == 'darwin':

    from AppKit import NSSound

    class AudioFeedback(object):
        def __init__(self, audio_filename):
            self.snd = None
            if not audio_filename:
                return
            audio_file_path = utils2to3.abspathmaker(__file__, 'sounds', audio_filename)
            if os.path.exists(audio_file_path):
                self.snd = NSSound.alloc().initWithContentsOfFile_byReference_(audio_file_path, False)
            
        def play(self):
            if self.snd:
                self.snd.play()

elif platform == 'win32':
    import winsound

    class AudioFeedback(object):
        def __init__(self, audio_filename):
            self.snd = None
            if not audio_filename:
                return
            audio_file_path = utils2to3.abspathmaker(__file__, 'sounds', audio_filename)
            if os.path.exists(audio_file_path):
                self.snd = audio_file_path

        def play(self):
            if self.snd:
                winsound.PlaySound(self.snd, winsound.SND_ASYNC)


elif platform == 'linux':
    from playsound import playsound

    class AudioFeedback(object):
        def __init__(self, audio_filename):
            self.snd = None
            if not audio_filename:
                return
            audio_file_path = utils2to3.abspathmaker(__file__, 'sounds', audio_filename)
            if os.path.exists(audio_file_path):
                self.snd = audio_file_path

        def play(self):
            if self.snd:
                playsound(self.snd)