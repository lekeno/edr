"""
Plugin for "EDR"
"""
from edentities import EDCmdr
from edrclient import EDRClient
from edtime import EDTime
from edrlog import EDRLog

EDR_CLIENT = EDRClient()
EDRLOG = EDRLog()

def plugin_start():
    """
    Start up EDR, check for updates
    :return:
    """
    EDR_CLIENT.apply_config()

    if not EDR_CLIENT.email:
        EDR_CLIENT.email = ""

    if not EDR_CLIENT.password:
        EDR_CLIENT.password = ""
        
    EDR_CLIENT.login()
    EDR_CLIENT.check_version()


def plugin_stop():
    EDR_CLIENT.shutdown()


def plugin_app(parent):
    return EDR_CLIENT.app_ui(parent)


def plugin_prefs(parent):
    return EDR_CLIENT.prefs_ui(parent)


def prefs_changed():
    EDR_CLIENT.prefs_changed()


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

    if EDR_CLIENT.mandatory_update:
        EDRLOG.log(u"[EDR]Out-of-date client, aborting.", "ERROR")
        return

    if not EDR_CLIENT.is_logged_in():
        EDRLOG.log(u"[EDR]Not logged in, aborting.", "ERROR")
        return

    if is_beta:
        EDRLOG.log(u"[EDR]Player is in beta: skip!", "INFO")
        return

    place = ""
    ship = ""
    cmdr_status_updated = False
    reason_for_update = ""

    if entry["event"] in ["Music"] and entry["MusicTrack"] == "MainMenu":
        ed_player.game_mode = None
        ed_player.leave_wing()
        EDRLOG.log(u"[EDR]Player is on the main menu.", "DEBUG")
        return

    if entry["event"] == "Resurrect":
        ed_player.resurrect()
        EDRLOG.log(u"[EDR]Player has been resurrected.", "DEBUG")
        return

    if entry["event"] in ["Fileheader"] and entry["part"] == 1:
        ed_player.inception()
        EDR_CLIENT.status = "friends & wing: OK!"
        EDRLOG.log(u"Journal player just got created, we should have an accurate picture of friends/wings.", "DEBUG")


    if entry["event"] in ["LoadGame"]:
        EDR_CLIENT.warmup()
        ed_player.inception()
        ed_player.game_mode = entry["GameMode"]
        EDRLOG.log(u"Game mode is {}".format(ed_player.game_mode), "DEBUG")
    
    if entry["event"] in ["Friends"]:
        ed_player.update_friend(entry["Name"], entry["Status"])
        friend_u = entry["Name"].encode('utf-8', 'replace')
        EDR_CLIENT.status = u"friend {name} is {status}.".format(name=friend_u, status=entry["Status"])
        EDRLOG.log(u"Updated friend: {name} is {status}".format(name=friend_u, status=entry["Status"]), "DEBUG")

    if ed_player.in_solo_or_private():
        EDR_CLIENT.status = "disabled in Solo/Private."
        EDRLOG.log(u"game mode is Solo or Group: skip! {}".format(ed_player.game_mode), "INFO")
        return

    if entry["event"] in ["WingAdd"]:
        ed_player.add_to_wing(entry["Name"])
        EDR_CLIENT.status = "added to wing: " + entry["Name"]
        EDRLOG.log(u"Addition to wing: {}".format(ed_player.wing), "INFO")
    
    if entry["event"] in ["WingJoin"]:
        ed_player.join_wing(entry["Others"])
        EDR_CLIENT.status = "joined wing."
        EDRLOG.log(u"Joined a wing: {}".format(ed_player.wing), "INFO")
        
    if entry["event"] in ["WingLeave"]:
        ed_player.leave_wing()
        EDR_CLIENT.status = "left wing."
        EDRLOG.log(u" Left the wing.", "INFO")

    EDR_CLIENT.player_name(cmdr)
    ship = state["ShipType"]

    cmdr_status_updated = ed_player.update_ship_if_obsolete(ship, entry["timestamp"])
    cmdr_status_updated |= ed_player.update_star_system_if_obsolete(system, entry["timestamp"])

    if entry["event"] in ["Location"]:
        if entry["Docked"]:
            place = entry["StationName"]
        else:
            place = entry["Body"]
        cmdr_status_updated |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        reason_for_update = "Location event"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")

    if entry["event"] in ["Undocked", "Docked", "DockingCancelled", "DockingDenied", "DockingGranted", "DockingRequested", "DockingTimeout"]:
        place = entry["StationName"]
        cmdr_status_updated |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        reason_for_update = "Docking events"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")

    if entry["event"] in ["SupercruiseExit"]:
        place = entry["Body"]
        cmdr_status_updated |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        reason_for_update = "Supercruise exit"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")

    if entry["event"] in ["FSDJump", "SupercruiseEntry"]:
        place = "Supercruise"
        cmdr_status_updated |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        reason_for_update = "Jump events"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")

    
    if entry["event"] == ["StartJump"] and entry["JumpType"] == "Hyperspace":
        place = "Hyperspace"
        cmdr_status_updated |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        reason_for_update = "Jump events"
        EDR_CLIENT.check_system(entry["StarSystem"])
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
    
    if entry["event"] in ["ApproachSettlement"]:
        place = entry["Name"]
        cmdr_status_updated |= ed_player.update_place_if_obsolete(place, entry["timestamp"])
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
        reason_for_update = "Approach event"

    if entry["event"] in ["Interdicted", "Died", "EscapeInterdiction", "Interdiction", "PvPKill"]:
        report_crime(ed_player, entry)

    if entry["event"] in ["ReceiveText", "SendText"]:
        report_comms(ed_player, entry)

    if entry["event"] in ["SendText"]:
        handle_commands(ed_player, entry)

    if cmdr_status_updated:
        edr_update_cmdr_status(ed_player, reason_for_update)


