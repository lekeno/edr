"""
Plugin for "EDR"
"""
from edspacesuits import EDSpaceSuit
import sys
import re
import random
import codecs

try:
    import edmc_data
except ImportError:
    import plug as edmc_data

from edrclient import EDRClient
from edentities import EDPlayer
from edsitu import EDPlanetaryLocation
from edvehicles import EDVehicleFactory
from edrrawdepletables import EDRRawDepletables
from edtime import EDTime
from edrlog import EDRLog
import edentities
import edrautoupdater
from edri18n import _, _c

EDR_CLIENT = EDRClient()
EDRLOG = EDRLog()
LAST_KNOWN_SHIP_NAME = ""
OVERLAY_DUMMY_COUNTER = 0

def plugin_start3(plugin_dir):
    return plugin_start()

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
        plugin_update()
    EDRLOG.log(u"Plugin stopped", "INFO")

def plugin_update():
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


def plugin_prefs(parent, cmdr, is_beta):
    return EDR_CLIENT.prefs_ui(parent)

def prefs_changed(cmdr, is_beta):
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
        EDR_CLIENT.who(wingmate, autocreate=True)
    elif entry["event"] in ["WingJoin"]:
        # TODO some inconsistency when other members leave the wing, and others come in...
        ed_player.join_wing(entry["Others"])
        EDR_CLIENT.status = _(u"joined wing.")
        EDRLOG.log(u"Joined a wing: {}".format(ed_player.wing), "INFO")
    elif entry["event"] in ["WingLeave"]:
        ed_player.leave_wing()
        EDR_CLIENT.status = _(u"left wing.")
        EDRLOG.log(u" Left the wing.", "INFO")
    elif entry["event"] in ["WingInvite"]:
        requester = plain_cmdr_name(entry["Name"])
        EDR_CLIENT.status = _(u"wing invite from: ").format(requester)
        EDRLOG.log(u"Wing invite from: {}".format(requester), "INFO")
        EDR_CLIENT.who(requester, autocreate=True)


def handle_multicrew_events(ed_player, entry):
    if entry["event"] in ["CrewMemberJoins", "CrewMemberRoleChange", "CrewLaunchFighter"]:
        crew = plain_cmdr_name(entry["Crew"])
        success = ed_player.add_to_crew(crew)
        if success: # only show intel on the first add 
            EDR_CLIENT.status = _(u"added to crew: ").format(crew)
            EDRLOG.log(u"Addition to crew: {}".format(ed_player.crew.members), "INFO")
            EDR_CLIENT.who(crew, autocreate=True)

    if entry["event"] in ["CrewMemberQuits", "KickCrewMember"]:
        crew = plain_cmdr_name(entry["Crew"])
        duration = ed_player.crew_time_elapsed(crew)
        kicked = entry["event"] == "KickCrewMember"
        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        ed_player.remove_from_crew(crew)
        EDR_CLIENT.status = _(u"{} left the crew.").format(crew)
        EDRLOG.log(u"{} left the crew.".format(crew), "INFO")
        edt = EDTime()
        edt.from_journal_timestamp(entry["timestamp"])
        report = {
            "captain": ed_player.crew.captain,
            "timestamp": edt.as_js_epoch(),
            "crew" : crew,
            "duration": duration,
            "kicked": kicked,
            "crimes": crimes,
            "destroyed":  ed_player.destroyed if ed_player.is_captain() else False
        }
        edr_submit_multicrew_session(ed_player, report)

    if entry["event"] in ["JoinACrew"]:
        captain = plain_cmdr_name(entry["Captain"])
        ed_player.join_crew(captain)
        EDR_CLIENT.status = _(u"joined a crew.")
        EDRLOG.log(u"Joined captain {}'s crew".format(captain), "INFO")
        EDR_CLIENT.who(captain, autocreate=True)

    if entry["event"] in ["QuitACrew"] and ed_player.crew:
        for member in ed_player.crew.members:
            duration = ed_player.crew_time_elapsed(member)
            edt = EDTime()
            edt.from_journal_timestamp(entry["timestamp"])
            report = {
                "captain": ed_player.crew.captain,
                "timestamp": edt.as_js_epoch(),
                "crew" : member,
                "duration": duration,
                "kicked": False,
                "crimes": False,
                "destroyed": ed_player.destroyed if ed_player.is_captain() else False
            }    
            edr_submit_multicrew_session(ed_player, report)
        ed_player.leave_crew()
        EDR_CLIENT.status = _(u"left crew.")
        EDRLOG.log(u"Left the crew.", "INFO")

    if entry["event"] in ["EndCrewSession"] and ed_player.crew:
        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        for member in ed_player.crew.members:
            duration = ed_player.crew_time_elapsed(member)
            edt = EDTime()
            edt.from_journal_timestamp(entry["timestamp"])
            report = {
                "captain": ed_player.crew.captain,
                "timestamp": edt.as_js_epoch(),
                "crew" : member,
                "duration": duration,
                "kicked": False,
                "crimes": crimes,
                "destroyed": ed_player.destroyed if ed_player.is_captain() else False
            }    
            edr_submit_multicrew_session(ed_player, report)
        ed_player.disband_crew()
        EDR_CLIENT.status = _(u"crew disbanded.")
        EDRLOG.log(u"Crew disbanded.", "INFO")

def handle_carrier_events(ed_player, entry):
    if entry["event"] == "CarrierBuy":
        ed_player.fleet_carrier.bought(entry)
    elif entry["event"] == "CarrierStats":
        ed_player.fleet_carrier.update_from_stats(entry)
    elif entry["event"] == "CarrierJumpRequest":
        EDR_CLIENT.fc_jump_requested(entry)
    elif entry["event"] == "CarrierJumpCancelled":
        EDR_CLIENT.fc_jump_cancelled(entry)
    elif entry["event"] == "CarrierDecomission":
        ed_player.fleet_carrier.decommission_requested(entry)
    elif entry["event"] == "CarrierCancelDecommission":
        ed_player.fleet_carrier.cancel_decommission(entry)
    elif entry["event"] == "CarrierDockingPermission":
        ed_player.fleet_carrier.update_docking_permissions(entry)
    elif entry["event"] == "CarrierJump":
        ed_player.fleet_carrier.update_from_jump_if_relevant(entry)

def handle_movement_events(ed_player, entry):
    outcome = {"updated": False, "reason": None}

    if entry["event"] in ["SupercruiseExit"]:
        body = entry["Body"]
        outcome["updated"] |= ed_player.update_body_if_obsolete(body)
        outcome["updated"] |= ed_player.update_place_if_obsolete(body)
        outcome["reason"] = "Supercruise exit"
        ed_player.to_normal_space()
        EDRLOG.log(u"Body changed: {}".format(body), "INFO")
    elif entry["event"] in ["FSDJump", "CarrierJump"]:
        place = "Supercruise"
        outcome["updated"] |= ed_player.update_place_if_obsolete(place)
        ed_player.wanted = entry.get("Wanted", False)
        ed_player.mothership.fuel_level = entry.get("FuelLevel", ed_player.mothership.fuel_level)
        EDR_CLIENT.docking_guidance(entry)
        EDR_CLIENT.noteworthy_about_system(entry)
        ed_player.location.population = entry.get('Population', 0)
        ed_player.location.allegiance = entry.get('SystemAllegiance', 0)
        outcome["reason"] = entry["event"]
        ed_player.to_super_space()
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
    elif entry["event"] in ["SupercruiseEntry"]:
        place = "Supercruise"
        outcome["updated"] |= ed_player.update_place_if_obsolete(place)
        outcome["reason"] = "Jump events"
        ed_player.to_super_space()
        EDR_CLIENT.docking_guidance(entry)
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
    elif entry["event"] == "StartJump" and entry["JumpType"] == "Hyperspace":
        place = "Hyperspace"
        outcome["updated"] |= ed_player.update_place_if_obsolete(place)
        outcome["reason"] = "Hyperspace"
        ed_player.to_hyper_space()
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
        EDR_CLIENT.docking_guidance(entry)
        EDR_CLIENT.check_system(entry["StarSystem"], may_create=True)
    elif entry["event"] in ["ApproachSettlement"]:
        place = entry["Name"]
        body = entry.get("BodyName", None)
        outcome["updated"] |= ed_player.update_place_if_obsolete(place)
        outcome["updated"] |= ed_player.update_body_if_obsolete(body)        
        EDRLOG.log(u"Place/Body changed: {}, {}".format(place, body), "INFO")
        outcome["reason"] = "Approach event"
    elif entry["event"] in ["ApproachBody"]:
        body = entry["Body"]
        outcome["updated"] |= ed_player.update_body_if_obsolete(body)
        outcome["updated"] |= ed_player.update_place_if_obsolete(body)
        EDRLOG.log(u"Body & place changed: {}".format(body), "INFO")
        outcome["reason"] = "Approach event"
        if EDR_CLIENT.noteworthy_about_body(entry["StarSystem"], entry["Body"]) and ed_player.planetary_destination is None:
            poi = EDR_CLIENT.closest_poi_on_body(entry["StarSystem"], entry["Body"], ed_player.attitude)
            ed_player.planetary_destination = EDPlanetaryLocation(poi)
    elif entry["event"] in ["LeaveBody"]:
        place = "Supercruise"
        ed_player.planetary_destination = None
        outcome["updated"] |= ed_player.update_place_if_obsolete(place)
        outcome["updated"] |= ed_player.update_body_if_obsolete(None)
        EDRLOG.log(u"Place changed: {}, body cleared".format(place), "INFO")
        outcome["reason"] = "Leave event"
    return outcome

