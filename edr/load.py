"""
Plugin for "EDR"
"""
from edrclient import EDRClient
from edentities import EDCmdr
from edtime import EDTime
from edrlog import EDRLog
import edentities
import edrautoupdater
from edri18n import _, _c

EDR_CLIENT = EDRClient()
EDRLOG = EDRLog()

def plugin_start():
    """
    Start up EDR, try to login
    :return:
    """
    EDR_CLIENT.apply_config()

    if not EDR_CLIENT.email:
        EDR_CLIENT.email = ""

    if not EDR_CLIENT.password:
        EDR_CLIENT.password = ""

    EDR_CLIENT.login()


def plugin_stop():
    EDRLOG.log(u"Stopping the plugin...", "INFO")
    EDR_CLIENT.shutdown(everything=True)
    if EDR_CLIENT.autoupdate_pending:
        EDRLOG.log(u"Please wait: auto updating EDR", "INFO")
        auto_updater = edrautoupdater.EDRAutoUpdater()
        downloaded = auto_updater.download_latest()
        if downloaded:
            EDRLOG.log(u"Download successful, creating a backup.", "INFO")
            auto_updater.make_backup()
            EDRLOG.log(u"Cleaning old backups.", "INFO")
            auto_updater.clean_old_backups()
            EDRLOG.log(u"Extracting latest version.", "INFO")
            auto_updater.extract_latest()


def plugin_app(parent):
    return EDR_CLIENT.app_ui(parent)


def plugin_prefs(parent):
    return EDR_CLIENT.prefs_ui(parent)


def prefs_changed():
    EDR_CLIENT.prefs_changed()

def prerequisites(edr_client, is_beta):
    if edr_client.mandatory_update:
        EDRLOG.log(u"Out-of-date client, aborting.", "ERROR")
        return False

    if not edr_client.is_logged_in():
        EDRLOG.log(u"Not logged in, aborting.", "ERROR")
        return False

    if is_beta:
        EDRLOG.log(u"Player is in beta: skip!", "INFO")
        return False
    return True

def plain_cmdr_name(journal_cmdr_name):
    if journal_cmdr_name.startswith("$cmdr_decorate:#name="):
            return journal_cmdr_name[len("$cmdr_decorate:#name="):-1]
    return journal_cmdr_name

def handle_wing_events(ed_player, entry):
    if entry["event"] in ["WingAdd"]:
        wingmate = plain_cmdr_name(entry["Name"])
        ed_player.add_to_wing(wingmate)
        EDR_CLIENT.status = _(u"added to wing: ").format(wingmate)
        EDRLOG.log(u"Addition to wing: {}".format(ed_player.wing), "INFO")
        EDR_CLIENT.who(wingmate, autocreate=True) # TODO passive check

    if entry["event"] in ["WingJoin"]:
        ed_player.join_wing(entry["Others"])
        EDR_CLIENT.status = _(u"joined wing.")
        EDRLOG.log(u"Joined a wing: {}".format(ed_player.wing), "INFO")
        wingmates = entry["Others"]
        for wingmate in wingmates:
            EDR_CLIENT.who(plain_cmdr_name(wingmate), autocreate=True) # TODO passive check

    if entry["event"] in ["WingLeave"]:
        ed_player.leave_wing()
        EDR_CLIENT.status = _(u"left wing.")
        EDRLOG.log(u" Left the wing.", "INFO")

def handle_multicrew_events(ed_player, entry):
    if entry["event"] in ["CrewMemberJoins", "CrewMemberRoleChange"]:
        crew = plain_cmdr_name(entry["Crew"])
        success = ed_player.add_to_crew(crew)
        EDR_CLIENT.status = _(u"added to crew: ").format(crew)
        EDRLOG.log(u"Addition to crew: {}".format(ed_player.crew), "INFO")
        if success: # only show intel on the first add 
            EDR_CLIENT.who(crew, autocreate=True) # TODO passive check

    # captain disbanded crew or kicked me and got this:
    # {"timestamp":"2018-06-19T20:05:01Z", "event":"CrewMemberQuits", "Crew":"crew" }
    # { "timestamp":"2018-06-19T20:05:01Z", "event":"QuitACrew", "Captain":"" }
    if entry["event"] in ["CrewMemberQuits", "KickCrewMember"]:
        crew = plain_cmdr_name(entry["Crew"])
        duration = ed_player.crew_time_elapsed(crew)
        kicked = entry["event"] == "KickCrewMember"
        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        ed_player.remove_from_crew(crew)
        EDR_CLIENT.status = _(u"{} left the crew.".format(crew))
        EDRLOG.log(u"{} left the crew.".format(crew), "INFO")
        edr_submit_multicrew_session(ed_player, entry["timestamp"], crew, duration, kicked, crimes, False)

    if entry["event"] in ["JoinACrew"]:
        captain = plain_cmdr_name(entry["Captain"])
        ed_player.join_crew(captain)
        EDR_CLIENT.status = _(u"joined a crew.")
        EDRLOG.log(u"Joined captain {}'s crew".format(captain), "INFO")
        EDR_CLIENT.who(captain, autocreate=True) # TODO passive check

    if entry["event"] in ["QuitACrew"] and ed_player.crew:
        # Note: captain can be empty... { "timestamp":"2018-06-19T20:05:01Z", "event":"QuitACrew", "Captain":"" }
        # crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        for member in ed_player.crew.members:
            duration = ed_player.crew_time_elapsed(member)
            edr_submit_multicrew_session(ed_player, entry["timestamp"], member, duration, False, False, False) #TODO confirm when destroyed should be set
        ed_player.leave_crew()
        EDR_CLIENT.status = _(u"left crew.")
        EDRLOG.log(u"Left the crew.", "INFO")

    if entry["event"] in ["EndCrewSession"] and ed_player.crew:
        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        for member in ed_player.crew.members:
            duration = ed_player.crew_time_elapsed(member)
            edr_submit_multicrew_session(ed_player, entry["timestamp"], member, duration, False, crimes, False) #TODO confirm when destroyed should be set
        ed_player.disband_crew()
        EDR_CLIENT.status = _(u"crew disbanded.")
        EDRLOG.log(u"Crew disbanded.", "INFO")

