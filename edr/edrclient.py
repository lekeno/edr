import os
import pickle

import Tkinter as tk
import ttk
import myNotebook as notebook
from config import config
import edrconfig

import lrucache
import edentities
import edrserver
import edrinara
import audiofeedback
import edrlog
import ingamemsg
import edrsystems

EDRLOG = edrlog.EDRLog()

class EDRClient(object):
    EDR_CMDRS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/cmdrs.p')
    EDR_INARA_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/inara.p')

    IN_GAME_MSG = ingamemsg.InGameMsg()
    AUDIO_FEEDBACK = audiofeedback.AudioFeedback()

    def __init__(self):
        edr_config = edrconfig.EDRConfig()

        self.edr_version = edr_config.edr_version()

        self.system_novelty_threshold = edr_config.system_novelty_threshold()
        self.place_novelty_threshold = edr_config.place_novelty_threshold()
        self.ship_novelty_threshold = edr_config.ship_novelty_threshold()

        try:
            with open(self.EDR_CMDRS_CACHE, 'rb') as handle:
                self.cmdrs_cache = pickle.load(handle)
        except IOError:
            #TODO increase after there is a good set of cmdrs in the backend
            self.cmdrs_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.cmdrs_max_age())

        try:
            with open(self.EDR_INARA_CACHE, 'rb') as handle:
                self.inara_cache = pickle.load(handle)
        except IOError:
            self.inara_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                 edr_config.inara_max_age())

        self.blips_cache = lrucache.LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.traffic_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                               edr_config.traffic_max_age())

        self._email = tk.StringVar(value=config.get("EDREmail"))
        self._password = tk.StringVar(value=config.get("EDRPassword"))
        self._status = tk.StringVar(value="not authenticated.")

        visual = 1 if config.get("EDRVisualFeedback") == "True" else 0
        self._visual_feedback = tk.IntVar(value=visual)

        audio = 1 if config.get("EDRAudioFeedback") == "True" else 0
        self._audio_feedback = tk.IntVar(value=audio)

        self.player = edentities.EDCmdr()
        self.server = edrserver.EDRServer()
        self.edrsystems = edrsystems.EDRSystems(self.server)
        self.inara = edrinara.EDRInara()
        self.mandatory_update = False
        self.crimes_reporting = True
        self.motd = []

    def loud_audio_feedback(self):
        config.set("EDRAudioFeedbackVolume", "loud")
        self.AUDIO_FEEDBACK.loud()
        self.status = "loud audio cues."

    def soft_audio_feedback(self):
        config.set("EDRAudioFeedbackVolume", "soft")
        self.AUDIO_FEEDBACK.soft()
        self.status = "soft audio cues."

    def apply_config(self):
        c_email = config.get("EDREmail")
        c_password = config.get("EDRPassword")
        c_visual_feedback = config.get("EDRVisualFeedback")
        c_audio_feedback = config.get("EDRAudioFeedback")
        c_audio_volume = config.get("EDRAudioFeedbackVolume")

        if c_email is None:
            self._email.set("")
        else:
            self._email.set(c_email)

        if c_password is None:
            self._password.set("")
        else:
            self._password.set(c_password)

        if c_visual_feedback is None or c_visual_feedback == "False":
            self._visual_feedback.set(0)
        else:
            self._visual_feedback.set(1)

        if c_audio_feedback is None or c_audio_feedback == "False":
            self._audio_feedback.set(0)
        else:
            self._audio_feedback.set(1)

        if c_audio_volume is None or c_audio_volume == "loud":
            self.loud_audio_feedback()
        else:
            self.soft_audio_feedback()


    def check_version(self):
        version_range = self.server.server_version()
        self.motd = version_range["motd"]

        if version_range is None:
            self.status = "check for version update has failed."
            return

        if self.is_obsolete(version_range["min"]):
            self.status = "mandatory EDR update!"
            EDRLOG.log(u"Mandatory update! {version} vs. {min}"
                       .format(version=self.edr_version, min=version_range["min"]), "ERROR")
            self.mandatory_update = True
        elif self.is_obsolete(version_range["latest"]):
            self.status = "please update EDR."
            EDRLOG.log(u"EDR update available! {version} vs. {latest}"
                       .format(version=self.edr_version, latest=version_range["latest"]), "INFO")
            self.mandatory_update = False

    def is_obsolete(self, advertised_version):
        client_parts = map(int, self.edr_version.split('.'))
        advertised_parts = map(int, advertised_version.split('.'))
        return client_parts < advertised_parts

    @property
    def email(self):
        return self._email.get()

    @email.setter
    def email(self, new_email):
        self._email.set(new_email)

    @property
    def password(self):
        return self._password.get()

    @password.setter
    def password(self, new_password):
        self._password.set(new_password)

    @property
    def status(self):
        return self._status.get()

    @status.setter
    def status(self, new_status):
        self._status.set(new_status)

    @property
    def visual_feedback(self):
        return self._visual_feedback.get() == 1

    @visual_feedback.setter
    def visual_feedback(self, new_value):
        self._visual_feedback.set(new_value)

    @property
    def audio_feedback(self):
        return self._audio_feedback.get() == 1

    @audio_feedback.setter
    def audio_feedback(self, new_value):
        self._audio_feedback.set(new_value)

    def player_name(self, name):
        self.inara.cmdr_name = name
        self.player.name = name

    def login(self):
        self.server.logout()
        if self.server.login(self.email, self.password):
            self.status = "authenticated."
            return True
        self.status = "not authenticated."
        return False

    def is_logged_in(self):
        return self.server.is_authenticated()

    def warmup(self):
        EDRLOG.log(u"Warming up client.", "INFO")
        details = ["by LeKeno (Cobra Kai)",
                   "",
                   "...warming up overlay...",
                   "Please check that ED has the focus."]
        if self.mandatory_update:
            details[1] = "Mandatory update pending!"
        details += self.motd
        self.__notify("EDR v{}".format(self.edr_version), details)

    def shutdown(self):
        self.write_caches()
        self.edrsystems.persist()
        self.server.logout()
        self.IN_GAME_MSG.shutdown()
        self.player.persist()

    def app_ui(self, parent):
        label = tk.Label(parent, text="EDR:")
        status = tk.Label(parent, textvariable=self._status, anchor=tk.W)
        return (label, status)

    def prefs_ui(self, parent):
        frame = notebook.Frame(parent)
        frame.columnconfigure(1, weight=1)

        notebook.Label(frame, text='Credentials').grid(padx=10, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        cred_label = notebook.Label(frame, text='Please log in with your EDR account details')
        cred_label.grid(padx=10, columnspan=2, sticky=tk.W)

        notebook.Label(frame, text="Email").grid(padx=10, row=11, sticky=tk.W)
        notebook.Entry(frame, textvariable=self._email).grid(padx=10, row=11,
                                                             column=1, sticky=tk.EW)

        notebook.Label(frame, text="Password").grid(padx=10, row=12, sticky=tk.W)
        notebook.Entry(frame, textvariable=self._password,
                       show=u'*').grid(padx=10, row=12, column=1, sticky=tk.EW)

        notebook.Label(frame, text="EDR Feedback:").grid(padx=10, row=13, sticky=tk.W)
        notebook.Checkbutton(frame, text="Overlay (windowed/borderless)",
                             variable=self._visual_feedback).grid(padx=10, row=14,
                                                                  sticky=tk.W)
        notebook.Checkbutton(frame, text="Sound",
                             variable=self._audio_feedback).grid(padx=10, row=15, sticky=tk.W)

        if self.server.is_authenticated():
            self.status = "authenticated."
        else:
            self.status = "not authenticated."

        return frame

    def prefs_changed(self):
        if self.mandatory_update:
            print EDRLOG.log(u"Out-of-date client, aborting.", "ERROR")
            self.status = "mandatory EDR update!"
            return

        config.set("EDREmail", self.email)
        config.set("EDRPassword", self.password)
        config.set("EDRVisualFeedback", "True" if self.visual_feedback else "False")
        config.set("EDRAudioFeedback", "True" if self.audio_feedback else "False")
        EDRLOG.log(u"Audio cues: {}, {}".format(config.get("EDRAudioFeedback"),
                                                config.get("EDRAudioFeedbackVolume")), "DEBUG")
        self.login()

    def check_system(self, star_system):
        EDRLOG.log(u"Check system called: {}".format(star_system), "INFO")
        details = []
        notams = self.edrsystems.active_notams(star_system)
        if not notams is None:
            EDRLOG.log(u"NOTAMs for {}: {}".format(star_system, notams), "DEBUG")
            details += notams
        
        if not self.edrsystems.has_sitrep(star_system):
            EDRLOG.log(u"No sitrep for {system}".format(system=star_system), "INFO")
            details += ["No reports for the last {d}.".format(d=self.edrsystems.timespan_s()),
                       "Recon this system: tag any suspicious contacts by sending them an o7."]
        else:
            if self.edrsystems.has_recent_crimes(star_system):
                EDRLOG.log(u"Recent crime for {system}".format(system=star_system), "INFO")
                details += [u"Crime reported {}".format(self.edrsystems.crimes_t_minus(star_system))]
            if self.edrsystems.has_recent_traffic(star_system):
                EDRLOG.log(u"Recent traffic for {system}".format(system=star_system), "INFO")
                t_minus = self.edrsystems.traffic_t_minus(star_system)
                details += [u"Traffic reported {}".format(t_minus)]        
        if details:
            self.__sitrep(star_system, details)
            summary = self.edrsystems.summarize_recent_activity(star_system)
            for section in summary:
                details.append(u"{}: {}".format(section, "; ".join(summary[section])))
            self.__sitrep(star_system, details)

        return False

    def cmdr_id(self, cmdr_name):
        profile = self.cmdr(cmdr_name, check_inara_server=False)
        if not (profile is None or profile.cid is None):
            EDRLOG.log(u"Cmdr {cmdr} known as id={cid}".format(cmdr=cmdr_name,
                                                               cid=profile.cid), "DEBUG")
            return profile.cid

        EDRLOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
        return None

    def cmdr(self, cmdr_name, autocreate=True, check_inara_server=False):
        profile = self.cmdrs_cache.get(cmdr_name)
        if not profile is None:
            EDRLOG.log(u"Cmdr {cmdr} is in the cache with id={cid}".format(cmdr=cmdr_name,
                                                                           cid=profile.cid),
                       "DEBUG")
        else:
            profile = self.server.cmdr(cmdr_name, autocreate)

            if not profile is None:
                self.cmdrs_cache.set(cmdr_name, profile)
                EDRLOG.log(u"Cached {cmdr} with id={id}".format(cmdr=cmdr_name,
                                                                id=profile.cid), "DEBUG")

        inara_profile = self.inara_cache.get(cmdr_name)
        if not inara_profile is None:
            EDRLOG.log(u"Cmdr {} is in the Inara cache (name={})".format(cmdr_name,
                                                                         inara_profile.name),
                       "DEBUG")
        elif check_inara_server:
            EDRLOG.log(u"No match in Inara cache. Inara API call for {}.".format(cmdr_name), "INFO")
            inara_profile = self.inara.cmdr(cmdr_name)

            if not inara_profile is None:
                self.inara_cache.set(cmdr_name, inara_profile)
                EDRLOG.log(u"Cached Inara profile {}: {},{},{}".format(cmdr_name,
                                                                       inara_profile.name,
                                                                       inara_profile.squadron,
                                                                       inara_profile.role), "DEBUG")
            else:
                self.inara_cache.set(cmdr_name, None)
                EDRLOG.log(u"No match on Inara. Temporary entry to be nice on Inara's server.",
                           "INFO")

        if profile is None and inara_profile is None:
            EDRLOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
            return None
        elif (not profile is None) and (not inara_profile is None):
            EDRLOG.log(u"Combining info from EDR and Inara for cmdr {}".format(cmdr_name), "INFO")
            profile.complement(inara_profile)
            return profile
        return inara_profile if profile is None else profile

    def write_caches(self):
        with open(self.EDR_CMDRS_CACHE, 'wb') as handle:
            pickle.dump(self.cmdrs_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_INARA_CACHE, 'wb') as handle:
            pickle.dump(self.inara_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)


    def evict_system(self, star_system):
        self.edrsystems.evict(star_system)

    def evict_cmdr(self, cmdr):
        try:
            del self.cmdrs_cache[cmdr]
        except KeyError:
            pass

        try:
            del self.inara_cache[cmdr]
        except KeyError:
            pass


    def novel_enough_blip(self, cmdr_id, blip):
        last_blip = self.blips_cache.get(cmdr_id)
        if last_blip is None:
            return True

        delta = blip["timestamp"] - last_blip["timestamp"]

        if blip["starSystem"] != last_blip["starSystem"]:
            return delta > self.system_novelty_threshold

        if blip["place"] != last_blip["place"]:
            return (last_blip["place"] == "" or
                    last_blip["place"] == "Unknown" or
                    delta > self.place_novelty_threshold)

        if blip["ship"] != last_blip["ship"]:
            return (last_blip["ship"] == "" or
                    last_blip["ship"] == "Unknown" or
                    delta > self.ship_novelty_threshold)

    def novel_enough_traffic_report(self, sighted_cmdr, report):
        last_report = self.traffic_cache.get(sighted_cmdr)
        if last_report is None:
            return True

        delta = report["timestamp"] - last_report["timestamp"]

        if report["starSystem"] != last_report["starSystem"]:
            return delta > self.system_novelty_threshold

        if report["place"] != last_report["place"]:
            return (last_report["place"] == "" or
                    last_report["place"] == "Unknown" or
                    delta > self.place_novelty_threshold)

        if report["ship"] != last_report["ship"]:
            return (last_report["ship"] == "" or
                    last_report["ship"] == "Unknown" or
                    delta > self.ship_novelty_threshold)

    def who(self, cmdr_name):
        profile = self.cmdr(cmdr_name, autocreate=False, check_inara_server=True)
        if not profile is None:
            self.status = "got info about {}".format(cmdr_name)
            EDRLOG.log(u"Who {} : {}".format(cmdr_name, profile.short_profile()), "INFO")
            self.__intel(cmdr_name, [profile.short_profile()])
        else:
            EDRLOG.log(u"Who {} : no info".format(cmdr_name), "INFO")
            self.__intel(cmdr_name, ["No info about {}".format(cmdr_name)])

    def blip(self, cmdr_name, blip):
        cmdr_id = self.cmdr_id(cmdr_name)
        if cmdr_id is None:
            self.status = "no cmdr id (contact)."
            EDRLOG.log(u"Can't submit blip (no cmdr id for {}).".format(cmdr_name), "ERROR")
            return

        profile = self.cmdr(cmdr_name)
        if (not profile is None) and (self.player.name != cmdr_name) and profile.is_dangerous():
            self.status = "{} is bad news.".format(cmdr_name)
            self.__warning(u"Warning!", [profile.short_profile()])

        if not self.novel_enough_blip(cmdr_id, blip):
            self.status = "skipping blip (not novel enough)."
            EDRLOG.log(u"Blip is not novel enough to warrant reporting", "INFO")
            return True

        success = self.server.blip(cmdr_id, blip)
        if success:
            self.status = "blip reported for {}.".format(cmdr_name)
            self.blips_cache.set(cmdr_id, blip)

        return success


    def traffic(self, star_system, traffic):
        sigthed_cmdr = traffic["cmdr"]
        if not self.novel_enough_traffic_report(sigthed_cmdr, traffic):
            self.status = "traffic report isn't novel enough."
            EDRLOG.log(u"Traffic report is not novel enough to warrant reporting", "INFO")
            return True

        sid = self.edrsystems.system_id(star_system)
        if sid is None:
            EDRLOG.log(u"Failed to report traffic for system {} : no id found.".format(star_system),
                       "DEBUG")
            return False

        success = self.server.traffic(sid, traffic)
        if success:
            self.status = "traffic reported."
            self.traffic_cache.set(sigthed_cmdr, traffic)

        return success


    def crime(self, star_system, crime):
        if not self.crimes_reporting:
            return False

        sid = self.edrsystems.system_id(star_system)
        if sid is None:
            EDRLOG.log(u"Failed to report crime in system {} : no id found.".format(star_system),
                       "DEBUG")
            return False

        return self.server.crime(sid, crime)

    def __sitrep(self, star_system, details):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.notify()
        if not self.visual_feedback:
            return
        EDRLOG.log(u"sitrep for {}; details: {}".format(star_system, details[0]), "DEBUG")
        self.IN_GAME_MSG.sitrep(u"SITREP for {}".format(star_system), details)

    def __intel(self, who, details):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.notify()
        if not self.visual_feedback:
            return
        EDRLOG.log(u"Intel for {}; details: {}".format(who, details[0]), "DEBUG")
        self.IN_GAME_MSG.intel(u"Intel", details)

    def __warning(self, header, details):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.warn()
        if not self.visual_feedback:
            return
        EDRLOG.log(u"Warning; details: {}".format(details[0]), "DEBUG")
        self.IN_GAME_MSG.warning(header, details)
    
    def __notify(self, header, details):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.notify()
        if not self.visual_feedback:
            return
        EDRLOG.log(u"Notify about {}; details: {}".format(header, details[0]), "DEBUG")
        self.IN_GAME_MSG.notify(header, details)

    def notify_with_details(self, notice, details):
        self.__notify(notice, details)

    def warn_with_details(self, warning, details):
        self.__warning(warning, details)