def handle_change_events(ed_player, entry):
    outcome = {"updated": False, "reason": None}
    if entry["event"] in ["Location"]:
        if entry["Docked"]:
            place = entry["StationName"]
            outcome["updated"] |= ed_player.update_place_if_obsolete(place)
            EDRLOG.log(u"Place changed: {} (location event)".format(place), "INFO")
        body = entry.get("Body", None)
        outcome["updated"] |= ed_player.update_body_if_obsolete(body)
        EDRLOG.log(u"Body changed: {} (location event)".format(body), "INFO")
        ed_player.to_normal_space()
        ed_player.wanted = entry.get("Wanted", False)
        ed_player.location_security(entry.get("SystemSecurity", None))
        ed_player.location.population = entry.get("Population", None)
        ed_player.location.allegiance = entry.get("SystemAllegiance", None)
        outcome["reason"] = "Location event"
        EDR_CLIENT.check_system(entry["StarSystem"], may_create=True, coords=entry.get("StarPos", None))

    if entry["event"] in ["Undocked", "Docked", "DockingCancelled", "DockingDenied",
                          "DockingGranted", "DockingRequested", "DockingTimeout"]:
        place = entry.get("StationName", "Unknown")
        outcome["updated"] |= ed_player.update_place_if_obsolete(place)
        ed_player.to_normal_space()
        EDR_CLIENT.docking_guidance(entry)
        if entry["event"] == "Docked":
            ed_player.wanted = entry.get("Wanted", False)
            ed_player.mothership.update_cargo()
            if ed_player.mothership.could_use_limpets():
                limpets = ed_player.mothership.cargo.how_many("drones")
                capacity = ed_player.mothership.cargo_capacity
                EDR_CLIENT.notify_with_details(_(U"Restock reminder"), [_(u"Don't forget to restock on limpets before heading out."), _(u"Limpets: {}/{}").format(limpets, capacity)])
        elif entry["event"] == "Undocked" and ed_player.mothership.is_mining_rig():
            ed_player.reset_stats()
        outcome["reason"] = "Docking events"
        EDRLOG.log(u"Place changed: {}".format(place), "INFO")
    return outcome

def handle_fc_position_related_events(ed_player, entry):
    if entry["event"] in ["Location", "Docked", "Undocked", "DockingCancelled", "DockingDenied", "DockingGranted", "DockingRequested", "DockingTimeout"]:
        station_type = entry.get("StationType", None)
        if station_type and station_type != "FleetCarrier":
            return
        station_name = entry.get("StationName", None)
        market_id = entry.get("MarketID", 0)
        star_system = entry.get("StarSystem", ed_player.star_system)
        if not star_system:
            return
        ed_player.fleet_carrier.update_star_system_if_relevant(star_system, market_id, station_name)

def handle_lifecycle_events(ed_player, entry, state, from_genesis=False):
    if entry["event"] == "Music":
        if entry["MusicTrack"] == "MainMenu" and not ed_player.is_crew_member():
            # Checking for 'is_crew_member' because "MainMenu" shows up when joining a multicrew session
            # Assumption: being a crew member while main menu happens means that a multicrew session is about to start.
            # { "timestamp":"2018-06-19T13:06:04Z", "event":"QuitACrew", "Captain":"Dummy" }
            # { "timestamp":"2018-06-19T13:06:16Z", "event":"Music", "MusicTrack":"MainMenu" }
            EDR_CLIENT.clear()
            EDR_CLIENT.game_mode(None)
            ed_player.leave_wing()
            ed_player.leave_crew()
            ed_player.leave_vehicle()
            EDRLOG.log(u"Player is on the main menu.", "DEBUG")
            return
        elif entry["MusicTrack"] == "Combat_Dogfight":
            if ed_player.mothership:
                ed_player.mothership.skirmish() # TODO check music event for on foot combat
            return
        elif entry["MusicTrack"] == "Combat_LargeDogFight":
            if ed_player.mothership:
                ed_player.mothership.battle()  # TODO check music event for on foot combat
            return
        elif entry["MusicTrack"] == "Combat_SRV":
            if ed_player.srv:
                ed_player.srv.skirmish()
            return
        elif entry["MusicTrack"] in ["Supercruise", "Exploration", "NoTrack"] and ed_player.in_a_fight():
            ed_player.in_danger(False)
            return
        elif entry["MusicTrack"] == "SystemMap":
            EDR_CLIENT.noteworthy_signals_in_system() # probably annoying
            return
        elif entry["MusicTrack"] == "OnFoot":
            ed_player.in_spacesuit()
            return

    if entry["event"] == "Shutdown":
        EDRLOG.log(u"Shutting down in-game features...", "INFO")
        EDR_CLIENT.shutdown()
        return

    if entry["event"] == "Resurrect":
        EDR_CLIENT.clear()
        ed_player.resurrect(entry["Option"] in ["rebuy", "recover"])
        EDRLOG.log(u"Player has been resurrected.", "DEBUG")
        return

    if entry["event"] in ["Fileheader"] and entry["part"] == 1:
        EDR_CLIENT.clear()
        ed_player.inception(genesis=True)
        EDR_CLIENT.status = _(u"initialized.")
        EDRLOG.log(u"Journal player got created: accurate picture of friends/wings.",
                   "DEBUG")
        return

    if entry["event"] in ["LoadGame"]:
        if ed_player.inventory.stale_or_incorrect():
            ed_player.inventory.initialize_with_edmc(state)
        EDR_CLIENT.clear()
        ed_player.inception(genesis=from_genesis)
        if from_genesis:
            EDRLOG.log(u"Heuristics genesis: probably accurate picture of friends/wings.",
                   "DEBUG")
        if entry.get("Odyssey", False):
            EDR_CLIENT.set_dlc("Odyssey")
            EDRLOG.log(u"DLC is Odyssey", "DEBUG")
        elif entry.get("Horizons", False):
            EDR_CLIENT.set_dlc("Horizons")
            EDRLOG.log(u"DLC is Horizons", "DEBUG")
        EDR_CLIENT.game_mode(entry["GameMode"], entry.get("Group", None))
        
        ed_player.update_vehicle_or_suit_if_obsolete(entry)
        EDRLOG.log(u"Game mode is {}".format(entry["GameMode"]), "DEBUG")
        EDR_CLIENT.warmup()
        return

    if entry["event"] in ["Loadout"]:
        if ed_player.mothership.id == entry.get("ShipID", None):
            ed_player.mothership.update_from_loadout(entry)
            ed_player.mothership.update_cargo()
            if ed_player.mothership.could_use_limpets() and ed_player.is_docked:
                limpets = ed_player.mothership.cargo.how_many("drones")
                capacity = ed_player.mothership.cargo_capacity
                EDR_CLIENT.notify_with_details(_(U"Restock reminder"), [_(u"Don't forget to restock on limpets before heading out."), _(u"Limpets: {}/{}").format(limpets, capacity)])
            global LAST_KNOWN_SHIP_NAME
            LAST_KNOWN_SHIP_NAME = ed_player.mothership.name
        else:
            ed_player.update_vehicle_if_obsolete(EDVehicleFactory.from_load_game_event(entry), piloted=True)
        return

    if entry["event"] in ["SuitLoadout", "SwitchSuitLoadout"]:
        ed_player.update_vehicle_or_suit_if_obsolete(entry)
        return

    if entry["event"] in ["LaunchSRV"] and entry.get("PlayerControlled", False):
        ed_player.in_srv()
        return
    
    if entry["event"] in ["DockSRV"]:
        ed_player.in_mothership()
        return

    if entry["event"] in ["Disembark"]:
        ed_player.disembark(entry)
        return

    if entry["event"] in ["Embark"]:
        ed_player.embark(entry)
        return

    if entry["event"] in ["DropshipDeploy"]:
        ed_player.dropship_deployed(entry)
        return

def handle_friends_events(ed_player, entry):
    if entry["event"] != "Friends":
        return

    if entry["Status"] == "Requested":
        requester = plain_cmdr_name(entry["Name"])
        EDR_CLIENT.who(requester, autocreate=True)
    elif entry["Status"] == "Offline":
        ed_player.deinstanced_player(entry["Name"])

def handle_engineer_progress(ed_player, entry):
    if entry["event"] != "EngineerProgress":
        return
    ed_player.engineers.update(entry)

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

