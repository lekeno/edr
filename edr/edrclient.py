# coding= utf-8
from __future__ import absolute_import
#from builtins import map, filter

import datetime
import time
import random
import math

#import tkinter as tk
import Tkinter as tk
import ttk
import ttkHyperlinkLabel
import myNotebook as notebook
from config import config

from edrconfig import EDRConfig
from lrucache import LRUCache
from edentities import EDPlanetaryLocation, EDFineOrBounty, EDLocation
from edrserver import EDRServer, CommsJammedError
from audiofeedback import AudioFeedback
from edrlog import EDRLog
from ingamemsg import InGameMsg
from edrtogglingpanel import EDRTogglingPanel
from edrsystems import EDRSystems
from edrresourcefinder import EDRResourceFinder
from edrbodiesofinterest import EDRBodiesOfInterest
from edrcmdrs import EDRCmdrs
from edropponents import EDROpponents
from randomtips import RandomTips
from helpcontent import HelpContent
from edtime import EDTime
from edrlegalrecords import EDRLegalRecords
from edrxzibit import EDRXzibit

from edri18n import _, _c, _edr, set_language
from clippy import copy

EDRLOG = EDRLog()

class EDRClient(object):
    AUDIO_FEEDBACK = AudioFeedback()

    def __init__(self):
        edr_config = EDRConfig()
        set_language(config.get("language"))

        self.edr_version = edr_config.edr_version()
        EDRLOG.log(u"Version {}".format(self.edr_version), "INFO")

        self.enemy_alerts_pledge_threshold = edr_config.enemy_alerts_pledge_threshold()
        self.system_novelty_threshold = edr_config.system_novelty_threshold()
        self.place_novelty_threshold = edr_config.place_novelty_threshold()
        self.ship_novelty_threshold = edr_config.ship_novelty_threshold()
        self.cognitive_novelty_threshold = edr_config.cognitive_novelty_threshold()
        self.intel_even_if_clean = edr_config.intel_even_if_clean()
        
        self.edr_needs_u_novelty_threshold = edr_config.edr_needs_u_novelty_threshold()
        self.previous_ad = None

        self.searching = False

        self.blips_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.cognitive_blips_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.traffic_cache = LRUCache(edr_config.lru_max_size(), edr_config.traffic_max_age())
        self.scans_cache = LRUCache(edr_config.lru_max_size(), edr_config.scans_max_age())
        self.cognitive_scans_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.alerts_cache = LRUCache(edr_config.lru_max_size(), edr_config.alerts_max_age())
        self.fights_cache = LRUCache(edr_config.lru_max_size(), edr_config.fights_max_age())

        self._email = tk.StringVar(value=config.get("EDREmail"))
        self._password = tk.StringVar(value=config.get("EDRPassword"))
        # Translators: this is shown on the EDMC's status line
        self._status = tk.StringVar(value=_(u"not authenticated."))
        
        visual = 1 if config.get("EDRVisualFeedback") == "True" else 0
        self.IN_GAME_MSG = InGameMsg() if visual else None
        self._visual_feedback = tk.IntVar(value=visual)

        visual_alt = 1 if config.get("EDRVisualAltFeedback") == "True" else 0
        self._visual_alt_feedback = tk.IntVar(value=visual_alt)
        
        self.ui = EDRTogglingPanel(self._status, self._visual_alt_feedback)

        audio = 1 if config.get("EDRAudioFeedback") == "True" else 0
        self._audio_feedback = tk.IntVar(value=audio)

        self.server = EDRServer()

        anonymous_reports = _(u"Auto")
        self.server.anonymous_reports = None
        if config.get("EDRRedactMyInfo") in [_(u"Always"), _(U"Never")]:
            anonymous_reports = config.get("EDRRedactMyInfo")
            self.server.anonymous_reports = anonymous_reports == _(u"Always")
        self._anonymous_reports = tk.StringVar(value=anonymous_reports)

        
        self.realtime_params = {
            EDROpponents.OUTLAWS: { "min_bounty": None if config.get("EDROutlawsAlertsMinBounty") == "None" else config.getint("EDROutlawsAlertsMinBounty"),
                         "max_distance": None if config.get("EDROutlawsAlertsMaxDistance") == "None" else config.getint("EDROutlawsAlertsMaxDistance")},
            EDROpponents.ENEMIES: { "min_bounty": None if config.get("EDREnemiesAlertsMinBounty") == "None" else config.getint("EDREnemiesAlertsMinBounty"),
                         "max_distance": None if config.get("EDREnemiesAlertsMaxDistance") == "None" else config.getint("EDREnemiesAlertsMaxDistance")}
        }
        
        self.edrsystems = EDRSystems(self.server)
        self.edrresourcefinder = EDRResourceFinder(self.edrsystems)
        self.edrcmdrs = EDRCmdrs(self.server)
        self.edropponents = {
            EDROpponents.OUTLAWS: EDROpponents(self.server, EDROpponents.OUTLAWS, self._realtime_callback),
            EDROpponents.ENEMIES: EDROpponents(self.server, EDROpponents.ENEMIES, self._realtime_callback),
        }
        self.edrlegal = EDRLegalRecords(self.server)

        self.mandatory_update = False
        self.autoupdate_pending = False
        self.crimes_reporting = True
        self.motd = []
        self.tips = RandomTips()
        self.help_content = HelpContent()
        self._throttle_until_timestamp = None
        self.ui.notify(_(u"Troubleshooting"), [_(u"If the overlay doesn't show up, try one of the following:"), _(u" - In Elite: go to graphics options, and select Borderless or Windowed."), _(" - With Elite and EDR launched, check that EDMCOverlay.exe is running in the task manager"), _(" - Reach out to LeKeno on discord (LeKeno#8484) or the Elite forums (LeKeno)")])

    def loud_audio_feedback(self):
        config.set("EDRAudioFeedbackVolume", "loud")
        self.AUDIO_FEEDBACK.loud()
        # Translators: this is shown on EDMC's status bar when a user enables loud audio cues
        self.status = _(u"loud audio cues.")

    def soft_audio_feedback(self):
        config.set("EDRAudioFeedbackVolume", "soft")
        self.AUDIO_FEEDBACK.soft()
        # Translators: this is shown on EDMC's status bar when a user enables soft audio cues
        self.status = _(u"soft audio cues.")

    def apply_config(self):
        c_email = config.get("EDREmail")
        c_password = config.get("EDRPassword")
        c_visual_feedback = config.get("EDRVisualFeedback")
        c_visual_alt_feedback = config.get("EDRVisualAltFeedback")
        c_audio_feedback = config.get("EDRAudioFeedback")
        c_audio_volume = config.get("EDRAudioFeedbackVolume")
        c_redact_my_info = config.get("EDRRedactMyInfo")

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

        if c_visual_alt_feedback is None or c_visual_alt_feedback == "False":
            self._visual_alt_feedback.set(0)
        else:
            self._visual_alt_feedback.set(1)
                
        if c_audio_feedback is None or c_audio_feedback == "False":
            self._audio_feedback.set(0)
        else:
            self._audio_feedback.set(1)

        if c_audio_volume is None or c_audio_volume == "loud":
            self.loud_audio_feedback()
        else:
            self.soft_audio_feedback()

        if c_redact_my_info is None:
            self.anonymous_reports = _(u"Auto")
        elif c_redact_my_info in [_(u"Always"), _(u"Never")]:
            self.anonymous_reports = c_redact_my_info


    def check_version(self):
        version_range = self.server.server_version()
        self.motd = _edr(version_range["l10n_motd"])

        if version_range is None:
            # Translators: this is shown on EDMC's status bar when the version check fails
            self.status = _(u"check for version update has failed.")
            return

        if self.is_obsolete(version_range["min"]):
            EDRLOG.log(u"Mandatory update! {version} vs. {min}"
                       .format(version=self.edr_version, min=version_range["min"]), "ERROR")
            self.mandatory_update = True
            self.autoupdate_pending = version_range.get("autoupdatable", False)
            self.__status_update_pending()
        elif self.is_obsolete(version_range["latest"]):
            EDRLOG.log(u"EDR update available! {version} vs. {latest}"
                       .format(version=self.edr_version, latest=version_range["latest"]), "INFO")
            self.mandatory_update = False
            self.autoupdate_pending = version_range.get("autoupdatable", False)
            self.__status_update_pending()

    def is_obsolete(self, advertised_version):
        client_parts = map(int, self.edr_version.split('.'))
        advertised_parts = map(int, advertised_version.split('.'))
        return client_parts < advertised_parts

    @property
    def player(self):
        return self.edrcmdrs.player

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
        self.ui.nolink()

    def linkable_status(self, link, new_status = None):
        #TODO verify if this needs to be truncated
        self._status.set(new_status if new_status else link)
        self.ui.link(link)

    @property
    def visual_feedback(self):
        if self._visual_feedback.get() == 0:
            return False
        
        if not self.IN_GAME_MSG:
             self.IN_GAME_MSG = InGameMsg() 
        return True

    @visual_feedback.setter
    def visual_feedback(self, new_value):
        self._visual_feedback.set(new_value)

    @property
    def visual_alt_feedback(self):
        return self._visual_alt_feedback.get() == 1

    @visual_alt_feedback.setter
    def visual_alt_feedback(self, new_value):
        self._visual_alt_feedback.set(new_value)


    @property
    def audio_feedback(self):
        return self._audio_feedback.get() == 1

    @audio_feedback.setter
    def audio_feedback(self, new_value):
        self._audio_feedback.set(new_value)

    @property
    def anonymous_reports(self):
        return self._anonymous_reports.get()

    @anonymous_reports.setter
    def anonymous_reports(self, new_value):
        self._anonymous_reports.set(new_value)
        if new_value is None or new_value == _(u"Auto"):
            self.server.anonymous_reports = None
        elif new_value in [_(u"Always"), _(u"Never")]:
            self.server.anonymous_reports = (new_value == _(u"Always")) 


    def player_name(self, name):
        self.edrcmdrs.set_player_name(name)
        self.server.set_player_name(name)

    def game_mode(self, mode, group = None):
        self.player.game_mode = mode
        self.player.private_group = group  
        self.server.set_game_mode(mode, group)

    def pledged_to(self, power, time_pledged=0):
        if self.server.is_anonymous():
            EDRLOG.log(u"Skipping pledged_to call since the user is anonymous.", "INFO")
            return
        nodotpower = power.replace(".", "") if power else None
        if self.edrcmdrs.player_pledged_to(nodotpower, time_pledged):
            for kind in self.edropponents:
                self.edropponents[kind].pledged_to(nodotpower, time_pledged)

    def login(self):
        self.server.logout()
        if self.server.login(self.email, self.password):
            # Translators: this is shown on EDMC's status bar when the authentication succeeds
            self.status = _(u"authenticated (guest).") if self.is_anonymous() else _(u"authenticated.")
            return True
        # Translators: this is shown on EDMC's status bar when the authentication fails
        self.status = _(u"not authenticated.")
        return False

    def is_logged_in(self):
        return self.server.is_authenticated()

    def is_anonymous(self):
        return (self.is_logged_in() and self.server.is_anonymous())

    def warmup(self):
        EDRLOG.log(u"Warming up client.", "INFO")
        # Translators: this is shown when EDR warms-up via the overlay
        details = [_(u"Check that Elite still has the focus!")]
        if self.mandatory_update:
            # Translators: this is shown when EDR warms-up via the overlay if there is a mandatory update pending
            details = [_(u"Mandatory update!")]
        details += self.motd
        # Translators: this is shown when EDR warms-up via the overlay, the -- are for presentation purpose
        details.append(_(u"-- Feeling lost? Send !help via the in-game chat --"))
        details.append(self.tips.tip())
        # Translators: this is shown when EDR warms-up via the overlay
        self.__notify(_(u"EDR v{} by LeKeno").format(self.edr_version), details, clear_before=True)

    def shutdown(self, everything=False):
        self.edrcmdrs.persist()
        self.player.persist()
        self.edrsystems.persist()
        self.edrresourcefinder.persist()
        for kind in self.edropponents:
            self.edropponents[kind].persist()
            self.edropponents[kind].shutdown_comms_link()
        self.edrlegal.persist()
        if self.IN_GAME_MSG:
            self.IN_GAME_MSG.shutdown()
        config.set("EDRVisualAltFeedback", "True" if self.visual_alt_feedback else "False")

        if not everything:
            return
        
        self.server.logout()

    def app_ui(self, parent):
        self.check_version()
        return self.ui

    def prefs_ui(self, parent):
        frame = notebook.Frame(parent)
        frame.columnconfigure(1, weight=1)

        # Translators: this is shown in the preferences panel
        ttkHyperlinkLabel.HyperlinkLabel(frame, text=_(u"EDR website"), background=notebook.Label().cget('background'), url="https://edrecon.com", underline=True).grid(padx=10, sticky=tk.W)       

        # Translators: this is shown in the preferences panel
        notebook.Label(frame, text=_(u'Credentials')).grid(padx=10, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        # Translators: this is shown in the preferences panel
        cred_label = notebook.Label(frame, text=_(u'Log in with your EDR account for full access (https://edrecon.com/account)'))
        cred_label.grid(padx=10, columnspan=2, sticky=tk.W)

        notebook.Label(frame, text=_(u"Email")).grid(padx=10, row=11, sticky=tk.W)
        notebook.Entry(frame, textvariable=self._email).grid(padx=10, row=11,
                                                             column=1, sticky=tk.EW)

        notebook.Label(frame, text=_(u"Password")).grid(padx=10, row=12, sticky=tk.W)
        notebook.Entry(frame, textvariable=self._password,
                       show=u'*').grid(padx=10, row=12, column=1, sticky=tk.EW)

        notebook.Label(frame, text=_(u'Sitrep Broadcasts')).grid(padx=10, row=14, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        notebook.Label(frame, text=_("Redact my info")).grid(padx=10, row = 16, sticky=tk.W)
        choices = { _(u'Auto'),_(u'Always'),_(u'Never')}
        popupMenu = notebook.OptionMenu(frame, self._anonymous_reports, self.anonymous_reports, *choices)
        popupMenu.grid(padx=10, row=16, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")

        if self.server.is_authenticated():
            if self.is_anonymous():
                self.status = _(u"authenticated (guest).")
            else:
                self.status = _(u"authenticated.")
        else:
            self.status = _(u"not authenticated.")

        # Translators: this is shown in the preferences panel as a heading for feedback options (e.g. overlay, audio cues)
        notebook.Label(frame, text=_(u"EDR Feedback:")).grid(padx=10, row=17, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        
        notebook.Checkbutton(frame, text=_(u"Overlay"),
                             variable=self._visual_feedback).grid(padx=10, row=19,
                                                                  sticky=tk.W)
        notebook.Checkbutton(frame, text=_(u"Sound"),
                             variable=self._audio_feedback).grid(padx=10, row=20, sticky=tk.W)


        return frame

    def __status_update_pending(self):
        # Translators: this is shown in EDMC's status
        if self.autoupdate_pending:
            self.status = _(u"mandatory update pending (relaunch EDMC)") if self.mandatory_update else _(u"update pending (relaunch EDMC to apply)")
        else:
            # Translators: this is shown in EDMC's status
            status = _(u"mandatory EDR update!") if self.mandatory_update else _(u"please update EDR!")
            link = "https://edrecon.com/latest"
            self.linkable_status(link, status)
            

    def prefs_changed(self):
        set_language(config.get("language"))
        if self.mandatory_update:
            EDRLOG.log(u"Out-of-date client, aborting.", "ERROR")
            self.__status_update_pending()
            return

        config.set("EDREmail", self.email)
        config.set("EDRPassword", self.password)
        config.set("EDRVisualFeedback", "True" if self.visual_feedback else "False")
        config.set("EDRAudioFeedback", "True" if self.audio_feedback else "False")
        config.set("EDRRedactMyInfo", self.anonymous_reports)
        EDRLOG.log(u"Audio cues: {}, {}".format(config.get("EDRAudioFeedback"),
                                                config.get("EDRAudioFeedbackVolume")), "DEBUG")
        EDRLOG.log(u"Anonymous reports: {}".format(config.get("EDRRedactMyInfo")), "DEBUG")
        self.login()

    def noteworthy_about_system(self, fsdjump_event):
        self.edrsystems.system_id(fsdjump_event['StarSystem'], may_create=True, coords=fsdjump_event.get("StarPos", None))
        facts = self.edrresourcefinder.assess_jump(fsdjump_event, self.player.inventory)
        header = _('Rare materials in {} (USS-HGE/EE, Mission Rewards)'.format(fsdjump_event['StarSystem']))
        if not facts:
            facts = EDRBodiesOfInterest.bodies_of_interest(fsdjump_event['StarSystem'])
            header = _('Noteworthy stellar bodies in {}').format(fsdjump_event['StarSystem'])
        
        if not facts:
            return False
        self.__notify(header, facts, clear_before = True)
        return True

    def noteworthy_about_body(self, star_system, body_name):
        pois = EDRBodiesOfInterest.points_of_interest(star_system, body_name)
        if pois:
            facts = [poi["title"] for poi in pois]
            self.__notify(_(u'Noteworthy about {}: {} sites').format(body_name, len(facts)), facts, clear_before = True)
            return True
        materials_info = self.edrsystems.materials_on(star_system, body_name)
        facts = self.edrresourcefinder.assess_materials_density(materials_info, self.player.inventory)
        if facts:
            self.__notify(_(u'Noteworthy material densities on {}').format(body_name), facts, clear_before = True)

    def noteworthy_about_scan(self, scan_event):
        if scan_event["event"] != "Scan" or scan_event["ScanType"] != "Detailed":
            return
        if "Materials" not in scan_event or "BodyName" not in scan_event:
            return
        facts = self.edrresourcefinder.assess_materials_density(scan_event["Materials"], self.player.inventory)
        if facts:
            self.__notify(_(u'Noteworthy about {}').format(scan_event["BodyName"]), facts, clear_before = True)

    def noteworthy_about_signal(self, fss_event):
        facts = self.edrresourcefinder.assess_signal(fss_event, self.player.location, self.player.inventory)
        if not facts:
            return False
        header = _(u'Signal Insights (potential outcomes)')
        self.__notify(header, facts, clear_before = True)
        return True

    def process_scan(self, scan_event):
        if "Materials" not in scan_event:
            return False
        self.edrsystems.materials_info(self.player.star_system, scan_event["BodyName"], scan_event["Materials"])

    def closest_poi_on_body(self, star_system, body_name, attitude):
        body = self.edrsystems.body(self.player.star_system, self.player.place)
        radius = body.get("radius", None) if body else None
        return EDRBodiesOfInterest.closest_point_of_interest(star_system, body_name, attitude, radius)

    def navigation(self, latitude, longitude):
        position = {"latitude": float(latitude), "longitude": float(longitude)}
        loc = EDPlanetaryLocation(position)
        if loc.valid():
            self.player.planetary_destination = loc
            self.__notify(_(u'Assisted Navigation'), [_(u"Destination set to {} | {}").format(latitude, longitude), _(u"Guidance will be shown when approaching a stellar body")], clear_before = True)
        else:
            self.player.planetary_destination = None
            self.__notify(_(u'Assisted Navigation'), [_(u"Invalid destination")], clear_before = True)

    def show_navigation(self):
        current = self.player.piloted_vehicle.attitude
        destination = self.player.planetary_destination

        if not destination or not current:
            return
        
        if not current.valid() or not destination.valid():
            return

        bearing = destination.bearing(current)
        
        body = self.edrsystems.body(self.player.star_system, self.player.place)
        radius = body.get("radius", None) if body else None
        distance = destination.distance(current, radius) if radius else None
        if distance <= 1.0:
            return
        pitch = destination.pitch(current, distance) if distance and distance <= 700 else None
                
        if self.visual_feedback:
            self.IN_GAME_MSG.navigation(bearing, destination, distance, pitch)
        self.status = _(u"> {:03} < for Lat:{:.4f} Lon:{:.4f}".format(bearing, destination.latitude, destination.longitude))

    def check_system(self, star_system, may_create=False, coords=None):
        try:
            EDRLOG.log(u"Check system called: {}".format(star_system), "INFO")
            details = []
            notams = self.edrsystems.active_notams(star_system, may_create, coords)
            if notams:
                EDRLOG.log(u"NOTAMs for {}: {}".format(star_system, notams), "DEBUG")
                details += notams
            
            if self.edrsystems.has_sitrep(star_system):
                if star_system == self.player.star_system and self.player.in_bad_neighborhood():
                    EDRLOG.log(u"Sitrep system is known to be an anarchy. Crimes aren't reported.", "INFO")
                    # Translators: this is shown via the overlay if the system of interest is an Anarchy (current system or !sitrep <system>)
                    details.append(_c(u"Sitrep|Anarchy: not all crimes are reported."))
                if self.edrsystems.has_recent_activity(star_system):
                    summary = self.edrsystems.summarize_recent_activity(star_system, self.player.power)
                    for section in summary:
                        details.append(u"{}: {}".format(section, "; ".join(summary[section])))
            if details:
                # Translators: this is the heading for the sitrep of a given system {}; shown via the overlay
                header = _(u"SITREP for {}") if self.player.in_open() else _(u"SITREP for {} (Open)")
                self.__sitrep(header.format(star_system), details)
        except CommsJammedError:
            self.__commsjammed()
        

    def notams(self):
        summary = self.edrsystems.systems_with_active_notams()
        if summary:
            details = []
            # Translators: this shows a ist of systems {} with active NOtice To Air Men via the overlay
            details.append(_(u"Active NOTAMs for: {}").format("; ".join(summary)))
            # Translators: this is the heading for the active NOTAMs overlay
            self.__sitrep(_(u"NOTAMs"), details)
        else:
            self.__sitrep(_(u"NOTAMs"), [_(u"No active NOTAMs.")])

    def notam(self, star_system):
        summary = self.edrsystems.active_notams(star_system)
        if summary:
            EDRLOG.log(u"NOTAMs for {}: {}".format(star_system, summary), "DEBUG")
            # Translators: this is the heading to show any active NOTAM for a given system {} 
            self.__sitrep(_(u"NOTAM for {}").format(star_system), summary)
        else:
            self.__sitrep(_(u"NOTAM for {}").format(star_system), [_(u"No active NOTAMs.")])

    def sitreps(self):
        try:
            details = []
            summary = self.edrsystems.systems_with_recent_activity()
            for section in summary:
                details.append(u"{}: {}".format(section, "; ".join(summary[section])))
            if details:
                header = _(u"SITREPS") if self.player.in_open() else _(u"SITREPS (Open)")
                self.__sitrep(header, details)
        except CommsJammedError:
            self.__commsjammed()


    def cmdr_id(self, cmdr_name):
        try:
            profile = self.cmdr(cmdr_name, check_inara_server=False)
            if not (profile is None or profile.cid is None):
                EDRLOG.log(u"Cmdr {cmdr} known as id={cid}".format(cmdr=cmdr_name,
                                                                cid=profile.cid), "DEBUG")
                return profile.cid

            EDRLOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
            return None
        except CommsJammedError:
            self.__commsjammed()
            return None

    def cmdr(self, cmdr_name, autocreate=True, check_inara_server=False):
        try:
            return self.edrcmdrs.cmdr(cmdr_name, autocreate, check_inara_server)
        except CommsJammedError:
            self.__commsjammed()
            return None

    def eval_build(self, eval_type):
        canonical_commands = ["power"]
        synonym_commands = ["priority", "pp", "priorities"]
        supported_commands = set(canonical_commands + synonym_commands)
        if eval_type not in supported_commands:
            self.__notify(_(u"EDR Evals"), [_(u"Yo dawg, I don't do evals for '{}'").format(eval_type), _(u"Try {} instead.").format(", ".join(canonical_commands))], clear_before=True)
            return

        vehicle = self.player.mothership
        if not vehicle.modules:
            self.__notify(_(u"Basic Power Assessment"), [_(u"Yo dawg, U sure that you got modules on this?")], clear_before=True)
            return

        if vehicle.module_info_timestamp and vehicle.slots_timestamp < vehicle.module_info_timestamp:
            self.__notify(_(u"Basic Power Assessment"), [_(u"Yo dawg, the info I got from FDev might be stale."), _(u"Try again later after a bunch of random actions."), _(u"Or try this: relog, look at your modules, try again.")], clear_before=True)
            return
        
        build_master = EDRXzibit(vehicle)
        assessment = build_master.assess_power_priorities()
        if not assessment:
            self.__notify(_(u"Basic Power Assessment"), [_(u"Yo dawg, sorry but I can't help with dat.")], clear_before=True)
            return
        formatted_assessment = []
        grades = [u'F', u'E', u'D', u'C', u'B-', u'B', u'B+', u'A-', u'A', u'A+']
        for fraction in sorted(assessment):
            grade = grades[int(assessment[fraction]["grade"]*(len(grades)-1))]
            powered = _(u"⚡: {}").format(assessment[fraction]["annotation"]) if assessment[fraction]["annotation"] else u""
            formatted_assessment.append(_(u"{}: {}\t{}").format(grade, assessment[fraction]["situation"], powered))
            recommendation = _(u"   ⚑: {}").format(assessment[fraction]["recommendation"]) if "recommendation" in assessment[fraction] else u""
            praise = _(u"  ✓: {}").format(assessment[fraction]["praise"]) if "praise" in assessment[fraction] else u""
            formatted_assessment.append(_(u"{}{}").format(recommendation, praise))
        self.__notify(_(u"Basic Power Assessment (β; oddities? relog, look at your modules)"), formatted_assessment, clear_before=True)
        
    
    def evict_system(self, star_system):
        self.edrsystems.evict(star_system)

    def __novel_enough_situation(self, new, old, cognitive = False):
        if old is None:
            return True

        delta = new["timestamp"] - old["timestamp"]
        
        if cognitive:
            return (new["starSystem"] != old["starSystem"] or new["place"] != old["place"]) or delta > self.cognitive_novelty_threshold

        if new["starSystem"] != old["starSystem"]:
            return delta > self.system_novelty_threshold

        if new["place"] != old["place"]:
            return (old["place"] == "" or
                    old["place"] == "Unknown" or
                    delta > self.place_novelty_threshold)

        if new["ship"] != old["ship"]:
            return (old["ship"] == "" or
                    old["ship"] == "Unknown" or
                    delta > self.ship_novelty_threshold)
        
        if "wanted" in new:
            return ("wanted" not in old or
                    new["wanted"] > old["wanted"])
        
        if "bounty" in new:
            return ("bounty" not in old or
                    new["bounty"] > old["bounty"])
        return False

    def novel_enough_alert(self, alert_for_cmdr, alert):
        last_alert = self.alerts_cache.get(alert_for_cmdr)
        return self.__novel_enough_situation(alert, last_alert)

    def novel_enough_blip(self, cmdr_id, blip, cognitive = False):
        last_blip = self.cognitive_blips_cache.get(cmdr_id) if cognitive else self.blips_cache.get(cmdr_id)
        return self.__novel_enough_situation(blip, last_blip, cognitive)

    def novel_enough_scan(self, cmdr_id, scan, cognitive = False):
        last_scan = self.cognitive_scans_cache.get(cmdr_id) if cognitive else self.scans_cache.get(cmdr_id)
        novel_situation = self.__novel_enough_situation(scan, last_scan, cognitive)
        return novel_situation or (scan["wanted"] != last_scan["wanted"]) or (scan["bounty"] != last_scan["bounty"])

    def novel_enough_traffic_report(self, sighted_cmdr, report):
        last_report = self.traffic_cache.get(sighted_cmdr)
        return self.__novel_enough_situation(report, last_report)

    def __novel_enough_fight(self, new, old):
        if old is None:
            return True

        target_cmdr = new.get('target', None) 
        if not target_cmdr:
            return False

        if self.player.is_wingmate(target_cmdr["cmdr"]):
            return False

        if self.edrcmdrs.is_friend(target_cmdr["cmdr"]):
            return False

        if self.edrcmdrs.is_ally(target_cmdr["cmdr"]):
            return False

        if abs(new["ship"]["hullHealth"].get("value", 0) - old["ship"]["hullHealth"].get("value", 0)) >= 20:
            return True

        if new["ship"]["shieldUp"] != old["ship"]["shieldUp"]:
            return True

        return self.__novel_enough_combat_contact(new["target"])

    def __novel_enough_combat_contact(self, contact):
        contact_old_state = self.fights_cache.get(contact["cmdr"].lower())
        if not contact_old_state:
            return True

        ship_new_state = contact["ship"]
        ship_old_state = contact_old_state["ship"]
        if abs(ship_new_state["hullHealth"].get("value", 0) - ship_old_state["hullHealth"].get("value", 0)) >= 20:
            return True

        if abs(ship_new_state["shieldHealth"].get("value", 0) - ship_old_state["shieldHealth"].get("value", 0)) >= 50:
            return True           
        return False

    def novel_enough_fight(self, involved_cmdr, fight):
        last_fight = self.fights_cache.get(involved_cmdr)
        return self.__novel_enough_fight(fight, last_fight)

    def outlaws_alerts_enabled(self, silent=True):
        return self._alerts_enabled(EDROpponents.OUTLAWS, silent)
    
    def enemies_alerts_enabled(self, silent=True):
        return self._alerts_enabled(EDROpponents.ENEMIES, silent)

    def _alerts_enabled(self, kind, silent=True):
        enabled = self.edropponents[kind].is_comms_link_up()
        if not silent:
            details = [_(u"{} alerts enabled").format(_(kind)) if enabled else _(u"{} alerts disabled").format(_(kind))]
            if self.realtime_params[kind]["max_distance"]:
                details.append(_(u" <={max_distance}ly").format(max_distance=self.realtime_params[kind]["max_distance"]))
            if self.realtime_params[kind]["min_bounty"]:
                details.append(_(u" >={min_bounty}cr").format(min_bounty=self.realtime_params[kind]["min_bounty"]))
            self.notify_with_details(_(u"EDR Alerts"), details)
        return enabled
    
    def enable_outlaws_alerts(self, silent=False):
        self._enable_alerts(EDROpponents.OUTLAWS, silent)
    
    def enable_enemies_alerts(self, silent=False):
        self._enable_alerts(EDROpponents.ENEMIES, silent)

    def _enable_alerts(self, kind, silent=False):
        try:
            details = ""
            if self._alerts_enabled(kind, silent=True):
                details = _(u"{} alerts already enabled").format(_(kind))
            elif kind == EDROpponents.ENEMIES:
                if self.is_anonymous():
                    details = _(u"Request an EDR account to access enemy alerts (https://edrecon.com/account)")
                elif not self.player.power:
                    details = _(u"Pledge to a power to access enemy alerts")
                elif self.player.time_pledged < self.enemy_alerts_pledge_threshold:
                    details = _(u"Remain loyal for at least {} days to access enemy alerts").format(int(self.enemy_alerts_pledge_threshold // 24*60*60))
                else:
                    details = _(u"Enabling Enemy alerts") if self.edropponents[kind].establish_comms_link() else _(u"Couldn't enable Enemy alerts")
            else:            
                details = _(u"Enabling {kind} alerts").format(kind=_(kind)) if self.edropponents[kind].establish_comms_link() else _(u"Couldn't enable {kind} alerts").format(kind=_(kind))
            if not silent:
                if self.realtime_params[kind]["max_distance"]:
                    details += _(u" <={max_distance}ly").format(max_distance=self.realtime_params[kind]["max_distance"])
                if self.realtime_params[kind]["min_bounty"]:
                    details += _(u" >={min_bounty}cr").format(min_bounty=self.realtime_params[kind]["min_bounty"])
                self.notify_with_details(_(u"EDR Alerts"), [details])
        except CommsJammedError:
            self.__commsjammed()
        
    def disable_outlaws_alerts(self, silent=False):
        self._disable_alerts(EDROpponents.OUTLAWS, silent)

    def disable_enemies_alerts(self, silent=False):
        self._disable_alerts(EDROpponents.ENEMIES, silent)

    def _disable_alerts(self, kind, silent=False):
        details = ""
        if self.edropponents[kind].is_comms_link_up():
            self.edropponents[kind].shutdown_comms_link()
            details = _(u"Disabling {} alerts").format(_(kind))
        else:
            details = _(u"{} alerts already disabled").format(_(kind))
        if not silent:
            self.notify_with_details(_(u"EDR Alerts"), [details])

    def min_bounty_outlaws_alerts(self, min_bounty):
        self._min_bounty_alerts(EDROpponents.OUTLAWS, min_bounty)

    def min_bounty_enemies_alerts(self, min_bounty):
        self._min_bounty_alerts(EDROpponents.ENEMIES, min_bounty)

    def _min_bounty_alerts(self, kind, min_bounty):
        new_value = self.realtime_params[kind]["min_bounty"]
        if min_bounty:
            try:
                new_value = int(min_bounty)
                self.notify_with_details(_(u"EDR Alerts"), [_(u"minimum bounty set to {min_bounty} cr for {kind}").format(min_bounty=EDFineOrBounty(new_value).pretty_print(), kind=_(kind))])
            except ValueError:
                self.notify_with_details(_(u"EDR Alerts"), [_(u"invalid value for minimum bounty")])
                new_value = None
        else:
            self.notify_with_details(_(u"EDR Alerts"), [_(u"no minimum bounty required")])
        self.realtime_params[kind]["min_bounty"] = new_value
        if new_value is None:
            config.set("EDR{}AlertsMinBounty".format(kind), "None")
        else:
            config.set("EDR{}AlertsMinBounty".format(kind), new_value)


    def max_distance_outlaws_alerts(self, max_distance):
        self._max_distance_alerts(EDROpponents.OUTLAWS, max_distance)

    def max_distance_enemies_alerts(self, max_distance):
        self._max_distance_alerts(EDROpponents.ENEMIES, max_distance)

    def _max_distance_alerts(self, kind, max_distance):
        new_value = self.realtime_params[kind]["max_distance"]
        if max_distance:
            try:
                new_value = int(max_distance)
                self.notify_with_details(_(u"EDR Alerts"), [_(u"maximum distance set to {max_distance} ly for {kind}").format(max_distance=new_value, kind=_(kind))])
            except ValueError:
                self.notify_with_details(_(u"EDR Alerts"), [_(u"invalid value, removing maximal distance")])
                new_value = None
        else:
            self.notify_with_details(_(u"Outlaws Alerts"), [_(u"no limits on distance")])

        self.realtime_params[kind]["max_distance"] = new_value
        if new_value is None:
            config.set("EDR{}AlertsMaxDistance".format(kind), "None")
        else:
            config.set("EDR{}AlertsMaxDistance".format(kind), new_value)

    def _realtime_callback(self, kind, events):
        summary = []
        if kind not in [EDROpponents.OUTLAWS, EDROpponents.ENEMIES]:
            return
        if events in ["cancel", "auth_revoked"]:
            summary = [_(u"Comms link interrupted. Send '?{} on' to re-establish.").format(kind.lower())]
        else:
            summary = self._summarize_realtime_alert(kind, events)
        if summary:
            self.notify_with_details(_(u"EDR Alerts"), summary)

    def _worthy_alert(self, kind, event):
        self_uid = self.server.uid()
        if event["uid"] == self_uid:
            return False
        if self.realtime_params[kind]["max_distance"]:
            try:
                origin = self.player.star_system
                distance = self.edrsystems.distance(origin, event["starSystem"])
                threshold = self.realtime_params[kind]["max_distance"]
                if distance > threshold:
                    EDRLOG.log(u"EDR alert not worthy. Distance {} between systems {} and {} exceeds threshold {}".format(distance, origin, event["starSystem"], threshold), "DEBUG")
                    return False
            except ValueError:
                EDRLOG.log(u"Can't compute distance between systems {} and {}: unknown system(s)".format(self.player.star_system, event["starSystem"]), "WARNING")
                pass
        if self.realtime_params[kind]["min_bounty"]:
            if "bounty" not in event:
                return False
            if event["bounty"] < self.realtime_params[kind]["min_bounty"]:
                EDRLOG.log(u"EDR alert not worthy. Bounty {} does not exceeds threshold {}".format(event["bounty"], self.realtime_params[kind]["min_bounty"]), "DEBUG")
                return False
        return self.novel_enough_alert(event["cmdr"].lower(), event)

    def _summarize_realtime_alert(self, kind, event):
        summary =  []
        EDRLOG.log(u"realtime {} alerts, handling {}".format(kind, event), "DEBUG")
        if not self._worthy_alert(kind, event):
            EDRLOG.log(u"Skipped realtime {} event because it wasn't worth alerting about: {}.".format(kind, event), "DEBUG")
        else:
            location = EDLocation(event["starSystem"], event["place"])
            copy(event["starSystem"])
            distance = None
            try:
                distance = self.edrsystems.distance(self.player.star_system, location.star_system)
            except ValueError:
                pass
            
            oneliner = _(u"{cmdr} ({ship}) sighted in {location}")
            if kind is EDROpponents.ENEMIES and event.get("enemy", None):
                oneliner = _(u"Enemy {cmdr} ({ship}) sighted in {location}")
            elif kind is EDROpponents.OUTLAWS:
                oneliner = _(u"Outlaw {cmdr} ({ship}) sighted in {location}")
            oneliner = oneliner.format(cmdr=event["cmdr"], ship=event["ship"], location=location.pretty_print())
            
            if distance:
                oneliner += _(u" [{distance:.3g} ly]").format(distance=distance) if distance < 50.0 else _(u" [{distance} ly]").format(distance=int(distance))
            if event.get("wanted", None):
                if event["bounty"] > 0:
                    oneliner += _(u" wanted for {bounty} cr").format(bounty=EDFineOrBounty(event["bounty"]).pretty_print())
                else:
                    oneliner += _(u" wanted somewhere")
            
            if oneliner:
                summary.append(oneliner)
            
            self.alerts_cache.set(event["cmdr"].lower(), event)
        return summary

    def who(self, cmdr_name, autocreate=False):
        try:
            profile = self.cmdr(cmdr_name, autocreate, check_inara_server=True)
            if profile:
                self.status = _(u"got info about {}").format(cmdr_name)
                EDRLOG.log(u"Who {} : {}".format(cmdr_name, profile.short_profile(self.player.powerplay)), "INFO")
                legal = self.edrlegal.summarize_recents(profile.cid)
                if legal:
                    self.__intel(cmdr_name, [profile.short_profile(self.player.powerplay), legal], clear_before=True)
                else:
                    self.__intel(cmdr_name, [profile.short_profile(self.player.powerplay)], clear_before=True)
            else:
                EDRLOG.log(u"Who {} : no info".format(cmdr_name), "INFO")
                self.__intel(cmdr_name, [_("No info about {cmdr}").format(cmdr=cmdr_name)], clear_before=True)
        except CommsJammedError:
            self.__commsjammed()    

    def distance(self, from_system, to_system):
        details = []
        distance = None
        try:
            distance = self.edrsystems.distance(from_system, to_system)
        except ValueError:
            pass
            
        if distance:
            pretty_dist = _(u"{distance:.3g}").format(distance=distance) if distance < 50.0 else _(u"{distance}").format(distance=int(distance))
            details.append(_(u"{dist}ly from {from_sys} to {to_sys}").format(dist=pretty_dist, from_sys=from_system, to_sys=to_system))
            taxi_jump_range = 50
            jumping_time = self.edrsystems.jumping_time(from_system, to_system, taxi_jump_range)
            transfer_time = self.edrsystems.transfer_time(from_system, to_system)
            details.append(_(u"Taxi time ({}LY): {}").format(taxi_jump_range, EDTime.pretty_print_timespan(jumping_time)))
            details.append(_(u"Transfer time: {}").format(EDTime.pretty_print_timespan(transfer_time)))
            self.status = _(u"distance: {dist}ly").format(dist=pretty_dist)
        else:
            self.status = _(u"distance failed")
            details.append(_(u"Couldn't calculate a distance. Invalid or unknown system names?"))
        self.__notify("Distance", details, clear_before = True)


    def blip(self, cmdr_name, blip):
        if self.player.in_solo():
            EDRLOG.log(u"Skipping blip since the user is in solo (unexpected).", "INFO")
            return False

        cmdr_id = self.cmdr_id(cmdr_name)
        if cmdr_id is None:
            self.status = _(u"no cmdr id (contact).")
            EDRLOG.log(u"Can't submit blip (no cmdr id for {}).".format(cmdr_name), "ERROR")
            its_actually_fine = self.is_anonymous()
            return its_actually_fine

        profile = self.cmdr(cmdr_name, check_inara_server=True)
        if profile and (self.player.name != cmdr_name) and profile.is_dangerous(self.player.powerplay):
            self.status = _(u"{} is bad news.").format(cmdr_name)
            if self.novel_enough_blip(cmdr_id, blip, cognitive = True):
                self.__warning(_(u"Warning!"), [profile.short_profile(self.player.powerplay)], clear_before=True)
                self.cognitive_blips_cache.set(cmdr_id, blip)
                if self.player.in_open() and self.is_anonymous() and profile.is_dangerous(self.player.powerplay):
                    self.advertise_full_account(_("You could have helped other EDR users by reporting this outlaw."))
                elif self.player.in_open() and self.is_anonymous():
                    self.advertise_full_account(_("You could have helped other EDR users by reporting this enemy."))
            else:
                EDRLOG.log(u"Skipping warning since a warning was recently shown.", "INFO")

        if not self.novel_enough_blip(cmdr_id, blip):
            self.status = u"skipping blip (not novel enough)."
            EDRLOG.log(u"Blip is not novel enough to warrant reporting", "INFO")
            return True

        if self.is_anonymous():
            EDRLOG.log("Skipping blip since the user is anonymous.", "INFO")
            self.blips_cache.set(cmdr_id, blip)
            return True

        success = self.server.blip(cmdr_id, blip)
        if success:
            self.status = u"blip reported for {}.".format(cmdr_name)
            self.blips_cache.set(cmdr_id, blip)

        return success

    def scanned(self, cmdr_name, scan):
        if self.player.in_solo():
            EDRLOG.log(u"Skipping scanned since the user is in solo (unexpected).", "INFO")
            return False

        cmdr_id = self.cmdr_id(cmdr_name)
        if cmdr_id is None:
            self.status = _(u"cmdr unknown to EDR.")
            EDRLOG.log(u"Can't submit scan (no cmdr id for {}).".format(cmdr_name), "ERROR")
            its_actually_fine = self.is_anonymous()
            return its_actually_fine

        if self.novel_enough_scan(cmdr_id, scan, cognitive = True):
            profile = self.cmdr(cmdr_name, check_inara_server=True)
            legal = self.edrlegal.summarize_recents(profile.cid)
            bounty = EDFineOrBounty(scan["bounty"]) if scan["bounty"] else None
            if profile and (self.player.name != cmdr_name):
                if profile.is_dangerous(self.player.powerplay):
                    # Translators: this is shown via EDMC's EDR status line upon contact with a known outlaw
                    self.status = _(u"{} is bad news.").format(cmdr_name)
                    details = [profile.short_profile(self.player.powerplay)]
                    status = ""
                    if scan["enemy"]:
                        status += _(u"PP Enemy (weapons free). ")
                    if scan["bounty"]:
                        status += _(u"Wanted for {} cr").format(EDFineOrBounty(scan["bounty"]).pretty_print())
                    elif scan["wanted"]:
                        status += _(u"Wanted somewhere. A Kill-Warrant-Scan will reveal their highest bounty.")
                    if status:
                        details.append(status)
                    if legal:
                        details.append(legal)
                    self.__warning(_(u"Warning!"), details, clear_before=True)
                elif self.intel_even_if_clean or (scan["wanted"] and bounty.is_significant()):
                    self.status = _(u"Intel for cmdr {}.").format(cmdr_name)
                    details = [profile.short_profile(self.player.powerplay)]
                    if bounty:
                        details.append(_(u"Wanted for {} cr").format(EDFineOrBounty(scan["bounty"]).pretty_print()))
                    elif scan["wanted"]:
                        details.append(_(u"Wanted somewhere but it could be minor offenses."))
                    if legal:
                        details.append(legal)
                    self.__intel(_(u"Intel"), details, clear_before=True)
                if not self.player.in_solo() and (self.is_anonymous() and (profile.is_dangerous(self.player.powerplay) or (scan["wanted"] and bounty.is_significant()))):
                    # Translators: this is shown to users who don't yet have an EDR account
                    self.advertise_full_account(_(u"You could have helped other EDR users by reporting this outlaw."))
                elif not self.player.in_solo() and self.is_anonymous() and scan["enemy"] and self.player.power:
                    # Translators: this is shown to users who don't yet have an EDR account
                    self.advertise_full_account(_(u"You could have helped other {power} pledges by reporting this enemy.").format(self.player.power))
                self.cognitive_scans_cache.set(cmdr_id, scan)

        if not self.novel_enough_scan(cmdr_id, scan):
            self.status = _(u"not novel enough (scan).")
            EDRLOG.log(u"Scan is not novel enough to warrant reporting", "INFO")
            return True

        if self.is_anonymous():
            EDRLOG.log("Skipping reporting scan since the user is anonymous.", "INFO")
            self.scans_cache.set(cmdr_id, scan)
            return True

        success = self.server.scanned(cmdr_id, scan)
        if success:
            self.status = _(u"scan reported for {}.").format(cmdr_name)
            self.scans_cache.set(cmdr_id, scan)

        return success

    def traffic(self, star_system, traffic):
        if self.player.in_solo():
            EDRLOG.log(u"Skipping traffic since the user is in solo (unexpected).", "INFO")
            return False

        try:
            if self.is_anonymous():
                EDRLOG.log(u"Skipping traffic report since the user is anonymous.", "INFO")
                return True

            sigthed_cmdr = traffic["cmdr"]
            if not self.novel_enough_traffic_report(sigthed_cmdr, traffic):
                self.status = _(u"not novel enough (traffic).")
                EDRLOG.log(u"Traffic report is not novel enough to warrant reporting", "INFO")
                return True

            sid = self.edrsystems.system_id(star_system, may_create=True)
            if sid is None:
                EDRLOG.log(u"Failed to report traffic for system {} : no id found.".format(star_system),
                        "DEBUG")
                return False

            success = self.server.traffic(sid, traffic)
            if success:
                self.status = _(u"traffic reported.")
                self.traffic_cache.set(sigthed_cmdr, traffic)

            return success
        except CommsJammedError:
            self.__commsjammed()
            return False


    def crime(self, star_system, crime):
        if self.player.in_solo():
            EDRLOG.log(u"Skipping crime since the user is in solo (unexpected).", "INFO")
            return False
            
        if not self.crimes_reporting:
            EDRLOG.log(u"Crimes reporting is off (!crimes on to re-enable).", "INFO")
            self.status = _(u"Crimes reporting is off (!crimes on to re-enable)")
            return True
            
        if self.player.in_bad_neighborhood():
            EDRLOG.log(u"Crime not being reported because the player is in an anarchy.", "INFO")
            self.status = _(u"Anarchy system (crimes not reported).")
            return True

        if self.is_anonymous():
            EDRLOG.log(u"Skipping crime report since the user is anonymous.", "INFO")
            if crime["victim"] == self.player.name:
                self.advertise_full_account(_(u"You could have helped other EDR users or get help by reporting this crime!"))
            return True

        sid = self.edrsystems.system_id(star_system, may_create=True)
        if sid is None:
            EDRLOG.log(u"Failed to report crime in system {} : no id found.".format(star_system),
                       "DEBUG")
            return False

        if self.server.crime(sid, crime):
            self.status = _(u"crime reported!")
            return True
        return False

    def fight(self, fight):
        if self.player.in_solo():
            EDRLOG.log(u"Skipping fight since the user is in solo (unexpected).", "INFO")
            return False

        if not self.crimes_reporting:
            EDRLOG.log(u"Crimes reporting is off (!crimes on to re-enable).", "INFO")
            self.status = _(u"Crimes reporting is off (!crimes on to re-enable)")
            return
            
        if self.player.in_bad_neighborhood():
            EDRLOG.log(u"Fight not being reported because the player is in an anarchy.", "INFO")
            self.status = _(u"Anarchy system (fights not reported).")
            return

        if self.is_anonymous():
            EDRLOG.log(u"Skipping fight report since the user is anonymous.", "INFO")
            return

        if not self.player.recon_box.forced:
            outlaws_presence = self.player.instance.presence_of_outlaws(self.edrcmdrs, ignorables=self.player.wing_and_crew())
            if outlaws_presence:
                self.player.recon_box.activate()
                self.__notify(_(u"EDR Central"), [_(u"Fight reporting enabled"), _(u"Reason: presence of outlaws"), _(u"Turn it off: flash your lights twice, or leave this area, or escape danger and retract hardpoints.")], clear_before=True)
        
        if not self.player.recon_box.active:
            if not self.player.recon_box.advertised:
                self.__notify(_(u"Need assistance?"), [_(u"Flash your lights twice to report a PvP fight to enforcers."), _(u"Send '!crimes off' to make EDR go silent.")], clear_before=True)
                self.player.recon_box.advertised = True
            return

        if not self.novel_enough_fight(fight['cmdr'].lower(), fight):
            EDRLOG.log(u"Skipping fight report (not novel enough).", "INFO")
            return

        star_system = fight["starSystem"]
        sid = self.edrsystems.system_id(star_system, may_create=True)
        if sid is None:
            EDRLOG.log(u"Failed to report fight in system {} : no id found.".format(star_system),
                       "DEBUG")
            return
        instance_changes = self.player.instance.noteworthy_changes_json()
        if instance_changes:
            instance_changes["players"] = filter(lambda x: self.__novel_enough_combat_contact(x), instance_changes["players"])
            fight["instance"] = instance_changes
        fight["codeword"] = self.player.recon_box.keycode
        if self.server.fight(sid, fight):
            self.status = _(u"fight reported!")
            self.fights_cache.set(fight["cmdr"].lower(), fight)
            if fight.get("target", None):
                self.fights_cache.set(fight["target"]["cmdr"].lower(), fight["target"])
            if fight.get("instance", None) and fight["instance"].get("players", None):
                for change in fight["instance"]["players"]:
                    self.fights_cache.set(change["cmdr"].lower(), change)

    def crew_report(self, report):
        if self.player.in_solo():
            EDRLOG.log(u"Skipping crew report since the user is in solo (unexpected).", "INFO")
            return False

        if self.is_anonymous():
            EDRLOG.log(u"Skipping crew report since the user is anonymous.", "INFO")
            if report["captain"] == self.player.name and (report["crimes"] or report["kicked"]):
                self.advertise_full_account(_(u"You could have helped other EDR users by reporting this problematic crew member!"))
            return False

        crew_id = self.cmdr_id(report["crew"])
        if crew_id is None:
            self.status = _(u"{} is unknown to EDR.".format(report["crew"]))
            EDRLOG.log(u"Can't submit crew report (no cmdr id for {}).".format(report["crew"]), "ERROR")
            return False
        
        if self.server.crew_report(crew_id, report):
            self.status = _(u"multicrew session reported (cmdr {name}).").format(name=report["crew"])
            return True
        return False

    def __throttling_duration(self):
        now_epoch = EDTime.py_epoch_now()
        if now_epoch > self._throttle_until_timestamp:
            return 0
        return self._throttle_until_timestamp - now_epoch

    def call_central(self, service, info):
        if self.is_anonymous():
            EDRLOG.log(u"Skipping EDR Central call since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False
        
        throttling = self.__throttling_duration()
        if throttling:
            self.status = _(u"Message not sent. Try again in {duration}.").format(duration=EDTime.pretty_print_timespan(throttling))
            self.__notify(_(u"EDR central"), [self.status], clear_before = True)
            return False

        star_system = info["starSystem"]
        sid = self.edrsystems.system_id(star_system, may_create=True)
        if sid is None:
            EDRLOG.log(u"Failed to call central from system {} : no id found.".format(star_system),
                       "DEBUG")
            return False
        
        info["codeword"] = self.player.recon_box.gen_keycode()
        if self.server.call_central(service, sid, info):
            details = [_(u"Message sent with codeword '{}'.").format(info["codeword"]), _(u"Ask the codeword to identify trusted commanders.")]
            if service in ["fuel", "repair"]:
                fuel_service = random.choice([{"name": "Fuel Rats", "url": "https://fuelrats.com/"}, {"name": "Repair Corgis", "url": "https://candycrewguild.space/"}])
                attachment = [_(u"For good measure, also reach out to these folks with the info below:"), fuel_service["url"]]
                fuel_info = "Fuel: {:.1f}/{:.0f}".format(info["ship"]["fuelLevel"], info["ship"]["fuelCapacity"]) if info["ship"].get("fuelLevel") else ""
                hull_info = "Hull: {:.0f}%".format(info["ship"]["hullHealth"]["value"]) if info["ship"].get("hullHealth") else ""
                info = u"{} ({}) in {}, {} - {} {}\nInfo provided by EDR.".format(info["cmdr"], info["ship"]["type"], info["starSystem"], info["place"], fuel_info, hull_info)
                copy(info)
                attachment.append(info)
                self.ui.notify(fuel_service["name"], attachment)
                details.append(_(u"Check ED Market Connector for instructions about other options"))
                status = _(u"Sent to EDR central - Also try: {}").format(fuel_service["name"])
                link = fuel_service["url"]
                self.linkable_status(link, status)
            else:
                self.status = _(u"Message sent to EDR central")
            self.__notify(_(u"EDR central"), details, clear_before = True)
            self._throttle_until_timestamp = EDTime.py_epoch_now() + 60*5 #TODO parameterize
            return True
        return False

    def tag_cmdr(self, cmdr_name, tag):
        if self.is_anonymous():
            EDRLOG.log(u"Skipping tag cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False
        
        if  tag in ["enemy", "ally"]:
            if not self.player.squadron:
                EDRLOG.log(u"Skipping squadron tag since the user isn't a member of a squadron.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to join a squadron on https://inara.cz to use this feature."), _(u"Then, reboot EDR to reflect these changes.")])
                return False
            elif not self.player.is_empowered_by_squadron():
                EDRLOG.log(u"Skipping squadron tag since the user isn't trusted.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to reach {} to tag enemies or allies.").format(self.player.squadron_empowered_rank())])
                return False

        success = self.edrcmdrs.tag_cmdr(cmdr_name, tag)
        dex_name = _(u"Squadron Dex") if tag in ["enemy", "ally"] else _(u"Cmdr Dex") 
        if success:
            self.__notify(dex_name, [_(u"Successfully tagged cmdr {name} with {tag}").format(name=cmdr_name, tag=tag)], clear_before = True)
        else:
            self.__notify(dex_name, [_(u"Could not tag cmdr {name} with {tag}").format(name=cmdr_name, tag=tag)], clear_before = True)
        return success
    
    def memo_cmdr(self, cmdr_name, memo):
        if self.is_anonymous():
            EDRLOG.log(u"Skipping memo cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        success = self.edrcmdrs.memo_cmdr(cmdr_name, memo)
        if success:
            self.__notify(_(u"Cmdr Dex"), [_(u"Successfully attached a memo to cmdr {}").format(cmdr_name)], clear_before = True)
        else:
            self.__notify(_(u"Cmdr Dex"), [_(u"Failed to attach a memo to cmdr {}").format(cmdr_name)], clear_before = True)
        return success

    def clear_memo_cmdr(self, cmdr_name):
        if self.is_anonymous():
            EDRLOG.log(u"Skipping clear_memo_cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        success = self.edrcmdrs.clear_memo_cmdr(cmdr_name)
        if success:
            self.__notify(_(u"Cmdr Dex"),[_(u"Successfully removed memo from cmdr {}").format(cmdr_name)], clear_before = True)
        else:
            self.__notify(_(u"Cmdr Dex"), [_(u"Failed to remove memo from cmdr {}").format(cmdr_name)], clear_before = True)
        return success

    def untag_cmdr(self, cmdr_name, tag):
        if self.is_anonymous():
            EDRLOG.log(u"Skipping untag cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        if  tag in ["enemy", "ally"]:
            if not self.player.squadron:
                EDRLOG.log(u"Skipping squadron untag since the user isn't a member of a squadron.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to join a squadron on https://inara.cz to use this feature."), _(u"Then, reboot EDR to reflect these changes.")])
                return False
            elif not self.player.is_empowered_by_squadron():
                EDRLOG.log(u"Skipping squadron untag since the user isn't trusted.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to reach {} to tag enemies or allies.").format(self.player.squadron_empowered_rank())])
                return False

        success = self.edrcmdrs.untag_cmdr(cmdr_name, tag)
        dex_name = _(u"Squadron Dex") if tag in ["enemy", "ally"] else _(u"Cmdr Dex")
        if success:
            if tag is None:
                self.__notify(dex_name, [_(u"Successfully removed all tags from cmdr {}").format(cmdr_name)], clear_before = True)
            else:
                self.__notify(dex_name, [_(u"Successfully removed tag {} from cmdr {}").format(tag, cmdr_name)], clear_before = True)
        else:
            self.__notify(dex_name, [_(u"Could not remove tag(s) from cmdr {}").format(cmdr_name)], clear_before = True)
        return success

    def where(self, cmdr_name):
        report = {}
        try:
            for kind in self.edropponents:
                candidate_report = self.edropponents[kind].where(cmdr_name)
                if candidate_report and (not report or report["timestamp"] < candidate_report["timestamp"]):
                    report = candidate_report
            
            if report:
                self.status = _(u"got info about {}").format(cmdr_name)
                header = _(u"Intel for {}") if self.player.in_open() else _(u"Intel for {} (Open)")
                self.__intel(header.format(cmdr_name), report["readable"], clear_before=True)
            else:
                EDRLOG.log(u"Where {} : no info".format(cmdr_name), "INFO")
                self.status = _(u"no info about {}").format(cmdr_name)
                header = _(u"Intel for {}") if self.player.in_open() else _(u"Intel for {} (Open)")
                self.__intel(header.format(cmdr_name), [_(u"Not recently sighted or not an outlaw.")], clear_before=True)
        except CommsJammedError:
            self.__commsjammed()

    def where_ship(self, name_or_type):
        results = self.player.fleet.where(name_or_type)
        if results:
            hits = []
            random.shuffle(results)
            in_clipboard = False
            for hit in results:
                transit = _(u" @ {}").format(EDTime.t_plus_py(hit[3])) if hit[3] else u""
                if hit[0]:
                    hits.append(_(u"'{}' ({}): {}{}").format(hit[0], hit[1], hit[2], transit))
                else:
                    hits.append(_(u"{}: {}{}").format(hit[1], hit[2], transit))
                if not in_clipboard and hit[2]:
                    copy(hit[2])
                    in_clipboard = True
            self.__notify(_(u"Ship locator"), hits, clear_before = True)
        elif results == False:
            self.__notify(_(u"Ship locator"), [_(u"No info about your fleet."), _(u"Visit a shipyard to update your fleet info.")], clear_before = True)
        else:
            self.__notify(_(u"Ship locator"), [_(u"Couldn't find anything")], clear_before = True)

    def contract(self, target_cmdr, reward):
        if self.is_anonymous():
            EDRLOG.log(u"Skipping contract since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        if target_cmdr is None:
            contracts = self.player.contracts()
            self.__notify(_(u"Kill Rewards"),[_(u"Reward of {} void opals for a kill on Cmdr {}").format(c["cmdr_name"],c["reward"]) for c in contracts], clear_before = True)
            return True
        
        if reward is None:
            contract = self.player.contract(target_cmdr)
            if not contract:
                self.__notify(_(u"Kill Rewards"),[_(u"You haven't set any reward for a kill on Cmdr {}").format(target_cmdr), _(u"Send '!contract {} 10' in chat to set a reward of 10 void opals").format(target_cmdr)], clear_before = True)
                return True
            self.__notify(_(u"Kill Rewards"),[_(u"Reward of {} void opals for a kill on Cmdr {}").format(target_cmdr,contract["reward"]), _(u"Send '!contract {} 0' in chat to remove the kill reward").format(target_cmdr)], clear_before = True)
            return True

        outcome = self.player.place_contract(cmdr_name, reward)
        if outcome["success"]:
            self.__notify(_(u"Kill Rewards"),[_(u"Successfully set a reward of {} void opals for a kill on {}").format(target_cmdr,reward), _(u"Send '!contract {} 0' in chat to remove the kill reward").format(target_cmdr)], clear_before = True)
        else:
            self.__notify(_(u"Kill Rewards"),[_(u"Failed to set a kill reward on {}").format(target_cmdr), _(u"Reason: {}").format(outcome["comment"])], clear_before = True)
        return outcome["success"]


    def outlaws(self):
        try:
            return self._opponents(EDROpponents.OUTLAWS)
        except CommsJammedError:
            self.__commsjammed()
            return False

    def enemies(self):
        try:
            return self._opponents(EDROpponents.ENEMIES)
        except CommsJammedError:
            self.__commsjammed()
            return False

    def _opponents(self, kind):
        if kind is EDROpponents.ENEMIES and not self.player.power:
            EDRLOG.log(u"Not pledged to any power, can't have enemies.", "INFO")
            self.__notify(_(u"Recently Sighted {kind}").format(kind=_(kind)), [_(u"You need to be pledged to a power.")], clear_before = True)
            return False
        opponents_report = self.edropponents[kind].recent_sightings()
        if not opponents_report:
            EDRLOG.log(u"No recently sighted {}".format(kind), "INFO")
            header = _(u"Recently Sighted {kind}") if self.player.in_open() else _(u"Recently Sighted {kind} (Open)")
            self.__sitrep(header.format(kind=_(kind)), [_(u"No {kind} sighted in the last {timespan}").format(kind=_(kind).lower(), timespan=EDTime.pretty_print_timespan(self.edropponents[kind].timespan))])
            return False
        
        self.status = _(u"recently sighted {kind}").format(kind=_(kind))
        EDRLOG.log(u"Got recently sighted {}".format(kind), "INFO")
        header = _(u"Recently Sighted {kind}") if self.player.in_open() else _(u"Recently Sighted {kind} (Open)")
        self.__sitrep(header.format(kind=_(kind)), opponents_report)

    def help(self, section):
        content = self.help_content.get(section)
        if not content:
            return False

        if self.visual_feedback:
            EDRLOG.log(u"Show help for {} with header: {} and details: {}".format(section, content["header"], content["details"][0]), "DEBUG")
            self.IN_GAME_MSG.help(content["header"], content["details"])
        EDRLOG.log(u"[Alt] Show help for {} with header: {} and details: {}".format(section, content["header"], content["details"][0]), "DEBUG")
        self.ui.help(_(content["header"]), _(content["details"]))
        return True

    def clear(self):
        if self.visual_feedback:
            self.IN_GAME_MSG.clear()
        self.ui.clear()
           

    def __sitrep(self, header, details):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.notify()
        if self.visual_feedback:
            EDRLOG.log(u"sitrep with header: {}; details: {}".format(header, details[0]), "DEBUG")
            self.IN_GAME_MSG.clear_sitrep()
            self.IN_GAME_MSG.sitrep(header, details)
        EDRLOG.log(u"[Alt] sitrep with header: {}; details: {}".format(header, details[0]), "DEBUG")
        self.ui.sitrep(header, details)

    def __intel(self, who, details, clear_before=False):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.notify()
        if self.visual_feedback:
            EDRLOG.log(u"Intel for {}; details: {}".format(who, details[0]), "DEBUG")
            if clear_before:
                self.IN_GAME_MSG.clear_intel()
            self.IN_GAME_MSG.intel(_(u"Intel"), details)
        EDRLOG.log(u"[Alt] Intel for {}; details: {}".format(who, details[0]), "DEBUG")
        self.ui.intel(_(u"Intel"), details)

    def __warning(self, header, details, clear_before=False):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.warn()
        if self.visual_feedback:
            EDRLOG.log(u"Warning; details: {}".format(details[0]), "DEBUG")
            if clear_before:
                self.IN_GAME_MSG.clear_warning()
            self.IN_GAME_MSG.warning(header, details)
        EDRLOG.log(u"[Alt] Warning; details: {}".format(details[0]), "DEBUG")
        self.ui.warning(header, details)
    
    def __notify(self, header, details, clear_before=False):
        if self.audio_feedback:
            self.AUDIO_FEEDBACK.notify()
        if self.visual_feedback:
            EDRLOG.log(u"Notify about {}; details: {}".format(header, details[0]), "DEBUG")
            if clear_before:
                self.IN_GAME_MSG.clear_notice()
            self.IN_GAME_MSG.notify(header, details)
        EDRLOG.log(u"[Alt] Notify about {}; details: {}".format(header, details[0]), "DEBUG")
        self.ui.notify(header, details)

    def __commsjammed(self):
        self.__notify(_(u"Comms Link Error"), [_(u"EDR Central can't be reached at the moment"), _(u"Try again later or contact Cmdr LeKeno if it keeps failing")])

    def notify_with_details(self, notice, details):
        self.__notify(notice, details)

    def warn_with_details(self, warning, details):
        self.__warning(warning, details)
    
    def advertise_full_account(self, context, passive=True):
        now = datetime.datetime.now()
        now_epoch = time.mktime(now.timetuple())            
        if passive and self.previous_ad:
            if (now_epoch - self.previous_ad) <= self.edr_needs_u_novelty_threshold:
                return False

        self.__notify(_(u"EDR needs you!"), [context, u"--", _(u"Apply for an account at https://edrecon.com/account"), _(u"It's free, no strings attached.")], clear_before=True)
        self.previous_ad = now_epoch
        return True

    def interstellar_factors_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        try:
            self.edrsystems.search_interstellar_factors(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), override_sc_distance = override_sc_distance)
            self.searching = True
            self.status = _(u"I.Factors: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Interstellar Factors: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"I.Factors: failed")
            self.notify_with_details(_(u"EDR Search"), [_(u"Unknown system")])

    def raw_material_trader_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        try:
            self.edrsystems.search_raw_trader(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), override_sc_distance = override_sc_distance)
            self.searching = True
            self.status = _(u"Raw mat. trader: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Raw material trader: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"Raw mat. trader: failed")
            self.notify_with_details(_(u"EDR Search"), [_(u"Unknown system")])
        
    def encoded_material_trader_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        try:
            self.edrsystems.search_encoded_trader(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), override_sc_distance = override_sc_distance)
            self.searching = True
            self.status = _(u"Encoded data trader: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Encoded data trader: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"Encoded data trader: failed")
            self.notify_with_details(_(u"EDR Search"), [_(u"Unknown system")])


    def manufactured_material_trader_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return
        
        try:
            self.edrsystems.search_manufactured_trader(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), override_sc_distance = override_sc_distance)
            self.searching = True
            self.status = _(u"Manufactured mat. trader: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Manufactured material trader: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"Manufactured mat. trader: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)


    def staging_station_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return

        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return
        
        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        try:
            self.edrsystems.search_staging_station(star_system, self.__staoi_found)
            self.searching = True
            self.status = _(u"Staging station: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Staging station: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"Staging station: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def human_tech_broker_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        try:
            self.edrsystems.search_human_tech_broker(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), override_sc_distance = override_sc_distance)
            self.searching = True
            self.status = _(u"Human tech broker: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Human tech broker: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"Human tech broker: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)
    
    def guardian_tech_broker_near(self, star_system, override_sc_distance = None):
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        try:
            self.edrsystems.search_guardian_tech_broker(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), override_sc_distance = override_sc_distance)
            self.searching = True
            self.status = _(u"Guardian tech broker: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Guardian tech broker: searching...")], clear_before = True)
        except ValueError:
            self.status = _(u"Guardian tech broker: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def __staoi_found(self, reference, radius, sc, soi_checker, result):
        self.searching = False
        details = []
        if result:
            sc_distance = result['station']['distanceToArrival']
            distance = result['distance']
            pretty_dist = _(u"{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _(u"{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _(u"{dist}LS").format(dist=int(sc_distance))
            details.append(_(u"{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            details.append(_(u"{station} ({type}), {sc_dist}").format(station=result['station']['name'], type=result['station']['type'], sc_dist=pretty_sc_dist))
            details.append(_(u"as of {date} {ci}").format(date=result['station']['updateTime']['information'],ci=result.get('comment', '')))
            self.status = u"{item}: {system}, {dist} - {station} ({type}), {sc_dist}".format(item=soi_checker.name, system=result['name'], dist=pretty_dist, station=result['station']['name'], type=result['station']['type'], sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            self.status = _(u"{}: nothing within [{}LY, {}LS] of {}".format(soi_checker.name, int(radius), int(sc), reference))
            checked = _("checked {} systems").format(soi_checker.systems_counter) 
            if soi_checker.stations_counter: 
                checked = _("checked {} systems and {} stations").format(soi_checker.systems_counter, soi_checker.stations_counter) 
            details.append(_(u"nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if soi_checker.hint:
                details.append(soi_checker.hint)
        self.__notify(_(u"{} near {}").format(soi_checker.name, reference), details, clear_before = True)

    def search_resource(self, resource):
        star_system = self.player.star_system
        if not star_system:
            return
        
        if self.searching:
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        cresource = self.edrresourcefinder.canonical_name(resource)
        if cresource is None:
            self.status = _(u"{}: not supported.").format(resource)
            self.__notify(_(u"EDR Search"), [_(u"{}: not supported.").format(resource), _(u"To learn how to use the feature, send: !help search")], clear_before = True)
            return

        try:
            outcome = self.edrresourcefinder.resource_near(resource, star_system, self.__resource_found)
            if outcome == True:
                self.searching = True
                self.status = _(u"{}: searching...".format(cresource))
                self.__notify(_(u"EDR Search"), [_(u"{}: searching...").format(cresource)], clear_before = True)
            elif outcome == False or outcome == None:
                self.status = _(u"{}: failed...").format(cresource)
                self.__notify(_(u"EDR Search"), [_(u"{}: failed...").format(cresource), _(u"To learn how to use the feature, send: !help search")], clear_before = True)
            else:
                self.status = _(u"{}: found").format(cresource)
                self.__notify(u"{}".format(cresource), outcome, clear_before = True)
        except ValueError:
            self.status = _(u"{}: failed...").format(cresource)
            self.__notify(_(u"EDR Search"), [_(u"{}: failed...").format(cresource), _(u"To learn how to use the feature, send: !help search")], clear_before = True)

    def __resource_found(self, resource, reference, radius, checker, result, grade):
        self.searching = False
        details = []
        if result:
            distance = result['distance']
            pretty_dist = _(u"{dist:.3g}").format(dist=distance) if distance < 50.0 else _(u"{dist}").format(dist=int(distance))
            details.append(_(u"{} ({}LY, {})").format(result['name'], pretty_dist, '+' * grade))
            edt = EDTime()
            if 'updateTime' in result:
                edt.from_js_epoch(result['updateTime'] * 1000)
                details.append(_(u"as of {}").format(edt.as_date()))
            if checker.hint():
                details.append(checker.hint())
            self.status = u"{}: {} ({}LY)".format(checker.name, result['name'], pretty_dist)
            copy(result["name"])
        else:
            self.status = _(u"{}: nothing within [{}LY] of {}".format(checker.name, int(radius), reference))
            checked = _("checked {} systems").format(checker.systems_counter) 
            if checker.stations_counter: 
                checked = _("checked {} systems").format(checker.systems_counter)
            details.append(_(u"nothing found within {}LY, {}.").format(int(radius), checked))
            if checker.hint():
                details.append(checker.hint())
        self.__notify(_(u"{} near {}").format(checker.name, reference), details, clear_before = True)