def handle_movement_events(ed_player, entry):
    outcome = {"updated": False, "reason": None}

    if entry["event"] in ["SupercruiseExit"]:
        place = entry["Body"]
        outcome["updated"] |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        outcome["reason"] = "Supercruise exit"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")

    if entry["event"] in ["FSDJump", "SupercruiseEntry"]:
        place = "Supercruise"
        outcome["updated"] |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        if entry["event"] == "FSDJump" and entry["SystemSecurity"]:
            ed_player.location_security(entry["SystemSecurity"])
            if ed_player.in_bad_neighborhood():
                EDR_CLIENT.IN_GAME_MSG.warning(_(u"Anarchy system"), [_(u"Crimes will not be reported.")])
        outcome["reason"] = "Jump events"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")

    if entry["event"] == "StartJump" and entry["JumpType"] == "Hyperspace":
        place = "Hyperspace"
        outcome["updated"] |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        outcome["reason"] = "Hyperspace"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
        EDR_CLIENT.check_system(entry["StarSystem"])

    if entry["event"] in ["ApproachSettlement"]:
        place = entry["Name"]
        outcome["updated"] |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
        outcome["reason"] = "Approach event"
    return outcome

def handle_change_events(ed_player, entry):
    outcome = {"updated": False, "reason": None}
    if entry["event"] in ["Location"]:
        if entry["Docked"]:
            place = entry["StationName"]
        else:
            place = entry["Body"]
        outcome["updated"] |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        outcome["reason"] = "Location event"
        EDRLOG.log(u"Place changed: {} (location event)".format(place), "INFO")
        EDR_CLIENT.check_system(entry["StarSystem"])

    if entry["event"] in ["Undocked", "Docked", "DockingCancelled", "DockingDenied",
                          "DockingGranted", "DockingRequested", "DockingTimeout"]:
        place = entry["StationName"]
        outcome["updated"] |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        outcome["reason"] = "Docking events"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
    return outcome

def handle_lifecycle_events(ed_player, entry):
    if entry["event"] in ["Music"] and entry["MusicTrack"] == "MainMenu" and not ed_player.in_a_crew():
        # Checking for 'in_a_crew' because "MainMenu" shows up when joining a multicrew session
        # Assumption: being in a crew while main menu happens means that a multicrew session is about to start.
        # { "timestamp":"2018-06-19T13:06:04Z", "event":"QuitACrew", "Captain":"Dummy" }
        # { "timestamp":"2018-06-19T13:06:16Z", "event":"Music", "MusicTrack":"MainMenu" }
        EDR_CLIENT.clear()
        ed_player.game_mode = None
        ed_player.leave_wing()
        ed_player.leave_crew()
        EDRLOG.log(u"Player is on the main menu.", "DEBUG")
        return

    if entry["event"] == "Shutdown":
        EDRLOG.log(u"Shutting down in-game features...", "INFO")
        EDR_CLIENT.shutdown()
        return

    if entry["event"] == "Resurrect":
        EDR_CLIENT.clear()
        ed_player.resurrect()
        EDRLOG.log(u"Player has been resurrected.", "DEBUG")
        return

    if entry["event"] in ["Fileheader"] and entry["part"] == 1:
        EDR_CLIENT.clear()
        ed_player.inception()
        EDR_CLIENT.status = _(u"initialized.")
        EDRLOG.log(u"Journal player got created: accurate picture of friends/wings.",
                   "DEBUG")

    if entry["event"] in ["LoadGame"]:
        EDR_CLIENT.clear()
        ed_player.inception()
        ed_player.game_mode = entry["GameMode"]
        EDRLOG.log(u"Game mode is {}".format(ed_player.game_mode), "DEBUG")
        if not ed_player.in_solo_or_private():
            EDR_CLIENT.warmup()