def dashboard_entry(cmdr, is_beta, entry):
    # TODO suit/on foot specific flags
    ed_player = EDR_CLIENT.player
    
    if not prerequisites(EDR_CLIENT, is_beta):
        return

    if not 'Flags' in entry:
        return

    flags = entry.get('Flags', 0)
    flags2 = entry.get('Flags2', 0)

    # TODO in multicrew
    
    if (flags2 & (edmc_data.Flags2OnFoot | edmc_data.Flags2OnFootInStation | edmc_data.Flags2OnFootOnPlanet | edmc_data.Flags2OnFootInHangar | edmc_data.Flags2OnFootSocialSpace | edmc_data.Flags2OnFootExterior)):
        ed_player.in_spacesuit()
        EDR_CLIENT.on_foot()
    else:
        EDR_CLIENT.in_ship()
        if (flags & edmc_data.FlagsInMainShip) and not (flags2 & edmc_data.Flags2InTaxi):
            ed_player.in_mothership()
        
        if (flags & edmc_data.FlagsInFighter):
            ed_player.in_slf()

        if (flags & edmc_data.FlagsInSRV):
            ed_player.in_srv()
        
        if (flags2 & edmc_data.Flags2InTaxi):
            ed_player.in_taxi()
    
    ed_player.spacesuit.low_health = flags2 & edmc_data.Flags2LowHealth
    ed_player.spacesuit.low_oxygen = flags2 & edmc_data.Flags2LowOxygen
    
    if (entry.get("Oxygen", None)):
        ed_player.spacesuit.oxygen = entry["Oxygen"]
    
    if (entry.get("Health", None)):
        ed_player.spacesuit.health = entry["Health"]


    if (flags & edmc_data.FlagsFsdJump or flags2 & edmc_data.Flags2GlideMode):
        ed_player.in_blue_tunnel()
    else:
        ed_player.in_blue_tunnel(False)
    
    if ed_player.piloted_vehicle:
        ed_player.piloted_vehicle.low_fuel = bool(flags & edmc_data.FlagsLowFuel)
    ed_player.docked(bool(flags & edmc_data.FlagsDocked))
    unsafe = bool(flags & edmc_data.FlagsIsInDanger)
    ed_player.in_danger(unsafe)
    deployed = bool(flags & edmc_data.FlagsHardpointsDeployed)
    ed_player.hardpoints(deployed)
    
    safe = not unsafe
    retracted = not deployed
    if ed_player.recon_box.active and (safe and retracted):
        ed_player.recon_box.reset()
        EDR_CLIENT.notify_with_details(_(u"EDR Central"), [_(u"Fight reporting disabled"), _(u"Looks like you are safe, and disengaged.")])
    
    if ed_player.in_normal_space() and ed_player.recon_box.process_signal(flags & edmc_data.FlagsLightsOn):
        if ed_player.recon_box.active:
            EDR_CLIENT.notify_with_details(_(u"EDR Central"), [_(u"Fight reporting enabled"), _(u"Turn it off: flash your lights twice, or leave this area, or escape danger and retract hardpoints.")])
        else:
            EDR_CLIENT.notify_with_details(_(u"EDR Central"), [_(u"Fight reporting disabled"), _(u"Flash your lights twice to re-enable.")])

    fuel = entry.get('Fuel', None)
    if fuel and ed_player.piloted_vehicle:  # TODO on foot case?
        main = fuel.get('FuelMain', ed_player.piloted_vehicle.fuel_level)
        reservoir = fuel.get('FuelReservoir', 0)
        ed_player.piloted_vehicle.fuel_level = main + reservoir

    attitude_keys = { "Latitude", "Longitude", "Heading", "Altitude"}
    if sys.version_info.major == 2:
        if entry.viewkeys() < attitude_keys:
            return
    else:
        if entry.keys() < attitude_keys:
            return
    
    attitude = { key.lower():value for key,value in entry.items() if key in attitude_keys }
    if "altitude" in attitude:
        attitude["altitude"] /= 1000.0
    ed_player.update_attitude(attitude)
    if ed_player.planetary_destination:
        EDR_CLIENT.show_navigation()

def handle_mining_events(ed_player, entry):
    if entry["event"] not in ["MiningRefined", "ProspectedAsteroid"]:
        return
    if entry["event"] == "ProspectedAsteroid":
        ed_player.prospected(entry)
    elif entry["event"] == "MiningRefined":
        ed_player.refined(entry)
    EDR_CLIENT.mining_guidance()

def handle_bounty_hunting_events(ed_player, entry):
    if entry["event"] not in ["Bounty", "ShipTargeted"]:
        return
    if entry["event"] == "Bounty" and entry.get("Rewards", None):
        ed_player.bounty_awarded(entry)
        EDR_CLIENT.bounty_hunting_guidance()
    elif entry["event"] == "ShipTargeted":
        if entry["TargetLocked"] and entry["ScanStage"] >= 3 and entry.get("Bounty", 0) > 0:
            ed_player.bounty_scanned(entry)
            EDR_CLIENT.bounty_hunting_guidance()
        else:
            EDR_CLIENT.bounty_hunting_guidance(turn_off=True) 
            
