from __future__ import absolute_import
from copy import deepcopy
import datetime
import itertools
from sys import float_repr_style
import time
import random
import math
import re
import json
import webbrowser

try:
    # for Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # for Python3
    import tkinter as tk
    from tkinter import ttk
import ttkHyperlinkLabel
import myNotebook as notebook
from config import config

from edrfleetcarrier import EDRFleetCarrier
from edrconfig import EDRConfig
from lrucache import LRUCache
from edentities import EDFineOrBounty
from edsitu import EDPlanetaryLocation, EDLocation
from edrserver import EDRServer, CommsJammedError
from edsmserver import EDSMServer
from audiofeedback import EDRSoundEffects
from edrlog import EDR_LOG
from ingamemsg import InGameMsg
from edrtogglingpanel import EDRTogglingPanel
from edrclientui import EDRClientUI
from edrsystems import EDRSystems
from edrfactions import EDRFactions
from edrresourcefinder import EDRResourceFinder
from edrbodiesofinterest import EDRBodiesOfInterest
from edrcmdrs import EDRCmdrs
from edropponents import EDROpponents
from randomtips import RandomTips
from helpcontent import HelpContent
from edtime import EDTime
from edrlegalrecords import EDRLegalRecords
from edrxzibit import EDRXzibit
from edrdiscord import EDRDiscordIntegration
from edvehicles import EDVehicleFactory
from edrsysplacheck import EDRGenusCheckerFactory
from edrsyssetlcheck import EDRSettlementCheckerFactory

from edri18n import _, _c, _edr, set_language
from clippy import copy, paste
from edrfssinsights import EDRFSSInsights
from edrcommands import EDRCommands
import edrroutes
from edrutils import simplified_body_name, pretty_print_number