def edr_update_cmdr_status(cmdr, reason_for_update):
    """
    Send a status update for a given cmdr
    :param cmdr:
    :param reason_for_update:
    :return:
    """

    if not cmdr.in_open():
        EDR_CLIENT.status = "not in Open? Start EDR before Elite."
        EDRLOG.log(u"Skipping cmdr update due to unconfirmed Open mode", "ERROR")
        return

    if cmdr.has_partial_status():
        EDR_CLIENT.status = "partial status."
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

    EDRLOG.log(u"name: {name}, starSystem: {star_system}, place:{place}, ship:{ship}, timestamp:{timestamp}, source:{source}".format(name=cmdr.name, star_system=cmdr.star_system, place=cmdr.place, ship=cmdr.ship, timestamp=cmdr.timestamp, source=reason_for_update), "DEBUG")
    
    if not EDR_CLIENT.blip(cmdr.name, report):
        EDR_CLIENT.status = "status update failed."
        EDR_CLIENT.evict_cmdr(cmdr.name)
        return

    EDR_CLIENT.status = "status updated!"


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
        EDR_CLIENT.status = "not in Open? Start EDR before Elite."
        return

    criminals = []
    for criminal_cmdr in criminal_cmdrs:
        EDRLOG.log(u"Appending criminal {name} with ship {ship}".format(name=criminal_cmdr.name, ship=criminal_cmdr.ship), "DEBUG")
        criminals.append({"name": criminal_cmdr.name, "ship": criminal_cmdr.ship})

    report = {
        "starSystem": victim.star_system,
        "place": victim.place,
        "timestamp": victim.timestamp_js_epoch(),
        "criminals": criminals,
        "offence": offence,
        "victim": victim.name,
        "victimShip": victim.ship,
        "reportedBy": victim.name
    }

    system_id = EDR_CLIENT.system_id(victim.star_system)
    if system_id is None:
        EDR_CLIENT.status = "no system id (crime)."
        EDRLOG.log(u"Can't submit crime report (no system id).", "ERROR")
        return

    if not EDR_CLIENT.crime(system_id, report):
        EDR_CLIENT.status = "failed to report crime."
        EDR_CLIENT.evict_system(victim.star_system)
        return

    EDR_CLIENT.status = "crime reported!"


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
        EDR_CLIENT.status = "not in Open? Start EDR before Elite."
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
        "reportedBy": criminal_cmdr.name
    }

    system_id = EDR_CLIENT.system_id(criminal_cmdr.star_system)
    if system_id is None:
        EDR_CLIENT.status = "no system id (crime)."
        EDRLOG.log(u"Can't submit perpetrated crime (no system id).", "ERROR")
        return

    EDRLOG.log(u"Perpetrated crime in system {} on {}".format(system_id, victim), "INFO")
    EDRLOG.log(u"Perpetrated crime json: {}".format(report), "DEBUG")
   
    if not EDR_CLIENT.crime(system_id, report):
        EDR_CLIENT.status = "failed to report crime (self)."
        EDR_CLIENT.evict_system(criminal_cmdr.star_system)
        return

    EDR_CLIENT.status = "crime reported!"