def handle_friends_events(ed_player, entry):
    if entry["event"] != "Friends":
        return

    if entry["Status"] == "Requested":
        requester = plain_cmdr_name(entry["Name"])
        EDR_CLIENT.who(requester, autocreate=True)

    if entry["Status"] == "Online":
        friend = plain_cmdr_name(entry["Name"])
        # TODO EDR server heartbeat ?

    if entry["Status"] == "Offline":
        friend = plain_cmdr_name(entry["Name"])
        # TODO EDR server anti-heartbeat ?

def handle_powerplay_events(ed_player, entry):
    if entry["event"] == "Powerplay":
        EDRLOG.log(u"Initial powerplay event: {}".format(entry), "DEBUG")
        EDR_CLIENT.pledged_to(entry["Power"], entry["TimePledged"])
    elif entry["event"] == "PowerplayDefect":
        EDR_CLIENT.pledged_to(entry["ToPower"])
    elif entry["event"] == "PowerplayJoin":
        EDR_CLIENT.pledged_to(entry["Power"])
    elif entry["event"] == "PowerplayLeave":
        EDR_CLIENT.pledged_to(None)

def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    ed_player = EDR_CLIENT.player
    ed_player.friends = state["Friends"]

    if not prerequisites(EDR_CLIENT, is_beta):
        return

    if entry["event"] in ["Shutdown", "ShutDown", "Music", "Resurrect", "Fileheader", "LoadGame"]:
        handle_lifecycle_events(ed_player, entry)
    
    if entry["event"].startswith("Powerplay"):
        EDRLOG.log(u"Powerplay event: {}".format(entry), "INFO")
        handle_powerplay_events(ed_player, entry)
    
    if entry["event"] == "Statistics" and not ed_player.powerplay:
        # There should be a Powerplay event before the Statistics event
        # if not then the player is not pledged and we should reflect that on the server
        EDR_CLIENT.pledged_to(None)

    if entry["event"] == "Friends":
        handle_friends_events(ed_player, entry)


    if ed_player.in_solo_or_private():
        EDR_CLIENT.status = _(u"disabled in Solo/Private.")
        EDRLOG.log(u"Game mode is {}: skip!".format(ed_player.game_mode), "INFO")
        return

    if "Crew" in entry["event"]:
        handle_multicrew_events(ed_player, entry)
        
    if entry["event"] in ["WingAdd", "WingJoin", "WingLeave"]:
        handle_wing_events(ed_player, entry)

    EDR_CLIENT.player_name(cmdr)
    ship = state["ShipType"] # TODO does this work well with multicrew?
    print ship # TODO temp
    status_outcome = {"updated": False, "reason": "Unspecified"}

    status_outcome["updated"] = ed_player.update_ship_if_obsolete(ship, entry["timestamp"])
    status_outcome["updated"] |= ed_player.update_star_system_if_obsolete(system,
                                                                          entry["timestamp"])

    if entry["event"] in ["Location", "Undocked", "Docked", "DockingCancelled", "DockingDenied",
                          "DockingGranted", "DockingRequested", "DockingTimeout"]:
        outcome = handle_change_events(ed_player, entry)
        if outcome["updated"]:
            status_outcome["updated"] = True
            status_outcome["reason"] = outcome["reason"]

    if entry["event"] in ["SupercruiseExit", "FSDJump", "SupercruiseEntry", "StartJump",
                          "ApproachSettlement"]:
        outcome = handle_movement_events(ed_player, entry)
        if outcome["updated"]:
            status_outcome["updated"] = True
            status_outcome["reason"] = outcome["reason"]

    if entry["event"] in ["Interdicted", "Died", "EscapeInterdiction", "Interdiction", "PVPKill"]:
        report_crime(ed_player, entry)

    if entry["event"] in ["ShipTargeted"] and "ScanStage" in entry and entry["ScanStage"] > 0:
        handle_scan_events(ed_player, entry)

    if entry["event"] in ["ReceiveText", "SendText"]:
        report_comms(ed_player, entry)

    if entry["event"] in ["SendText"]:
        handle_commands(ed_player, entry)

    if status_outcome["updated"]:
        edr_update_cmdr_status(ed_player, status_outcome["reason"])
        # TODO is the system, place guaranteed to be correct on first multicrew event?
        if ed_player.in_a_crew():
            print ed_player.star_system
            ship = ed_player.ship if ed_player.is_captain() else u"Unknown"
            for member in ed_player.crew.members:
                if member == ed_player.name:
                    continue
                source = u"Multicrew (captain)" if ed_player.is_captain() else u"Multicrew (crew)"
                edr_submit_contact(member, ship, entry["timestamp"], source, ed_player)
        