class EDRClient(object):
    SFX = EDRSoundEffects()

    def __init__(self):
        edr_config = EDRConfig()
        set_language(config.get_str("language"))

        self.edr_version = edr_config.edr_version()
        EDR_LOG.log(u"Version {}".format(self.edr_version), "INFO")

        self.enemy_alerts_pledge_threshold = edr_config.enemy_alerts_pledge_threshold()
        self.system_novelty_threshold = edr_config.system_novelty_threshold()
        self.place_novelty_threshold = edr_config.place_novelty_threshold()
        self.ship_novelty_threshold = edr_config.ship_novelty_threshold()
        self.cognitive_novelty_threshold = edr_config.cognitive_novelty_threshold()
        self.intel_even_if_clean = edr_config.intel_even_if_clean()
        
        self.edr_needs_u_novelty_threshold = edr_config.edr_needs_u_novelty_threshold()
        self.previous_ad = None
        self.feature_ads = {
            "parking": { "advertised": False, "ad": [_(u"You may want to give a shot to the !parking command next time."), _(u"It will help you find a parking slot for your Fleet Carrier near busy systems.")]}
        }

        self.searching = {
            "active": False,
            "timestamp": EDTime.py_epoch_now()
        }

        self.blips_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.cognitive_blips_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.traffic_cache = LRUCache(edr_config.lru_max_size(), edr_config.traffic_max_age())
        self.scans_cache = LRUCache(edr_config.lru_max_size(), edr_config.scans_max_age())
        self.cognitive_scans_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.alerts_cache = LRUCache(edr_config.lru_max_size(), edr_config.alerts_max_age())
        self.fights_cache = LRUCache(edr_config.lru_max_size(), edr_config.fights_max_age())

        self._email = tk.StringVar(value=config.get_str("EDREmail"))
        self._password = tk.StringVar(value=config.get_str("EDRPassword"))
        # Translators: this is shown on the EDMC's status line
        self._status = tk.StringVar(value=_(u"not authenticated."))
        
        visual_feedback_type = _("Enabled") if config.get_str("EDRVisualFeedback") == "True" else _("Disabled")
        standalone_overlay = False
        if config.get_str("EDRVisualFeedback2") != None:
            visual_feedback_type = config.get_str("EDRVisualFeedback2")
            standalone_overlay = visual_feedback_type == _("Standalone (for VR or multi-display)")
        visual = 1 if visual_feedback_type != _("Disabled") else 0
        self.IN_GAME_MSG = InGameMsg(standalone = standalone_overlay) if visual else None
        self._visual_feedback_type = tk.StringVar(value=visual_feedback_type)
        self._visual_feedback = True if visual else False

        visual_alt = 1 if config.get_str("EDRVisualAltFeedback") == "True" else 0
        self._visual_alt_feedback = tk.IntVar(value=visual_alt)
        
        self.client_ui = None

        audio = 1 if config.get_str("EDRAudioFeedback") == "True" else 0
        self._audio_feedback = tk.IntVar(value=audio)

        g_triggers = 1 if config.get_str("EDRGestureTriggers") == "True" else 0
        self._gesture_triggers = tk.IntVar(value=g_triggers)
        
        
        self.server = EDRServer()
        crimes_reporting = 1 if config.get_str("EDRCrimesReporting") == "True" else 0
        self.server.crimes_reporting = bool(crimes_reporting)
        self._crimes_reporting = tk.IntVar(value=crimes_reporting)
        
        anonymous_reports = _(u"Auto")
        self.server.anonymous_reports = None
        if config.get_str("EDRRedactMyInfo") in [_(u"Always"), _(U"Never")]:
            anonymous_reports = config.get_str("EDRRedactMyInfo")
            self.server.anonymous_reports = anonymous_reports == _(u"Always")
        self._anonymous_reports = tk.StringVar(value=anonymous_reports)

        fc_jump_psa = _(u"Never")
        self.server.fc_jump_psa = None
        if config.get_str("EDRFCJumpPSA") in [_(u"Public"), _(U"Private"), _(u"Direct")]:
            fc_jump_psa = config.get_str("EDRFCJumpPSA")
            self.server.fc_jump_psa = fc_jump_psa == _(u"Public")
        self._fc_jump_psa = tk.StringVar(value=fc_jump_psa)

        
        self.realtime_params = {
            EDROpponents.OUTLAWS: self.__get_realtime_params("EDROutlawsAlerts"),
            EDROpponents.ENEMIES: self.__get_realtime_params("EDREnemiesAlerts")
        }
 
        self.edsm_server = EDSMServer()
        self.edrfactions = EDRFactions(self.edsm_server)
        self.edrsystems = EDRSystems(self.server, self.edsm_server, self.edrfactions)
        self.edrresourcefinder = EDRResourceFinder(self.edrsystems, self.edrfactions)
        self.edrboi = EDRBodiesOfInterest()
        self.edrcmdrs = EDRCmdrs(self.server)
        self.edropponents = {
            EDROpponents.OUTLAWS: EDROpponents(self.server, EDROpponents.OUTLAWS, self._realtime_callback),
            EDROpponents.ENEMIES: EDROpponents(self.server, EDROpponents.ENEMIES, self._realtime_callback),
        }
        self.edrlegal = EDRLegalRecords(self.server)

        self.mandatory_update = False
        self.autoupdate_pending = False
        self.motd = []
        self.tips = RandomTips()
        self.help_content = HelpContent()
        self._throttle_until_timestamp = None
        self.edrfssinsights = EDRFSSInsights()
        self.edrdiscord = EDRDiscordIntegration(self.edrcmdrs)
        self.edrcommands = EDRCommands(self)
        
    def __get_realtime_params(self, kind):
        min_bounty = None
        key = "{}MinBounty".format(kind)
        try:
            min_bounty = config.get_str(key)
        except:
            min_bounty = config.get_int(key)
        
        if min_bounty == "None":
            min_bounty = None

        max_distance = None
        key = "{}MaxBounty".format(kind)
        try:
            max_distance = config.get_str(key)
        except:
            max_distance = config.get_int(key)
        
        if max_distance == "None":
            max_distance = None

        return { "min_bounty": min_bounty, "max_distance": max_distance} 
    
    def loud_audio_feedback(self):
        config.set("EDRAudioFeedbackVolume", "loud")
        self.SFX.loud()
        # Translators: this is shown on EDMC's status bar when a user enables loud audio cues
        self.status = _(u"loud audio cues.")

    def soft_audio_feedback(self):
        config.set("EDRAudioFeedbackVolume", "soft")
        self.SFX.soft()
        # Translators: this is shown on EDMC's status bar when a user enables soft audio cues
        self.status = _(u"soft audio cues.")

    def apply_config(self):
        c_email = config.get_str("EDREmail")
        c_password = config.get_str("EDRPassword")
        c_visual_feedback_type = config.get_str("EDRVisualFeedback2") or (_("Enabled") if config.get_str("EDRVisualFeedback") == "True" else _("Disabled"))
        c_visual_alt_feedback = config.get_str("EDRVisualAltFeedback")
        c_audio_feedback = config.get_str("EDRAudioFeedback")
        c_audio_volume = config.get_str("EDRAudioFeedbackVolume")
        c_gesture_triggers = config.get_str("EDRGestureTriggers")
        c_redact_my_info = config.get_str("EDRRedactMyInfo")
        c_crimes_reporting = config.get_str("EDRCrimesReporting")
        c_fc_jump_announcements = config.get_str("EDRFCJumpPSA")

        if c_email is None:
            self._email.set("")
        else:
            self._email.set(c_email)

        if c_password is None:
            self._password.set("")
        else:
            self._password.set(c_password)

        self.visual_feedback_type = c_visual_feedback_type
        
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

        if c_gesture_triggers is None or c_gesture_triggers == "False":
            self._gesture_triggers.set(0)
        else:
            self._gesture_triggers.set(1)

        if c_redact_my_info is None:
            self.anonymous_reports = _(u"Auto")
        elif c_redact_my_info in [_(u"Always"), _(u"Never")]:
            self.anonymous_reports = c_redact_my_info

        if c_crimes_reporting is None or c_crimes_reporting == "True":
            self._crimes_reporting.set(1)
        else:
            self._crimes_reporting.set(0)

        if c_fc_jump_announcements is None:
            self.fc_jump_psa = _(u"Never")
        elif c_fc_jump_announcements in [_(u"Public"), _(u"Private")]:
            self.fc_jump_psa = c_fc_jump_announcements


    def check_version(self):
        version_range = self.server.server_version()
        self.motd = _edr(version_range["l10n_motd"])

        if version_range is None:
            # Translators: this is shown on EDMC's status bar when the version check fails
            self.status = _(u"check for version update has failed.")
            return

        if self.is_obsolete(version_range["min"]):
            EDR_LOG.log(u"Mandatory update! {version} vs. {min}"
                       .format(version=self.edr_version, min=version_range["min"]), "ERROR")
            self.mandatory_update = True
            self.autoupdate_pending = version_range.get("autoupdatable", False)
            self.__status_update_pending()
        elif self.is_obsolete(version_range["latest"]):
            EDR_LOG.log(u"EDR update available! {version} vs. {latest}"
                       .format(version=self.edr_version, latest=version_range["latest"]), "INFO")
            self.mandatory_update = False
            self.autoupdate_pending = version_range.get("autoupdatable", False)
            self.__status_update_pending()

    def is_obsolete(self, advertised_version):
        client_parts = list(map(int, self.edr_version.split('.')))
        advertised_parts = list(map(int, advertised_version.split('.')))
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
        if self.client_ui:
            self.client_ui.nolink()

    def linkable_status(self, link, new_status = None):
        short_link = (link[:30] + u'…') if link and len(link) > 30 else link
        self._status.set(new_status if new_status else short_link)
        if self.client_ui:
            self.client_ui.link(link)

    @property
    def visual_feedback(self):
        if self._visual_feedback == 0:
            return False
        
        if not self.IN_GAME_MSG:
             standalone_overlay = self.visual_feedback_type == _("Standalone (for VR or multi-display)")
             self.IN_GAME_MSG = InGameMsg(standalone = standalone_overlay)
        return True

    @visual_feedback.setter
    def visual_feedback(self, new_value):
        self._visual_feedback = new_value

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
    def gesture_triggers(self):
        return self._gesture_triggers.get() == 1

    @gesture_triggers.setter
    def gesture_triggers(self, new_value):
        self._gesture_triggers.set(new_value)

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

    @property
    def crimes_reporting(self):
        return self._crimes_reporting.get() == 1

    @crimes_reporting.setter
    def crimes_reporting(self, new_value):
        self._crimes_reporting.set(new_value)

    @property
    def fc_jump_psa(self):
        return self._fc_jump_psa.get()

    @fc_jump_psa.setter
    def fc_jump_psa(self, new_value):
        self._fc_jump_psa.set(new_value)
        if new_value is None or new_value == _(u"Never"):
            self.server.fc_jump_psa = None
        elif new_value in [_(u"Public"), _(u"Private"), _(u"Direct")]:
            self.server.fc_jump_psa = (new_value == _(u"Public")) 

    @property
    def visual_feedback_type(self):
        return self._visual_feedback_type.get()

    @visual_feedback_type.setter
    def visual_feedback_type(self, new_value):
        self._visual_feedback_type.set(new_value)
        if new_value is None or new_value == _(u"Disabled"):
            self.visual_feedback = 0
            if self.IN_GAME_MSG:
                self.IN_GAME_MSG.shutdown()
                self.IN_GAME_MSG = None
        else:
            self.visual_feedback = 1
            standalone_overlay = new_value == _("Standalone (for VR or multi-display)")
            if self.IN_GAME_MSG and self.IN_GAME_MSG.standalone_overlay != standalone_overlay:
                self.IN_GAME_MSG.shutdown()
                self.IN_GAME_MSG = None
                self.IN_GAME_MSG = InGameMsg(standalone = standalone_overlay)

    def player_name(self, name):
        self.edrcmdrs.set_player_name(name)
        self.server.set_player_name(name)

    def game_mode(self, mode, group = None):
        self.player.game_mode = mode
        self.player.private_group = group  
        self.server.set_game_mode(mode, group)

    def set_dlc(self, dlc):
        self.player.dlc_name = dlc
        self.server.set_dlc(dlc)
        self.edrsystems.set_dlc(dlc)
        self.edrboi.set_dlc(dlc)
        self.edrresourcefinder.set_dlc(dlc)

    def pledged_to(self, power, time_pledged=0):
        if self.server.is_anonymous():
            EDR_LOG.log(u"Skipping pledged_to call since the user is anonymous.", "INFO")
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
        EDR_LOG.log(u"Warming up client.", "INFO")
        details = []
        if not self.crimes_reporting:
            details.append(_(u"Crimes reporting is off (!crimes on to re-enable)"))
        if self.mandatory_update:
            # Translators: this is shown when EDR warms-up via the overlay if there is a mandatory update pending
            details = [_(u"Mandatory update!")]
        details += self.motd
        # Translators: this is shown when EDR warms-up via the overlay, the -- are for presentation purpose
        if self.IN_GAME_MSG and self.IN_GAME_MSG.compatibility_issue and self.IN_GAME_MSG.standalone_overlay:
            details.append(_(u"Standalone overlay requires EDMCOverlay Version >= 1.1."))
            details.append(_(u"Try to disable / upgrade the global EDMCOverlay module."))
        else:
            details.append(_(u"-- Feeling lost? Send !help via the in-game chat --"))
            details.append(self.tips.tip())
        # Translators: this is shown when EDR warms-up via the overlay
        self.__notify(_(u"EDR v{} by LeKeno").format(self.edr_version), details, clear_before=True)
        if self.audio_feedback:
            self.SFX.startup()
        if self.client_ui:
            self.client_ui.enable_entry()

    def shutdown(self, everything=False):
        self.edrcmdrs.persist()
        self.player.persist()
        self.edrsystems.persist()
        self.edrfactions.persist()
        for kind in self.edropponents:
            self.edropponents[kind].persist()
            self.edropponents[kind].shutdown_comms_link()
        self.edrlegal.persist()
        if self.IN_GAME_MSG:
            self.IN_GAME_MSG.shutdown()
        if self.client_ui:
            self.client_ui.disable_entry()
        config.set("EDRVisualAltFeedback", "True" if self.visual_alt_feedback else "False")

        if not everything:
            return
        
        self.server.logout()

    def app_ui(self, parent):
        if self.client_ui is None:
            self.client_ui = EDRClientUI(self, parent)
        self.check_version()
        return self.client_ui.app_ui()

    def prefs_ui(self, parent):
        return self.client_ui.prefs_ui(parent)

    def __status_update_pending(self):
        # Translators: this is shown in EDMC's status
        if self.autoupdate_pending:
            self.status = _(u"mandatory update pending (relaunch EDMC)") if self.mandatory_update else _(u"update pending (relaunch EDMC to apply)")
        else:
            # Translators: this is shown in EDMC's status
            status = _(u"mandatory EDR update!") if self.mandatory_update else _(u"please update EDR!")
            link = "https://edrecon.com/latest"
            self.linkable_status(link, status)

    def on_foot(self):
        self.player.in_spacesuit()
        if self.IN_GAME_MSG:
            self.IN_GAME_MSG.on_foot_layout()
        

    def in_ship(self):
        self.player.in_spacesuit()
        if self.IN_GAME_MSG:
            self.IN_GAME_MSG.in_ship_layout()

    def prefs_changed(self):
        set_language(config.get_str("language"))
        if self.mandatory_update:
            EDR_LOG.log(u"Out-of-date client, aborting.", "ERROR")
            self.__status_update_pending()
            return

        config.set("EDREmail", self.email)
        config.set("EDRPassword", self.password)
        visual_feedback_type = self.visual_feedback_type
        config.set("EDRVisualFeedback2", visual_feedback_type)
        # Note: ugly stuff to trigger the setter with the side-effects behaviors... 
        self.visual_feedback_type = visual_feedback_type
        config.set("EDRAudioFeedback", "True" if self.audio_feedback else "False")
        config.set("EDRRedactMyInfo", self.anonymous_reports)
        config.set("EDRCrimesReporting", "True" if self.crimes_reporting else "False")
        config.set("EDRFCJumpPSA", self.fc_jump_psa)
        EDR_LOG.log(u"Audio cues: {}, {}".format(config.get_str("EDRAudioFeedback"),
                                                config.get_str("EDRAudioFeedbackVolume")), "DEBUG")
        EDR_LOG.log(u"Anonymous reports: {}".format(config.get_str("EDRRedactMyInfo")), "DEBUG")
        EDR_LOG.log(u"Crimes reporting: {}".format(config.get_str("EDRCrimesReporting")), "DEBUG")
        if self.client_ui:
            self.client_ui.refresh_theme()
        self.login()

    def process_sent_message(self, entry):
        if self.client_ui:
            self.client_ui.enable_entry()
        
        return self.edrcommands.process(entry["Message"], entry.get("To", None))

    def noteworthy_about_system(self, fsdjump_event):
        if fsdjump_event["SystemSecurity"]:
            self.player.location_security(fsdjump_event["SystemSecurity"])
        self.edrsystems.system_id(fsdjump_event['StarSystem'], may_create=True, coords=fsdjump_event.get("StarPos", None))
        self.edrfactions.process_jump_event(fsdjump_event)
        facts = self.edrresourcefinder.assess_jump(fsdjump_event, self.player.inventory)
        header = _('Rare materials in {} (USS-HGE/EE, Mission Rewards)').format(fsdjump_event['StarSystem'])
        if not facts:
            facts = self.edrboi.bodies_of_interest(fsdjump_event['StarSystem'])
            header = _('Noteworthy stellar bodies in {}').format(fsdjump_event['StarSystem'])
        
        if self.player.dlc_name == "odyssey":
            bio_info = self.edrsystems.biology_spots(self.player.star_system)
            if bio_info:
                body_count = self.edrsystems.body_count(self.player.star_system)
                facts.append(_("Bio-suitable: {} [{} among {} known bodies]").format(", ".join(bio_info), len(bio_info), body_count))
        

        if not facts:
            if self.player.in_bad_neighborhood() and (self.edrsystems.in_bubble(self.player.star_system, 700) or self.edrsystems.in_colonia(self.player.star_system, 350)):
                header = _(u"Anarchy system")
                facts = [_(u"Crimes will not be reported.")]
            else:
                return False
            
        self.__notify(header, facts, clear_before = True)
        return True

    def noteworthy_about_settlement(self, entry):
        self.edrfactions.process_approach_event(entry, self.player.star_system)
        if "StationFaction" not in entry or "Name" not in entry:
            return
        
        details = []
        name = entry.get("Name", _("Settlement"))
        economy = entry.get("StationEconomy_Localised", "ECO?")
        header = u"{settlementName} ({settlementEconomy})".format(settlementName=name, settlementEconomy=economy)
        
        factionName = entry["StationFaction"].get("Name", "???")
        faction = self.edrfactions.get(factionName, self.player.star_system)
        details = self.describe_ed_settlement(entry, faction)
        self.__notify(header, details, clear_before=True)

    def describe_ed_settlement(self, entry, faction):
        details = []
        if entry["event"] != "ApproachSettlement":
            return details
        
        settlement_services = (entry.get("StationServices", []) or [])
        
        a = u"●" if "refuel" in settlement_services else u"◌"
        b = u"●" if "repair" in settlement_services else u"◌"
        c = u"●" if "rearm" in settlement_services else u"◌"
        details.append(_(u"Refuel:{}   Repair:{}   Restock:{}").format(a,b,c))
        
        a = u"●" if "commodities" in settlement_services else u"◌"
        b = u"●" if "blackmarket" in settlement_services else u"◌"
        c = u"●" if "facilitator" in settlement_services else u"◌"
        details.append(_(u"Market:{}   B.Market:{}   I.Factor:{}").format(a,b,c))
        
        if "StationFaction" in entry:
            factionName = entry["StationFaction"].get("Name", "???")
            qualifiers = []
            if "StationAllegiance" in entry:
                qualifiers.append(entry["StationAllegiance"])

            if "StationGovernment_Localised" in entry:
                qualifiers.append(entry["StationGovernment_Localised"])
            
            if faction and faction.isPMF != None:
                qualifiers.append(_("PMF: {}").format(u"●" if faction.isPMF else u"◌"))

            if entry["StationFaction"].get("FactionState", "").lower() not in ["", "none"]:
                qualifiers.append(entry["StationFaction"]["FactionState"])
            elif faction and faction.state and faction.state.lower() != "none":
                qualifiers.append(faction.state)
                
            if qualifiers:
                details.append("{name} ({qualifiers})".format(name=factionName, qualifiers=", ".join(qualifiers)))
            else:
                details.append("{name}".format(name=factionName))
            
        
        return details

    def docked_at(self, docking_entry):
        self.player.docked_at(docking_entry)
        self.edrfactions.process_docking_event(docking_entry, self.player.star_system)

    def process_location_event(self, entry):
        if not (entry and entry.get("event", "") == "Location"):
            return

        self.edrfssinsights.update_system(entry.get("SystemAddress", None), entry.get("StarSystem", None))
        self.edrfactions.process_location_event(entry)
        self.check_system(entry["StarSystem"], may_create=True, coords=entry.get("StarPos", None))
        
    def noteworthy_about_body(self, star_system, body_name):
        route_facts = self.player.routenav.noteworthy_about_body(star_system, body_name)
        
        pois = self.edrboi.points_of_interest(star_system, body_name)
        if pois:
            facts = [poi["title"] for poi in pois]
            if route_facts:
                facts.extend(route_facts)
            self.__notify(_(u'Noteworthy about {}: {} sites').format(body_name, len(facts)), facts, clear_before = True)
            return True
        
        materials_info = self.edrsystems.materials_on(star_system, body_name)
        facts = self.edrresourcefinder.assess_materials_density(materials_info, self.player.inventory)
        header = _("Noteworthy about {}").format(body_name)
        details = []

        if route_facts:
            details.extend(route_facts)

        if facts:
            qualifier = self.edrresourcefinder.raw_profile or _("Noteworthy")
            details.append(_(u'{} materials: {}').format(qualifier, ",".join(facts)))
        
        bio_info = self.edrsystems.biology_on(star_system, body_name)
        if bio_info and bio_info.get("species", None):
            details.append(_("Expected Bio: {}").format(", ".join(bio_info["species"])))
            progress = self.__biome_progress_oneliner(star_system, body_name)
            if progress:
                details.append(progress)

        if details:
            self.__notify(header, details, clear_before = True)

    def leave_body(self, star_system, body_name):
        place = "Supercruise"
        self.player.planetary_destination = None
        outcome = self.player.update_place_if_obsolete(place)
        outcome |= self.player.update_body_if_obsolete(None)

        if not self.player.routenav.leave_body(star_system, body_name):
            EDR_LOG.log("RouteNav: no update upon leaving a body {} in {}".format(body_name, star_system), "DEBUG")
            return outcome
        
        wp_sys_name = self.player.routenav.current_wp_sysname()
        if not wp_sys_name or wp_sys_name != star_system:
            EDR_LOG.log("RouteNav: updated from leave body but system {} is not the current waypoint {}".format(star_system, wp_sys_name), "DEBUG")
            return outcome
        
        details = self.player.routenav.describe_wp_bodies()
        EDR_LOG.log("RouteNav: waypoint bodies: {}".format(details), "DEBUG")
        if details:
            self.notify_with_details(_("EDR Journey: survey targets"), details, clear_before=True)
        return outcome
        

    def __biome_progress_oneliner(self, star_system, body_id_or_name):
        progress = self.edrsystems.analyzed_biome(star_system, body_id_or_name)
        genus_analyzed = progress["genuses"].get("analyzed", None)
        genus_detected = progress["genuses"].get("detected", None)
        genus_expected = progress["genuses"].get("expected", None)
        localized = progress["genuses"].get("localized", [])
        genus_localized = ", ".join(localized) if localized else "n/a"
        genus_bit = ""
        if genus_detected:
            genus_bit = _("genus {}/{};  analyzed: {}").format(genus_analyzed, genus_detected, genus_localized)
        elif genus_expected:
            genus_bit = _("genus {}/{}?;  analyzed: {}").format(genus_analyzed, genus_expected, genus_localized)
        else:
            genus_bit = _("genus {}/???;  analyzed: {}").format(genus_analyzed, genus_localized)

        species_analyzed = progress["species"].get("analyzed", None)
        species_bit = ""
        if species_analyzed:
            species_bit = _("; species {}").format(species_analyzed)
        
        if not genus_bit and not species_bit:
            return None
        return _("Progress: {}{}").format(genus_bit, species_bit)

    def noteworthy_about_scan(self, scan_event):
        if scan_event["event"] != "Scan" or not scan_event["ScanType"] in ["Detailed", "Basic", "AutoScan"]:
            return
        
        if "BodyName" not in scan_event:
            return
        
        # TODO tweak species info with mats coloring
        header = _(u'Noteworthy about {}').format(scan_event["BodyName"])
        star_system = scan_event.get("StarSystem", self.player.star_system)
        facts = []
        if scan_event["BodyName"]:
            value = self.edrsystems.body_value(star_system, scan_event["BodyName"])
            if value:
                flags = [] 
                if "wasDiscovered" in value:
                    flags.append(_(u"[KNOWN]") if value["wasDiscovered"] else _(u"[FIRST DISCOVERED]"))
                
                if "wasMapped" in value and "PlanetClass" in scan_event:
                    flags.append(_(u"[CHARTED]") if value["wasMapped"] else _(u"[UNCHARTED]"))

                if value.get("wasEfficient", False):
                    flags.append(_(u"[EFF. BONUS]"))

                flags = " ".join(flags)
                if pretty_print_number(value["valueMax"]) != pretty_print_number(value["valueScanned"]):
                    facts.append(_("Estimated value: {} cr (mapped: {}) @ {} LS; {}").format(pretty_print_number(value["valueScanned"]), pretty_print_number(value["valueMax"]), pretty_print_number(value["distance"]), flags))
                else:
                    facts.append(_("Estimated value: {} cr @ {} LS; {}").format(pretty_print_number(value["valueMax"]), pretty_print_number(value["distance"]), flags))

        bio_info = self.edrsystems.biology_on(star_system, scan_event["BodyName"])
        if bio_info and bio_info.get("species", None):
            facts.append(_("Expected Bio: {}").format(", ".join(bio_info["species"])))
            progress = self.__biome_progress_oneliner(star_system, scan_event["BodyName"])
            if progress:
                facts.append(progress)

        if "Materials" in scan_event:
            mats_assessment = self.edrresourcefinder.assess_materials_density(scan_event["Materials"], self.player.inventory)
            if mats_assessment:
                facts.extend(mats_assessment)
                qualifier = self.edrresourcefinder.raw_profile
                if qualifier:
                    header = _(u'Noteworthy about {} ({} mats)').format(scan_event["BodyName"], qualifier)
        
        if facts:
            self.__notify(header, facts, clear_before = True)

    
    def register_fss_signals(self, system_address=None, override_star_system=None, force_reporting=False):
        self.edrfssinsights.update_system(system_address or self.player.star_system_address, override_star_system or self.player.star_system)
        if self.edrfssinsights.reported:
            if force_reporting:
                # Skipping further FSS signals because the signals are additive only (no events for FC signals that are no longer relevant...)
                self.status = _(u"Skipped FC report for consistency reasons (fix: leave and come back)")
                new_fc = self.edrfssinsights.newly_found_fleet_carriers()
                if new_fc:
                    # Report new FC to help with CG (e.g. unloading/loading commodities from newly arrived FC)
                    # TODO this one gets in the way of the system value notification...
                    # self.notify_with_details(_(u"Discovered {} fleet carriers").format(len(new_fc)), ["{} : {}".format(callsign, new_fc[callsign]) for callsign in new_fc])
                    pass
            return
        fc_report = self.edrfssinsights.fleet_carriers_report(force_reporting)
        if fc_report is not None:
            EDR_LOG.log(u"Registering FSS signals; fc_report: {} with sys_address {} and star_system {}".format(fc_report, system_address, override_star_system), "DEBUG")
            fc_report["reportedBy"] = self.player.name
            if self.edrsystems.update_fc_presence(fc_report):
                self.edrfssinsights.reported = True
                if fc_report["fcCount"] <= 1:
                    self.status = _(u"Reported {} fleet carrier in system {}").format(fc_report["fcCount"], fc_report["starSystem"])
                else:
                    self.status = _(u"Reported {} fleet carriers in system {}").format(fc_report["fcCount"], fc_report["starSystem"])

    
    def noteworthy_about_signal(self, fss_event):
        self.edrfssinsights.process(fss_event)
        facts = self.edrresourcefinder.assess_signal(fss_event, self.player.location, self.player.inventory)
        if facts:
            header = _(u'Signal Insights (potential outcomes)')
            self.__notify(header, facts, clear_before = True)
            return True

    def noteworthy_signals_in_system(self):
        self.edrfssinsights.update(self.player.star_system)
        
        if not self.edrfssinsights.noteworthy:
            return False
        summary = self.edrfssinsights.summarize()
        if not summary:
            return False
        header = _(u"Known signals in {system}").format(system=self.player.star_system)
        self.__notify(header, summary, clear_before = True)
        return True

    def process_scan(self, scan_event):
        if scan_event["event"] == "Scan":
            return self.__process_space_scan(scan_event)
        elif scan_event["event"] == "ScanOrganic":
            result = self.player.process_organic_scan(scan_event)
            self.edrsystems.reflect_organic_scan(self.player.star_system, scan_event["Body"], scan_event)
            if scan_event["ScanType"] == "Analyse":
                progress = self.edrsystems.analyzed_biome(self.player.star_system, scan_event["Body"])
                details = []
                genus_analyzed = progress["genuses"].get("analyzed", "1+?") # should be at least 1
                genus_detected = progress["genuses"].get("detected", None)
                genus_expected = progress["genuses"].get("expected", None)
                genus_localized = progress["genuses"].get("localized", None)
                genus_togo = progress["genuses"].get("togo", None)
                if genus_detected:
                    details.append(_("Genus: {}/{}").format(genus_analyzed, genus_detected))
                elif genus_expected:
                    details.append(_("Genus: {}/{}").format(genus_analyzed, genus_expected))
                else:
                    details.append(_("Genus: {}/???").format(genus_analyzed))
                
                if genus_localized:
                    details.append(_(" - analyzed: {}").format(", ".join(genus_localized)))
                    
                if genus_togo:
                    genuses_credits = []
                    for g in genus_togo:
                        if not genus_togo[g]["credits"]:
                            genuses_credits.append(genus_togo[g]["localized"])
                            continue
                        
                        if genus_togo[g]["credits"]["min"] == genus_togo[g]["max"]:
                            value = pretty_print_number(genus_togo[g]["max"])
                            genuses_credits.append("{} ({} cr)".format(genus_togo[g]["localized"], value))
                            continue

                        min_value = pretty_print_number(genus_togo[g]["min"])
                        max_value = pretty_print_number(genus_togo[g]["max"])
                        genuses_credits.append("{} ({} ~ {} cr)".format(genus_togo[g]["localized"], min_value, max_value))
                        
                    details.append(_(" - remaining: {}").format(", ".join(genuses_credits)))
                
                species_analyzed = progress["species"].get("analyzed", "1+?") # should be at least 1
                details.append(_("Species: {}").format(species_analyzed))

                if not genus_togo:
                    surveyed = self.player.routenav.surveyed_body(self.player.star_system, self.player.body)
                    if surveyed:
                        other_bodies = self.player.routenav.wp_bodies_to_survey(self.player.star_system)
                        if other_bodies:
                            details.append(_("To survey: {}").format(", ".join(other_bodies)))
                        else:
                            details.append(_("Waypoint completed; Use '!journey next' to advance."))
                
                self.__notify(_("Biome analysis progress"), details, clear_before=True)
            
            return result
        return False
        
    def __process_space_scan(self, scan_event):
        self.edrsystems.reflect_scan(self.player.star_system, scan_event["BodyName"], scan_event)
        if "Materials" not in scan_event:
            return False
        self.edrsystems.materials_info(self.player.star_system, scan_event["BodyName"], scan_event["Materials"])

    def closest_poi_on_body(self, star_system, body_name, attitude):
        body = self.edrsystems.body(star_system, body_name)
        radius = body.get("radius", None) if body else None
        return self.edrboi.closest_point_of_interest(star_system, body_name, attitude, radius)

    def navigation(self, latitude, longitude, title="Navpoint"):
        position = {"latitude": float(latitude), "longitude": float(longitude)}
        boi = {}
        poi = {}
        body = self.player.body or "unknown body"
        poi[body.lower()] = [{
            "title": title,
            "latitude": float(latitude),
            "longitude": float(longitude)
        }]
        boi[self.player.star_system.lower()] = poi
        copy(json.dumps(boi))
        loc = EDPlanetaryLocation(position)
        if loc.valid():
            self.player.planetary_destination = loc
            self.__notify(_(u'Assisted Navigation'), [_(u"Destination set to {} | {}").format(latitude, longitude), _(u"Guidance will be shown when approaching a stellar body"), _(u"Destination added to the clipboard")], clear_before = True)
        else:
            self.player.planetary_destination = None
            self.__notify(_(u'Assisted Navigation'), [_(u"Invalid destination")], clear_before = True)

    def docking_guidance(self, entry):
        if not self.visual_feedback:
            # TODO only works if visual feedback is allowed due to how the docking feature is tied to IN_GAME_MSG which can be None if visual feedback is turned off
            return
        if entry["event"] == "DockingGranted":
            station = self.edrsystems.station(self.player.star_system, entry["StationName"], entry["StationType"])
            faction = None
            if station and "controllingFaction" in station:
                controllingFaction = station["controllingFaction"]
                factionName = controllingFaction.get("Name", "???")
                faction = self.edrfactions.get(factionName, self.player.star_system)
        
            description = self.describe_station(station, faction)
            summary = self.IN_GAME_MSG.docking(self.player.star_system, station, entry["LandingPad"], faction, description)
            if summary:
                if self.client_ui:
                    self.client_ui.notify(summary["header"], summary["body"])
                if self.audio_feedback:
                    self.SFX.docking()
        else:
            self.IN_GAME_MSG.clear_docking()

    def describe_station(self, station, faction):
        if not station:
            return
        station_type = (station.get("type","N/A") or "N/A").lower()
        station_other_services = (station.get("otherServices", []) or []) 
        station_economy = (station.get('economy', "") or "").lower()
        station_second_economy = (station.get('secondEconomy', "") or "").lower()
        details = []
        a = u"◌" if station_type in ["outpost"] else u"●"
        b = u"●" if station.get("haveOutfitting", False) else u"◌"
        c = u"●" if station.get("haveShipyard", False) else u"◌"
        details.append(_(u"LG. Pad:{}   Outfit:{}   Shipyard:{}").format(a,b,c))
        a = u"●" if "Refuel" in station_other_services else u"◌"
        b = u"●" if "Repair" in station_other_services else u"◌"
        c = u"●" if "Restock" in station_other_services else u"◌"
        details.append(_(u"Refuel:{}   Repair:{}   Restock:{}").format(a,b,c))
        a = u"●" if station.get("haveMarket", False) else u"◌"
        b = u"●" if "Black Market" in station_other_services else u"◌"
        c = u"◌"
        m = _c(u"material trader|M.") 
        if "Material Trader" in station_other_services:
            c = u"●"
            if station_economy in ['extraction', 'refinery']:
                if not station["secondEconomy"]:
                    m = _(u"RAW")
                elif station_second_economy == "industrial":
                    m = _(u"R/M")
                elif station_second_economy in ["high tech", "military"]:
                    m = _(u"R/E")
            elif station_economy == 'industrial':
                if not station["secondEconomy"]:
                    m = _(u"MAN")
                elif station_second_economy in ["extraction", "refinery"]:
                    m = _(u"M/R")
                elif station_second_economy in ["high tech", "military"]:
                    m = _(u"M/E")
            elif station_economy in ['high tech', 'military']:
                if not station["secondEconomy"]:
                    m = _(u"ENC")
                elif station_second_economy in ["extraction", "refinery"]:
                    m = _(u"E/R")
                elif station_second_economy == "industrial":
                    m = _(u"E/M")
        details.append(_(u"Market:{}   B.Market:{}   {} Trad:{}").format(a,b,m,c))
        a = u"●" if "Interstellar Factors Contact" in station_other_services else u"◌"
        t = _c(u"tech broker|T.")
        b =  u"◌" 
        if "Technology Broker" in station_other_services:
            b = u"●"
            if station_economy == 'high tech':
                if not station["secondEconomy"]:
                    t = _c(u"guardian tech|GT.")
                elif station_second_economy == "industrial":
                    t = _c(u"ambiguous tech|T.")
            elif station_economy == 'industrial':
                if not station["secondEconomy"]:
                    t = _c(u"human tech|HT.") 
                elif station_second_economy == "high tech":
                    t = _c(u"ambiguous tech|T.")

        details.append(_(u"I.Factor:{}   {} Broker:{}").format(a,t,b))
        if "controllingFaction" in station:
            controllingFaction = station["controllingFaction"]
            controllingFactionName=controllingFaction.get("name", "???")

            qualifiers = []

            if "allegiance" in station:
                qualifiers.append(station["allegiance"])

            if "government" in station:
                qualifiers.append(station["government"])
            
            if faction:
                if faction.state != None and faction.state.lower() != "none":
                    qualifiers.append(faction.state)

                if faction.isPMF != None:
                    qualifiers.append(_("PMF: {}").format(u"●" if faction.isPMF else u"◌"))

            if qualifiers:
                details.append("{name} ({qualifiers})".format(name=controllingFactionName, qualifiers=", ".join(qualifiers)))
            else:
                details.append("{name}".format(name=controllingFactionName))

        updated = EDTime()
        updated.from_edsm_timestamp(station['updateTime']['information'])
        details.append(_(u"as of {date}").format(date=updated.as_local_timestamp()))
        return details

    def destination_guidance(self, destination):
        if not self.player.set_destination(destination):
            return

        if not self.player.has_destination():
            return

        if not self.player.in_game:
            return
        
        dst = self.player.destination
        body_id = dst.body
        name = dst.name
        system_address = dst.system
        
        if not self.edrfssinsights.same_system(system_address) and body_id == 0:
            if self.system_guidance(name, passive=True):
                return
        
        if self.edrfssinsights.is_signal(name):
            if self.edrfssinsights.is_uss(name):
                # TODO show materials for uss? Possible?
                return
            if self.edrfssinsights.is_nav_beacon(name):
                # TODO show materials for system? Possible?
                return
            if self.edrfssinsights.is_scenario_signal(name):
                return
            if self.edrfssinsights.is_station(name):
                self.station_in_current_system(name, passive=True)
                return
        
            if dst.is_fleet_carrier():
                fc_regexp = r"^(?:.+ )?([A-Z0-9]{3}-[A-Z0-9]{3})$"
                m = re.match(fc_regexp, name)
                callsign = m.group(1)
                self.fc_in_current_system(callsign)
                return
            return
        
        # check if body > 0 ?
        # TODO value of system if different system
        if self.body_guidance(self.player.star_system, name, passive=True):
            return

        ## for the outpost/... cases that aren't marked as stations
        if self.station_in_current_system(name, passive=True):
            return

        # last resort?
        if self.edrfssinsights.no_signals():
            if self.edrfssinsights.is_scenario_signal(name):
                return
            if self.edrfssinsights.is_station(name):
                self.station_in_current_system(name, passive=True)
                return
        
            if dst.is_fleet_carrier():
                fc_regexp = r"^(?:.+ )?([A-Z0-9]{3}-[A-Z0-9]{3})$"
                m = re.match(fc_regexp, name)
                callsign = m.group(1)
                self.fc_in_current_system(callsign)
                return

    def system_value(self, star_system=None):
        # avoid belts since it's noisy and worthless
        if star_system is None:
            star_system = self.player.star_system
        sys_value = self.edrsystems.system_value(star_system)
        if sys_value:
            details = []
            estimatedValue = pretty_print_number(sys_value["estimatedValue"]) if "estimatedValue" in sys_value else "?"
            estimatedValueMapped = pretty_print_number(sys_value["estimatedValueMapped"]) if "estimatedValueMapped" in sys_value else "?"
            if estimatedValueMapped != estimatedValue:
                details.append(_("Scanned: {}, Mapped: {}").format(estimatedValue, estimatedValueMapped))
            else:
                details.append(_("Scanned: {}").format(estimatedValue))
            
            valuableBodies = sorted(sys_value.get("valuableBodies", []), key=lambda b: b['valueMax'], reverse=True)

            first_disco = 0
            first_map = 0
            top = 5
            extra_details = []
            for body in valuableBodies:
                adjBodyName = simplified_body_name(star_system, body.get("bodyName", "?"), " 0")
                flags = []
                if "wasDiscovered" in body and body["wasDiscovered"] == False:
                    first_disco += 1
                    if top:
                        flags.append(_(u"[FIRST SCAN]") if body.get("scanned", False) else _(u"[UNKNOWN]"))

                if "wasMapped" in body and body["wasMapped"] == False and body.get("type", "") == "planet":
                    first_map += 1
                    if top:
                        flags.append(_(u"[FIRST MAP]") if body.get("mapped", False) else _(u"[UNCHARTED]"))

                if top <= 0:
                    continue
                
                flags = " ".join(flags)
                if pretty_print_number(body["valueMax"]) != pretty_print_number(body["valueScanned"]):
                    extra_details.append(_("{}: {} (mapped: {}) @ {} LS    {}").format(adjBodyName, pretty_print_number(body["valueScanned"]), pretty_print_number(body["valueMax"]), pretty_print_number(body["distance"]), flags))
                else:
                    extra_details.append(_("{}: {} @ {} LS    {}").format(adjBodyName, pretty_print_number(body["valueScanned"]), pretty_print_number(body["distance"]), flags))   
                top -= 1
            
            firsts = ""
            if first_disco or first_map:
                if first_disco and first_map:
                    firsts = _("Unknown: {}, Uncharted: {}").format(first_disco, first_map)
                elif first_disco:
                    firsts = _("Unknown: {}").format(first_disco)
                else:
                    firsts = _("Uncharted: {}").format(first_map)
            if "progress" in sys_value and sys_value["progress"] < 1.0 and sys_value.get("bodyCount", None):
                body_count = sys_value["bodyCount"]
                scanned_body_count = round(body_count * sys_value["progress"])
                progress = int(sys_value["progress"]*100.0)
                details.append(_("Discovered {}/{} {}%    {}").format(scanned_body_count, body_count, progress, firsts))
            elif first_disco or first_map:
                details.append(firsts)
            
            details.extend(extra_details)
            self.__notify(_("Estimated value of {}").format(star_system), details, clear_before= True)

    def saa_scan_complete(self, entry):
        self.edrsystems.saa_scan_complete(self.player.star_system, entry)
        self.player.location.from_entry(entry)
        
        bodyname = entry.get("BodyName", None)
        checked_off = self.player.routenav.mapped_body(self.player.star_system, bodyname)
        if checked_off:
            other_bodies = self.player.routenav.wp_bodies_to_survey(self.player.star_system)
            details = []
            if other_bodies:
                if len(other_bodies) > 1:
                    details.append(_("{} bodies to check: {}").format(len(other_bodies), ", ".join(other_bodies)))
                else:
                    details.append(_("1 body to check: {}").format(", ".join(other_bodies)))
            else:
                details.append(_("Waypoint completed; Use '!journey next' to advance."))
                
            self.__notify(_("Bodies survey progress"), details, clear_before=True)
        
        
    def biology_on(self, body_name, star_system=None):
        star_system = star_system or self.player.star_system
        bio_info = self.edrsystems.biology_on(star_system, body_name)
        
        if not body_name or body_name.lower() == "unknown":
            return
        
        header = _("Biome assessment for {}").format(body_name)
        details = []
        
        if not (bio_info and "species" in bio_info):
            body_name = star_system + " " + body_name
            bio_info = self.edrsystems.biology_on(star_system, body_name)

        if not (bio_info and "species" in bio_info):
            EDR_LOG.log("No bio on {}".format(bio_info), "INFO")
            details.append(_("Expected Bio: none"))
            self.__notify(header, details, clear_before=True)
            return

        details.append(_("Expected Bio: {}").format(", ".join(bio_info["species"])))
        progress = self.__biome_progress_oneliner(self.player.star_system, body_name)
        if progress:
            details.append(progress)
        self.__notify(header, details, clear_before=True)

    def biology_spots(self, star_system):
        bio_info = self.edrsystems.biology_spots(star_system)
        body_count = self.edrsystems.body_count(star_system)
        header = _("Bodies suitable for exobiology in {}").format(star_system)
        details = []
        if bio_info:
            details.append(", ".join(bio_info))
        else:
            details.append(_("None detected"))
        details.append(_("[among {} known bodies]").format(body_count))
                
        self.__notify(header, details, clear_before=True)

    def body_signals_found(self, entry):
        self.edrsystems.body_signals_found(self.player.star_system, entry)
        body_name = entry["BodyName"]
        details = []
        if "Signals" in entry:
            signals = []
            for s in entry["Signals"]:
                name = s["Type_Localised"] if "Type_Localised" in s else s.get("Type", _("???"))
                count = s.get("Count", _("???"))
                signals.append("{}: {}".format(name, count))

            if signals:
               details.extend(signals)
        
        if "Genuses" in entry:
            bio_info = self.edrsystems.biology_on(self.player.star_system, body_name)
            # TODO some assessment step => reorder, add credit estimates?
            if bio_info and bio_info.get("species", None):
                details.append(_("Expected Bio: {}").format(", ".join(bio_info["species"])))
                progress = self.__biome_progress_oneliner(self.player.star_system, body_name)
                if progress:
                    details.append(progress)
        
        if details:
            self.__notify(_(u'Signals on {}').format(body_name), details, clear_before = True)

    def reflect_fss_discovery_scan(self, entry):
        self.edrsystems.fss_discovery_scan_update(entry)
        
    def process_codex_entry(self, entry):
        if entry.get("event", "") != "CodexEntry":
            return

        self.player.location.from_entry(entry)
        self.player.codex.process(entry)
        
        if entry.get("Category", "") != "$Codex_Category_Biology;" or entry.get("SubCategory", "") != "$Codex_SubCategory_Organic_Structures;":
            return
        
        if self.player.on_foot:
            EDR_LOG.log("Player is on foot, so no cutom POI from codex entry needed (not coming from the com scanner", "INFO")
            return
        now = datetime.datetime.now()
        name = entry.get("Name_Localised", "Comp.Scan")
        title = "{} ({})".format(name, now.strftime("%H:%M:%S"))
        
        if "Latitude" not in entry or "Longitude" not in entry:
            EDR_LOG.log("No Lat/Lon for codex", "WARNING")
            return

        poi = {
            "title": title,
            "latitude": entry["Latitude"],
            "longitude": entry["Longitude"],
            "heading": self.player.attitude.heading
        }
        system_name = entry["System"]
        body_name = self.edrsystems.body_name_with_id(system_name, entry["BodyID"])
        if not body_name:
            EDR_LOG.log("No body name found for codex with {}, {}".format(system_name, entry["BodyID"]), "WARNING")
            return

        if self.edrboi.add_custom_poi(system_name, body_name, poi):
            details = [
                _("Added a point of interest at the current position."),
                    _("Use the '!nav next' or '!nav previous! to select the next or previous POI."),
                    _("Use the 'stop' gesture or '!nav clear' to clear the current point of interest."),
                    _("Use the '!nav reset' to reset all custom POI for the current planet.")
            ]
            self.__notify(_("EDR Navigation (comp. scanner)"), details)

        
 
    def show_navigation(self):
        current = self.player.attitude
        destination = self.player.planetary_destination

        if not destination or not current:
            return
        
        if not current.valid() or not destination.valid():
            return

        bearing = destination.bearing(current)
        
        location = self.player.location
        body = self.edrsystems.body(location.star_system, location.body or location.place)
        radius = body.get("radius", None) if body else None
        distance = destination.distance(current, radius) if radius else None
        
        if distance is None:
            EDR_LOG.log(u"No distance info out of System:{}, Body:{}, Place: {}, Radius:{}".format(location.star_system, location.body, location.place, radius), "DEBUG")
            return
        
        threshold = 0.1
        if self.player.piloted_vehicle is None:
            threshold = 0.001
        elif EDVehicleFactory.is_surface_vehicle(self.player.piloted_vehicle):
            threshold = 0.01
        if distance <= threshold:
            return
        pitch = destination.pitch(current, distance) if distance and distance <= 700 else None
        
        if self.visual_feedback:
            self.IN_GAME_MSG.navigation(bearing, destination, distance, pitch) # TODO consider showing current heading for when on foot or an arrow for the direction to  aim for
            if self.audio_feedback:
                    self.SFX.navigation()
        self.status = _(u"> {:03} < for Lat:{:.4f} Lon:{:.4f}").format(bearing, destination.latitude, destination.longitude)

    def try_custom_poi(self):
        current = self.player.attitude
        if not current or not current.valid():
            return
        
        location = self.player.location
        body = self.edrsystems.body(location.star_system, location.body or location.place)
        radius = body.get("radius", None) if body else None

        star_system = location.star_system
        body_name = location.body or location.place
        if not star_system or not body_name:
            return
        
        poi = self.edrboi.closest_custom_point_of_interest(star_system, body_name, current, radius)
        if not poi:
            return

        self.player.planetary_destination = EDPlanetaryLocation(poi)
    
    def biology_guidance(self):
        current = self.player.attitude
        if not current or not current.valid():
            return
        
        genetic_sampler = self.player.closet.genetic_sampler
        locations = genetic_sampler.samples_locations()
        ccr = genetic_sampler.clonal_colony_range()
        species = genetic_sampler.species_tracked()
        credits = genetic_sampler.tracked_species_credits()
        
        location = self.player.location
        body = self.edrsystems.body(location.star_system, location.body or location.place)
        radius = body.get("radius", None) if body else None

        if not locations or ccr is None or not species:
            return
        
        if not genetic_sampler.has_samples_from(location.star_system_address, location.body_id):
            return

        distances = []
        bearings = []
        distances_summary = ""
        i = 1
        for loc in locations:
            poi = EDPlanetaryLocation()
            poi.update_from_obj(loc)
            bearing = poi.bearing(current)
            distance = poi.distance(current, radius) * 1000 if radius else None
            if distance is None:
                EDR_LOG.log(u"No distance info out of System:{}, Body:{}, Place: {}, Radius:{}".format(location.star_system, location.body, location.place, radius), "DEBUG")
                continue
            distances.append(distance)
            distances_summary += _(" [{loc_index}]: {dist}m  >{head:03}<").format(loc_index=i, dist=math.floor(distance), head=bearing)
            bearings.append(bearing)
            i += 1
        
        if self.visual_feedback:
            self.IN_GAME_MSG.biology_guidance(species, ccr, credits, distances,  bearings)
            if self.audio_feedback:
                self.SFX.biology()
        self.status = _(u"Value: {} cr; Gene diversity: +{}m => {}").format(pretty_print_number(credits), ccr, distances_summary)

    def check_system(self, star_system, may_create=False, coords=None):
        try:
            EDR_LOG.log(u"Check system called: {}".format(star_system), "INFO")
            details = []
            notams = self.edrsystems.active_notams(star_system, may_create, coords)
            if notams:
                EDR_LOG.log(u"NOTAMs for {}: {}".format(star_system, notams), "DEBUG")
                details += notams
            
            if self.edrsystems.has_sitrep(star_system):
                if star_system == self.player.star_system and self.player.in_bad_neighborhood():
                    EDR_LOG.log(u"Sitrep system is known to be an anarchy. Crimes aren't reported.", "INFO")
                    # Translators: this is shown via the overlay if the system of interest is an Anarchy (current system or !sitrep <system>)
                    details.append(_c(u"Sitrep|Anarchy: not all crimes are reported."))
                if self.edrsystems.has_recent_activity(star_system):
                    summary = self.edrsystems.summarize_recent_activity(star_system, self.player.power)
                    for section in summary:
                        details.append(u"{}: {}".format(section, "; ".join(summary[section])))
                    recent_outlaws = self.edrsystems.recent_outlaws(star_system)
                    summary_for_chat = ""
                    separator = "'' "
                    max_copy_pastable = 100
                    for outlaw in recent_outlaws:
                        if len(summary_for_chat) + len(separator) + len(outlaw) > max_copy_pastable:
                            break
                        if summary_for_chat != "":
                            summary_for_chat += " '{}'".format(outlaw)
                        else:
                            summary_for_chat = "'{}'".format(outlaw)
                    copy(summary_for_chat)
            
            #if self.player.routenav.is_waypoint(star_system):
            #    coords = self.edrsystems.system_coords(star_system)
            #    waypoint_details = self.player.routenav.describe_wp(coords)
            #    if waypoint_details:
            #        waypoint_details.append(_("Next waypoint has been placed in the clipboard."))
            #        self.__notify(_("EDR Journey"), waypoint_details, clear_before=True)
            
            if details:
                # Translators: this is the heading for the sitrep of a given system {}; shown via the overlay
                header = _(u"SITREP for {}") if self.player.in_open() else _(u"SITREP for {} (Open)")
                self.__sitrep(header.format(star_system), details)
        except CommsJammedError:
            self.__commsjammed()

    def mining_guidance(self):
        if self.visual_feedback:
            self.IN_GAME_MSG.mining_guidance(self.player.mining_stats)
            if self.audio_feedback:
                self.SFX.mining()
        
        if len(self.player.mining_stats.last["minerals_stats"]) > 0 and self.player.mining_stats.last["proportion"]:
            self.status = _(u"[Yield: {:.2f}%]   [Items: {} ({:.0f}/hour)]").format(self.player.mining_stats.last["proportion"], self.player.mining_stats.refined_nb, self.player.mining_stats.item_per_hour())
    
    def bounty_hunting_guidance(self, turn_off=False):
        if self.visual_feedback:
            if turn_off:
                self.IN_GAME_MSG.clear_bounty_hunting_guidance()
                return
            self.IN_GAME_MSG.bounty_hunting_guidance(self.player.bounty_hunting_stats)
            if self.audio_feedback:
                self.SFX.bounty_hunting()
        
        bounty = EDFineOrBounty(self.player.bounty_hunting_stats.last["bounty"])
        credits_per_hour = EDFineOrBounty(int(self.player.bounty_hunting_stats.credits_per_hour()))
        self.status = _(u"[Last: {} cr [{}]]   [Totals: {} cr/hour ({} awarded)]").format(bounty.pretty_print(), self.player.bounty_hunting_stats.last["name"], self.player.bounty_hunting_stats.awarded_nb, credits_per_hour.pretty_print())

    def target_guidance(self, target_event, turn_off=False):
        if turn_off or (not target_event or not self.player.target_pilot() or not self.player.target_pilot().vehicle):
            if self.visual_feedback:
                self.IN_GAME_MSG.clear_target_guidance()
            return
        
        tgt = self.player.target_vehicle() or self.player.target_pilot().vehicle
        meaningful = tgt.hull_health_stats().meaningful() or tgt.shield_health_stats().meaningful()
        
        subsys_details = None
        if "Subsystem" in target_event:
            meaningful = True # Class and Rank of submodule can be interesting info to show
            subsys_details = tgt.subsystem_details(target_event["Subsystem"])

        if not meaningful:
            EDR_LOG.log("Target info is not that interesting, skipping", "DEBUG")
            return False

        shield_label = u"{:.4g}".format(tgt.shield_health) if tgt.shield_health else u"-"
        hull_label = u"{:.4g}".format(tgt.hull_health) if tgt.hull_health else u"-"
        
        if subsys_details:
            self.status = _(u"S/H %: {}/{} - {} %: {:.4g}").format(shield_label, hull_label, subsys_details["shortname"], subsys_details["stats"].last_value())
        else:
            self.status = _(u"S/H %: {}/{}").format(shield_label, hull_label)
        
        if self.visual_feedback:
            self.IN_GAME_MSG.target_guidance(self.player.target_pilot(), subsys_details)
            if self.audio_feedback:
                self.SFX.target()

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
            EDR_LOG.log(u"NOTAMs for {}: {}".format(star_system, summary), "DEBUG")
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
                EDR_LOG.log(u"Cmdr {cmdr} known as id={cid}".format(cmdr=cmdr_name,
                                                                cid=profile.cid), "DEBUG")
                return profile.cid

            EDR_LOG.log(u"Failed to retrieve/create cmdr {}".format(cmdr_name), "ERROR")
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

    def eval_mission(self, entry, passive=True):
        if entry["event"] not in ["MissionAccepted", "MissionCompleted"]:
            return
        if entry["event"] == "MissionAccepted":
            commodity = entry.get("Commodity", None)
            if not commodity:
                return

            localized_commodity = entry.get("Commodity_Localised", commodity)
            description = self.player.describe_item(commodity)
            if not description:
                if not passive:
                    self.__notify(_(u"Mission Eval"), [_("Nothing noteworthy to share")], clear_before=True)
                return
            
            inventory_description = self.player.inventory.oneliner(commodity)
            details = []
            header = _(u"Eval of mission item : {}").format(localized_commodity)
            if inventory_description:
                header = _(u"Eval of mission item")
                details.append(inventory_description)
            details.extend(description)
            self.__notify(header, details, clear_before=True)
        elif entry["event"] == "MissionCompleted":
            if "MaterialsReward" not in entry:
                return
            details = []
            for reward in entry["MaterialsReward"]:
                commodity = reward["Name"]
                inventory_description = self.player.inventory.oneliner(commodity)
                if inventory_description:
                    details.append(inventory_description)
                description = self.player.describe_item(commodity)
                if description:
                    details.extend(description)
            if details:
                self.__notify(_("Mission rewards eval"), details, clear_before=True)
            elif not passive:
                self.__notify(_("Mission rewards eval"), [_("Nothing noteworthy to share")], clear_before=True)

    def eval(self, eval_type):
        canonical_commands = ["power", "backpack", "locker", "bar", "bar stock", "bar demand"]
        synonym_commands = {"power": ["priority", "pp", "priorities"]}
        supported_commands = set(canonical_commands + synonym_commands["power"])
        if eval_type not in supported_commands:
            description = self.player.describe_item(eval_type)
            if description:
                details = []
                inventory_description = self.player.inventory.oneliner(eval_type)
                if inventory_description:
                    details.append(inventory_description)
                details.extend(description)
                self.__notify(_(u"EDR Evals"), details, clear_before=True)
            else:
                self.__notify(_(u"EDR Evals"), [_(u"Yo dawg, I don't do evals for '{}'").format(eval_type), _(u"Try {} instead.").format(", ".join(canonical_commands)), _(u"Or specific materials (e.g. '!eval surveillance equipment').")], clear_before=True)
            return

        if eval_type == "power" or eval_type in synonym_commands["power"]:
            self.eval_build()
        elif eval_type == "backpack":
            self.eval_backpack()
        elif eval_type == "locker":
            self.eval_locker()
        elif eval_type in ["bar", "bar stock"]:
            self.eval_bar()
        elif eval_type == "bar demand":
            self.eval_bar(stock=False)

    def eval_build(self):
        if not self.player.mothership.update_modules():
            self.notify_with_details(_(u"Loadout information is stale"), [_(u"Congrats, you've found a bug in Elite!"), _(u"The modules info isn't updated right away :("), _(u"Try again after moving around or relog and check your modules.")])
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

    def eval_backpack(self, passive=False):
        micro_resources = dict(sorted(self.player.inventory.all_in_backpack().items(), key=lambda item: item[1], reverse=True))
        if micro_resources:
            details = self.__eval_micro_resources(micro_resources, from_backpack=True)
            if details:
                self.__notify(_("Backpack assessment"), details, clear_before=True)
            elif not passive:
                self.__notify(_("Backpack assessment"), [_(u"Nothing superfluous")], clear_before = True)
        elif not passive:
            self.__notify(_("Backpack assessment"), [_(u"Empty backpack?")], clear_before=True)

    def eval_locker(self, passive=False):
        micro_resources = dict(sorted(self.player.inventory.all_in_locker().items(), key=lambda item: item[1], reverse=True))
        if micro_resources:
            details = self.__eval_micro_resources(micro_resources)
            if details:
                self.__notify(_(u"Storage assessment"), details, clear_before=True)
            elif not passive:
                self.__notify(_("Storage assessment"), [_(u"Nothing superfluous")], clear_before=True)
        elif not passive:
            self.__notify(_("Storage assessment"), [_(u"Empty ship locker?")], clear_before=True)

    def eval_bar(self, stock=True):
        header = _("Bar: stock assessment") if stock else _("Bar: demand assessment")
        if not self.player.last_station or not self.player.last_station.type == "FleetCarrier" or not self.player.last_station.bar:
            self.__notify(header, [_(u"Unexpected state: either no fleet carrier, or no bar?")], clear_before = True)
            return False

        bar = self.player.last_station.bar
        items = bar.items_in_stock() if stock else bar.items_in_demand()
        if items:
            details = self.__eval_good_micro_resources(items) if stock else self.__eval_bad_micro_resources(items)
            if details:
                legend = [_(u"Kind: best items (b=blueprint, u=upgrades, x=trading, e=eng. unlocks)")] if stock else [_(u"Kind: worst items (b=blueprint, u=upgrades, x=trading, e=eng. unlocks)")]
                self.__notify(header, legend + details, clear_before=True)
                return True
            else:
                self.__notify(header, [_(u"Nothing noteworthy")], clear_before = True)
                return False
    
    def __eval_micro_resources(self, micro_resources, from_backpack=False):
        discardable = [self.player.inventory.oneliner(name, from_backpack) for name in micro_resources if (self.player.engineers.is_useless(name) and self.player.inventory.count(name, from_backpack=from_backpack, from_locker=not from_backpack))]
        unnecessary = [self.player.inventory.oneliner(name, from_backpack) for name in micro_resources if (self.player.engineers.is_unnecessary(name) and self.player.inventory.count(name, from_backpack=from_backpack, from_locker=not from_backpack))]
        details = []
        discardable = discardable[0:min(len(discardable), 3)]
        unnecessary = unnecessary[0:min(len(unnecessary), 3)]
        if discardable:
            details.append(_(u"Useless: {}").format(", ".join(discardable)))
        if unnecessary:
            details.append(_(u"Unnecessary: {}").format(", ".join(unnecessary)))
        return details

    def __eval_good_micro_resources(self, micro_resources):
        self_unlocking = [self.player.describe_odyssey_material_short(name) for name in micro_resources if self.player.engineers.is_necessary(name)]
        other_unlocking = [self.player.describe_odyssey_material_short(name) for name in micro_resources if (self.player.engineers.is_contributing(name) and self.player.engineers.is_unnecessary(name))]
        engineering_assets = [[self.player.describe_odyssey_material_short(name, ignore_eng_unlocks=True), self.player.remlok_helmet.how_useful(name)] for name in micro_resources if self.player.remlok_helmet.is_assets(name) and self.player.remlok_helmet.how_useful(name) > 0]
        engineering_goods = [[self.player.describe_odyssey_material_short(name, ignore_eng_unlocks=True), self.player.remlok_helmet.how_useful(name)] for name in micro_resources if self.player.remlok_helmet.is_goods(name) and self.player.remlok_helmet.how_useful(name) > 0]
        engineering_data = [[self.player.describe_odyssey_material_short(name, ignore_eng_unlocks=True), self.player.remlok_helmet.how_useful(name)] for name in micro_resources if self.player.remlok_helmet.is_data(name) and self.player.remlok_helmet.how_useful(name) > 0]
        sorted_engineering_assets = sorted(engineering_assets, key=lambda b: b[1], reverse=True)
        sorted_engineering_goods = sorted(engineering_goods, key=lambda b: b[1], reverse=True)
        sorted_engineering_data = sorted(engineering_data, key=lambda b: b[1], reverse=True)
        details = []
        if self_unlocking:
            details.append(_(u"Unlocks: {}").format(", ".join(self_unlocking)))
        if sorted_engineering_assets:
            details.append(_(u"Assets: {}").format(", ".join([pair[0] for pair in sorted_engineering_assets])))
        if sorted_engineering_goods:
            details.append(_(u"Goods: {}").format(", ".join([pair[0] for pair in sorted_engineering_goods])))
        if sorted_engineering_data:
            details.append(_(u"Data: {}").format(", ".join([pair[0] for pair in sorted_engineering_data])))
        if other_unlocking:
            details.append(_(u"Unlocked: {}").format(", ".join(other_unlocking)))
        return details

    def __eval_bad_micro_resources(self, micro_resources):
        other_unlocking = [self.player.describe_odyssey_material_short(name) for name in micro_resources if (self.player.engineers.is_contributing(name) and self.player.engineers.is_unnecessary(name) and self.player.inventory.count(name))]
        engineering_assets = [[self.player.describe_odyssey_material_short(name, ignore_eng_unlocks=True), self.player.remlok_helmet.how_useful(name)] for name in micro_resources if self.player.remlok_helmet.is_assets(name) and self.player.inventory.count(name)]
        engineering_goods = [[self.player.describe_odyssey_material_short(name, ignore_eng_unlocks=True), self.player.remlok_helmet.how_useful(name)] for name in micro_resources if self.player.remlok_helmet.is_goods(name) and self.player.inventory.count(name)]
        engineering_data = [[self.player.describe_odyssey_material_short(name, ignore_eng_unlocks=True), self.player.remlok_helmet.how_useful(name)] for name in micro_resources if self.player.remlok_helmet.is_data(name) and self.player.inventory.count(name)]
        sorted_engineering_assets = sorted(engineering_assets, key=lambda b: b[1])
        sorted_engineering_goods = sorted(engineering_goods, key=lambda b: b[1])
        sorted_engineering_data = sorted(engineering_data, key=lambda b: b[1])
        details = []
        if sorted_engineering_assets:
            details.append(_(u"Assets: {}").format(", ".join([pair[0] for pair in sorted_engineering_assets])))
        if sorted_engineering_goods:
            details.append(_(u"Goods: {}").format(", ".join([pair[0] for pair in sorted_engineering_goods])))
        if sorted_engineering_data:
            details.append(_(u"Data: {}").format(", ".join([pair[0] for pair in sorted_engineering_data])))
        if other_unlocking:
            details.append(_(u"Unlocked: {}").format(", ".join(other_unlocking)))
        return details

    def __summarize_fc_market(self, sale_orders, purchase_orders, max_len=2048):
        remaining = max_len
        details_purchases = []
        details_sales = []
        if sale_orders:
            sale_orders_with_value = [[sale_orders[order], self.player.remlok_helmet.how_useful(order), order] for order in sale_orders if self.player.remlok_helmet.how_useful(order) >= 0]
            sorted_sale_orders = sorted(sale_orders_with_value, key=lambda b: b[1], reverse=True)
            for order in sorted_sale_orders:
                quantity = pretty_print_number(order[0]["quantity"])
                item = order[0]["l10n"][:21].capitalize()
                price = pretty_print_number(order[0]["price"])
                worthy = self.player.remlok_helmet.worthiness_odyssey_material(order[2])
                if worthy:
                    details_sales.append(f'{quantity: >5} {item: <21} {price: >7} {worthy: >15}')
                else:
                    details_sales.append(f'{quantity: >5} {item: <21} {price: >7}')

        for order in purchase_orders:
            quantity = pretty_print_number(purchase_orders[order]["quantity"])
            item = purchase_orders[order]["l10n"][:21].capitalize()
            price = pretty_print_number(purchase_orders[order]["price"])
            details_purchases.append(f'{quantity: >5} {item: <21} {price: >7}')

        
        header_sales = ""
        if details_sales:
            header_sales += _(f'{"Units": >5} {"Item": <21} {"Credits": >7} {"Worthiness*": >15}\n')
            header_sales += _(f'{" [Selling] ":-^50}\n')
            

        header_purchases = ""                
        if details_purchases:
            if header_sales:
                header_purchases += "\n\n"
                header_purchases += _(f'{" [Buying] ":-^50}\n')
            else:
                header_purchases += _(f'{"Units": >5} {"Item": <15} {"Credits": >7}\n')
                header_purchases += _(f'{" [Buying] ":-^50}\n')
            
        opening = "```"
        closing = "```"
        summary = opening
        summary_footer = closing
        if details_sales:
            summary_footer = "\n\n*: b=blueprint u=upgrades x=trading e=eng. unlocks"
            summary_footer += closing
        
        included_sales = []
        included_purchases = []
        remaining -= len(summary) + len(header_sales) + len(header_purchases) + len(summary_footer) 
        for s,p in itertools.zip_longest(details_sales, details_purchases):
            if remaining <= 0:
                break
            if s and len(s) <= remaining:
                included_sales.append(s)
                remaining -= len(s)+1
            if p and len(p) <= remaining:
                included_purchases.append(p)
                remaining -= len(p)+1
        
        if included_sales:
            summary += header_sales
            summary += "\n".join(included_sales)
    
        if included_purchases:
            summary += header_purchases
            summary += "\n".join(included_purchases)

        summary += summary_footer
        return summary

    def evict_system(self, star_system):
        self.edrsystems.evict(star_system)

    def __novel_enough_situation(self, new, old, cognitive = False, system_wide=False):
        if old is None:
            return True

        delta = new["timestamp"] - old["timestamp"]
        
        if cognitive:
            return (not system_wide and (new["starSystem"] != old["starSystem"] or new["place"] != old["place"])) or delta > self.cognitive_novelty_threshold + random.randint(0, 5*1000)

        if new["starSystem"] != old["starSystem"]:
            return delta > self.system_novelty_threshold

        if new["place"] != old["place"]:
            return (old["place"] == "" or
                    old["place"] == "Unknown" or
                    delta > self.place_novelty_threshold)

        if (new.get("ship", None) != old.get("ship", None)) and "ship" in old:
            return (old["ship"] == "" or
                    old["ship"] == "Unknown" or
                    delta > self.ship_novelty_threshold)
        
        if (new.get("suit", None) != old.get("suit", None)) and "suit" in old:
            return (old["suit"] == "" or
                    old["suit"] == "Unknown" or
                    delta > self.ship_novelty_threshold)

        if "suit" in new:
            return ("suit" not in old)

        if "ship" in new:
            return ("ship" not in old)
        
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

    def novel_enough_blip(self, cmdr_id, blip, cognitive = False, system_wide=False):
        last_blip = self.cognitive_blips_cache.get(cmdr_id) if cognitive else self.blips_cache.get(cmdr_id)
        return self.__novel_enough_situation(blip, last_blip, cognitive, system_wide)

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

        try:
            if self.player.is_wingmate(target_cmdr["cmdr"]):
                return False
        except:
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
                    details = _(u"Remain loyal for at least {} days to access enemy alerts").format(int(self.enemy_alerts_pledge_threshold // (24*60*60)))
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
                    EDR_LOG.log(u"EDR alert not worthy. Distance {} between systems {} and {} exceeds threshold {}".format(distance, origin, event["starSystem"], threshold), "DEBUG")
                    return False
            except ValueError:
                EDR_LOG.log(u"Can't compute distance between systems {} and {}: unknown system(s)".format(self.player.star_system, event["starSystem"]), "WARNING")
                pass
        if self.realtime_params[kind]["min_bounty"]:
            if "bounty" not in event:
                return False
            if event["bounty"] < self.realtime_params[kind]["min_bounty"]:
                EDR_LOG.log(u"EDR alert not worthy. Bounty {} does not exceeds threshold {}".format(event["bounty"], self.realtime_params[kind]["min_bounty"]), "DEBUG")
                return False
        return self.novel_enough_alert(event["cmdr"].lower(), event)

    def _summarize_realtime_alert(self, kind, event):
        summary =  []
        EDR_LOG.log(u"realtime {} alerts, handling {}".format(kind, event), "DEBUG")
        if not self._worthy_alert(kind, event):
            EDR_LOG.log(u"Skipped realtime {} event because it wasn't worth alerting about: {}.".format(kind, event), "DEBUG")
        else:
            location = EDLocation(event["starSystem"], place=event["place"], body=event.get("body", None))
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
                EDR_LOG.log(u"Who {} : {}".format(cmdr_name, profile.short_profile(self.player.powerplay)), "INFO")
                legal = self.edrlegal.summarize(profile.cid)
                details = [profile.short_profile(self.player.powerplay)]
                if legal:
                    details.append(legal["overview"])
                self.__intel(_(u"Intel about {}").format(cmdr_name), details, clear_before=True, legal=legal)
            else:
                EDR_LOG.log(u"Who {} : no info".format(cmdr_name), "INFO")
                self.__intel(_(u"Intel about {}").format(cmdr_name), [_("No info").format(cmdr=cmdr_name)], clear_before=True)
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
        self.__notify(_("Distance"), details, clear_before = True)


    def blip(self, cmdr_name, blip, system_wide=False):
        if self.player.in_solo() and not system_wide:
            EDR_LOG.log(u"Skipping blip since the user is in solo (unexpected).", "INFO")
            return False

        cmdr_id = self.cmdr_id(cmdr_name)
        if cmdr_id is None:
            self.status = _(u"no cmdr id (contact).")
            EDR_LOG.log(u"Can't submit blip (no cmdr id for {}).".format(cmdr_name), "ERROR")
            its_actually_fine = self.is_anonymous()
            return its_actually_fine

        profile = self.cmdr(cmdr_name, check_inara_server=True)
        legal = self.edrlegal.summarize(profile.cid)
        if profile and (self.player.name != cmdr_name) and profile.is_dangerous(self.player.powerplay):
            self.status = _(u"{} is bad news.").format(cmdr_name)
            if self.novel_enough_blip(cmdr_id, blip, cognitive = True, system_wide=system_wide):
                details = [profile.short_profile(self.player.powerplay)]
                if legal:
                    details.append(legal["overview"])
                lut = {
                    "Received text (local)": _("Signal: local comms"),
                    "Received text (non wing/friend player)": _("Signal: direct comms"),
                    "Received text (starsystem channel)": _("Signal: system comms"),
                    "Emote sent (non wing/friend player)": _("Signal: emote"),
                    "Sent text (non wing/friend player)": _("Signal: direct comms"),
                    "Ship targeted": _("Signal: targeted"),
                    "Multicrew (captain)": _("Signal: multicrew captain"),
                    "Multicrew (crew)": _("Signal: multicrew member"),

                }
                if blip.get("source", "") in lut:
                    details.append(lut[blip["source"]])
                header = _(u"[Caution!] Intel about {}").format(cmdr_name)
                self.__warning(header, details, clear_before=True, legal=legal)
                self.cognitive_blips_cache.set(cmdr_id, blip)
                if self.player.in_open() and self.is_anonymous() and profile.is_dangerous(self.player.powerplay):
                    self.advertise_full_account(_("You could have helped other EDR users by reporting this outlaw."))
                elif self.player.in_open() and self.is_anonymous():
                    self.advertise_full_account(_("You could have helped other EDR users by reporting this enemy."))
            else:
                EDR_LOG.log(u"Skipping warning since a warning was recently shown.", "INFO")

        if not self.novel_enough_blip(cmdr_id, blip, system_wide):
            EDR_LOG.log(u"Blip is not novel enough to warrant reporting", "INFO")
            return True

        if self.is_anonymous():
            EDR_LOG.log("Skipping blip since the user is anonymous.", "INFO")
            self.blips_cache.set(cmdr_id, blip)
            return True

        success = self.server.blip(cmdr_id, blip)
        if success:
            self.blips_cache.set(cmdr_id, blip)
        else:
            EDR_LOG.log("Blip failed (server side) for {} with {}".format(cmdr_id, blip), "DEBUG")

        return success

    def scanned(self, cmdr_name, scan):
        if self.player.in_solo():
            EDR_LOG.log(u"Skipping scanned since the user is in solo (unexpected).", "INFO")
            self.status = _(u"failed to report scan.")
            return False

        cmdr_id = self.cmdr_id(cmdr_name)
        if cmdr_id is None:
            self.status = _(u"cmdr unknown to EDR.")
            EDR_LOG.log(u"Can't submit scan (no cmdr id for {}).".format(cmdr_name), "ERROR")
            its_actually_fine = self.is_anonymous()
            return its_actually_fine

        if self.novel_enough_scan(cmdr_id, scan, cognitive = True):
            profile = self.cmdr(cmdr_name, check_inara_server=True)
            legal = self.edrlegal.summarize(profile.cid)
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
                        details.append(legal["overview"])
                    header = _(u"[Caution!] Intel about {}").format(cmdr_name)
                    self.__warning(header, details, clear_before=True, legal=legal)
                elif self.intel_even_if_clean or (scan["wanted"] and bounty.is_significant()):
                    self.status = _(u"Intel for cmdr {}.").format(cmdr_name)
                    details = [profile.short_profile(self.player.powerplay)]
                    if bounty:
                        details.append(_(u"Wanted for {} cr").format(EDFineOrBounty(scan["bounty"]).pretty_print()))
                    elif scan["wanted"]:
                        details.append(_(u"Wanted somewhere but it could be minor offenses."))
                    if legal:
                        details.append(legal["overview"])
                    self.__intel(_(u"Intel about {}").format(cmdr_name), details, clear_before=True, legal=legal)
                if not self.player.in_solo() and (self.is_anonymous() and (profile.is_dangerous(self.player.powerplay) or (scan["wanted"] and bounty.is_significant()))):
                    # Translators: this is shown to users who don't yet have an EDR account
                    self.advertise_full_account(_(u"You could have helped other EDR users by reporting this outlaw."))
                elif not self.player.in_solo() and self.is_anonymous() and scan["enemy"] and self.player.power:
                    # Translators: this is shown to users who don't yet have an EDR account
                    self.advertise_full_account(_(u"You could have helped other {power} pledges by reporting this enemy.").format(self.player.power))
                self.cognitive_scans_cache.set(cmdr_id, scan)

        if not self.novel_enough_scan(cmdr_id, scan):
            self.status = _(u"not novel enough (scan).")
            EDR_LOG.log(u"Scan is not novel enough to warrant reporting", "INFO")
            return True

        if self.is_anonymous():
            EDR_LOG.log("Skipping reporting scan since the user is anonymous.", "INFO")
            self.scans_cache.set(cmdr_id, scan)
            return True

        if not self.player.in_open():
            EDR_LOG.log(u"Scan not submitted due to unconfirmed Open mode", "INFO")
            self.status = _(u"Scan reporting disabled in solo/private modes.")
            return False

        if self.player.has_partial_status():
            EDR_LOG.log(u"Scan not submitted due to partial status", "INFO")
            return False

        success = self.server.scanned(cmdr_id, scan)
        if success:
            self.status = _(u"scan reported for {}.").format(cmdr_name)
            self.scans_cache.set(cmdr_id, scan)

        return success

    def traffic(self, star_system, traffic, system_wide=False):
        if self.player.in_solo() and not system_wide:
            EDR_LOG.log(u"Skipping traffic since the user is in solo (unexpected).", "INFO")
            return False

        try:
            if self.is_anonymous():
                EDR_LOG.log(u"Skipping traffic report since the user is anonymous.", "INFO")
                return True

            sigthed_cmdr = traffic["cmdr"]
            if not self.novel_enough_traffic_report(sigthed_cmdr, traffic):
                self.status = _(u"not novel enough (traffic).")
                EDR_LOG.log(u"Traffic report is not novel enough to warrant reporting", "INFO")
                return True

            sid = self.edrsystems.system_id(star_system, may_create=True)
            if sid is None:
                EDR_LOG.log(u"Failed to report traffic for system {} : no id found.".format(star_system),
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
            EDR_LOG.log(u"Skipping crime since the user is in solo (unexpected).", "INFO")
            return False
            
        if not self.crimes_reporting:
            EDR_LOG.log(u"Crimes reporting is off (!crimes on to re-enable).", "INFO")
            self.status = _(u"Crimes reporting is off (!crimes on to re-enable)")
            return True
            
        if self.player.in_bad_neighborhood():
            EDR_LOG.log(u"Crime not being reported because the player is in an anarchy.", "INFO")
            self.status = _(u"Anarchy system (crimes not reported).")
            return True

        if self.is_anonymous():
            EDR_LOG.log(u"Skipping crime report since the user is anonymous.", "INFO")
            if crime["victim"] == self.player.name:
                self.advertise_full_account(_(u"You could have helped other EDR users or get help by reporting this crime!"))
            return True

        sid = self.edrsystems.system_id(star_system, may_create=True)
        if sid is None:
            EDR_LOG.log(u"Failed to report crime in system {} : no id found.".format(star_system),
                       "DEBUG")
            return False

        if self.server.crime(sid, crime):
            self.status = _(u"crime reported!")
            return True
        return False

    def fight(self, fight):
        if self.player.in_solo():
            EDR_LOG.log(u"Skipping fight since the user is in solo (unexpected).", "INFO")
            return False

        if not self.crimes_reporting:
            EDR_LOG.log(u"Crimes reporting is off (!crimes on to re-enable).", "INFO")
            self.status = _(u"Crimes reporting is off (!crimes on to re-enable)")
            return
            
        if self.player.in_bad_neighborhood():
            EDR_LOG.log(u"Fight not being reported because the player is in an anarchy.", "INFO")
            self.status = _(u"Anarchy system (fights not reported).")
            return

        if self.is_anonymous():
            EDR_LOG.log(u"Skipping fight report since the user is anonymous.", "INFO")
            return

        if not self.player.recon_box.forced:
            outlaws_presence = self.player.instance.presence_of_outlaw_players(self.edrcmdrs, ignorables=self.player.wing_and_crew())
            if outlaws_presence:
                self.player.recon_box.activate()
                self.__notify(_(u"EDR Central"), [_(u"Fight reporting enabled"), _(u"Reason: presence of outlaws"), _(u"Turn it off: flash your lights twice, or leave this area, or escape danger and retract hardpoints.")], clear_before=True)
        
        if not self.player.recon_box.active:
            if not self.player.recon_box.advertised:
                self.__notify(_(u"Need assistance?"), [_(u"Flash your lights twice to report a PvP fight to enforcers."), _(u"Send '!crimes off' to make EDR go silent.")], clear_before=True)
                self.player.recon_box.advertised = True
            return

        if not self.novel_enough_fight(fight['cmdr'].lower(), fight):
            EDR_LOG.log(u"Skipping fight report (not novel enough).", "INFO")
            return

        star_system = fight["starSystem"]
        sid = self.edrsystems.system_id(star_system, may_create=True)
        if sid is None:
            EDR_LOG.log(u"Failed to report fight in system {} : no id found.".format(star_system),
                       "DEBUG")
            return
        instance_changes = self.player.instance.noteworthy_changes_json()
        if instance_changes:
            instance_changes["players"] = list(filter(lambda x: self.__novel_enough_combat_contact(x), instance_changes["players"]))
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
            EDR_LOG.log(u"Skipping crew report since the user is in solo (unexpected).", "INFO")
            return False

        if self.is_anonymous():
            EDR_LOG.log(u"Skipping crew report since the user is anonymous.", "INFO")
            if report["captain"] == self.player.name and (report["crimes"] or report["kicked"]):
                self.advertise_full_account(_(u"You could have helped other EDR users by reporting this problematic crew member!"))
            return False

        crew_id = self.cmdr_id(report["crew"])
        if crew_id is None:
            self.status = _(u"{} is unknown to EDR.").format(report["crew"])
            EDR_LOG.log(u"Can't submit crew report (no cmdr id for {}).".format(report["crew"]), "ERROR")
            return False
        
        if self.server.crew_report(crew_id, report):
            self.status = _(u"multicrew session reported (cmdr {name}).").format(name=report["crew"])
            return True
        return False

    def fc_jump_requested(self, event):
        self.advertise_advanced_feature("parking")
        self.player.fleet_carrier.jump_requested(event)
        jump_info = self.player.fleet_carrier.json_jump_schedule()
        if not jump_info:
            return

        if self.fc_jump_psa == _(u"Never"):
            EDR_LOG.log(u"FC Jump reporting is off.", "INFO")
            self.status = _(u"Skipped FC jump announcement.")
            return True

        jump_info["owner"] = self.player.name
        if self.fc_jump_psa in [_(u"Public"), _(u"Private")]:
            if self.is_anonymous():
                EDR_LOG.log(u"Skipping fleet carrier jump report since the user is anonymous.", "INFO")
                self.status = _(u"Skipped Public/Private FC jump announcement (EDR account needed).")
                return True
        
            if self.server.fc_jump_scheduled(jump_info):
                if self.fc_jump_psa == _(u"Public"):
                    self.status = _(u"Sent PSA for FC jump schedule.")
                else:
                    self.status = _(u"Sent Private PSA for FC jump schedule.")
                return True
        elif self.fc_jump_psa == _(u"Direct"):
            if self.edrdiscord.fc_jump_scheduled(jump_info):
                self.status = _(u"Sent Direct PSA for FC jump schedule.")
                return True
        return False
    
    def fc_jump_cancelled(self, event):
        self.player.fleet_carrier.jump_cancelled(event)
        
        if self.fc_jump_psa == _(u"Never"):
            EDR_LOG.log(u"FC Jump reporting is off.", "INFO")
            self.status = _(u"Skipped FC jump announcement.")
            return True

        status = self.player.fleet_carrier.json_status()
        status["owner"] = self.player.name
        if self.fc_jump_psa in [_(u"Public"), _(u"Private")]:
            if self.is_anonymous():
                EDR_LOG.log(u"Skipping fleet carrier jump report since the user is anonymous.", "INFO")
                self.status = _(u"Skipped Public/Private FC jump announcement (EDR account needed).")
                return True
            
            if self.server.fc_jump_cancelled(status):
                self.status = _(u"Cancelled FC jump schedule.")
                return True
        elif self.fc_jump_psa == _(u"Direct"):
            if self.edrdiscord.fc_jump_scheduled(status):
                self.status = _(u"Cancelled FC jump schedule.")
                return True
        
        return False

    def fc_jumped(self, entry):
        self.edrfssinsights.reset()
        self.edrfssinsights.update_system(entry.get("SystemAddress", None), entry["StarSystem"])
        self.update_star_system_if_obsolete(entry["StarSystem"], entry.get("SystemAddress", None))
        self.player.fleet_carrier.update_from_jump_if_relevant(entry)
        self.edrfactions.process_fc_jump_event(entry)

    def fc_materials(self, entry):
        if self.player.last_station == None or self.player.last_station.type != "FleetCarrier":
            self.player.last_station = EDRFleetCarrier()
        
        if not self.player.last_station.update_from_fcmaterials(entry):
            return False

        if not self.player.last_station.bar:
            return False
        return True

    def ack_station_pending_reports(self):
        if self.player.last_station == None:
            return False
        if self.player.last_station.type != "FleetCarrier":
            return False

        if not self.player.last_station.bar:
            return False
        
        if not self.player.last_station.bar.has_changed():
            return True

        adjusted_entry = {
            "timestamp": self.player.last_station.bar.timestamp.as_js_epoch(), 
            "name": self.player.last_station.name,
            "callsign": self.player.last_station.callsign,
            "starSystem": self.player.star_system,
            "reportedBy": self.player.name
        }

        if self.player.last_station.bar.items:
            adjusted_entry["items"] = deepcopy(self.player.last_station.bar.items)
        
        if self.edrsystems.update_fc_materials(self.player.star_system, adjusted_entry):
            self.status = _(u"Reported bartender resources")
        self.player.last_station.bar.acknowledge()

    def __throttling_duration(self):
        now_epoch = EDTime.py_epoch_now()
        if now_epoch > self._throttle_until_timestamp:
            return 0
        return self._throttle_until_timestamp - now_epoch

    def call_central(self, service, info):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping EDR Central call since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False
        
        throttling = self.__throttling_duration()
        if throttling:
            self.status = _(u"Message not sent. Try again in {duration}.").format(duration=EDTime.pretty_print_timespan(throttling))
            self.__notify(_(u"EDR central"), [self.status], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.jammed()
            return False

        star_system = info["starSystem"]
        sid = self.edrsystems.system_id(star_system, may_create=True)
        if sid is None:
            EDR_LOG.log(u"Failed to call central from system {} : no id found.".format(star_system),
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
                if self.client_ui:
                    self.client_ui.notify(fuel_service["name"], attachment)
                details.append(_(u"Check ED Market Connector for instructions about other options"))
                status = _(u"Sent to EDR central - Also try: {}").format(fuel_service["name"])
                link = fuel_service["url"]
                self.linkable_status(link, status)
            else:
                self.status = _(u"Message sent to EDR central")
            self.__notify(_(u"EDR central"), details, clear_before = True)
            self._throttle_until_timestamp = EDTime.py_epoch_now() + 60*5
            return True
        return False

    def tag_cmdr(self, cmdr_name, tag):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping tag cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False
        
        if  tag in ["enemy", "ally"]:
            if not self.player.squadron:
                EDR_LOG.log(u"Skipping squadron tag since the user isn't a member of a squadron.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to join a squadron on https://inara.cz to use this feature."), _(u"Then, reboot EDR to reflect these changes.")])
                return False
            elif not self.player.is_empowered_by_squadron():
                EDR_LOG.log(u"Skipping squadron tag since the user isn't trusted.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to reach {} to tag enemies or allies.").format(self.player.squadron_empowered_rank())])
                return False

        success = self.edrcmdrs.tag_cmdr(cmdr_name, tag)
        dex_name = _(u"Squadron Dex") if tag in ["enemy", "ally"] else _(u"Cmdr Dex") 
        if success:
            self.__notify(dex_name, [_(u"Successfully tagged cmdr {name} with {tag}").format(name=cmdr_name, tag=tag)], clear_before = True)
        else:
            self.__notify(dex_name, [_(u"Could not tag cmdr {name} with {tag}").format(name=cmdr_name, tag=tag)], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()
        return success
    
    def memo_cmdr(self, cmdr_name, memo):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping memo cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        success = self.edrcmdrs.memo_cmdr(cmdr_name, memo)
        if success:
            self.__notify(_(u"Cmdr Dex"), [_(u"Successfully attached a memo to cmdr {}").format(cmdr_name)], clear_before = True)
        else:
            self.__notify(_(u"Cmdr Dex"), [_(u"Failed to attach a memo to cmdr {}").format(cmdr_name)], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()
        return success

    def clear_memo_cmdr(self, cmdr_name):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping clear_memo_cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        success = self.edrcmdrs.clear_memo_cmdr(cmdr_name)
        if success:
            self.__notify(_(u"Cmdr Dex"),[_(u"Successfully removed memo from cmdr {}").format(cmdr_name)], clear_before = True)
        else:
            self.__notify(_(u"Cmdr Dex"), [_(u"Failed to remove memo from cmdr {}").format(cmdr_name)], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()
        return success

    def untag_cmdr(self, cmdr_name, tag):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping untag cmdr since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        if  tag in ["enemy", "ally"]:
            if not self.player.squadron:
                EDR_LOG.log(u"Skipping squadron untag since the user isn't a member of a squadron.", "INFO")
                self.notify_with_details(_(u"Squadron Dex"), [_(u"You need to join a squadron on https://inara.cz to use this feature."), _(u"Then, reboot EDR to reflect these changes.")])
                return False
            elif not self.player.is_empowered_by_squadron():
                EDR_LOG.log(u"Skipping squadron untag since the user isn't trusted.", "INFO")
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
            self.__notify(dex_name, [_(u"Could not remove tag(s) from cmdr {}").format(cmdr_name)], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()
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
                header = _(u"Intel about {}") if self.player.in_open() else _(u"Intel about {} (Open)")
                self.__intel(header.format(cmdr_name), report["readable"], clear_before=True)
            else:
                EDR_LOG.log(u"Where {} : no info".format(cmdr_name), "INFO")
                self.status = _(u"no info about {}").format(cmdr_name)
                header = _(u"Intel about {}") if self.player.in_open() else _(u"Intel about {} (Open)")
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
                location = _(u"{}").format(hit[2])
                marketInfo = self.edrsystems.market(hit[4])
                if marketInfo and marketInfo.get("sName", None) is not None:
                    location = _(u" {} ({})").format(hit[2], marketInfo["sName"])
                if hit[0]:
                    hits.append(_(u"'{}' ({}): {}{}").format(hit[0], hit[1], location, transit))
                else:
                    hits.append(_(u"{}: {}{}").format(hit[1], location, transit))
                if not in_clipboard and hit[2]:
                    copy(hit[2])
                    in_clipboard = True
            self.__notify(_(u"Ship locator"), hits, clear_before = True)
        elif results == False:
            self.__notify(_(u"Ship locator"), [_(u"No info about your fleet."), _(u"Visit a shipyard to update your fleet info.")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()
        else:
            self.__notify(_(u"Ship locator"), [_(u"Couldn't find anything")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()

    def contracts(self):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping contracts since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        contracts = self.edrcmdrs.contracts()
        if contracts:
            self.__notify(_(u"Kill Rewards"),[_(u"{} on Cmdr {}").format(contracts[c]["reward"], contracts[c]["cname"]) for c in contracts], clear_before = True)
        else:
            instructions = _(u"Send '!contract example $$$ 10' in chat to set a reward of 10 million credits on Cmdr 'example'")
            self.__notify(_(u"Kill Rewards"),[_(u"You haven't set any contract yet"), instructions], clear_before = True)
        return True

    def contract(self, cmdr_name):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping contract since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False

        c = self.edrcmdrs.contract_for(cmdr_name)
        self.__notify(_(u"Kill Rewards"),[_(u"Reward of {} for a kill on Cmdr {}").format(c["reward"], cmdr_name)], clear_before = True)
        return True

    def contract_on(self, cmdr_name, reward):
        if self.is_anonymous():
            EDR_LOG.log(u"Skipping contract since the user is anonymous.", "INFO")
            self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
            return False
        
        if reward > 0:
            reward = min(reward, 1000)
            success = self.edrcmdrs.place_contract(cmdr_name, reward)
            if success:
                self.__notify(_(u"Kill Rewards"),[_(u"Reward of {} for a kill on Cmdr {}").format(reward, cmdr_name), _(u"Send '!contract {} $$$ 0' in chat to remove the kill reward").format(cmdr_name)], clear_before = True)
                return True
            self.__notify(_(u"Kill Rewards"),[_(u"Failed to place a reward for a kill on Cmdr {}").format(cmdr_name), _(u"You may have too many active contracts."), _(u"Send '!contracts' to see all your contracts.").format(cmdr_name)], clear_before = True)
            return False
        
        success = self.edrcmdrs.remove_contract(cmdr_name)
        instructions = _(u"Send '!contract {cmdr} $$$ 10' in chat to set a reward of 10 million credits on Cmdr '{cmdr}'")
        if success:
            self.__notify(_(u"Kill Rewards"),[_(u"Removed reward for a kill on Cmdr {}").format(cmdr_name), instructions.format(cmdr=cmdr_name)], clear_before = True)
            return True
        
        self.__notify(_(u"Kill Rewards"),[_(u"Failed to remove reward for a kill on Cmdr {} (not even set?)").format(cmdr_name), instructions.format(cmdr=cmdr_name)], clear_before = True)
        return False

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
        if kind is EDROpponents.ENEMIES:
            if self.is_anonymous():
                EDR_LOG.log(u"Skipping enemies since the user is anonymous.", "INFO")
                self.advertise_full_account(_(u"Sorry, this feature only works with an EDR account."), passive=False)
                return False
            elif not self.player.power:
                EDR_LOG.log(u"Not pledged to any power, can't have enemies.", "INFO")
                self.__notify(_(u"Recently Sighted {kind}").format(kind=_(kind)), [_(u"You need to be pledged to a power.")], clear_before = True, sfx=False)
                if self.audio_feedback:
                    self.SFX.failed()
                return False
        opponents_report = self.edropponents[kind].recent_sightings()
        if not opponents_report:
            EDR_LOG.log(u"No recently sighted {}".format(kind), "INFO")
            header = _(u"Recently Sighted {kind}") if self.player.in_open() else _(u"Recently Sighted {kind} (Open)")
            self.__sitrep(header.format(kind=_(kind)), [_(u"No {kind} sighted in the last {timespan}").format(kind=_(kind).lower(), timespan=EDTime.pretty_print_timespan(self.edropponents[kind].timespan))])
            return False
        
        self.status = _(u"recently sighted {kind}").format(kind=_(kind))
        EDR_LOG.log(u"Got recently sighted {}".format(kind), "INFO")
        header = _(u"Recently Sighted {kind}") if self.player.in_open() else _(u"Recently Sighted {kind} (Open)")
        self.__sitrep(header.format(kind=_(kind)), opponents_report)

    def help(self, section):
        content = self.help_content.get(section)
        if not content:
            return False

        translated_content_details = [_(line) for line in content["details"]]
        if self.visual_feedback:
            EDR_LOG.log(u"Show help for {} with header: {} and details: {}".format(section, content["header"], content["details"][0]), "DEBUG")
            self.IN_GAME_MSG.help(_(content["header"]), translated_content_details)
            if self.audio_feedback:
                self.SFX.help()
        EDR_LOG.log(u"[Alt] Show help for {} with header: {} and details: {}".format(section, content["header"], content["details"][0]), "DEBUG")
        if self.client_ui:
            self.client_ui.help(_(content["header"]), translated_content_details)
        return True

    def tip(self, category=None):
        the_tip = self.tips.tip(category)
        if not the_tip:
            return False

        if self.visual_feedback:
            EDR_LOG.log(u"Show tip for {} with details: {}".format(category, the_tip), "DEBUG")
            self.__notify(_(u"EDR pro-tips"), [the_tip], clear_before=True)
            if self.audio_feedback:
                self.SFX.help()
        EDR_LOG.log(u"[Alt] Show tip for {} with details: {}".format(category, the_tip), "DEBUG")
        if self.client_ui:
            self.client_ui.help(_(u"EDR pro-tips"), [the_tip])
        return True

    def clear(self):
        if self.visual_feedback:
            self.IN_GAME_MSG.clear()
        if self.client_ui:
            self.client_ui.clear()
           

    def __sitrep(self, header, details):
        if self.audio_feedback:
            self.SFX.sitrep()
        if self.visual_feedback:
            EDR_LOG.log(u"sitrep with header: {}; details: {}".format(header, details[0]), "DEBUG")
            self.IN_GAME_MSG.clear_sitrep()
            self.IN_GAME_MSG.sitrep(header, details)
        EDR_LOG.log(u"[Alt] sitrep with header: {}; details: {}".format(header, details[0]), "DEBUG")
        if self.client_ui:
            self.client_ui.sitrep(header, details)

    def __intel(self, header, details, clear_before=False, legal=None):
        if self.audio_feedback:
            self.SFX.intel()
        if self.visual_feedback:
            EDR_LOG.log(u"Intel; details: {}".format(details[0]), "DEBUG")
            if clear_before:
                self.IN_GAME_MSG.clear_intel()
            self.IN_GAME_MSG.intel(header, details, legal)
        EDR_LOG.log(u"[Alt] Intel; details: {}".format(details[0]), "DEBUG")
        if self.client_ui:
            self.client_ui.intel(header, details)

    def __warning(self, header, details, clear_before=False, legal=None):
        if self.audio_feedback:
            self.SFX.warning()
        if self.visual_feedback:
            EDR_LOG.log(u"Warning; details: {}".format(details[0]), "DEBUG")
            if clear_before:
                self.IN_GAME_MSG.clear_warning()
            self.IN_GAME_MSG.warning(header, details, legal)
        EDR_LOG.log(u"[Alt] Warning; details: {}".format(details[0]), "DEBUG")
        if self.client_ui:
            self.client_ui.warning(header, details)
    
    def __notify(self, header, details, clear_before=False, sfx=True):
        if sfx and self.audio_feedback:
            self.SFX.notify()
        if self.visual_feedback:
            EDR_LOG.log(u"Notify about {}; details: {}".format(header, details[0]), "DEBUG")
            if clear_before:
                self.IN_GAME_MSG.clear_notice()
            self.IN_GAME_MSG.notify(header, details)
        EDR_LOG.log(u"[Alt] Notify about {}; details: {}".format(header, details[0]), "DEBUG")
        if self.client_ui:
            self.client_ui.notify(header, details)

    def __commsjammed(self):
        self.__notify(_(u"Comms Link Error"), [_(u"EDR Central can't be reached at the moment"), _(u"Try again later. Join https://edrecon.com/discord or contact Cmdr LeKeno if it keeps failing")], sfx=False)
        if self.audio_feedback:
            self.SFX.jammed()

    def notify_with_details(self, notice, details, clear_before=False):
        self.__notify(notice, details, clear_before)

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

    def advertise_advanced_feature(self, feature_name):
        if feature_name not in self.feature_ads or self.feature_ads[feature_name]["advertised"]:
            return False

        self.__notify(_(u"EDR pro-tips"), self.feature_ads[feature_name]["ad"], clear_before=True)
        self.feature_ads[feature_name]["advertised"] = True
        return True

    def __search_prerequisites(self, star_system):
        if not star_system:
            return False

        if self.__is_searching_recently():
            self.__notify(_(u"EDR Search"), [_(u"Already searching for something, please wait...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
            return False
        
        if not (self.edrsystems.in_bubble(star_system) or self.edrsystems.in_colonia(star_system)):
            self.__notify(_(u"EDR Search"), [_(u"Search features only work in the bubble or Colonia.")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.failed()
            return False
        return True

    def interstellar_factors_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_interstellar_factors(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"I.Factors: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Interstellar Factors: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"I.Factors: failed")
            self.notify_with_details(_(u"EDR Search"), [_(u"Unknown system")])

    def raw_material_trader_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_raw_trader(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"Raw mat. trader: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Raw material trader: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Raw mat. trader: failed")
            self.notify_with_details(_(u"EDR Search"), [_(u"Unknown system")])
        
    def encoded_material_trader_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_encoded_trader(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"Encoded data trader: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Encoded data trader: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Encoded data trader: failed")
            self.notify_with_details(_(u"EDR Search"), [_(u"Unknown system")])


    def manufactured_material_trader_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return
        
        try:
            self.edrsystems.search_manufactured_trader(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"Manufactured mat. trader: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Manufactured material trader: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Manufactured mat. trader: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)


    def staging_station_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_staging_station(star_system, self.__staoi_found, override_sc_distance=override_sc_distance)
            self.__searching()
            self.status = _(u"Staging station: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Staging station: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Staging station: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def parking_system_near(self, star_system, override_rank = None):
        self.feature_ads["parking"]["advertised"] = True # no need to advertise since the user clearly knows about it
        if not self.__search_prerequisites(star_system):
            return

        self.register_fss_signals() # we might as well gets this out in case it's useful

        try:
            self.edrsystems.search_parking_system(star_system, self.__parking_found, override_rank=override_rank)
            self.__searching()
            self.status = _(u"Parking system: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Parking system: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Parking system: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def rrr_fc_near(self, star_system, override_radius = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_rrr_fc(star_system, self.__staoi_found, override_radius=override_radius)
            self.__searching()
            self.status = _(u"RRR Fleet Carrier: searching...")
            details = [_(u"RRR Fleet Carrier: searching in {}...").format(star_system), _(u"If there are no results, try: !rrrfc {} < 15").format(star_system)]
            if override_radius:
                details = [_(u"RRR Fleet Carrier: searching within {} LY of {}...").format(override_radius, star_system)]
            self.__notify(_(u"EDR Search"), details, clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"RRR Fleet Carrier: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def rrr_near(self, star_system, override_radius = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_rrr(star_system, self.__staoi_found, override_radius=override_radius)
            self.__searching()
            self.status = _(u"RRR Station: searching...")
            details = [_(u"RRR Station: searching in {}...").format(star_system), _(u"If there are no results, try: !rrr {} < 15").format(star_system)]
            if override_radius:
                details = [_(u"RRR Station: searching within {} LY of {}...").format(override_radius, star_system)]
            self.__notify(_(u"EDR Search"), details, clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"RRR Station: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def fc_in_current_system(self, callsign_or_name):
        fcs = self.edrfssinsights.fuzzy_match_fleet_carriers(callsign_or_name)
        callsign = callsign_or_name
        fc_name = "Fleet Carrier"
        if len(fcs) == 1:
            callsign = next(iter(fcs))
            fc_name = fcs[callsign]
        elif len(fcs) > 1:
            self.__notify(_(u"EDR Fleet Carrier Local Search"), [_("{} fleet carriers have {} in their callsign or name").format(len(fcs), callsign_or_name), _("Try something more specific, or the full callsign.")], clear_before=True)
            return
        
        fc_regexp = r"^([A-Z0-9]{3}-[A-Z0-9]{3})$"
        if not re.match(fc_regexp, callsign):
            self.__notify(_(u"EDR Fleet Carrier Local Search"), [_("Couldn't find a fleet carrier with {} in its callsign or name").format(callsign_or_name), _("{} is not a valid callsign").format(callsign), _(u"Try a more specific term, the full callsign, or honk your discovery scanner first.")], clear_before=True)
            return

        fc = self.edrsystems.fleet_carrier(self.player.star_system, callsign)
        if fc is None:
            self.__notify(_(u"EDR Fleet Carrier Local Search"), [_("No info on fleet carrier with {} callsign").format(callsign)], clear_before=True)
            return
        
        header = u"{} ({})".format(fc_name, fc["name"])
        details = self.describe_fleet_carrier(fc)
        self.__notify(header, details, clear_before=True)

    def describe_fleet_carrier(self, fc):
        fc_other_services = (fc.get("otherServices", []) or []) 
        details = []
        
        a = u"●" if fc.get("haveOutfitting", False) else u"◌"
        b = u"●" if fc.get("haveShipyard", False) else u"◌"
        details.append(_(u"Outfit:{}   Shipyard:{}").format(a,b))
        
        a = u"●" if "Refuel" in fc_other_services else u"◌"
        b = u"●" if "Repair" in fc_other_services else u"◌"
        c = u"●" if "Restock" in fc_other_services else u"◌"
        details.append(_(u"Refuel:{}   Repair:{}   Restock:{}").format(a,b,c))
        
        a = u"●" if fc.get("haveMarket", False) else u"◌"
        b = u"●" if "Black Market" in fc_other_services else u"◌"
        details.append(_(u"Market:{}   B.Market:{}").format(a,b))
        
        a = u"●" if "Universal Cartographics" in fc_other_services else u"◌"
        b = u"●" if "Vista Genomics" in fc_other_services else u"◌"
        if a == u"●" or b == u"●":
             details.append(_(u"U.Cart:{}   Vista G:{}").format(a,b))
        
        a = u"●" if "Pioneer Supplies" in fc_other_services else u"◌"
        b = u"●" if "Contacts" in fc_other_services else u"◌"
        c = u"●" if "Crew Lounge" in fc_other_services else u"◌"
        if a == u"●" or b == u"●" or c == u"●":
            details.append(_(u"Redempt.O:{}   Pioneer S:{}   Lounge:{}").format(a,b,c))

        updated= EDTime()
        updated.from_edsm_timestamp(fc['updateTime']['information'])
        details.append(_(u"as of {date}").format(date=updated.as_local_timestamp()))
        return details

    def station_in_current_system(self, station_name, passive=False):
        stations = self.edrsystems.fuzzy_stations(self.player.star_system, station_name)
        if stations is None:
            if not passive:
                self.__notify(_(u"EDR Station Local Search"), [_("No info on Station with {} in its name").format(station_name)], clear_before=True)
            return False

        if len(stations) > 1:
            if passive:
                return False
            self.__notify(_(u"EDR Station Local Search"), [_("{} stations have {} in their name").format(len(stations), station_name), _("Try something more specific, or the full name.")], clear_before=True)
            return True
        elif len(stations) == 0:
            if not passive:
                self.__notify(_(u"EDR Station Local Search"), [_("No Station with {} in their name").format(station_name)], clear_before=True)
            return False
        
        station = stations[0]
                
        economy = u"{}/{}".format(station["economy"], station["secondEconomy"]) if station["secondEconomy"] else station["economy"]
        header = u"{} ({})".format(station["name"], economy)

        faction = None
        if station and "controllingFaction" in station:
            controllingFaction = station["controllingFaction"]
            factionName = controllingFaction.get("name", "???")
            faction = self.edrfactions.get(factionName, self.player.star_system)
        details = self.describe_station(station, faction)
        self.__notify(header, details, clear_before=True)
        return True

    def pointing_guidance(self, entry):
        if (not self.gesture_triggers):
            EDR_LOG.log("Gestures setting is off, skipping processing", "INFO")
            return True
        # TODO add the name of the thing in the header
        target = self.player.remlok_helmet.pointing_at(entry)
        if not target:
            return False
        details = []
        description = self.player.describe_item(target)
        inventory_description = self.player.inventory.oneliner(target, fallback=False)
        if inventory_description:
            details.append(inventory_description)
        if not description:
            return False

        details.extend(description)
        self.__notify(_("Remlok Insights"), details, clear_before=True)
        
        return True
    
    def gesture(self, entry):
        if (not self.gesture_triggers):
            EDR_LOG.log("Gestures setting is off, skipping processing", "INFO")
            return
        default_emote_regex = r"^\$HumanoidEmote_DefaultMessage:#player=\$cmdr_decorate:#name=(.+);:#action=\$HumanoidEmote_(.+)_Action[;]+$"
        m = re.match(default_emote_regex, entry.get("Message", ""))
        action = None
        target = None
        if not m:
            targeted_emote_regex = r"^\$HumanoidEmote_TargetMessage:#player=\$cmdr_decorate:#name=(.+);:#targetedAction=\$HumanoidEmote_(.+)_Action_Targeted;:#target=(.+)[;]+$"
            m = re.match(targeted_emote_regex, entry.get("Message", ""))
            if m:
                target = m.group(3)
            
        if not m:
            return
        
        action = m.group(2)
        
        if action == "point":
            if not (self.player.body and self.player.star_system):
                EDR_LOG.log("Skipping point gesture: not on/near a body, or no system set", "INFO")
                return

            if not (self.player.location.on_foot_location.on_planet):
                EDR_LOG.log("Skipping point gesture: not on a planet", "INFO")
                return

            now = datetime.datetime.now()
            title = "POI ({})".format(now.strftime("%H:%M:%S"))
            if target:
                m = re.match(r"^\$Codex_Ent_([^_]+)_.+_Name[;]+$", target)
                if m:
                    title = "{} ({})".format(m.group(1), now.strftime("%H:%M:%S"))
            poi = {
                "title": title,
                "latitude": self.player.attitude.latitude,
                "longitude": self.player.attitude.longitude,
                "heading": self.player.attitude.heading
            }
            system_name = self.player.star_system
            body_name = self.player.body
            if not body_name or body_name.lower() == "unknown":
                return

            if self.edrboi.add_custom_poi(system_name, body_name, poi):
                details = [
                    _("Added a point of interest at the current position."),
                    _("Use the '!nav next' or '!nav previous! to select the next or previous POI."),
                    _("Use the 'stop' gesture or '!nav clear' to clear the current point of interest."),
                    _("Use the '!nav reset' to reset all custom POI for the current planet.")
                ]
                self.__notify(_("EDR Navigation (pointing gesture)"), details)
            pass
        elif action == "wave":
            pass
        elif action == "agree":
            pass
        elif action == "disagree":
            pass
        elif action == "go":
            pass
        elif action == "stop":
            pass
        elif action == "applaud":
            pass
        elif action == "salute":
            pass        
    
    def reset_custom_pois(self):
        system_name = self.player.star_system
        body_name = self.player.body
        if not body_name or body_name.lower() == "unknown":
            EDR_LOG.log("Can't reset custom POIs, no body name: {}".format(body_name), "WARNING")
            return

        self.edrboi.reset_custom_poi(system_name, body_name)
    
    def clear_current_custom_poi(self):
        system_name = self.player.star_system
        body_name = self.player.body
        if not body_name or body_name.lower() == "unknown":
            EDR_LOG.log("Can't clear current custom POI, no body name: {}".format(body_name), "WARNING")
            return

        self.edrboi.clear_current_custom_poi(system_name, body_name)
    
    def next_custom_poi(self):
        return self.__next_previous_custom_poi(True)
    
    def previous_custom_poi(self):
        return self.__next_previous_custom_poi(False)

    def __next_previous_custom_poi(self, next):
        location = self.player.location
        
        poi = None
        if next:
            poi = self.edrboi.next_custom_point_of_interest(location.star_system, location.body or location.place)
        else:
            poi = self.edrboi.previous_custom_point_of_interest(location.star_system, location.body or location.place)
        
        if not poi:
            return

        self.player.planetary_destination = EDPlanetaryLocation(poi)

    def fleet_carrier_update(self):
        if self.player.fleet_carrier.has_market_changed():
            timeframe = 60*15
            market = self.player.fleet_carrier.json_market(timeframe)
            text_summary = self.player.fleet_carrier.text_summary(timeframe)
            details = []
            if market.get("sales", None):
                details.append(_("{} sale orders").format(len(market["sales"])))
            if market.get("purchases", None):
                details.append(_("{} purchase orders").format(len(market["purchases"])))
            
            fc = self.server.fc(self.player.fleet_carrier.callsign, self.player.fleet_carrier.name, self.player.fleet_carrier.position, may_create=True)
            if market and fc:
                if self.player.fleet_carrier.is_open_to_all():
                    fc_id = list(fc)[0] if fc else None
                    market["owner"] = self.player.name
                    if self.server.report_fc_market(fc_id, market):
                        details.append(_("Access: all => Market info sent."))
                    else:
                        EDR_LOG.log("Failed to report FC market update.", "DEBUG")
                else:
                    EDR_LOG.log("Skip reporting FC market given that the FC is not open to all.", "DEBUG")
                sale_orders = self.player.fleet_carrier.sale_orders_within(timeframe)
                purchase_orders = self.player.fleet_carrier.purchase_orders_within(timeframe)
                summary = self.__summarize_fc_market(sale_orders, purchase_orders)
                market["summary"] = summary
                if self.edrdiscord.fc_market_update(market):
                    details.append(_(u"Sent FC trading info to your discord channel."))

            self.player.fleet_carrier.acknowledge_market()

            if details:
                copy(text_summary)
                details.append(_("Summary placed in the clipboard"))
                self.__notify(_("Fleet Carrier status summary"), details, clear_before=True)

    def carrier_trade(self, entry):
        if entry.get("event", "") != "CarrierTradeOrder":
            return
        item = entry.get("Commodity", None)
        if item is None:
            return
        description = self.player.describe_item(item)
        if description:
            l_item = entry.get("Commodity_Localised", item)
            self.__notify(_("Trading Insights for {}").format(l_item), description, clear_before=True)
        
        self.player.fleet_carrier.trade_order(entry)

    def hyperspace_jump(self, system):
        self.player.to_hyper_space()
        if self.player.piloted_vehicle:
            self.player.routenav.fsd_range(self.player.piloted_vehicle.max_jump_range)
        coords = self.edrsystems.system_coords(system)
        updates = self.player.routenav.update(system, coords)
        
        if updates["route_updated"]:
            if self.visual_feedback:
                self.IN_GAME_MSG.navroute(self.player.routenav)
            
        if updates["journey_updated"]:
            self.journey_show_waypoint()

    def update_star_system_if_obsolete(self, system, address=None):
        updated = self.player.update_star_system_if_obsolete(system, address)
        if updated:
            if self.player.piloted_vehicle:
                self.player.routenav.fsd_range(self.player.piloted_vehicle.max_jump_range)
            coords = self.edrsystems.system_coords(system)
            updates = self.player.routenav.update(system, coords)
            
        return updated

    def system_guidance(self, system_name, passive=False):
        description = self.edrsystems.describe_system(system_name, self.player.star_system == system_name)
        if not description:
            if not passive:
                self.__notify(_(u"EDR System Search"), [_("No info on System called {}").format(system_name)], clear_before=True)
            return False

        header = u"{}".format(system_name)
        self.__notify(header, description, clear_before=True)
        return True

    def body_guidance(self, system_name, body_name, passive=False):
        description = self.edrsystems.describe_body(system_name, body_name, self.player.star_system == system_name)
        if not description:
            if not passive:
                self.__notify(_(u"EDR System Search"), [_("No info on Body called {}").format(body_name)], clear_before=True)
            return False

        materials_info = self.edrsystems.materials_on(system_name, body_name)
        facts = self.edrresourcefinder.assess_materials_density(materials_info, self.player.inventory)
        if facts:
            description.extend(facts)
        bio_info = self.edrsystems.biology_on(system_name, body_name)
        if bio_info and bio_info.get("species", None):
            description.append(_("Expected Bio: {}").format(", ".join(bio_info["species"])))
            progress = self.__biome_progress_oneliner(system_name, body_name)
            if progress:
                description.append(progress)
        header = u"{}".format(body_name)
        self.__notify(header, description, clear_before=True)
        return True
        
    def human_tech_broker_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_human_tech_broker(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"Human tech broker: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Human tech broker: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Human tech broker: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)
    
    def guardian_tech_broker_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_guardian_tech_broker(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"Guardian tech broker: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Guardian tech broker: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Guardian tech broker: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def offbeat_station_near(self, star_system, override_sc_distance = None):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_offbeat_station(star_system, self.__staoi_found, with_large_pad=self.player.needs_large_landing_pad(), with_medium_pad=self.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.status = _(u"Offbeat station: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Offbeat station: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Offbeat station: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def search_genus_near(self, genus, star_system):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_planet_with_genus(star_system, genus, self.__plaoi_found)
            self.__searching()
            self.status = _(u"Biofit planet: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Biofit planet: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Biofit planet: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)

    def search_settlement_near(self, settlement, star_system):
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.edrsystems.search_settlement(star_system, settlement, self.__settloi_found)
            self.__searching()
            self.status = _(u"Settlement: searching...")
            self.__notify(_(u"EDR Search"), [_(u"Settlement: searching...")], clear_before = True, sfx=False)
            if self.audio_feedback:
                self.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.status = _(u"Settlement: failed")
            self.__notify(_(u"EDR Search"), [_(u"Unknown system")], clear_before = True)


    def __staoi_found(self, reference, radius, sc, soi_checker, result):
        self.__searching(False)
        details = []
        if result and "station" in result:
            sc_distance = result['station']['distanceToArrival']
            distance = result['distance']
            pretty_dist = _(u"{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _(u"{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _(u"{dist}LS").format(dist=int(sc_distance))
            updated = EDTime()
            updated.from_edsm_timestamp(result['station']['updateTime']['information'])
            details.append(_(u"{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            details.append(_(u"{station} ({type}), {sc_dist}").format(station=result['station']['name'], type=result['station']['type'], sc_dist=pretty_sc_dist))
            details.append(_(u"as of {date} {ci}").format(date=updated.as_local_timestamp(),ci=result['station'].get('comment', '')))
            self.status = u"{item}: {system}, {dist} - {station} ({type}), {sc_dist}".format(item=soi_checker.name, system=result['name'], dist=pretty_dist, station=result['station']['name'], type=result['station']['type'], sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            if 'station' not in result:
                EDR_LOG.log(u"Unsupported search result: {}".format(result), "ERROR")
            
            self.status = _(u"{}: nothing within [{}LY, {}LS] of {}").format(soi_checker.name, int(radius), int(sc), reference)
            checked = _("checked {} systems").format(soi_checker.systems_counter) 
            if soi_checker.stations_counter: 
                checked = _("checked {} systems and {} stations").format(soi_checker.systems_counter, soi_checker.stations_counter) 
            details.append(_(u"nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if soi_checker.hint:
                details.append(soi_checker.hint)
        self.__notify(_(u"{} near {}").format(soi_checker.name, reference), details, clear_before = True)

    def __plaoi_found(self, reference, radius, sc, plaoi_checker, result):
        self.__searching(False)
        details = []
        if result:
            sc_distance = result['planet']['distanceToArrival']
            distance = result['distance']
            pretty_dist = _(u"{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _(u"{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _(u"{dist}LS").format(dist=int(sc_distance))
            planet_name = simplified_body_name(result['name'], result['planet']['name'])
            updated = EDTime()
            updated.from_edsm_timestamp(result['planet']['updateTime'])
            details.append(_(u"{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            details.append(_(u"{planet} ({type}, {atm}), {sc_dist}").format(planet=planet_name, type=result['planet']['subType'], atm=result['planet']['atmosphereType'], sc_dist=pretty_sc_dist))
            details.append(_(u"as of {date}").format(date=updated.as_local_timestamp()))
            self.status = u"{item}: {system}, {dist} - {planet}, {sc_dist}".format(item=plaoi_checker.name, system=result['name'], dist=pretty_dist, planet=planet_name, sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            self.status = _(u"{}: nothing within [{}LY, {}LS] of {}").format(plaoi_checker.name, int(radius), int(sc), reference)
            checked = _("checked {} systems").format(plaoi_checker.systems_counter)
            if plaoi_checker.planets_counter: 
                checked = _("checked {} systems and {} planets").format(plaoi_checker.systems_counter, plaoi_checker.planets_counter)
            details.append(_(u"nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if plaoi_checker.hint:
                details.append(plaoi_checker.hint)
        self.__notify(_(u"{} near {}").format(plaoi_checker.name, reference), details, clear_before = True)

    def __settloi_found(self, reference, radius, sc, settloi_checker, result):
        self.__searching(False)
        details = []
        if result and 'settlement' in result:
            settlement = result['settlement']
            sc_distance = settlement['distanceToArrival']
            distance = result['distance']
            pretty_dist = _(u"{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _(u"{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _(u"{dist}LS").format(dist=int(sc_distance))
            updated = EDTime()
            updated.from_edsm_timestamp(settlement['updateTime']['information'])
            details.append(_(u"{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            if 'body' in settlement:
                bodyName = settlement['body']['name']
                adjBodyName = simplified_body_name(result['name'], bodyName, " 0")
                details.append(_(u"{settlement} ({eco}), {body}, {sc_dist}").format(settlement=settlement['name'], eco=settlement["economy"], body=adjBodyName, sc_dist=pretty_sc_dist))                
            else:
                details.append(_(u"{settlement} ({eco}), {sc_dist}").format(settlement=settlement['name'], eco=settlement["economy"], sc_dist=pretty_sc_dist))
            
            if 'controllingFaction' in settlement:
                faction = self.edrfactions.get(result["name"], settlement['controllingFaction']['name'])
                if faction:
                    updated = faction.lastUpdated
                    if faction.state != None:
                        details.append(_(u"{faction} ({bgs}, {gvt}, {alg})").format(faction=faction.name, bgs=faction.state, gvt=faction.government, alg=faction.allegiance))
                    else:
                        details.append(_(u"{faction} ({gvt}, {alg})").format(faction=settlement['controllingFaction']['name'], gvt=settlement['government'], alg=settlement['allegiance']))
                else:
                    if 'state' in settlement["controllingFaction"]:
                        details.append(_(u"{faction} ({bgs}, {gvt}, {alg})").format(faction=settlement['controllingFaction']['name'], bgs=settlement['controllingFaction']['state'], gvt=settlement['government'], alg=settlement['allegiance']))
                    else:
                        details.append(_(u"{faction} ({gvt}, {alg})").format(faction=settlement['controllingFaction']['name'], gvt=settlement['government'], alg=settlement['allegiance']))
            details.append(_(u"as of {date} {ci}").format(date=updated.as_local_timestamp(),ci=settlement.get('comment', '')))
            self.status = u"{system}, {dist} - {settlement}, {sc_dist}".format(system=result['name'], dist=pretty_dist, settlement=settlement['name'], sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            self.status = _(u"{}: nothing within [{}LY, {}LS] of {}").format(settloi_checker.name, int(radius), int(sc), reference)
            checked = _("checked {} systems").format(settloi_checker.systems_counter) 
            if settloi_checker.settlements_counter: 
                checked = _("checked {} systems and {} settlements").format(settloi_checker.systems_counter, settloi_checker.settlements_counter) 
            details.append(_(u"nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if settloi_checker.hint:
                details.append(settloi_checker.hint)
        self.__notify(_(u"Settlement near {}").format(reference), details, clear_before = True)

    def __parking_found(self, reference, radius, rank, result):
        self.__searching(False)
        details = []
        if result:
            distance = result['distance']
            pretty_dist = "0LY"
            if distance > 0:
                pretty_dist = _(u"{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _(u"{dist}LY").format(dist=int(distance))
                details.append(_(u"{system}, {dist} from {ref} [#{rank}]").format(system=result['name'], dist=pretty_dist, ref=reference, rank=rank))
            else:
                details.append(_(u"{system} [#{rank}]").format(system=result['name'], rank=rank))
            fc = self.edrsystems.fleet_carriers(result['name'])
            fc_count = fc.get("fcCount", None)
            timestamp = fc.get("timestamp", None)
            if not fc_count is None and fc_count >= 0 and timestamp:
                remaining = max(0, result['parking']['slots'] - fc_count)
                threshold = 1000*60*60*24
                plus = 0
                minus = 0
                observations = fc.get("observations", {})
                for o in observations:
                    if abs(timestamp - observations[o]) > threshold:
                        continue
                    count = int(o[1:])
                    if count > fc_count:
                        minus = max(minus, count-fc_count)
                    elif count < fc_count:
                        plus = max(plus, fc_count-count)
                tminus = EDTime.t_minus(timestamp, short=True)
                plusminus = ""
                if plus == minus and plus > 0:
                    plusminus = "±{}".format(plus)
                else:
                    if plus > 0:
                        plusminus = "+{}".format(plus)
                        if minus > 0:
                            plusminus += " -{}".format(minus)
                    elif minus > 0:
                        plusminus = "-{}".format(minus)

                
                if len(plusminus):
                    details.append(_(u"Slots ≈ {} ({}) / {} (as of {})").format(remaining, plusminus, result['parking']['slots'], tminus))
                else:
                    details.append(_(u"Slots ≈ {} / {} (as of {})").format(remaining, result['parking']['slots'], tminus))
            else:
                details.append(_(u"Slots: ???/{} (no intel)").format(result['parking']['slots']))
            stats = result['parking']['info']['all']['stats']
            stars_stats = result['parking']['info']['stars']['stats']
            if stats["count"] > 1 and stats["count"] > stars_stats["count"]:
                bodyCount = _(u"{nb} bodies").format(nb=stats["count"]) if stats["count"] > 0 else _(u"{nb} body").format(nb=stats["count"])
                median = pretty_print_number(int(stats['median']))
                avg = pretty_print_number(int(stats['avg']))
                max_v = pretty_print_number(int(stats['max']))
                details.append(_(u"{} (LS): median={}, avg={}, max={}").format(bodyCount, median, avg, max_v))
            
            starCount = _(u"{nb} stars").format(nb=stars_stats["count"]) if stars_stats["count"] > 0 else _(u"{nb} stars").format(nb=stars_stats["count"])
            stars_median = pretty_print_number(int(stars_stats['median']))
            stars_avg = pretty_print_number(int(stars_stats['avg']))
            stars_max = pretty_print_number(int(stars_stats['max']))
            if stars_stats["count"] > 1:
                details.append(_(u"{} (LS): median={}, avg={}, max={}").format(starCount, stars_median, stars_avg, stars_max))
            elif stars_stats["count"] == 1:
                details.append(_(u"1 star (no gravity well)"))

            if reference == self.player.star_system:
                details.append(_(u"If full, try the next one with !parking #{}.").format(int(rank+1)))
            else:
                details.append(_(u"If full, try the next one with !parking {} #{}.").format(reference, int(rank+1)))
            
            self.status = u"FC Parking: {system}, {dist}".format(system=result['name'], dist=pretty_dist)
            copy(result["name"])
        else:
            self.status = _(u"FC Parking: no #{} system within [{}LY] of {}").format(int(rank), int(radius), reference)
            details.append(_(u"No #{} system found within [{}LY].").format(int(rank), int(radius)))
            if rank > 0:
                if reference == self.player.star_system:
                    details.append(_(u"Try !parking #{}").format(int(rank-1)))
                else:
                    details.append(_(u"Try !parking {} #{}").format(reference, int(rank-1), int(rank-1)))
        self.__notify(_(u"FC Parking near {}").format(reference), details, clear_before = True)
        self.__searching(False)

    def configure_resourcefinder(self, raw_profile):
        canonical_raw_profile = raw_profile.lower()
        adjusted_profile = None if canonical_raw_profile == "default" else canonical_raw_profile
        result = self.edrresourcefinder.configure(adjusted_profile)
        if not result:
            self.__notify(_(u"Unrecognized materials profile"), [_(u"To see a list of profiles, send: !materials")], clear_before = True)
            return result
        
        if adjusted_profile:
            self.__notify(_(u"Using materials profile '{}'").format(raw_profile), [_(u"Revert to default profile by sending: !materials default")], clear_before = True)
        else:
            self.__notify(_(u"Using default materials profile"), [_(u"See the list of profiles by sending: !materials")], clear_before = True)
        return result

    def show_material_profiles(self):
        profiles = self.edrresourcefinder.profiles()
        self.__notify(_(u"Available materials profiles"), [" ;; ".join(profiles)], clear_before=True)

    def __searching(self, active=True):
        self.searching["active"] = active
        self.searching["timestamp"] = EDTime.py_epoch_now()
    
    def __is_searching_recently(self):
        if not self.searching["active"] or not self.searching["timestamp"]:
            return False
        
        threshold = 60*60*5
        if EDTime.py_epoch_now() - self.searching["timestamp"] < threshold:
            return self.searching["active"]

        EDR_LOG.log("Resetting searching state due to no completion in {} seconds".format(threshold), "DEBUG")
        self.__searching(False)
        return False
        
    def search(self, thing, star_system):
        cresource = self.edrresourcefinder.canonical_name(thing)
        if EDRGenusCheckerFactory.recognized_genus(thing):
            self.search_genus_near(thing, star_system)
        elif EDRSettlementCheckerFactory.recognized_settlement(thing):
            self.search_settlement_near(thing, star_system)
        elif cresource:
            self.search_resource(thing, star_system)
        else:
            matches = EDRGenusCheckerFactory.recognized_candidates(thing)
            matches.extend(self.edrresourcefinder.recognized_candidates(thing))
            matches.extend(EDRSettlementCheckerFactory.recognized_candidates(thing))
            if matches:
                self.__notify(_(u"EDR Search: suggested terms"), [" ;; ".join(matches)], clear_before=True)
            else:
                self.__notify(_(u"EDR Search"), [_(u"{}: not supported.").format(thing), _(u"To learn how to use the feature, send: !help search")], clear_before = True)
        

    def search_resource(self, resource, star_system):
        if not star_system:
            return
        
        if self.__is_searching_recently():
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
                self.__searching()
                self.status = _(u"{}: searching...").format(cresource)
                self.__notify(_(u"EDR Search"), [_(u"{}: searching...").format(cresource)], clear_before = True, sfx=False)
                if self.audio_feedback:
                    self.SFX.searching()
            elif outcome == False or outcome == None:
                self.status = _(u"{}: failed...").format(cresource)
                self.__notify(_(u"EDR Search"), [_(u"{}: failed...").format(cresource), _(u"To learn how to use the feature, send: !help search")], clear_before = True)
            else:
                self.status = _(u"{}: found").format(cresource)
                self.__notify(u"{}".format(cresource), outcome, clear_before = True)
        except ValueError:
            self.__searching(False)
            self.status = _(u"{}: failed...").format(cresource)
            self.__notify(_(u"EDR Search"), [_(u"{}: failed...").format(cresource), _(u"To learn how to use the feature, send: !help search")], clear_before = True)

    def __resource_found(self, resource, reference, radius, checker, result, grade):
        self.__searching(False)
        details = []
        if result:
            distance = result['distance']
            pretty_dist = _(u"{dist:.3g}").format(dist=distance) if distance < 50.0 else _(u"{dist}").format(dist=int(distance))
            details.append(_(u"{} ({}LY, {})").format(result['name'], pretty_dist, '+' * grade))
            edt = EDTime()
            if 'updateTime' in result:
                edt.from_js_epoch(result['updateTime'] * 1000)
                details.append(_(u"as of {}").format(edt.as_local_timestamp()))
            if checker.hint():
                details.append(checker.hint())
            self.status = u"{}: {} ({}LY)".format(checker.name, result['name'], pretty_dist)
            copy(result["name"])
        else:
            self.status = _(u"{}: nothing within [{}LY] of {}").format(checker.name, int(radius), reference)
            checked = _("checked {} systems").format(checker.systems_counter) 
            if checker.systems_counter: 
                checked = _("checked {} systems").format(checker.systems_counter)
            details.append(_(u"nothing found within {}LY, {}.").format(int(radius), checked))
            if checker.hint():
                details.append(checker.hint())
        self.__notify(_(u"{} near {}").format(checker.name, reference), details, clear_before = True)


    def journey_new_adv(self, destination=None, genre=None):
        range = None
        if self.player.piloted_vehicle and self.player.piloted_vehicle.max_jump_range:
            range = int(self.player.piloted_vehicle.max_jump_range)
        source = self.player.star_system
        url = edrroutes.SpanshServer.get_url(source, destination or source, range or 30, genre)
        webbrowser.open(url)
        details = []
        details.append(_("Opened Spansh in your web browser."))
        if source and destination and range:
            details.append(_("Wait for the route to complete, copy the URL to the clipboard, then send the '!journey fetch' command."))
        else:
            details.append(_("Adjust the source / destination / range, generate and wait for a route, copy the URL to the clipboard, then send the '!journey fetch' command."))
        self.notify_with_details(_("EDR Journey"), details, clear_before=True)

    def journey_load(self, filename):
        route = edrroutes.CSVJourney(filename)
        if route:
            self.player.routenav.set_journey(route)
            return True
        details = []
        details.append(_("Failed to load a csv route from {}.").format(filename))
        self.notify_with_details(_("EDR Journey"), details, clear_before=True)

        return False

    def journey_fetch(self):
        try:
            url_from_clipboard = paste()
            url_from_clipboard = url_from_clipboard.decode("ascii")
            if not edrroutes.SpanshServer.recognized_url(url_from_clipboard):
                details = []
                details.append(_("No recognized URL in the clipboard."))
                details.append(_("Visit spansh.co.uk, create a route, copy the URL to the clipboard, then resend the '!journey fetch' command"))
                self.notify_with_details(_("EDR Journey"), details, clear_before=True)
                return False
            spansh = edrroutes.SpanshServer(url_from_clipboard, self.__spansh_journey_set)
            spansh.start()
            details = []
            details.append(_("Fetching the route from Spansh."))
            details.append(_("Please wait..."))
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)
            return True
        except Exception as e:
            EDR_LOG.log(u"Journey Fetch failed with exception: {}".format(e), "ERROR")
            self.notify_with_details(_("EDR Journey"), [_("Something went wrong.")], clear_before=True)
            pass

    def journey_clear(self):
        self.player.routenav.clear_journey()
        details = []
        details.append(_("Route successfully cleared."))
        self.notify_with_details(_("EDR Journey"), details, clear_before=True)

    def nav_route_clear(self):
        self.player.routenav.clear_route()

    def nav_route_set(self, navroute):
        self.player.routenav.set_route(navroute)
        if self.visual_feedback:
            self.IN_GAME_MSG.navroute(self.player.routenav)
    
    def __spansh_journey_set(self, route):
        if not route:
            details = []
            details.append(_("Something went wrong."))
            details.append(_("Visit spansh.co.uk, create a route, copy the URL to the clipboard, then resend the '!journey fetch' command"))        
            self.notify_with_details(_("EDR Journey"), details)
            return False
        self.player.routenav.set_journey(route)
        system = self.player.star_system
        coords = self.edrsystems.system_coords(system)
        updates = self.player.routenav.update(system, coords)
        if updates["journey_updated"]:
            self.journey_show_overview()
        return True

    def __describe_waypoint(self):
        if not self.player.routenav or self.player.routenav.no_journey():
            return None
        
        current_wp = self.player.routenav.current()
        if not current_wp:
            return None
        
        details = []
        source_coords = self.edrsystems.system_coords(self.player.star_system)
        descr = self.player.routenav.describe_wp(source_coords)
        if descr:
            details.extend(descr)
        
        stats = self.player.routenav.journey_stats_summary()
        if stats:
            details.extend(stats)
        
        return details

    def journey_next(self):
        if self.player.routenav.no_journey():
            details = []
            details.append(_("No route."))
            details.append(_("Use '!journey new' or '!journey load' to create one."))
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)                
            return False
        
        if not self.player.routenav.journey_next():
            details = []
            details.append(_("Reached the end of the route."))
            details.append(_("Use '!journey previous' to go back one step."))
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)        
            return False
        
        details = self.__describe_waypoint()
        if details:
            wp = self.player.routenav.current_wp_sysname()
            if wp and not self.player.star_system == wp:
                details.append(_("Copied '{}' into the clipboard").format(wp))
                copy(wp)
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)
            return True
        details = []
        details.append(_("Something went wrong."))
        self.notify_with_details(_("EDR Journey - Current Waypoint"), details, clear_before=True)
        return False


    def journey_previous(self):
        if self.player.routenav.no_journey():
            details = []
            details.append(_("No route."))
            details.append(_("Use '!journey new' or '!journey load' to create one."))
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)                
            return False
        
        if not self.player.routenav.journey_previous():
            details = []
            details.append(_("Reached the start of the route."))
            details.append(_("Use '!journey next' to go to the next waypoint."))
            self.notify_with_details(_("EDR Journey - Current Waypoint"), details, clear_before=True)
            return False

        details = self.__describe_waypoint()
        if details:
            wp = self.player.routenav.current_wp_sysname()
            if wp and not self.player.star_system == wp:
                details.append(_("Copied '{}' into the clipboard").format(wp))
                copy(wp)
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)
            return True
        details = []
        details.append(_("Something went wrong."))
        self.notify_with_details(_("EDR Journey"), details, clear_before=True)
        return False

    def journey_show_waypoint(self):
        if self.player.routenav.no_journey():
            self.notify_with_details(_("EDR Journey"), [("No active route."), ("Send '!journey new' or '!journey load' to define a route.")])
            return False
        
        details = self.__describe_waypoint()
        if details:
            wp = self.player.routenav.current_wp_sysname()
            if wp and not self.player.star_system == wp:
                details.append(_("Copied '{}' into the clipboard").format(wp))
                copy(wp)
            self.notify_with_details(_("EDR Journey - Current Waypoint"), details, clear_before=True)
            return True
        return False
    
    def journey_show_overview(self, passive=False):
        if self.player.routenav.no_journey() and not passive:
            self.notify_with_details(_("EDR Journey"), [_("No active route."), _("Send '!journey new' or '!journey load' to define a route.")])
            return False
        
        details = self.player.routenav.describe()
        if details:
            wp = self.player.routenav.current_wp_sysname()
            if wp and not self.player.star_system == wp:
                details.append(_("Copied '{}' into the clipboard").format(wp))
                copy(wp)
            self.notify_with_details(_("EDR Journey"), details, clear_before=True)
            return True
        return False

    def journey_smart_behavior(self):
        if self.player.routenav.no_journey():
            if self.journey_fetch():
                return True
            if self.journey_load("route.csv"):
                return True
            return self.journey_new_adv()
        else:
            return self.journey_show_overview()

    def journey_show_bodies(self):
        if self.player.routenav.no_journey():
            return False
         
        details = self.player.routenav.describe_wp_bodies()
        EDR_LOG.log("Journey show bodies: {}".format(details), "INFO")
        if details:
            self.notify_with_details(_("EDR Journey: survey targets"), details, clear_before=True)
            return True
        else:
            self.notify_with_details(_("EDR Journey"), [_("Waypoint completed; Use '!journey next' to advance.")], clear_before=True)
        
        return False
    
    def journey_check_bodies(self, bodies_names, star_system=None):
        if self.player.routenav.no_journey():
            return False

        if star_system is None:
            star_system = self.player.star_system

        if self.player.routenav.check_bodies(star_system, bodies_names):
            self.notify_with_details(_("EDR Journey"), [_("Checked off specified bodies")], clear_before=True)
            return True
        
        self.notify_with_details(_("EDR Journey"), [_("Specified bodies already checked off or inexistent")], clear_before=True)
        return False
        