def edr_submit_contact(cmdr_name, timestamp, source, witness):
    """
    Report a contact with a cmdr
    :param cmdr:
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
        "ship" : u"Unknown",
        "source": source,
        "reportedBy": witness.name
    }

    if not witness.in_open():
        EDRLOG.log(u"Skipping submit contact due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = "not in Open? Start EDR before Elite."
        return

    if witness.has_partial_status():
        EDR_CLIENT.status = "partial status."
        EDRLOG.log(u"Skipping cmdr update due to partial status", "INFO")
        return

    if not EDR_CLIENT.blip(cmdr_name, report):
        EDR_CLIENT.status = "failed to report contact."
        EDR_CLIENT.evict_cmdr(cmdr_name)
    
    edr_submit_traffic(cmdr_name, timestamp, source, witness)


def edr_submit_traffic(cmdr_name, timestamp, source, witness):
    """
    Report a contact with a cmdr
    :param cmdr:
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
        "ship" : u"Unknown",
        "source": source,
        "reportedBy": witness.name
    }

    if not witness.in_open():
        EDRLOG.log(u"Skipping submit traffic due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = "not in Open? Start EDR before Elite."
        return

    if witness.has_partial_status():
        EDR_CLIENT.status = "partial status."
        EDRLOG.log(u"Skipping traffic update due to partial status", "INFO")
        return

    system_id = EDR_CLIENT.system_id(witness.star_system)
    if system_id is None:
        EDR_CLIENT.status = "no system id (traffic)."
        EDRLOG.log(u"Can't submit traffic report (no system id).", "ERROR")
        return

    if not EDR_CLIENT.traffic(system_id, report):
        EDR_CLIENT.status = "failed to report traffic."
        EDR_CLIENT.evict_system(witness.star_system)


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
                    criminal_cmdr.name = killer["Name"]
                    criminal_cmdrs.append(criminal_cmdr)
            edr_submit_crime(criminal_cmdrs, "Murder", cmdr)
        else:
            if "KillerName" in entry and entry["KillerName"].startswith("Cmdr "):
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
    if entry["event"] == "ReceiveText":
        if entry["Channel"] in ["local"]:
            fromCmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                fromCmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            edr_submit_contact(fromCmdr, entry["timestamp"], "Received text (local)", cmdr)
        elif entry["Channel"] in ["player"]:
            fromCmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                fromCmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            if cmdr.is_only_reachable_locally(fromCmdr):
                EDRLOG.log(u"Received text from {cmdr} who is not a friend nor in the wing == only reachable locally".format(cmdr=fromCmdr), "INFO")
                edr_submit_contact(fromCmdr, entry["timestamp"], "Received text (non wing/friend player)", cmdr)
            else:
                EDR_CLIENT.status = "comms origin is unclear."
                EDRLOG.log(u"Received text from {cmdr} who might be a friend or in the wing. No guarantees about that player's location".format(cmdr=fromCmdr), "INFO")
    elif entry["event"] == "SendText" and not entry["To"] in ["local", "wing"]:
        toCmdr = entry["To"]
        if entry["To"].startswith("$cmdr_decorate:#name="):
            toCmdr = entry["To"][len("$cmdr_decorate:#name="):-1]
        if cmdr.is_only_reachable_locally(toCmdr):
            EDRLOG.log(u"Sent text to {to} who is not a friend nor in the wing == only reachable locally".format(to=toCmdr), "INFO")
            edr_submit_contact(toCmdr, entry["timestamp"], "Sent text (non wing/friend player)", cmdr)
        else:
            EDR_CLIENT.status = "comms destination is unclear."
            EDRLOG.log(u"Sent text to {to} who might be a friend or in the wing. No guarantees about that player's location".format(to=toCmdr), "INFO")


def handle_commands(cmdr, entry):
    """
    Report a comms contact to the server
    :param cmdr:
    :param entry:
    :return:
    """
    if not (entry["event"] == "SendText"):
        return
    
    command = entry["Message"].split(" ", 1)
    if command[0] == "!overlay":
        overlay_command("" if len(command) == 1 else command[1])
    elif command[0] == "!normal_width" and len(command) == 2:
        EDRLOG.log(u"Setting width for normal font weight", "INFO")
        EDR_CLIENT.IN_GAME_MSG.normal_width = float(command[1])
    elif command[0] == "!large_width" and len(command) == 2:
        EDRLOG.log(u"Setting width for lage font weight", "INFO")
        EDR_CLIENT.IN_GAME_MSG.large_width = float(command[1])               
    elif command[0] == "!help":
        EDRLOG.log(u"!overlay [on/off/ ] to enable, disable or test EDR's overlay feature.", "INFO")
        EDRLOG.log(u"!audiocue [on/off/loud/soft] to enable or disable and control the volume of EDR's audio feedback.", "INFO")
        EDRLOG.log(u"!crimes [on/off/ ] to enable or disable and check the status of EDR's crime reporting feature.", "INFO")
    elif command[0] == "!audiocue" and len(command) == 2:
        audiocue_command(command[1])
    elif command[0] == "o7" and not entry["To"] in ["local", "voicechat", "wing", "friend"]:
        EDRLOG.log(u"Implicit who command for {}".format(entry["To"]), "INFO")
        toCmdr = entry["To"]
        if entry["To"].startswith("$cmdr_decorate:#name="):
            toCmdr = entry["To"][len("$cmdr_decorate:#name="):-1]
        EDR_CLIENT.who(toCmdr)
    elif command[0] == "!who" and len(command) == 2:
        EDRLOG.log(u"Explicit who command for {}".format(command[1]), "INFO")
        EDR_CLIENT.who(command[1])
    elif command[0] == "!crimes":
        crimes_command("" if len(command) == 1 else command[1])

def overlay_command(param):
    if param == "":
        EDRLOG.log(u"Is visual feedback enabled? {}".format("Yes." if EDR_CLIENT.visual_feedback else "No."), "INFO")
        EDR_CLIENT.notify_with_details("Test Notice", ["notice info 1", "notice info 2"])
        EDR_CLIENT.warn_with_details("Test Warning", ["warning info 1", "warning info 2"])
    elif param == "on":
        EDRLOG.log(u"Enabling visual feedback", "INFO")
        EDR_CLIENT.visual_feedback =True
        EDR_CLIENT.warmup()
    elif param == "off":
        EDRLOG.log(u"Disabling visual feedback", "INFO")
        EDR_CLIENT.notify_with_details("Visual Feedback System", ["disabling"])
        EDR_CLIENT.visual_feedback = False

def crimes_command(param):
    if param == "":
        EDRLOG.log(u"Is EDR's crimes report enabled? {}".format("Yes." if EDR_CLIENT.crimes_reporting else "No."), "INFO")
        EDR_CLIENT.notify_with_details("EDR crimes report", ["Enabled" if EDR_CLIENT.crimes_reporting else "Disabled"])
    elif param == "on":
        EDRLOG.log(u"Enabling crimes reporting", "INFO")
        EDR_CLIENT.crimes_reporting =True
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
        EDR_CLIENT.loudAudioFeedback()
        EDR_CLIENT.audio_feedback = True
        EDR_CLIENT.notify_with_details("EDR audio cues", ["Enabled", "Loud"])
    elif param == "soft":
        EDRLOG.log(u"Soft audio feedback", "INFO")
        EDR_CLIENT.softAudioFeedback()
        EDR_CLIENT.audio_feedback = True
        EDR_CLIENT.notify_with_details("EDR audio cues", ["Enabled", "Soft"])