def edr_update_cmdr_status(cmdr, reason_for_update):
    """
    Send a status update for a given cmdr
    :param cmdr:
    :param reason_for_update:
    :return:
    """

    if not cmdr.in_open():
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        EDRLOG.log(u"Skipping cmdr update due to unconfirmed Open mode", "ERROR")
        return

    if cmdr.has_partial_status():
        EDRLOG.log(u"Skipping cmdr update due to partial status", "ERROR")
        return

    report = {
        "cmdr" : cmdr.name,
        "starSystem": cmdr.star_system,
        "place": cmdr.place,
        "ship": cmdr.ship,
        "timestamp": cmdr.timestamp_js_epoch(),
        "source": reason_for_update,
        "reportedBy": cmdr.name
    }

    EDRLOG.log(u"report: {}".format(report), "DEBUG")

    if not EDR_CLIENT.blip(cmdr.name, report):
        EDR_CLIENT.status = _(u"blip failed.")
        EDR_CLIENT.evict_cmdr(cmdr.name)
        return

    EDR_CLIENT.status = _(u"blip succeeded!")


def edr_submit_crime(criminal_cmdrs, offence, victim):
    """
    Send a crime/incident report
    :param criminal:
    :param offence:
    :param victim:
    :return:
    """
    if not victim.in_open():
        EDRLOG.log(u"Skipping submit crime (wing) due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        return

    criminals = []
    for criminal_cmdr in criminal_cmdrs:
        EDRLOG.log(u"Appending criminal {} with ship {}".format(criminal_cmdr.name,
                                                                criminal_cmdr.ship),
                   "DEBUG")
        criminals.append({"name": criminal_cmdr.name, "ship": criminal_cmdr.ship})

    report = {
        "starSystem": victim.star_system,
        "place": victim.place,
        "timestamp": victim.timestamp_js_epoch(),
        "criminals": criminals,
        "offence": offence,
        "victim": victim.name,
        "victimShip": victim.ship,
        "reportedBy": victim.name,
        "byPledge": victim.powerplay.canonicalize() if victim.powerplay else ""
    }

    if not EDR_CLIENT.crime(victim.star_system, report):
        EDR_CLIENT.status = _(u"failed to report crime.")
        EDR_CLIENT.evict_system(victim.star_system)
        return

    EDR_CLIENT.status = _(u"crime reported!")


def edr_submit_crime_self(criminal_cmdr, offence, victim):
    """
    Send a crime/incident report
    :param criminal_cmdr:
    :param offence:
    :param victim:
    :return:
    """
    if not criminal_cmdr.in_open():
        EDRLOG.log(u"Skipping submit crime (self) due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        return

    report = {
        "starSystem": criminal_cmdr.star_system,
        "place": criminal_cmdr.place,
        "timestamp": criminal_cmdr.timestamp_js_epoch(),
        "criminals" : [
            {"name": criminal_cmdr.name,
             "ship" : criminal_cmdr.ship,
            }],
        "offence": offence,
        "victim": victim,
        "victimShip": u"Unknown",
        "reportedBy": criminal_cmdr.name,
        "byPledge": criminal_cmdr.powerplay.canonicalize() if criminal_cmdr.powerplay else ""
    }

    EDRLOG.log(u"Perpetrated crime: {}".format(report), "DEBUG")

    if not EDR_CLIENT.crime(criminal_cmdr.star_system, report):
        EDR_CLIENT.status = _(u"failed to report crime.")
        EDR_CLIENT.evict_system(criminal_cmdr.star_system)
        return

    EDR_CLIENT.status = _(u"crime reported!")


def edr_submit_contact(cmdr_name, ship, timestamp, source, witness):
    """
    Report a contact with a cmdr
    :param cmdr:
    :param timestamp:
    :param ship:
    :param source:
    :param witness:
    :return:
    """
    edt = EDTime()
    edt.from_journal_timestamp(timestamp)

    report = {
        "cmdr" : cmdr_name,
        "starSystem": witness.star_system,
        "place": witness.place,
        "timestamp": edt.as_js_epoch(),
        "ship" : ship if ship else u"Unknown",
        "source": source,
        "reportedBy": witness.name,
        "byPledge": witness.powerplay.canonicalize() if witness.powerplay else ""
    }

    if not witness.in_open():
        EDRLOG.log(u"Skipping submit contact due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        return

    if witness.has_partial_status():
        EDRLOG.log(u"Skipping cmdr update due to partial status", "INFO")
        return

    if not EDR_CLIENT.blip(cmdr_name, report):
        EDR_CLIENT.status = _(u"failed to report contact.")
        EDR_CLIENT.evict_cmdr(cmdr_name)

    EDR_CLIENT.status = _(u"contact reported (cmdr {name}).").format(name=cmdr_name)
    edr_submit_traffic(cmdr_name, ship, timestamp, source, witness)

def edr_submit_scan(scan, timestamp, source, witness):
    edt = EDTime()
    edt.from_journal_timestamp(timestamp)

    report = scan
    report["starSystem"] = witness.star_system
    report["place"] = witness.place
    report["timestamp"] = edt.as_js_epoch()
    report["source"] = source
    report["reportedBy"] = witness.name
    report["byPledge"] = witness.powerplay.canonicalize() if witness.powerplay else ""

    if not witness.in_open():
        EDRLOG.log(u"Scan not submitted due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        return

    if witness.has_partial_status():
        EDRLOG.log(u"Scan not submitted due to partial status", "INFO")
        return

    if not EDR_CLIENT.scanned(scan["cmdr"], report):
        EDR_CLIENT.status = _(u"failed to report scan.")
        EDR_CLIENT.evict_cmdr(scan["cmdr"])
    EDR_CLIENT.status = _(u"scan reported (cmdr {name}).").format(name=scan["cmdr"])

def edr_submit_traffic(cmdr_name, ship, timestamp, source, witness):
    """
    Report a contact with a cmdr
    :param cmdr:
    :param ship:
    :param timestamp:
    :param source:
    :param witness:
    :return:
    """
    edt = EDTime()
    edt.from_journal_timestamp(timestamp)

    report = {
        "cmdr" : cmdr_name,
        "starSystem": witness.star_system,
        "place": witness.place,
        "timestamp": edt.as_js_epoch(),
        "ship" : ship if ship else u"Unknown",
        "source": source,
        "reportedBy": witness.name,
        "byPledge": witness.powerplay.canonicalize() if witness.powerplay else ""
    }

    if not witness.in_open():
        EDRLOG.log(u"Skipping submit traffic due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        return

    if witness.has_partial_status():
        EDRLOG.log(u"Skipping traffic update due to partial status", "INFO")
        return

    if not EDR_CLIENT.traffic(witness.star_system, report):
        EDR_CLIENT.status = _(u"failed to report traffic.")
        EDR_CLIENT.evict_system(witness.star_system)
    EDR_CLIENT.status = _(u"traffic reported (cmdr {name}).").format(name=cmdr_name)

def edr_submit_multicrew_session(captain, timestamp, crew, duration, kicked, crimes, destroyed):
    edt = EDTime()
    edt.from_journal_timestamp(timestamp)

    report = {
        "captain": captain.name,
        "timestamp": edt.as_js_epoch(),
        "crew" : crew,
        "duration": duration,
        "kicked": kicked,
        "crimes": crimes,
        "destroyed": destroyed
    }

    if not captain.in_open():
        EDRLOG.log(u"Skipping submit traffic due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"not in Open? Start EDMC before Elite.")
        return

    if not EDR_CLIENT.crew_report(report):
        EDR_CLIENT.status = _(u"failed to report multicrew session.")
    EDR_CLIENT.status = _(u"multicrew session reported (cmdr {name}).").format(name=crew)

def report_crime(cmdr, entry):
    """
    Report a crime to the server
    :param cmdr:
    :param entry:
    :return:
    """
    if entry["event"] in ["Interdicted", "EscapeInterdiction"]:
        if entry["IsPlayer"]:
            criminal_cmdr = EDCmdr()
            criminal_cmdr.timestamp = entry["timestamp"]
            criminal_cmdr.star_system = cmdr.star_system
            criminal_cmdr.place = cmdr.place
            criminal_cmdr.ship = u"Unknown"
            criminal_cmdr.name = entry["Interdictor"]
            edr_submit_crime([criminal_cmdr], entry["event"], cmdr)

    if entry["event"] == "Died":
        if "Killers" in entry:
            criminal_cmdrs = []
            for killer in entry["Killers"]:
                if killer["Name"].startswith("Cmdr "):
                    criminal_cmdr = EDCmdr()
                    criminal_cmdr.timestamp = entry["timestamp"]
                    criminal_cmdr.star_system = cmdr.star_system
                    criminal_cmdr.place = cmdr.place
                    criminal_cmdr.ship = killer["Ship"]
                    criminal_cmdr.name = killer["Name"][5:]
                    criminal_cmdrs.append(criminal_cmdr)
            edr_submit_crime(criminal_cmdrs, "Murder", cmdr)
        elif "KillerName" in entry and entry["KillerName"].startswith("Cmdr "):
            criminal_cmdr = EDCmdr()
            criminal_cmdr.timestamp = entry["timestamp"]
            criminal_cmdr.star_system = cmdr.star_system
            criminal_cmdr.place = cmdr.place
            criminal_cmdr.ship = entry["KillerShip"]
            criminal_cmdr.name = entry["KillerName"][5:]
            edr_submit_crime([criminal_cmdr], "Murder", cmdr)
        EDR_CLIENT.player.killed()

    if entry["event"] == "Interdiction":
        if entry["IsPlayer"]:
            offence = "Interdiction" if entry["Success"] else "Failed interdiction"
            edr_submit_crime_self(cmdr, offence, entry["Interdicted"], )

    if entry["event"] == "PVPKill":
        EDRLOG.log(u"PVPKill!", "INFO")
        edr_submit_crime_self(cmdr, "Murder", entry["Victim"])


def report_comms(cmdr, entry):
    """
    Report a comms contact to the server
    :param cmdr:
    :param entry:
    :return:
    """
    # Note: Channel can be missing... probably not safe to assume anything in that case 
    if entry["event"] == "ReceiveText" and "Channel" in entry:
        if entry["Channel"] in ["local"]:
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            edr_submit_contact(from_cmdr, None, entry["timestamp"], "Received text (local)", cmdr)
        elif entry["Channel"] in ["player"]:
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            if cmdr.is_friend_or_in_wing(from_cmdr):
                EDRLOG.log(u"Text from {} friend / wing. Can't infer location".format(from_cmdr),
                           "INFO")
            else:
                EDRLOG.log(u"Text from {} (not friend/wing) == same location".format(from_cmdr),
                           "INFO")
                edr_submit_contact(from_cmdr, None, entry["timestamp"],
                                   "Received text (non wing/friend player)", cmdr)
    elif entry["event"] == "SendText" and not entry["To"] in ["local", "wing"]:
        to_cmdr = entry["To"]
        if entry["To"].startswith("$cmdr_decorate:#name="):
            to_cmdr = entry["To"][len("$cmdr_decorate:#name="):-1]
        if cmdr.is_friend_or_in_wing(to_cmdr):
            EDRLOG.log(u"Sent text to {} friend/wing: can't infer location".format(to_cmdr), "INFO")            
        else:
            EDRLOG.log(u"Sent text to {} (not friend/wing) == same location".format(to_cmdr),
                       "INFO")
            edr_submit_contact(to_cmdr, None, entry["timestamp"], "Sent text (non wing/friend player)",
                               cmdr)

def handle_scan_events(cmdr, entry):
    if not (entry["event"] == "ShipTargeted" and entry["TargetLocked"] and entry["ScanStage"] > 0):
        return False

    prefix = None
    if entry["PilotName"].startswith("$cmdr_decorate:#name="):
        prefix = "$cmdr_decorate:#name="
    elif entry["PilotName"].startswith("$RolePanel2_unmanned; $cmdr_decorate:#name="):
        prefix = "$RolePanel2_unmanned; $cmdr_decorate:#name="
    elif entry["PilotName"].startswith("$RolePanel2_crew; $cmdr_decorate:#name="):
        prefix = "$RolePanel2_crew; $cmdr_decorate:#name="
    
    if not prefix:
        return False

    cmdr_name = entry["PilotName"][len(prefix):-1]
    if cmdr_name == cmdr.name:
        # Happens when scanning one's unmanned ship, etc.
        return False

    ship = edentities.EDVehicles.canonicalize(entry["Ship"])

    edr_submit_contact(cmdr_name, ship, entry["timestamp"], "Ship targeted", cmdr)
    if entry["ScanStage"] == 3:
        wanted = entry["LegalStatus"] in ["Wanted", "WantedEnemy", "Warrant"]
        enemy = entry["LegalStatus"] in ["Enemy", "WantedEnemy", "Hunter"]
        scan = {
            "cmdr": cmdr_name,
            "ship": ship,
            "wanted": wanted,
            "enemy": enemy,
            "bounty": entry["Bounty"] if wanted and "Bounty" in entry else 0
        }
        edr_submit_scan(scan, entry["timestamp"], "Ship targeted [{}]".format(entry["LegalStatus"]), cmdr)
    return True

def handle_commands(cmdr, entry):
    if not entry["event"] == "SendText":
        return

    command_parts = entry["Message"].split(" ", 1)
    command = command_parts[0].lower()
    if command[0] == "!":
        handle_bang_commands(cmdr, command, command_parts)
    elif command[0] == "?":
        handle_query_commands(cmdr, command, command_parts)
    elif command[0] == "#":
        handle_hash_commands(command, command_parts, entry)
    elif command[0] == "-":
        handle_minus_commands(command, command_parts, entry)
    elif command[0] == "@":
        handle_at_commands(entry)
    elif command == "o7" and not entry["To"] in ["local", "voicechat", "wing", "friend"]:
        EDRLOG.log(u"Implicit who command for {}".format(entry["To"]), "INFO")
        to_cmdr = entry["To"]
        if entry["To"].startswith("$cmdr_decorate:#name="):
            to_cmdr = entry["To"][len("$cmdr_decorate:#name="):-1]
        EDR_CLIENT.who(to_cmdr, autocreate=True)

def handle_bang_commands(cmdr, command, command_parts):
    if command == "!overlay":
        overlay_command("" if len(command_parts) == 1 else command_parts[1])
    elif command == "!audiocue" and len(command_parts) == 2:
        audiocue_command(command_parts[1])
    elif command == "!who" and len(command_parts) == 2:
        EDRLOG.log(u"Explicit who command for {}".format(command_parts[1]), "INFO")
        EDR_CLIENT.who(command_parts[1])
    elif command == "!crimes":
        crimes_command("" if len(command_parts) == 1 else command_parts[1])
    elif command == "!sitrep":
        system = cmdr.star_system if len(command_parts) == 1 else command_parts[1]
        EDRLOG.log(u"Sitrep command for {}".format(system), "INFO")
        EDR_CLIENT.check_system(system)
    elif command == "!sitreps":
        EDRLOG.log(u"Sitreps command", "INFO")
        EDR_CLIENT.sitreps()
    elif command == "!notams":
        EDRLOG.log(u"Notams command", "INFO")
        EDR_CLIENT.notams()
    elif command == "!notam":
        system = cmdr.star_system if len(command_parts) == 1 else command_parts[1]
        EDRLOG.log(u"Notam command for {}".format(system), "INFO")
        EDR_CLIENT.notam(system)
    elif command == "!outlaws":
        EDRLOG.log(u"Outlaws command", "INFO")
        EDR_CLIENT.outlaws()
    elif command == "!enemies":
        EDRLOG.log(u"Enemies command", "INFO")
        EDR_CLIENT.enemies()
    elif command == "!where" and len(command_parts) == 2:
        EDRLOG.log(u"Explicit where command for {}".format(command_parts[1]), "INFO")
        EDR_CLIENT.where(command_parts[1])
    elif command in ["!distance", "!d"] and len(command_parts) >= 2:
        EDRLOG.log(u"Distance command", "INFO")
        systems = " ".join(command_parts[1:]).split(" > ", 1)
        if not systems:
            EDRLOG.log(u"Aborting distance calculation (no params).", "DEBUG")
            return
        from_sys = systems[0] if len(systems) == 2 else cmdr.star_system
        to_sys = systems[1] if len(systems) == 2 else systems[0]
        EDRLOG.log(u"Distance command from {} to {}".format(from_sys, to_sys), "INFO")
        EDR_CLIENT.distance(from_sys, to_sys)
    elif command == "!help":
        EDRLOG.log(u"Help command", "INFO")
        EDR_CLIENT.help("" if len(command_parts) == 1 else command_parts[1])
    elif command == "!clear":
        EDRLOG.log(u"Clear command", "INFO")
        EDR_CLIENT.clear()

def handle_query_commands(cmdr, command, command_parts):
    if command == "?outlaws":
        EDRLOG.log(u"Outlaws alerts command", "INFO")
        param = "" if len(command_parts) == 1 else command_parts[1]
        if param == "":
            EDR_CLIENT.outlaws_alerts_enabled(silent=False)
        elif param == "on": 
            EDRLOG.log(u"Enabling Outlaws alerts", "INFO")
            EDR_CLIENT.enable_outlaws_alerts()
        elif param == "off":
            EDRLOG.log(u"Disabling Outlaws alerts", "INFO")
            EDR_CLIENT.disable_outlaws_alerts()
        elif param.startswith("ly "):
            EDRLOG.log(u"Max distance for Outlaws alerts", "INFO")
            EDR_CLIENT.max_distance_outlaws_alerts(param[3:])
        elif param.startswith("cr "):
            EDRLOG.log(u"Min bounty for Outlaws alerts", "INFO")
            EDR_CLIENT.min_bounty_outlaws_alerts(param[3:])
    elif command == "?enemies":
        EDRLOG.log(u"Enemies alerts command", "INFO")
        param = "" if len(command_parts) == 1 else command_parts[1]
        if param == "":
            EDR_CLIENT.enemies_alerts_enabled(silent=False)
        elif param == "on": 
            EDRLOG.log(u"Enabling enemies alerts", "INFO")
            EDR_CLIENT.enable_enemies_alerts()
        elif param == "off":
            EDRLOG.log(u"Disabling enemies alerts", "INFO")
            EDR_CLIENT.disable_enemies_alerts()
        elif param.startswith("ly "):
            EDRLOG.log(u"Max distance for Enemies alerts", "INFO")
            EDR_CLIENT.max_distance_enemies_alerts(param[3:])
    
def handle_hash_commands(command, command_parts, entry):
    target_cmdr = command_parts[1] if len(command_parts) > 1 else None
    if target_cmdr is None and not entry["To"] in ["local", "voicechat", "wing", "friend"]:
        prefix = "$cmdr_decorate:#name="
        target_cmdr = entry["To"][len(prefix):-1] if entry["To"].startswith(prefix) else entry["To"]
    
    if (command == "#!" or command == "#outlaw"):
        EDRLOG.log(u"Tag outlaw command for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, "outlaw")
    elif (command == "#?" or command == "#neutral"):
        EDRLOG.log(u"Tag neutral command for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, "neutral")
    elif (command == "#+" or command == "#enforcer"):
        EDRLOG.log(u"Tag enforcer command for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, "enforcer")
    elif (command == "#s!" or command == "#enemy"):
        EDRLOG.log(u"Tag squadron enemy command for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, "enemy")
    elif (command == "#s+" or command == "#ally"):
        EDRLOG.log(u"Tag squadron ally command for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, "ally")
    elif (command == "#=" or command == "#friend"):
        EDRLOG.log(u"Tag friend command for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, "friend")
    elif (command[0] == "#" and len(command) > 1):
        tag = command[1:]
        EDRLOG.log(u"Tag command for {} with {}".format(target_cmdr, tag), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, tag)

def handle_minus_commands(command, command_parts, entry):
    target_cmdr = command_parts[1] if len(command_parts) > 1 else None
    if target_cmdr is None and not entry["To"] in ["local", "voicechat", "wing", "friend"]:
        prefix = "$cmdr_decorate:#name="
        target_cmdr = entry["To"][len(prefix):-1] if entry["To"].startswith(prefix) else entry["To"]

    if command == "-#":
        EDRLOG.log(u"Remove {} from dex".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, tag=None)
    elif command == "-#!" or command == "-#outlaw":
        EDRLOG.log(u"Remove outlaw tag for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, "outlaw")
    elif command == "-#?" or command == "-#neutral":
        EDRLOG.log(u"Remove neutral tag for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, "neutral")
    elif command == "-#+" or command == "-#enforcer":
        EDRLOG.log(u"Remove enforcer tag for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, "enforcer")
    elif command == "-#s!" or command == "-#enemy":
        EDRLOG.log(u"Remove squadron enemy tag for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, "enemy")
    elif command == "-#s+" or command == "-#ally":
        EDRLOG.log(u"Remove squadron ally tag for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, "ally")    
    elif command == "-#=" or command == "-#friend":
        EDRLOG.log(u"Remove friend tag for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, "friend")
    elif (command[0] == "-#" and len(command) > 2):
        tag = command[2:]
        EDRLOG.log(u"Remove tag {} for {}".format(tag, target_cmdr), "INFO")
        EDR_CLIENT.untag_cmdr(target_cmdr, tag)
    elif command == "-@#":
        EDRLOG.log(u"Remove memo for {}".format(target_cmdr), "INFO")
        EDR_CLIENT.clear_memo_cmdr(target_cmdr)
    

def handle_at_commands(entry):
    if not entry["event"] == "SendText":
        return
    command_parts = entry["Message"].split(" memo=", 1)
    command = command_parts[0].lower()
    
    if command == "@# " and not entry["To"] in ["local", "voicechat", "wing", "friend"]:
        prefix = "$cmdr_decorate:#name="
        target_cmdr = entry["To"][len(prefix):-1] if entry["To"].startswith(prefix) else entry["To"]
        EDRLOG.log(u"Memo command for tagged cmdr {}".format(target_cmdr), "INFO")
        EDR_CLIENT.memo_cmdr(target_cmdr, command_parts[1])
    elif command.startswith("@# ") and len(command)>2:
        target_cmdr = command[3:]
        EDRLOG.log(u"Memo command for tagged cmdr {}".format(target_cmdr), "INFO")
        EDR_CLIENT.memo_cmdr(target_cmdr, command_parts[1])


def overlay_command(param):
    if param == "":
        EDRLOG.log(u"Visual feedback is {}".format("enabled." if EDR_CLIENT.visual_feedback
                                                   else "disabled."), "INFO")
        EDR_CLIENT.notify_with_details("Test Notice", ["notice info 1", "notice info 2"])
        EDR_CLIENT.warn_with_details("Test Warning", ["warning info 1", "warning info 2"])
    elif param == "on":
        EDRLOG.log(u"Enabling visual feedback", "INFO")
        EDR_CLIENT.visual_feedback = True
        EDR_CLIENT.warmup()
    elif param == "off":
        EDRLOG.log(u"Disabling visual feedback", "INFO")
        EDR_CLIENT.notify_with_details("Visual Feedback System", ["disabling"])
        EDR_CLIENT.visual_feedback = False

def crimes_command(param):
    if param == "":
        EDRLOG.log(u"Crimes report is {}".format("enabled." if EDR_CLIENT.crimes_reporting
                                                 else "disabled."), "INFO")
        EDR_CLIENT.notify_with_details("EDR crimes report",
                                       ["Enabled" if EDR_CLIENT.crimes_reporting else "Disabled"])
    elif param == "on":
        EDRLOG.log(u"Enabling crimes reporting", "INFO")
        EDR_CLIENT.crimes_reporting = True
        EDR_CLIENT.notify_with_details("EDR crimes report", ["Enabling"])
    elif param == "off":
        EDRLOG.log(u"Disabling crimes reporting", "INFO")
        EDR_CLIENT.crimes_reporting = False
        EDR_CLIENT.notify_with_details("EDR crimes report", ["Disabling"])

def audiocue_command(param):
    if param == "on":
        EDRLOG.log(u"Enabling audio feedback", "INFO")
        EDR_CLIENT.audio_feedback = True
        EDR_CLIENT.notify_with_details("EDR audio cues", ["Enabling"])
    elif param == "off":
        EDRLOG.log(u"Disabling audio feedback", "INFO")
        EDR_CLIENT.audio_feedback = False
        EDR_CLIENT.notify_with_details("EDR audio cues", ["Disabling"])
    elif param == "loud":
        EDRLOG.log(u"Loud audio feedback", "INFO")
        EDR_CLIENT.loud_audio_feedback()
        EDR_CLIENT.audio_feedback = True
        EDR_CLIENT.notify_with_details("EDR audio cues", ["Enabled", "Loud"])
    elif param == "soft":
        EDRLOG.log(u"Soft audio feedback", "INFO")
        EDR_CLIENT.soft_audio_feedback()
        EDR_CLIENT.audio_feedback = True
        EDR_CLIENT.notify_with_details("EDR audio cues", ["Enabled", "Soft"])