def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    :param cmdr:
    :param system:
    :param station:
    :param entry:
    :param state:
    :return:
    """
    EDR_CLIENT.player_name(cmdr)
    ed_player = EDR_CLIENT.player
    ed_player.friends = state["Friends"]
        
    if not prerequisites(EDR_CLIENT, is_beta):
        return

    EDR_CLIENT.edrdiscord.process(entry)

    if entry["event"] in ["Shutdown", "ShutDown", "Music", "Resurrect", "Fileheader", "LoadGame", "Loadout", "SuitLoadout", "SwitchSuitLoadout", "LaunchSRV", "DockSRV", "Disembark", "Embark", "DropShipDeploy"]:
        from_genesis = False
        if "first_run" not in journal_entry.__dict__:
            journal_entry.first_run = False
            from_genesis = (entry["event"] == "LoadGame") and (cmdr and system is None and station is None)
        handle_lifecycle_events(ed_player, entry, state, from_genesis)

    if entry["event"] in ["BookTaxi", "BookDropship", "CancelTaxi", "CancelDropship"]:
        handle_shuttle_events(entry)
    
    if entry["event"] in ["SetUserShipName", "SellShipOnRebuy", "ShipyardBuy", "ShipyardNew", "ShipyardSell", "ShipyardTransfer", "ShipyardSwap"]:
        handle_fleet_events(entry)

    if entry["event"] in ["ModuleInfo"]:
        handle_modules_events(ed_player, entry)

    if entry["event"] in ["Cargo"]:
        ed_player.piloted_vehicle.update_cargo()

    if entry["event"] in ["EjectCargo", "CollectCargo"]:
        handle_cargo_events(ed_player, entry)

    
    if entry["event"].startswith("Powerplay"):
        EDRLOG.log(u"Powerplay event: {}".format(entry), "INFO")
        handle_powerplay_events(ed_player, entry)
    
    if entry["event"] == "Statistics" and not ed_player.powerplay:
        # There should be a Powerplay event before the Statistics event
        # if not then the player is not pledged and we should reflect that on the server
        EDR_CLIENT.pledged_to(None)

    if entry["event"] == "Friends":
        handle_friends_events(ed_player, entry)

    if entry["event"] == "EngineerProgress":
        handle_engineer_progress(ed_player, entry)

    if entry["event"] in ["Materials", "MaterialCollected", "MaterialDiscarded", "EngineerContribution", "EngineerCraft", "MaterialTrade", "MissionCompleted", "ScientificResearch", "TechnologyBroker", "Synthesis", "Backpack", "BackpackChange", "BuyMicroResources", "SellMicroResources", "TransferMicroResources", "TradeMicroResources", "ShipLockerMaterials", "ShipLocker"]:
        handle_material_events(ed_player, entry, state)

    if entry["event"] == "StoredShips":
        ed_player.update_fleet(entry)

    if "Crew" in entry["event"]:
        handle_multicrew_events(ed_player, entry)
        
    if entry["event"] in ["WingAdd", "WingJoin", "WingLeave"]:
        handle_wing_events(ed_player, entry)

    if entry["event"] in ["MiningRefined", "ProspectedAsteroid"]:
        handle_mining_events(ed_player, entry)
    
    if entry["event"] == "Bounty":
        handle_bounty_hunting_events(ed_player, entry)

    if entry["event"] in ["CarrierJump", "CarrierBuy", "CarrierStats", "CarrierJumpRequest", "CarrierJumpCancelled", "CarrierDecommission", "CarrierCancelDecommission", "CarrierDockingPermission"]:
        handle_carrier_events(ed_player, entry)

    status_outcome = {"updated": False, "reason": "Unspecified"}

    vehicle = None
    if ed_player.is_crew_member():
        vehicle = EDVehicleFactory.unknown_crew_vehicle()
    elif state.get("ShipType", None):
        vehicle = EDVehicleFactory.from_edmc_state(state)

    status_outcome["updated"] = ed_player.update_vehicle_if_obsolete(vehicle, piloted=False)
    status_outcome["updated"] |= ed_player.update_star_system_if_obsolete(system)
        
    if entry["event"] in ["Location", "Undocked", "Docked", "DockingCancelled", "DockingDenied",
                          "DockingGranted", "DockingRequested", "DockingTimeout"]:
        outcome = handle_change_events(ed_player, entry)
        handle_fc_position_related_events(ed_player, entry)
        if outcome["updated"]:
            status_outcome["updated"] = True
            status_outcome["reason"] = outcome["reason"]

    if entry["event"] in ["SupercruiseExit", "FSDJump", "SupercruiseEntry", "StartJump",
                          "ApproachSettlement", "ApproachBody", "LeaveBody", "CarrierJump"]:
        outcome = handle_movement_events(ed_player, entry)
        if outcome["updated"]:
            status_outcome["updated"] = True
            status_outcome["reason"] = outcome["reason"]

    if entry["event"] == "Touchdown" and entry.get("PlayerControlled", None) and entry.get("NearestDestination", None):
        depletables = EDRRawDepletables()
        depletables.visit(entry["NearestDestination"])
        
    if entry["event"] in ["FSSSignalDiscovered"]:
        EDR_CLIENT.noteworthy_about_signal(entry)

    if entry["event"] in ["NavBeaconScan"] and entry.get("NumBodies", 0):
        EDR_CLIENT.notify_with_details(_(u"System info acquired"), [_(u"Noteworthy material densities will be shown when approaching a planet.")])

    if entry["event"] in ["Scan"]:
        EDR_CLIENT.process_scan(entry)
        if entry["ScanType"] == "Detailed":
            EDR_CLIENT.noteworthy_about_scan(entry)

    if entry["event"] in ["Interdicted", "Died", "EscapeInterdiction", "Interdiction", "PVPKill", "CrimeVictim", "CommitCrime"]:
        report_crime(ed_player, entry)

    if entry["event"] in ["PayFines", "PayBounties"]:
        handle_legal_fees(ed_player, entry)

    if entry["event"] in ["ShipTargeted"]:
        if "ScanStage" in entry and entry["ScanStage"] > 0:
            handle_scan_events(ed_player, entry)
            handle_bounty_hunting_events(ed_player, entry)
        elif ("ScanStage" in entry and entry["ScanStage"] == 0) or ("TargetLocked" in entry and not entry["TargetLocked"]):
            ed_player.untarget()
            EDR_CLIENT.target_guidance(entry, turn_off=True)
            EDR_CLIENT.bounty_hunting_guidance(turn_off=True)
    
    if entry["event"] in ["HullDamage", "UnderAttack", "SRVDestroyed", "FighterDestroyed", "HeatDamage", "ShieldState", "CockpitBreached", "SelfDestruct"]:
        handle_damage_events(ed_player, entry)

    if entry["event"] in ["FuelScoop", "RefuelAll", "RefuelPartial", "Repair", "RepairAll", "AfmuRepairs", "RebootRepair", "RepairDrone"]:
        handle_fixing_events(ed_player, entry)

    if entry["event"] in ["ModuleStore", "ModuleSell", "ModuleBuy", "ModuleRetrieve", "MassModuleStore"]:
        handle_outfitting_events(ed_player, entry)

    if entry["event"] in ["ReceiveText", "SendText"]:
        report_comms(ed_player, entry)

    if entry["event"] in ["SendText"]:
        handle_commands(ed_player, entry)

    if status_outcome["updated"]:
        edr_update_cmdr_status(ed_player, status_outcome["reason"], entry["timestamp"])
        if ed_player.in_a_crew():
            for member in ed_player.crew.members:
                if member == ed_player.name:
                    continue
                source = u"Multicrew (captain)" if ed_player.is_captain(member) else u"Multicrew (crew)"
                crew_player = EDPlayer(member)
                crew_player.mothership = vehicle
                edr_submit_contact(crew_player, entry["timestamp"], source, ed_player)
    
    if ed_player.maybe_in_a_pvp_fight():
        report_fight(ed_player)


def edr_update_cmdr_status(cmdr, reason_for_update, timestamp):
    """
    Send a status update for a given cmdr
    :param cmdr:
    :param reason_for_update:
    :return:
    """
    if cmdr.in_solo():
        EDRLOG.log(u"Skipping cmdr update due to Solo mode", "ERROR")
        return

    if cmdr.has_partial_status():
        EDRLOG.log(u"Skipping cmdr update due to partial status", "ERROR")
        return

    edt = EDTime()
    edt.from_journal_timestamp(timestamp)
    report = {
        "cmdr" : cmdr.name,
        "starSystem": cmdr.star_system,
        "place": cmdr.place,
        "timestamp": edt.as_js_epoch(),
        "source": reason_for_update,
        "reportedBy": cmdr.name,
        "mode": cmdr.game_mode,
        "dlc": cmdr.dlc_name,
        "group": cmdr.private_group
    }

    if cmdr.vehicle_type():
        report["ship"] = cmdr.vehicle_type()
    elif cmdr.spacesuit_type():
        report["suit"] = cmdr.spacesuit_type()

    EDRLOG.log(u"report: {}".format(report), "DEBUG")

    if not EDR_CLIENT.blip(cmdr.name, report):
        EDR_CLIENT.status = _(u"blip failed.")
        return

    EDR_CLIENT.status = _(u"blip succeeded!")


def edr_submit_crime(criminal_cmdrs, offence, victim, timestamp):
    """
    Send a crime/incident report
    :param criminal:
    :param offence:
    :param victim:
    :return:
    """
    #TODO sort out ship and suit...
    if not victim.in_open():
        EDRLOG.log(u"Skipping submit crime due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"Crime reporting disabled in solo/private modes.")
        return

    criminals = []
    for criminal_cmdr in criminal_cmdrs:
        EDRLOG.log(u"Appending criminal {} with ship {}, suit {}".format(criminal_cmdr.name,
                                                                criminal_cmdr.vehicle_type(), criminal_cmdr.spacesuit_type()),
                   "DEBUG")
        blob = {"name": criminal_cmdr.name, "enemy": criminal_cmdr.enemy, "wanted": criminal_cmdr.wanted, "bounty": criminal_cmdr.bounty, "fine": criminal_cmdr.fine}
        if criminal_cmdr.vehicle_type():
            blob["ship"] = criminal_cmdr.vehicle_type()
        elif criminal_cmdr.spacesuit_type():
            blob["suit"] = criminal_cmdr.spacesuit_type()
        blob["power"] = criminal_cmdr.powerplay.canonicalize() if criminal_cmdr.powerplay else u""
        criminals.append(blob)

    edt = EDTime()
    edt.from_journal_timestamp(timestamp)
    report = {
        "starSystem": victim.star_system,
        "place": victim.place,
        "timestamp": edt.as_js_epoch(),
        "criminals": criminals,
        "offence": offence.capitalize(),
        "victim": victim.name,
        "reportedBy": victim.name,
        "victimPower": victim.powerplay.canonicalize() if victim.powerplay else u"",
        "byPledge": victim.powerplay.canonicalize() if victim.powerplay else "",
        "mode": victim.game_mode,
        "dlc": victim.dlc_name,
        "group": victim.private_group
    }

    if victim.vehicle_type():
        report["victimShip"] = victim.vehicle_type()
    elif victim.spacesuit_type():
        report["victimSuit"] = victim.spacesuit_type()

    if not EDR_CLIENT.crime(victim.star_system, report):
        EDR_CLIENT.status = _(u"failed to report crime.")
        EDR_CLIENT.evict_system(victim.star_system)


def edr_submit_crime_self(criminal_cmdr, offence, victim, timestamp):
    """
    Send a crime/incident report
    :param criminal_cmdr:
    :param offence:
    :param victim:
    :return:
    """
    if not criminal_cmdr.in_open():
        EDRLOG.log(u"Skipping submit crime (self) due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"Crime reporting disabled in solo/private modes.")
        return

    edt = EDTime()
    edt.from_journal_timestamp(timestamp)
    criminal_blob = {
        "name": criminal_cmdr.name,
        "wanted": criminal_cmdr.wanted,
        "bounty": criminal_cmdr.bounty,
        "fine": criminal_cmdr.fine,
        "power": criminal_cmdr.powerplay.canonicalize() if criminal_cmdr.powerplay else u"",
    }

    if criminal_cmdr.vehicle_type():
        criminal_blob["ship"] = criminal_cmdr.vehicle_type()
    elif criminal_cmdr.spacesuit_type():
        criminal_blob["suit"] = criminal_cmdr.spacesuit_type()


    report = {
        "starSystem": criminal_cmdr.star_system,
        "place": criminal_cmdr.place,
        "timestamp": edt.as_js_epoch(),
        "criminals" : [ criminal_blob ],
        "offence": offence.capitalize(),
        "victim": victim.name,
        "reportedBy": criminal_cmdr.name,
        "victimWanted": victim.wanted,
        "victimBounty": victim.bounty,
        "victimEnemy": victim.enemy,
        "victimPower": victim.powerplay.canonicalize() if victim.powerplay else u"",
        "byPledge": victim.powerplay.canonicalize() if victim.powerplay else "",
        "mode": criminal_cmdr.game_mode,
        "dlc": criminal_cmdr.dlc_name,
        "group": criminal_cmdr.private_group
    }

    if victim.vehicle_type():
        report["victimShip"] = victim.vehicle_type()
    elif victim.spacesuit_type():
        report["victimSuit"] = victim.spacesuit_type()

    EDRLOG.log(u"Perpetrated crime: {}".format(report), "DEBUG")

    if not EDR_CLIENT.crime(criminal_cmdr.star_system, report):
        EDR_CLIENT.status = _(u"failed to report crime.")
        EDR_CLIENT.evict_system(criminal_cmdr.star_system)

def report_fight(player):
    if not player.in_open():
        EDRLOG.log(u"Skipping reporting fight due to unconfirmed Open mode", "INFO")
        EDR_CLIENT.status = _(u"Fight reporting disabled in solo/private modes.")
        return

    report = player.json(with_target=True)
    EDR_CLIENT.fight(report)

def edr_submit_contact(contact, timestamp, source, witness, system_wide=False):
    """
    Report a contact with a cmdr
    :param contact:
    :param timestamp:
    :param source:
    :param witness:
    :return:
    """
    edt = EDTime()
    edt.from_journal_timestamp(timestamp)
    
    report = {
        "cmdr" : contact.name,
        "starSystem": witness.star_system,
        "place": witness.place,
        "timestamp": edt.as_js_epoch(),
        "source": source,
        "reportedBy": witness.name,
        "byPledge": witness.powerplay.canonicalize() if witness.powerplay else "",
        "mode": witness.game_mode,
        "dlc": witness.dlc_name,
        "group": witness.private_group
    }

    if contact.vehicle_type():
        report["ship"] = contact.vehicle_type()
    elif contact.spacesuit_type():
        report["suit"] = contact.spacesuit_type()

    if contact.sqid:
        report["sqid"] = contact.sqid

    if witness.has_partial_status():
        EDRLOG.log(u"Skipping cmdr update due to partial status", "INFO")
        return

    if not EDR_CLIENT.blip(contact.name, report):
        EDR_CLIENT.status = _(u"failed to report contact.")
        
    edr_submit_traffic(contact, timestamp, source, witness, system_wide)

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
    report["mode"] = witness.game_mode
    report["dlc"] = witness.dlc_name
    report["group"] = witness.private_group

    EDR_CLIENT.scanned(scan["cmdr"], report)
        
def edr_submit_traffic(contact, timestamp, source, witness, system_wide=False):
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
        "cmdr" : contact.name,
        "starSystem": witness.star_system,
        "place": witness.place,
        "timestamp": edt.as_js_epoch(),
        "source": source,
        "reportedBy": witness.name,
        "byPledge": witness.powerplay.canonicalize() if witness.powerplay else "",
        "mode": witness.game_mode,
        "dlc": witness.dlc_name,
        "group": witness.private_group
    }

    if contact.vehicle_type():
        report["ship"] = contact.vehicle_type()
    elif contact.spacesuit_type():
        report["ship"] = contact.spacesuit_type()

    if not witness.in_open() and not system_wide:
        EDRLOG.log(u"Skipping submit traffic due to unconfirmed Open mode, and event not being system wide.", "INFO")
        EDR_CLIENT.status = _(u"Traffic reporting disabled in solo/private modes.")
        return

    if witness.has_partial_status():
        EDRLOG.log(u"Skipping traffic update due to partial status", "INFO")
        return

    if not EDR_CLIENT.traffic(witness.star_system, report, system_wide):
        EDR_CLIENT.status = _(u"failed to report traffic.")
        EDR_CLIENT.evict_system(witness.star_system)

def edr_submit_multicrew_session(player, report):
    if not player.in_open() and not player.destroyed:
        EDRLOG.log(u"Skipping submit multicrew report: not in Open and not destroyed", "INFO")
        EDR_CLIENT.status = _(u"Multicrew reporting disabled in private mode.")
        return

    if not EDR_CLIENT.crew_report(report):
        EDR_CLIENT.status = _(u"failed to report multicrew session.")

def report_crime(cmdr, entry):
    """
    Report a crime to the server
    :param cmdr:
    :param entry:
    :return:
    """
    player_one = EDR_CLIENT.player
    if entry["event"] in ["Interdicted", "EscapeInterdiction"]:
        if entry["IsPlayer"]:
            interdictor = player_one.instanced_player(entry["Interdictor"])
            player_one.interdicted(interdictor, entry["event"] == "Interdicted")
            edr_submit_crime([interdictor], entry["event"], cmdr, entry["timestamp"])
        else:
            interdictor = player_one.instanced_npc(entry.get("Interdictor", "[N/A]"))
            player_one.interdicted(interdictor, entry["event"] == "Interdicted")
    elif entry["event"] == "Died":
        if "Killers" in entry:
            criminal_cmdrs = []
            for killer in entry["Killers"]:
                if killer["Name"].startswith("Cmdr "):
                    criminal_cmdr = player_one.instanced_player(killer["Name"][5:], ship_internal_name=killer["Ship"])
                    criminal_cmdrs.append(criminal_cmdr)
            edr_submit_crime(criminal_cmdrs, "Murder", cmdr, entry["timestamp"])
        elif "KillerName" in entry and entry["KillerName"].startswith("Cmdr "):
            criminal_cmdr = player_one.instanced_player(entry["KillerName"][5:], ship_internal_name=entry["KillerShip"])
            edr_submit_crime([criminal_cmdr], "Murder", cmdr, entry["timestamp"])
        player_one.killed()
    elif entry["event"] == "Interdiction":
        if entry["IsPlayer"]:
            offence = "Interdiction" if entry["Success"] else "Failed interdiction"
            interdicted = player_one.instanced_player(entry["Interdicted"])
            player_one.interdiction(interdicted, entry["Success"])
            edr_submit_crime_self(cmdr, offence, interdicted, entry["timestamp"])
        else:
            offence = "Interdiction" if entry["Success"] else "Failed interdiction"
            interdicted = player_one.instanced_npc(entry.get("Interdicted", "[N/A]"))
            player_one.interdiction(interdicted, entry["Success"])
    elif entry["event"] == "PVPKill":
        EDRLOG.log(u"PVPKill!", "INFO")
        victim = player_one.instanced_player(entry["Victim"])
        victim.killed()
        edr_submit_crime_self(cmdr, "Murder", victim, entry["timestamp"])
        player_one.destroy(victim)
    elif entry["event"] == "CrimeVictim" and "Offender" in entry and player_one.name:
        irrelevant_pattern = re.compile(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$")
        wingmate = player_one.is_wingmate(entry["Offender"]) 
        oneself = entry["Offender"].lower() == player_one.name.lower()
        crewmate = player_one.is_crewmate(entry["Offender"])
        instanced = player_one.is_instanced_with_player(entry["Offender"])
        if not irrelevant_pattern.match(entry["Offender"]) and instanced and not oneself and not wingmate and not crewmate:
            offender = player_one.instanced_player(entry["Offender"])
            if "Bounty" in entry:
                offender.bounty += entry["Bounty"]
            if "Fine" in entry:
                offender.fine += entry["Fine"]
            edr_submit_crime([offender], u"{} (CrimeVictim)".format(entry["CrimeType"]), cmdr, entry["timestamp"])
        else:
            # TODO extract npc name, instance, etc.
            EDRLOG.log(u"Ignoring 'CrimeVictim' event: offender={}; instanced_with={}".format(entry["Offender"], player_one.is_instanced_with_player(entry["Offender"])), "DEBUG")
    elif entry["event"] == "CommitCrime" and "Victim" in entry and player_one.name and (entry["Victim"].lower() != player_one.name.lower()):
        irrelevant_pattern = re.compile(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$")
        if not irrelevant_pattern.match(entry["Victim"]) and player_one.is_instanced_with_player(entry["Victim"]):
            victim = player_one.instanced_player(entry["Victim"])
            if "Bounty" in entry:
                player_one.bounty += entry["Bounty"]
            if "Fine" in entry:
                player_one.fine += entry["Fine"]
            edr_submit_crime_self(player_one, u"{} (CommitCrime)".format(entry["CrimeType"]), victim, entry["timestamp"])
        else:
            # TODO extract npc name, instance, etc.
            EDRLOG.log(u"Ignoring 'CommitCrime' event: Victim={}; instanced_with={}".format(entry["Victim"], player_one.is_instanced_with_player(entry["Victim"])), "DEBUG")


def report_comms(player, entry):
    """
    Report a comms contact to the server
    :param player:
    :param entry:
    :return:
    """
    # Note: Channel can be missing... probably not safe to assume anything in that case
    # TODO npc instancing
    if entry["event"] == "ReceiveText" and "Channel" in entry:
        if entry["Channel"] in ["local"]:
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            contact = player.instanced_player(from_cmdr)
            edr_submit_contact(contact, entry["timestamp"], "Received text (local)", player)
        elif entry["Channel"] in ["player"]:
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            if player.is_friend(from_cmdr) or player.is_wingmate(from_cmdr):
                EDRLOG.log(u"Text from {} friend / wing. Can't infer location".format(from_cmdr),
                           "INFO")
            else:
                if player.from_genesis:
                    EDRLOG.log(u"Text from {} (not friend/wing) == same location".format(from_cmdr),
                            "INFO")
                    contact = player.instanced_player(from_cmdr)
                    edr_submit_contact(contact, entry["timestamp"],
                                    "Received text (non wing/friend player)", player)
                else:
                    EDRLOG.log(u"Received text from {}. Player not created from game start => can't infer location".format(from_cmdr),
                        "INFO")
        elif entry["Channel"] in ["starsystem"]:
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            EDRLOG.log(u"Text from {} in star system".format(from_cmdr), "INFO")
            contact = EDPlayer(from_cmdr)
            contact.star_system = player.star_system
            # TODO add blip to systemwideinstance ?
            edr_submit_contact(contact, entry["timestamp"],
                                "Received text (starsystem channel)", player, system_wide = True)
    elif entry["event"] == "SendText" and not entry["To"] in ["local", "wing", "starsystem", "squadron", "squadleaders"]:
        to_cmdr = entry["To"]
        if entry["To"].startswith("$cmdr_decorate:#name="):
            to_cmdr = entry["To"][len("$cmdr_decorate:#name="):-1]
        if player.is_friend(to_cmdr) or player.is_wingmate(to_cmdr):
            EDRLOG.log(u"Sent text to {} friend/wing: can't infer location".format(to_cmdr), "INFO")            
        else:
            if player.from_genesis:
                EDRLOG.log(u"Sent text to {} (not friend/wing) == same location".format(to_cmdr),
                        "INFO")
                contact = player.instanced_player(to_cmdr)
                edr_submit_contact(contact, entry["timestamp"], "Sent text (non wing/friend player)",
                                player)
            else:
                EDRLOG.log(u"Sent text to {}. Player not created from game start => can't infer location".format(to_cmdr),
                        "INFO")

    m = re.findall(r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+)", entry["Message"], flags=re.IGNORECASE)
    if m:
        EDR_CLIENT.linkable_status(m[0])

def handle_damage_events(ed_player, entry):
    if not entry["event"] in ["HullDamage", "UnderAttack", "SRVDestroyed", "FighterDestroyed", "HeatDamage", "ShieldState", "CockpitBreached", "SelfDestruct"]:
        return False

    if entry["event"] == "HullDamage":
        if entry.get("Fighter", False):
            if ed_player.slf:
                ed_player.slf.taking_hull_damage(entry["Health"] * 100.0) # HullDamage's Health is normalized to 0.0 ... 1.0
            else:
                EDRLOG.log("SLF taking hull damage but player has none...", "WARNING")
        else:
            ed_player.mothership.taking_hull_damage(entry["Health"] * 100.0) # HullDamage's Health is normalized to 0.0 ... 1.0
    elif entry["event"] == "CockpitBreached":
        ed_player.piloted_vehicle.cockpit_breached()
    elif entry["event"] == "ShieldState":
        if ed_player.piloted_vehicle:
            ed_player.piloted_vehicle.shield_state(entry["ShieldsUp"])
        else:
            # TODO on_foot case
            pass
    elif entry["event"] == "UnderAttack":
        ed_player.attacked(entry["Target"])
    elif entry["event"] == "HeatDamage" and ed_player.piloted_vehicle:
        ed_player.piloted_vehicle.taking_heat_damage()
    elif entry["event"] == "SRVDestroyed":
        if ed_player.srv:
            ed_player.srv.destroy()
        else:
            EDRLOG.log("SRV got destroyed but player had none...", "WARNING")
    elif entry["event"] == "FighterDestroyed":
        if ed_player.slf:
            ed_player.slf.destroy()
        else:
            EDRLOG.log("SLF got destroyed but player had none...", "WARNING")
    elif entry["event"] == "SelfDestruct" and ed_player.piloted_vehicle:
        ed_player.piloted_vehicle.destroy() # TODO on foot case?
    else:
        return False
    return True

def handle_fixing_events(ed_player, entry):
    if entry["event"] not in ["FuelScoop", "RefuelAll", "RefuelPartial", "Repair", "RepairAll", "AfmuRepairs", "RebootRepair", "RepairDrone"]:
        return False

    if entry["event"] == "AfmuRepairs":
        ed_player.mothership.subsystem_health(entry["Module"], entry["Health"] * 100.0) # AfmuRepairs' health is normalized to 0.0 ... 1.0
    elif entry["event"] == "FuelScoop":
        ed_player.mothership.fuel_scooping(entry["Total"])
    elif entry["event"] == "RefuelAll":
        ed_player.mothership.refuel()
    elif entry["event"] == "RefuelPartial":
        ed_player.mothership.refuel(entry["Amount"])
    elif entry["event"] == "RepairAll":
        ed_player.mothership.repair()
    elif entry["event"] == "Repair":
        items = entry["Items"] if "Items" in entry else [entry["Item"]]
        for item in items:
            ed_player.mothership.repair(item)
    elif entry["event"] == "RepairDrone":
        if entry.get("HullRepaired", None):
            ed_player.mothership.hull_health = entry["HullRepaired"]
        if entry.get("CockpitRepaired", None):
            ed_player.mothership.cockpit_health(entry["CockpitRepaired"])

def handle_outfitting_events(player, entry):
    if entry["event"] not in ["MassModuleStore", "ModuleStore", "ModuleSell", "ModuleBuy", "ModuleRetrieve"]:
        return False

    if entry["event"] == "MassModuleStore":
        for item in entry["Items"]:
            player.mothership.remove_subsystem(item["Name"])
    elif entry["event"] == "ModuleStore":
        player.mothership.remove_subsystem(entry["StoredItem"])
        if entry.get("ReplacementItem", None):
            player.mothership.add_subsystem(entry["ReplacementItem"])
    elif entry["event"] == "ModuleBuy":
        if entry.get("StoredItem", None):
            player.mothership.remove_subsystem(entry["StoredItem"])
        elif entry.get("SellItem", None):
            player.mothership.remove_subsystem(entry["SellItem"])
        player.mothership.add_subsystem(entry["BuyItem"])
    elif entry["event"] == "ModuleSell":
        player.mothership.remove_subsystem(entry["SellItem"])
    elif entry["event"] == "ModuleRetrieve":
        if entry.get("SwapOutItem", None):
            player.mothership.remove_subsystem(entry["SwapOutItem"])
        player.mothership.add_subsystem(entry["RetrievedItem"])

def handle_legal_fees(player, entry):
    if entry["event"] not in ["PayFines", "PayBounties"]:
       return False
    
    #TODO this should be on a ship whose id is in the entry rather than the player
    if entry["event"] == "PayFines":
        if entry.get("AllFines", None):
            player.fine = 0
        else:
            true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0)/100.0)
            player.fine = max(0, player.fine - true_amount)
    elif entry["event"] == "PayBounties":
        if entry.get("AllFines", None):
            player.bounty = 0
        else:
            true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0)/100.0)
            player.bounty = max(0, player.bounty - true_amount)

def handle_scan_events(player, entry):
    if not (entry["event"] == "ShipTargeted"):
        return False

    if not (entry["TargetLocked"]) or entry["ScanStage"] <= 0:
        EDR_CLIENT.target_guidance(entry, turn_off=True)
        EDR_CLIENT.bounty_hunting_guidance(turn_off=True)
        return False
    
    prefix = None
    piloted = False
    mothership = True
    slf = False
    srv = False
    npc = False

    if entry["PilotName"].startswith("$cmdr_decorate:#name="):
        prefix = "$cmdr_decorate:#name="
        piloted = True
    elif entry["PilotName"].startswith("$RolePanel2_unmanned; $cmdr_decorate:#name="):
        prefix = "$RolePanel2_unmanned; $cmdr_decorate:#name="
    elif entry["PilotName"].startswith("$RolePanel2_crew; $cmdr_decorate:#name="):
        prefix = "$RolePanel2_crew; $cmdr_decorate:#name="
        mothership = False
        slf = True
        piloted = True
    elif entry["PilotName"].startswith("$npc_name_decorate:#name="):
        prefix = "$npc_name_decorate:#name="
        piloted = True
        npc = True
    elif entry["PilotName"] in ["$ShipName_Police_Independent;", "$ShipName_Police_Federation;", "$ShipName_Police_Empire;", "$LUASC_Scenario_Warzone_NPC_WarzoneGeneral_Ind;", "$ShipName_Military_Federation;", "$ShipName_Military_Independent;", "$ShipName_SearchAndRescue;", "$ShipName_ATR_Federation;", "$ShipName_Military_Empire;", "$ShipName_PassengerLiner_Wedding;", "$ShipName_PassengerLiner_Cruise;"]:
        piloted = True
        npc = True
    else:
        player.untarget()
        EDR_CLIENT.target_guidance(entry, turn_off=True)
        EDR_CLIENT.bounty_hunting_guidance(turn_off=True)
        return False
    
    target_name = entry.get("PilotName_Localised", entry["PilotName"])
    if prefix:
        target_name = entry["PilotName"][len(prefix):-1]
    
    if target_name == player.name:
        # Happens when scanning one's unmanned ship, etc.
        EDR_CLIENT.target_guidance(entry, turn_off=True)
        EDR_CLIENT.bounty_hunting_guidance(turn_off=True)
        return False

    if player.target_pilot() and target_name != player.target_pilot().name:
        # clear previous guidance if any
        EDR_CLIENT.target_guidance(entry, turn_off=True)
        EDR_CLIENT.bounty_hunting_guidance(turn_off=True)

    target = None
    if npc:
        target = player.instanced_npc(target_name, entry["PilotRank"], entry["Ship"], piloted)
    else:
        target = player.instanced_player(target_name, rank=entry["PilotRank"], ship_internal_name=entry["Ship"], piloted=piloted)

    target.sqid = entry.get("SquadronID", None)
    nodotpower = entry["Power"].replace(".", "") if "Power" in entry else None
    target.pledged_to(nodotpower)
 
    if target.is_human():
        edr_submit_contact(target, entry["timestamp"], "Ship targeted", player)

    if entry["ScanStage"] >= 2:
        if "ShieldHealth" in entry:
            target.vehicle.shield_health = entry["ShieldHealth"]
        if "HullHealth" in entry:
            target.vehicle.hull_health = entry["HullHealth"]

    if entry["ScanStage"] == 3:
        target.wanted = entry["LegalStatus"] in ["Wanted", "WantedEnemy", "Warrant"]
        target.enemy = entry["LegalStatus"] in ["Enemy", "WantedEnemy", "Hunter"]
        target.bounty = entry.get("Bounty", 0)
        if "Subsystem" in entry and "SubsystemHealth" in entry:
            target.vehicle.subsystem_health(entry["Subsystem"], entry["SubsystemHealth"])
        
        # Scans event are only for ships, so no need for dissociating ship vs. suit situations.
        scan = {
            "cmdr": target.name,
            "ship": target.vehicle_type(),
            "wanted": target.wanted,
            "enemy": target.enemy,
            "bounty": target.bounty
        }
        
        if target.sqid:
            scan["sqid"] = target.sqid

        if target.power:
            scan["power"] = target.powerplay.canonicalize() if target.powerplay else u""
        elif not player.is_independent():
            # Note: power is only present in shiptargeted events if the player is pledged
            # This means that we can only know that the target is independent if a player is pledged and the power attribute is missing
            scan["power"] = "independent"
    
        if target.is_human():
            edr_submit_scan(scan, entry["timestamp"], "Ship targeted [{}]".format(entry["LegalStatus"]), player)

    player.targeting(target, ship_internal_name=entry["Ship"])
    EDR_CLIENT.target_guidance(entry)

    return True

def handle_material_events(cmdr, entry, state):
    if entry["event"] in ["Materials", "ShipLockerMaterials"] or (entry["event"] == "ShipLocker" and len(entry.keys()) > 2) or (entry["event"] == "Backpack" and len(entry.keys()) > 2):
        cmdr.inventory.initialize(entry)
        
    if cmdr.inventory.stale_or_incorrect():
        cmdr.inventory.initialize_with_edmc(state)

    if entry["event"] == "MaterialCollected":
        cmdr.inventory.collected(entry)
    elif entry["event"] == "MaterialDiscarded":
        cmdr.inventory.discarded(entry)
    elif entry["event"] == "EngineerContribution":
        cmdr.inventory.donated_engineer(entry)
    elif entry["event"] == "ScientificResearch":
        cmdr.inventory.donated_science(entry)
    elif entry["event"] in ["EngineerCraft", "TechnologyBroker", "Synthesis"]:
        ingredients = entry["Ingredients"] if entry["event"] == "EngineerCraft" else entry["Materials"]
        cmdr.inventory.consumed(ingredients)
    elif entry["event"] == "MaterialTrade":
        cmdr.inventory.traded(entry)
    elif entry["event"] == "MissionCompleted":
        cmdr.inventory.rewarded(entry)
        EDR_CLIENT.eval_locker(passive=True)
    elif entry["event"] == "BackpackChange":
        cmdr.inventory.backpack_change(entry)
        if "Added" in entry:
            added = [cmdr.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if not(cmdr.engineers.is_useless(item["Name"]) or cmdr.engineers.is_unnecessary(item["Name"])) or "MissionID" in item]
            discardable = [cmdr.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if cmdr.engineers.is_useless(item["Name"]) and not cmdr.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
            unnecessary = [cmdr.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if cmdr.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
            details = [", ".join(added)]
            if discardable:
                details.append(_(u"Useless: {}").format(", ".join(discardable)))
            if unnecessary:
                details.append(_(u"Unnecessary: {}").format(", ".join(unnecessary)))
            EDR_CLIENT.notify_with_details("Materials Info", details)
        elif "Removed" in entry:
            EDR_CLIENT.eval_backpack(passive=True)
    elif entry["event"] == "SellMicroResources":
        cmdr.inventory.sold(entry)
        EDR_CLIENT.eval_locker(passive=True)
    elif entry["event"] == "BuyMicroResources":
        cmdr.inventory.bought(entry)
    elif entry["event"] == "TransferMicroResources":
        cmdr.inventory.bought(entry)
        EDR_CLIENT.eval_backpack(passive=True)
    elif entry["event"] == "TradeMicroResources":
        cmdr.inventory.traded(entry)
        EDR_CLIENT.eval_locker(passive=True)

def handle_commands(cmdr, entry):
    if not entry["event"] == "SendText":
        return

    command_parts = entry["Message"].split(" ", 1)
    command = command_parts[0].lower()
    if not command:
        return
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
    elif command == "o7" and not entry["To"] in ["local", "voicechat", "wing", "friend", "starsystem", "squadron", "squadleaders"]:
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
    elif command in ["!who", "!w"]:
        target_cmdr = None
        if len(command_parts) == 2:
            target_cmdr = command_parts[1]
        else:
            target = EDR_CLIENT.player.target_pilot()
            target_cmdr = target.name if target and target.is_human() else None
        if target_cmdr:
            EDRLOG.log(u"Explicit who command for {}".format(target_cmdr), "INFO")
            EDR_CLIENT.who(target_cmdr)
    elif command == "!crimes":
        crimes_command("" if len(command_parts) == 1 else command_parts[1])
    elif command == "!sitrep":
        system = cmdr.star_system if len(command_parts) == 1 else command_parts[1]
        EDRLOG.log(u"Sitrep command for {}".format(system), "INFO")
        EDR_CLIENT.check_system(system)
    elif command == "!sitreps":
        EDRLOG.log(u"Sitreps command", "INFO")
        EDR_CLIENT.sitreps()
    elif command == "!signals":
        EDRLOG.log(u"Signals command", "INFO")
        EDR_CLIENT.noteworthy_signals_in_system()
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
    elif command == "!where":
        target_cmdr = None
        if len(command_parts) == 2:
            target_cmdr = command_parts[1]
        else:
            target = EDR_CLIENT.player.target_pilot()
            target_cmdr = target.name if target and target.is_human() else None
        if target_cmdr:
            EDRLOG.log(u"Explicit where command for {}".format(target_cmdr), "INFO")
            EDR_CLIENT.where(target_cmdr)
    elif command == "!search":
        resource = None
        system = cmdr.star_system
        if len(command_parts) == 2:
            better_parts = command_parts[1].split("@", 1)
            if len(better_parts) == 2:
                system = better_parts[1].lstrip()
            resource = better_parts[0].rstrip()
        if resource:
            EDRLOG.log(u"Search command for {}".format(resource), "INFO")
            EDR_CLIENT.search_resource(resource, system)
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
    elif command == "!if":
        EDRLOG.log(u"Interstellar Factors command", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.interstellar_factors_near(search_center, override_sc_dist)
    elif command == "!raw":
        EDRLOG.log(u"Raw Material Trader command", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.raw_material_trader_near(search_center, override_sc_dist)
    elif command in ["!encoded", "!enc"]:
        EDRLOG.log(u"Encoded Material Trader command", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.encoded_material_trader_near(search_center, override_sc_dist)
    elif command in ["!manufactured", "!man"]:
        EDRLOG.log(u"Manufactured Material Trader command", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.manufactured_material_trader_near(search_center, override_sc_dist)
    elif command == "!staging":
        EDRLOG.log(u"Looking for a staging station", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.staging_station_near(search_center, override_sc_dist)
    elif command == "!rrrfc":
        EDRLOG.log(u"Looking for a RRR Fleet Carrier", "INFO")
        search_center = cmdr.star_system
        override_radius = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_radius = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.rrr_fc_near(search_center, override_radius)
    elif command == "!rrr":
        EDRLOG.log(u"Looking for a RRR Station", "INFO")
        search_center = cmdr.star_system
        override_radius = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_radius = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.rrr_near(search_center, override_radius)
    elif command in ["!htb", "!humantechbroker"]:
        EDRLOG.log(u"Looking for a human tech broker", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.human_tech_broker_near(search_center, override_sc_dist)
    elif command in ["!gtb", "!guardiantechbroker"]:
        EDRLOG.log(u"Looking for a guardian tech broker", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.guardian_tech_broker_near(search_center, override_sc_dist)
    elif command in ["!offbeat"]:
        EDRLOG.log(u"Looking for an offbeat station", "INFO")
        search_center = cmdr.star_system
        override_sc_dist = None
        if len(command_parts) >= 2:
            parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
            search_center = parameters[0] or cmdr.star_system
            override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
        EDR_CLIENT.offbeat_station_near(search_center, override_sc_dist)
    elif command in ["!edr", "!911", "!fuel", "!repair"]:
        services = {
            "!edr": "edr",
            "!911": "police",
            "!fuel": "fuel",
            "!repair": "repair"
        }
        service = services[command]
        message = command_parts[1] if len(command_parts) == 2 else "N/A"
        if service == "fuel" and not cmdr.lowish_fuel():
            EDRLOG.log(u"EDR Central for {} with {} not allowed (enough fuel)".format(service, message), "INFO")
            EDR_CLIENT.notify_with_details("EDR Central", [_(u"Call rejected: you seem to have enough fuel."), _("Contact Cmdr LeKeno if this is inaccurate")])
            return
        if service == "repair" and not cmdr.heavily_damaged():
            EDRLOG.log(u"EDR Central for {} with {} not allowed (no serious damage)".format(service, message), "INFO")
            EDR_CLIENT.notify_with_details("EDR Central", [_(u"Call rejected: you seem to have enough hull left."), _("Contact Cmdr LeKeno if this is inaccurate")])
            return
        info = EDR_CLIENT.player.json(fuel_info=(service == "fuel"))
        info["message"] = message
        EDRLOG.log(u"Message to EDR Central for {} with {}".format(service, message), "INFO")
        EDR_CLIENT.call_central(service, info)
    elif command == "!nav":
        if len(command_parts) < 2:
            EDRLOG.log(u"Not enough parameters for navigation command", "INFO")
            return
        if command_parts[1].lower() == "off":
            EDRLOG.log(u"Clearing destination", "INFO")
            EDR_CLIENT.player.planetary_destination = None
            return
        elif command_parts[1].lower() == "set" and EDR_CLIENT.player.attitude.valid():
            EDRLOG.log(u"Setting destination", "INFO")
            attitude = EDR_CLIENT.player.attitude
            EDR_CLIENT.navigation(attitude.latitude, attitude.longitude)
            return
        lat_long = command_parts[1].split(" ")
        if len(lat_long) != 2:
            EDRLOG.log(u"Invalid parameters for navigation command", "INFO")
            return
        EDRLOG.log(u"Navigation command", "INFO")
        EDR_CLIENT.navigation(lat_long[0], lat_long[1])
    elif command == "!ship" and len(command_parts) == 2:
        name_or_type = command_parts[1]
        EDRLOG.log(u"Ship search command for {}".format(name_or_type), "INFO")
        EDR_CLIENT.where_ship(name_or_type)
    elif command == "!eval" and len(command_parts) == 2:
        eval_type = command_parts[1]
        EDRLOG.log(u"Eval command for {}".format(eval_type), "INFO")
        EDR_CLIENT.eval(eval_type)
    elif command == "!contracts" and len(command_parts) == 1:
        EDRLOG.log(u"Contracts command", "INFO")
        EDR_CLIENT.contracts()
    elif command == "!contract":
        target_cmdr = cmdr.target
        reward = None
        if len(command_parts) >= 2:
            parts = [p.strip() for p in filter(len, " ".join(command_parts[1:]).split("$$$ ", 1))]
            target_cmdr = parts[0]
            if len(parts)>=2:
                reward = int(parts[1])
        EDRLOG.log(u"Contract command on {} with reward of {}".format(target_cmdr, reward), "INFO")
        if reward is None:
            EDR_CLIENT.contract(target_cmdr)
        else:
            EDR_CLIENT.contract_on(target_cmdr, reward)
    elif command == "!help":
        EDRLOG.log(u"Help command", "INFO")
        EDR_CLIENT.help("" if len(command_parts) == 1 else command_parts[1])
    elif command == "!clear":
        EDRLOG.log(u"Clear command", "INFO")
        EDR_CLIENT.clear()
    elif command == "!materials":
        if len(command_parts) == 2:
            profile = command_parts[1]
            EDRLOG.log(u"Configure material profile with {}".format(profile), "INFO")
            EDR_CLIENT.configure_resourcefinder(profile)
        else:
            EDR_CLIENT.show_material_profiles()
            EDRLOG.log(u"Listing material profiles", "INFO")

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
    target_cmdr = get_target_cmdr(command_parts, entry, EDR_CLIENT.player)
    
    if target_cmdr is None:
        EDRLOG.log(u"Skipping tag command: no valid target", "WARNING")
        return
    
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
    elif (len(command) > 1 and command[0] == "#"):
        tag = command[1:]
        EDRLOG.log(u"Tag command for {} with {}".format(target_cmdr, tag), "INFO")
        EDR_CLIENT.tag_cmdr(target_cmdr, tag)

def get_target_cmdr(command_parts, entry, player):
    target_cmdr = command_parts[1] if len(command_parts) > 1 else None
    if target_cmdr is None:
        if not entry["To"] in ["local", "voicechat", "wing", "friend", "starsystem", "squadron", "squadleaders"]:
            prefix = "$cmdr_decorate:#name="
            target_cmdr = entry["To"][len(prefix):-1] if entry["To"].startswith(prefix) else entry["To"]
        else:
            target = player.target_pilot()
            target_cmdr = target.name if target and target.is_human() else None
    return target_cmdr

def handle_minus_commands(command, command_parts, entry):
    target_cmdr = get_target_cmdr(command_parts, entry, EDR_CLIENT.player)
    if target_cmdr is None:
        EDRLOG.log(u"Skipping untag command: no valid target", "WARNING")
        return

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
    elif (len(command) > 2 and command[0] == "-#"):
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
    target_cmdr = None
    
    if command == "@# ":
        if not entry["To"] in ["local", "voicechat", "wing", "friend", "starsystem", "squadron", "squadleaders"]:
            prefix = "$cmdr_decorate:#name="
            target_cmdr = entry["To"][len(prefix):-1] if entry["To"].startswith(prefix) else entry["To"]
            EDRLOG.log(u"Memo command for tagged cmdr {}".format(target_cmdr), "INFO")
        else:
            target = EDR_CLIENT.player.target_pilot()
            target_cmdr = target.name if target and target.is_human() else None
    elif command.startswith("@# ") and len(command)>2:
        target_cmdr = command[3:]
        EDRLOG.log(u"Memo command for tagged cmdr {}".format(target_cmdr), "INFO")

    if target_cmdr:
        EDR_CLIENT.memo_cmdr(target_cmdr, command_parts[1])


def overlay_command(param):
    if param == "":
        EDRLOG.log(u"Visual feedback is {}".format("enabled." if EDR_CLIENT.visual_feedback
                                                   else "disabled."), "INFO")
        EDR_CLIENT.IN_GAME_MSG.reconfigure()
        random.seed()
        r = random.random()
        if r < 0.5:
            EDR_CLIENT.who(codecs.decode(random.choice(['yrxrab', 'E R C Y V P N A G', 'Nxhzn Grobev']), 'rot_13'))
        else:
            EDR_CLIENT.who(codecs.decode(random.choice(['Qnatrebhf.pbz', 'Yrzna Ehff IV', 'qvrtb anpxl', 'Ahzvqn', 'Nyovab Fnapurm']), 'rot_13')) # top 5 for self reported kills in 2021
        EDR_CLIENT.noteworthy_about_system({ "timestamp":"2021-10-22T12:34:56Z", "event":"FSDJump", "Taxi":False, "Multicrew":False, "StarSystem":"Deciat", "SystemAddress":6681123623626, "StarPos":[122.62500,-0.81250,-47.28125], "SystemAllegiance":"Independent", "SystemEconomy":"$economy_Industrial;", "SystemEconomy_Localised":"Industrial", "SystemSecondEconomy":"$economy_Refinery;", "SystemSecondEconomy_Localised":"Refinery", "SystemGovernment":"$government_Feudal;", "SystemGovernment_Localised":"Feudal", "SystemSecurity":"$SYSTEM_SECURITY_high;", "SystemSecurity_Localised":"High Security", "Population":31778844, "Body":"Deciat", "BodyID":0, "BodyType":"Star", "Powers":[ "A. Lavigny-Duval" ], "PowerplayState":"Exploited", "JumpDist":5.973, "FuelUsed":0.111415, "FuelLevel":8.000000, "Factions":[ { "Name":"Independent Deciat Green Party", "FactionState":"War", "Government":"Democracy", "Influence":0.109109, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand3;", "Happiness_Localised":"Discontented", "MyReputation":57.083599, "ActiveStates":[ { "State":"InfrastructureFailure" }, { "State":"War" } ] }, { "Name":"Kremata Incorporated", "FactionState":"Election", "Government":"Corporate", "Influence":0.105105, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":-6.000000, "ActiveStates":[ { "State":"Election" } ] }, { "Name":"Windri & Co", "FactionState":"War", "Government":"Corporate", "Influence":0.151151, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":-11.800000, "ActiveStates":[ { "State":"Boom" }, { "State":"War" } ] }, { "Name":"Deciat Flag", "FactionState":"None", "Government":"Dictatorship", "Influence":0.100100, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Deciat Corp.", "FactionState":"Election", "Government":"Corporate", "Influence":0.105105, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":-1.200000, "ActiveStates":[ { "State":"Election" } ] }, { "Name":"Deciat Blue Dragons", "FactionState":"None", "Government":"Anarchy", "Influence":0.010010, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":3.300000 }, { "Name":"Ryders of the Void", "FactionState":"Boom", "Government":"Feudal", "Influence":0.419419, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":93.099998, "PendingStates":[ { "State":"Expansion", "Trend":0 } ], "RecoveringStates":[ { "State":"CivilUnrest", "Trend":0 }, { "State":"PirateAttack", "Trend":0 } ], "ActiveStates":[ { "State":"Boom" } ] } ], "SystemFaction":{ "Name":"Ryders of the Void", "FactionState":"Boom" }, "Conflicts":[ { "WarType":"war", "Status":"active", "Faction1":{ "Name":"Independent Deciat Green Party", "Stake":"Carson Hub", "WonDays":2 }, "Faction2":{ "Name":"Windri & Co", "Stake":"Alonso Cultivation Estate", "WonDays":1 } }, { "WarType":"election", "Status":"active", "Faction1":{ "Name":"Kremata Incorporated", "Stake":"Folorunsho Military Enterprise", "WonDays":2 }, "Faction2":{ "Name":"Deciat Corp.", "Stake":"Amos Synthetics Moulding", "WonDays":1 } } ] })
        EDR_CLIENT.check_system("Deciat")
        global OVERLAY_DUMMY_COUNTER
        OVERLAY_DUMMY_COUNTER = (OVERLAY_DUMMY_COUNTER + 1) % 3
        if OVERLAY_DUMMY_COUNTER == 0:
            real_star_system = EDR_CLIENT.player.star_system
            EDR_CLIENT.player.star_system = "Deciat"
            EDR_CLIENT.docking_guidance({ "timestamp":"2021-10-22T12:34:56Z", "event":"DockingGranted", "LandingPad":7, "MarketID":3229756160, "StationName":"Garay Terminal", "StationType":"Coriolis" })
            EDR_CLIENT.player.star_system = real_star_system
        elif OVERLAY_DUMMY_COUNTER == 1:
            EDR_CLIENT.player.mining_stats.dummify()
            EDR_CLIENT.mining_guidance()
            EDR_CLIENT.player.mining_stats.reset()
        else:
            EDR_CLIENT.player.bounty_hunting_stats.dummify() # TODO
            EDR_CLIENT.bounty_hunting_guidance() 
            EDR_CLIENT.player.bounty_hunting_stats.reset()
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

def handle_shuttle_events(entry):
    if entry["event"]  not in ["BookTaxi", "BookDropship", "CancelTaxi", "CancelDropship"]:
        return
    ed_player = EDR_CLIENT.player
    if entry["event"] in ["BookTaxi", "BookDropship"]:
        ed_player.booked_shuttle(entry)
    elif entry["event"] in ["CancelTaxi", "CancelDropship"]:
        ed_player.cancelled_shuttle(entry)

def handle_fleet_events(entry):
    global LAST_KNOWN_SHIP_NAME
    if entry["event"] not in ["SetUserShipName", "SellShipOnRebuy", "ShipyardBuy", "ShipyardNew", "ShipyardSell", "ShipyardTransfer", "ShipyardSwap"]:
        return
    ed_player = EDR_CLIENT.player
    if entry["event"] == "SetUserShipName":
        ed_player.fleet.rename(entry)
        ed_player.mothership.update_name(entry)
        LAST_KNOWN_SHIP_NAME = ed_player.mothership.name
    elif entry["event"] in ["SellShipOnRebuy", "ShipyardSell"]:
        ed_player.fleet.sell(entry)
    elif entry["event"] == "ShipyardBuy":
        ed_player.fleet.buy(entry, ed_player.star_system, ed_player.mothership.name)
    elif entry["event"] == "ShipyardNew":
        ed_player.fleet.new(entry, ed_player.star_system)
    elif entry["event"] == "ShipyardTransfer":
        ed_player.fleet.transfer(entry, ed_player.star_system)
    elif entry["event"] == "ShipyardSwap":
        # Name is overwritten...
        ed_player.fleet.swap(entry, ed_player.star_system, LAST_KNOWN_SHIP_NAME)
        LAST_KNOWN_SHIP_NAME = ed_player.mothership.name

def handle_modules_events(ed_player, entry):
    if entry["event"] == "ModuleInfo":
        EDRLOG.log(u"ModuleInfo event", "DEBUG")
        ed_player.mothership.outfit_probably_changed(entry["timestamp"])

def handle_cargo_events(ed_player, entry):
    if entry["event"] == "EjectCargo":
        ed_player.piloted_vehicle.cargo.eject(entry)
    elif entry["event"] == "CollectCargo":
        ed_player.piloted_vehicle.cargo.collect(entry)
