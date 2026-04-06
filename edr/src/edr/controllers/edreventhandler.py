import re
import sys
from datetime import datetime, timezone
from edr.core.edri18n import _, _c
from edr.core.edrlog import EDR_LOG
from edr.utils.edtime import EDTime
from edr.models.edentities import EDPlayer
from edr.models.edsitu import EDPlanetaryLocation
from edr.models.edvehicles import EDVehicleFactory
from edr.models.edrrawdepletables import EDRRawDepletables

class EDREventHandler:
    """
    Handles journal and dashboard events from EDMC.
    Modularizes the complex event logic from load.py.
    """
    def __init__(self, edr_client, edmc_data):
        self.edr_client = edr_client
        self.edmc_data = edmc_data
        self.last_known_ship_name = ""

    def process_journal_entry(self, entry, state, from_genesis=False):
        """
        Processes a Journal entry from EDMC.
        """
        player = self.edr_client.player
        event = entry.get("event")

        # Lifecycle & Multi-categorical events
        if event in ["Shutdown", "ShutDown", "Music", "Resurrect", "Fileheader", "LoadGame", "Loadout", "SuitLoadout", "SwitchSuitLoadout", "LaunchSRV", "DockSRV", "Disembark", "Embark", "DropShipDeploy"]:
            self.handle_lifecycle_events(player, entry, state, from_genesis)

        if event in ["BookTaxi", "BookDropship", "CancelTaxi", "CancelDropship"]:
            self.handle_shuttle_events(entry)
        
        if event in ["NavRoute", "NavRouteClear"]:
            self.handle_nav_route_events(entry, state)

        if event in ["SetUserShipName", "SellShipOnRebuy", "ShipyardBuy", "ShipyardNew", "ShipyardSell", "ShipyardTransfer", "ShipyardSwap"]:
            self.handle_fleet_events(entry)

        if event == "ModuleInfo":
            self.handle_modules_events(player, entry)

        if event == "Cargo":
            player.piloted_vehicle.update_cargo()

        if event in ["EjectCargo", "CollectCargo"]:
            self.handle_cargo_events(player, entry)

        if event.startswith("Powerplay"):
            self.handle_powerplay_events(player, entry)
        
        if event == "Statistics" and not player.powerplay:
            self.edr_client.pledged_to(None)

        if event == "Friends":
            self.handle_friends_events(player, entry)

        if event == "EngineerProgress":
            self.handle_engineer_progress(player, entry)

        if event in ["Materials", "MaterialCollected", "MaterialDiscarded", "EngineerContribution", "EngineerCraft", "MaterialTrade", "MissionCompleted", "ScientificResearch", "TechnologyBroker", "Synthesis", "Backpack", "BackpackChange", "BuyMicroResources", "SellMicroResources", "TransferMicroResources", "TradeMicroResources", "ShipLockerMaterials", "ShipLocker"]:
            self.handle_material_events(player, entry, state)

        if event == "StoredShips":
            player.update_fleet(entry)

        if "Crew" in event:
            self.handle_multicrew_events(player, entry)
            
        if event in ["WingAdd", "WingJoin", "WingLeave"]:
            self.handle_wing_events(player, entry)

        if event in ["MiningRefined", "ProspectedAsteroid"]:
            self.handle_mining_events(player, entry)
        
        if event == "Bounty":
            self.handle_bounty_hunting_events(player, entry)

        if event in ["CarrierJump", "CarrierBuy", "CarrierStats", "CarrierJumpRequest", "CarrierJumpCancelled", "CarrierDecommission", "CarrierCancelDecommission", "CarrierDockingPermission", "CarrierTradeOrder", "FCMaterials"]:
            self.handle_carrier_events(player, entry)

        status_outcome = {"updated": False, "reason": "Unspecified"}
        vehicle = None
        if player.is_crew_member():
            vehicle = EDVehicleFactory.unknown_crew_vehicle()
        elif state.get("ShipType", None):
            vehicle = EDVehicleFactory.from_edmc_state(state)

        status_outcome["updated"] = player.update_vehicle_if_obsolete(vehicle, piloted=False)
        status_outcome["updated"] |= self.edr_client.update_star_system_if_obsolete(state.get("SystemName"), state.get("SystemAddress"))
            
        if event in ["Location", "Undocked", "Docked", "DockingCancelled", "DockingDenied", "DockingGranted", "DockingRequested", "DockingTimeout", "Touchdown", "Liftoff"]:
            outcome = self.handle_change_events(player, entry)
            self.handle_fc_position_related_events(player, entry)
            if outcome["updated"]:
                status_outcome["updated"] = True
                status_outcome["reason"] = outcome["reason"]

        if event in ["SupercruiseExit", "FSDJump", "SupercruiseEntry", "StartJump", "ApproachSettlement", "ApproachBody", "LeaveBody", "CarrierJump"]:
            outcome = self.handle_movement_events(player, entry)
            if outcome["updated"]:
                status_outcome["updated"] = True
                status_outcome["reason"] = outcome["reason"]
        
        if event == "Touchdown" and entry.get("PlayerControlled", None) and entry.get("NearestDestination", None):
            depletables = EDRRawDepletables()
            depletables.visit(entry["NearestDestination"])
            
        if event == "SAAScanComplete":
            self.edr_client.saa_scan_complete(entry)
        
        if event in ["SAASignalsFound", "FSSBodySignals"]:
            self.edr_client.body_signals_found(entry)
        
        if event in ["FSSSignalDiscovered"]:
            self.edr_client.noteworthy_about_signal(entry)

        if event == "FSSDiscoveryScan":
            if "SystemName" in entry:
                self.edr_client.update_star_system_if_obsolete(entry["SystemName"], entry.get("SystemAddress", None))
                self.edr_client.reflect_fss_discovery_scan(entry)
                self.edr_client.system_value(entry["SystemName"])
            self.edr_client.register_fss_signals(entry.get("SystemAddress", None), entry.get("SystemName", None), force_reporting=True)

        if event == "FSSAllBodiesFound":
            if "SystemName" in entry:
                player.update_star_system_if_obsolete(entry["SystemName"], entry.get("SystemAddress", None))
                self.edr_client.reflect_fss_discovery_scan(entry)
                self.edr_client.system_value(entry["SystemName"])

        if event == "NavBeaconScan" and entry.get("NumBodies", 0):
            if "SystemAddress" in entry:
                player.star_system_address = entry["SystemAddress"]
            self.edr_client.notify_with_details(_("System info acquired"), [_("Noteworthy material densities will be shown when approaching a planet.")])

        if event in ["Scan", "ScanOrganic"]:
            self.edr_client.process_scan(entry)
            if entry.get("ScanType") in ["Detailed", "Basic"]:
                self.edr_client.noteworthy_about_scan(entry)

        if event == "CodexEntry":
            self.edr_client.process_codex_entry(entry)
            
        if event in ["Interdicted", "Died", "EscapeInterdiction", "Interdiction", "PVPKill", "CrimeVictim", "CommitCrime"]:
            self.report_crime(player, entry)

        if event in ["PayFines", "PayBounties"]:
            self.handle_legal_fees(player, entry)

        if event == "ShipTargeted":
            if entry.get("ScanStage", 0) > 0:
                self.handle_scan_events(player, entry)
                self.handle_bounty_hunting_events(player, entry)
            elif (entry.get("ScanStage") == 0) or (not entry.get("TargetLocked", True)):
                player.untarget()
                self.edr_client.target_guidance(entry, turn_off=True)
                self.edr_client.bounty_hunting_guidance(turn_off=True)
        
        if event in ["HullDamage", "UnderAttack", "SRVDestroyed", "FighterDestroyed", "HeatDamage", "ShieldState", "CockpitBreached", "SelfDestruct"]:
            self.handle_damage_events(player, entry)

        if event in ["FuelScoop", "RefuelAll", "RefuelPartial", "Repair", "RepairAll", "AfmuRepairs", "RebootRepair", "RepairDrone"]:
            self.handle_fixing_events(player, entry)

        if event in ["ModuleStore", "ModuleSell", "ModuleBuy", "ModuleRetrieve", "MassModuleStore"]:
            self.handle_outfitting_events(player, entry)

        if event in ["ReceiveText", "SendText"]:
            self.report_comms(player, entry)

        if event == "SendText":
            self.edr_client.process_sent_message(entry)

        if event == "MissionAccepted":
            self.edr_client.eval_mission(entry)

        if status_outcome["updated"]:
            self.edr_update_cmdr_status(player, status_outcome["reason"], entry["timestamp"])
            if player.in_a_crew():
                for member in player.crew.members:
                    if member == player.name: continue
                    source = "Multicrew (captain)" if player.is_captain(member) else "Multicrew (crew)"
                    crew_player = EDPlayer(member)
                    crew_player.mothership = vehicle
                    self.edr_submit_contact(crew_player, entry["timestamp"], source, player)
        
        if player.maybe_in_a_pvp_fight():
            self.report_fight(player)

    def process_dashboard_entry(self, cmdr, entry):
        """
        Processes a Dashboard entry (status.json info).
        """
        player = self.edr_client.player
        if entry.get("GuiFocus", 0) > 0:
            player.in_game = True

        if 'Destination' in entry:
            if player.in_game:
                self.edr_client.destination_guidance(entry["Destination"])

        if 'Flags' not in entry:
            return

        flags = entry.get('Flags', 0)
        flags2 = entry.get('Flags2', 0)
        player.location.on_foot_location.update(flags2)

        if (flags2 & (self.edmc_data.Flags2OnFoot | self.edmc_data.Flags2OnFootInStation | self.edmc_data.Flags2OnFootOnPlanet | self.edmc_data.Flags2OnFootInHangar | self.edmc_data.Flags2OnFootSocialSpace | self.edmc_data.Flags2OnFootExterior)):
            player.in_spacesuit()
            self.edr_client.on_foot()
        else:
            self.edr_client.in_ship()
            if (flags & self.edmc_data.FlagsInMainShip) and not (flags2 & self.edmc_data.Flags2InTaxi):
                player.in_mothership()
            
            if (flags & self.edmc_data.FlagsInFighter):
                player.in_slf()

            if (flags & self.edmc_data.FlagsInSRV):
                player.in_srv()
            
            if (flags2 & self.edmc_data.Flags2InTaxi):
                player.in_taxi()
        
        if player.piloted_vehicle:
            player.piloted_vehicle.over_heating = flags & self.edmc_data.FlagsOverHeating
            player.piloted_vehicle.low_fuel = bool(flags & self.edmc_data.FlagsLowFuel)
            fuel = entry.get('Fuel', None)
            if fuel:
                main = fuel.get('FuelMain', player.piloted_vehicle.fuel_level)
                reservoir = fuel.get('FuelReservoir', 0)
                player.piloted_vehicle.fuel_level = main + reservoir
        
        if player.spacesuit:
            player.spacesuit.low_health = flags2 & self.edmc_data.Flags2LowHealth
            player.spacesuit.low_oxygen = flags2 & self.edmc_data.Flags2LowOxygen
            if entry.get("Oxygen"): player.spacesuit.oxygen = entry["Oxygen"]
            if entry.get("Health"): player.spacesuit.health = entry["Health"]

        if (flags & self.edmc_data.FlagsFsdJump or flags2 & self.edmc_data.Flags2GlideMode):
            player.in_blue_tunnel()
        else:
            player.in_blue_tunnel(False)
        
        docked = bool(flags & self.edmc_data.FlagsDocked)
        if player.is_docked and not docked:
            self.edr_client.ack_station_pending_reports()
        player.docked(docked)
        unsafe = bool(flags & self.edmc_data.FlagsIsInDanger)
        player.in_danger(unsafe)
        deployed = bool(flags & self.edmc_data.FlagsHardpointsDeployed)
        player.hardpoints(deployed)
        
        if player.recon_box.active and (not unsafe and not deployed):
            player.recon_box.reset()
            self.edr_client.notify_with_details(_("EDR Central"), [_("Fight reporting disabled"), _("Looks like you are safe, and disengaged.")])
        
        if player.in_normal_space() and player.recon_box.process_signal(flags & self.edmc_data.FlagsLightsOn):
            if player.recon_box.active:
                self.edr_client.notify_with_details(_("EDR Central"), [_("Fight reporting enabled"), _("Turn it off: flash your lights twice, or leave this area, or escape danger and retract hardpoints.")])
            else:
                self.edr_client.notify_with_details(_("EDR Central"), [_("Fight reporting disabled"), _("Flash your lights twice to re-enable.")])

        attitude_keys = {"Latitude", "Longitude", "Heading", "Altitude"}
        if all(key in entry for key in attitude_keys):
            attitude = {key.lower(): entry[key] for key in attitude_keys}
            if "altitude" in attitude: attitude["altitude"] /= 1000.0
            player.update_attitude(attitude)
            if player.body and player.tracking_organic():
                self.edr_client.biology_guidance()
            elif not player.planetary_destination and player.body and player.star_system:
                self.edr_client.try_custom_poi()

        if player.planetary_destination:
            self.edr_client.show_navigation()

    def handle_lifecycle_events(self, ed_player, entry, state, from_genesis=False):
        """Handle game lifecycle events (Music, LoadGame, Loadout, etc.)."""
        event = entry["event"]
        if event == "Music":
            if entry["MusicTrack"] in ["Supercruise", "NoTrack"]:
                self.edr_client.register_fss_signals()

            if entry["MusicTrack"] == "MainMenu" and not ed_player.is_crew_member():
                self.edr_client.clear()
                self.edr_client.edrfssinsights.reset()
                self.edr_client.game_mode(None)
                ed_player.leave_wing()
                ed_player.leave_crew()
                ed_player.leave_vehicle()
                ed_player.in_game = False
                EDR_LOG.debug("Player is on the main menu.")
                return
            
            ed_player.in_game = True
            if entry["MusicTrack"] == "Combat_Dogfight":
                if ed_player.mothership: ed_player.mothership.skirmish()
            elif entry["MusicTrack"] == "Combat_LargeDogFight":
                if ed_player.mothership: ed_player.mothership.battle()
            elif entry["MusicTrack"] == "Combat_SRV":
                if ed_player.srv: ed_player.srv.skirmish()
            elif entry["MusicTrack"] in ["Supercruise", "Exploration", "NoTrack"] and ed_player.in_a_fight():
                ed_player.in_danger(False)
            elif entry["MusicTrack"] == "SystemMap":
                self.edr_client.noteworthy_signals_in_system()
            elif entry["MusicTrack"] == "OnFoot":
                ed_player.in_spacesuit()
            elif entry["MusicTrack"] == "FleetCarrier_Managment":
                self.edr_client.fleet_carrier_update()

        if event == "Shutdown":
            self.edr_client.edrfssinsights.reset()
            self.edr_client.shutdown()
            return

        if event == "Resurrect":
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            ed_player.resurrect(entry["Option"] in ["rebuy", "recover"])
            return

        if event == "Fileheader" and entry.get("part") == 1:
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            ed_player.inception(genesis=True)
            self.edr_client.status = _("initialized.")
            return

        if event == "LoadGame":
            if ed_player.inventory.stale_or_incorrect():
                ed_player.inventory.initialize_with_edmc(state)
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            ed_player.inception(genesis=from_genesis)
            if entry.get("Odyssey", False): self.edr_client.set_dlc("Odyssey")
            elif entry.get("Horizons", False): self.edr_client.set_dlc("Horizons")
            self.edr_client.game_mode(entry["GameMode"], entry.get("Group"))
            ed_player.update_vehicle_or_suit_if_obsolete(entry)
            self.edr_client.warmup()
            return

        if event == "Loadout":
            if ed_player.mothership.id == entry.get("ShipID", -1):
                ed_player.mothership.update_from_loadout(entry)
                ed_player.mothership.update_cargo()
                if ed_player.mothership.could_use_limpets() and ed_player.is_docked:
                    limpets, capacity = ed_player.mothership.cargo.how_many("drones"), ed_player.mothership.cargo_capacity
                    self.edr_client.notify_with_details(_(U"Restock reminder"), [_("Don't forget to restock on limpets before heading out."), _("Limpets: {}/{}").format(limpets, capacity)])
                self.last_known_ship_name = ed_player.mothership.name
            else:
                ed_player.update_vehicle_if_obsolete(EDVehicleFactory.from_load_game_event(entry), piloted=True)
            return

        if event in ["SuitLoadout", "SwitchSuitLoadout"]:
            ed_player.update_suit_if_obsolete(entry)
            return

        if event == "LaunchSRV" and entry.get("PlayerControlled", False):
            ed_player.in_srv()
        elif event == "DockSRV":
            ed_player.in_mothership()
        elif event == "Disembark":
            ed_player.disembark(entry)
        elif event == "Embark":
            ed_player.embark(entry)
        elif event == "DropshipDeploy":
            ed_player.dropship_deployed(entry)

    def handle_friends_events(self, ed_player, entry):
        """Handle friend-related events."""
        if entry["event"] != "Friends": return
        if entry["Status"] == "Requested":
            self.edr_client.who(self.plain_cmdr_name(entry["Name"]), autocreate=True)
        elif entry["Status"] == "Offline":
            ed_player.deinstanced_player(entry["Name"])

    def handle_engineer_progress(self, ed_player, entry):
        """Handle engineer progress updates."""
        if entry["event"] == "EngineerProgress":
            ed_player.engineers.update(entry)

    def handle_powerplay_events(self, ed_player, entry):
        """Handle powerplay-related events."""
        event = entry["event"]
        if event == "Powerplay":
            self.edr_client.pledged_to(entry["Power"], entry["TimePledged"])
        elif event == "PowerplayDefect":
            self.edr_client.pledged_to(entry["ToPower"])
        elif event == "PowerplayJoin":
            self.edr_client.pledged_to(entry["Power"])
        elif event == "PowerplayLeave":
            self.edr_client.pledged_to(None)

    def handle_mining_events(self, ed_player, entry):
        """Handle mining-related events."""
        if entry["event"] == "ProspectedAsteroid":
            ed_player.prospected(entry)
        elif entry["event"] == "MiningRefined":
            ed_player.refined(entry)
        self.edr_client.mining_guidance()

    def handle_bounty_hunting_events(self, ed_player, entry):
        """Handle bounty hunting events."""
        if entry["event"] == "Bounty" and entry.get("Rewards"):
            ed_player.bounty_awarded(entry)
            self.edr_client.bounty_hunting_guidance()
        elif entry["event"] == "ShipTargeted":
            if entry.get("TargetLocked") and entry.get("ScanStage", 0) >= 3 and entry.get("Bounty", 0) > 0:
                ed_player.bounty_scanned(entry)
                self.edr_client.bounty_hunting_guidance()
            else:
                self.edr_client.bounty_hunting_guidance(turn_off=True)

    def handle_carrier_events(self, ed_player, entry):
        """Handle fleet carrier events."""
        event = entry["event"]
        if event == "CarrierBuy": ed_player.fleet_carrier.bought(entry)
        elif event == "CarrierStats": ed_player.fleet_carrier.update_from_stats(entry)
        elif event == "CarrierJumpRequest": self.edr_client.fc_jump_requested(entry)
        elif event == "CarrierJumpCancelled": self.edr_client.fc_jump_cancelled(entry)
        elif event == "CarrierDecommission": ed_player.fleet_carrier.decommission_requested(entry)
        elif event == "CarrierCancelDecommission": ed_player.fleet_carrier.cancel_decommission(entry)
        elif event == "CarrierDockingPermission": ed_player.fleet_carrier.update_docking_permissions(entry)
        elif event == "CarrierJump": self.edr_client.fc_jumped(entry)
        elif event == "CarrierTradeOrder": self.edr_client.carrier_trade(entry)
        elif event == "CarrierCrewServices": ed_player.fleet_carrier.tweak_crew_service(entry)
        elif event == "FCMaterials":
            self.edr_client.fc_materials(entry)
            if not self.edr_client.eval_bar(): self.edr_client.eval_bar(stock=False)

    def handle_fc_position_related_events(self, ed_player, entry):
        """Update fleet carrier position based on docking/location events."""
        if entry.get("StationType") == "FleetCarrier":
            self.edr_client.player.fleet_carrier.update_star_system_if_relevant(entry.get("StarSystem", ed_player.star_system), entry.get("MarketID", 0), entry.get("StationName"))

    def handle_shuttle_events(self, entry):
        """Handle apex/frontline shuttle events."""
        player = self.edr_client.player
        if entry["event"] in ["BookTaxi", "BookDropship"]:
            player.booked_shuttle(entry)
        elif entry["event"] in ["CancelTaxi", "CancelDropship"]:
            player.cancelled_shuttle(entry)

    def handle_nav_route_events(self, entry, state):
        """Handle navigation route events."""
        if entry["event"] == "NavRouteClear":
            self.edr_client.nav_route_clear()
        elif entry["event"] == "NavRoute" and state.get("NavRoute"):
            self.edr_client.nav_route_set(state["NavRoute"])

    def handle_fleet_events(self, entry):
        """Handle fleet management events (rename, buy, sell)."""
        player = self.edr_client.player
        event = entry["event"]
        if event == "SetUserShipName":
            player.fleet.rename(entry)
            player.mothership.update_name(entry)
            self.last_known_ship_name = player.mothership.name
        elif event in ["SellShipOnRebuy", "ShipyardSell"]:
            player.fleet.sell(entry)
        elif event == "ShipyardBuy":
            player.fleet.buy(entry, player.star_system, player.mothership.name)
        elif event == "ShipyardNew":
            player.fleet.new(entry, player.star_system)
        elif event == "ShipyardTransfer":
            player.fleet.transfer(entry, player.star_system)
        elif event == "ShipyardSwap":
            player.fleet.swap(entry, player.star_system, self.last_known_ship_name)
            self.last_known_ship_name = player.mothership.name

    def handle_modules_events(self, ed_player, entry):
        """Handle module information events."""
        if entry["event"] == "ModuleInfo":
            ed_player.mothership.outfit_probably_changed(entry["timestamp"])

    def handle_cargo_events(self, ed_player, entry):
        """Handle cargo-related events (eject/collect)."""
        if entry["event"] == "EjectCargo":
            ed_player.piloted_vehicle.cargo.eject(entry)
        elif entry["event"] == "CollectCargo":
            ed_player.piloted_vehicle.cargo.collect(entry)

    def handle_damage_events(self, ed_player, entry):
        """Handle damage and destruction events."""
        event = entry["event"]
        if event == "HullDamage":
            if entry.get("Fighter"):
                if ed_player.slf: ed_player.slf.taking_hull_damage(entry["Health"] * 100.0)
            else:
                ed_player.mothership.taking_hull_damage(entry["Health"] * 100.0)
        elif event == "CockpitBreached":
            ed_player.piloted_vehicle.cockpit_breached()
        elif event == "ShieldState":
            if ed_player.piloted_vehicle: ed_player.piloted_vehicle.shield_state(entry["ShieldsUp"])
        elif event == "UnderAttack":
            ed_player.attacked(entry.get("Target", "SRV"))
        elif event == "HeatDamage" and ed_player.piloted_vehicle:
            ed_player.piloted_vehicle.taking_heat_damage()
        elif event == "SRVDestroyed":
            if ed_player.srv: ed_player.srv.destroy()
        elif event == "FighterDestroyed":
            if ed_player.slf: ed_player.slf.destroy()
        elif event == "SelfDestruct" and ed_player.piloted_vehicle:
            ed_player.piloted_vehicle.destroy()

    def handle_fixing_events(self, ed_player, entry):
        """Handle repair and refueling events."""
        event = entry["event"]
        if event == "AfmuRepairs":
            ed_player.mothership.subsystem_health(entry["Module"], entry["Health"] * 100.0)
        elif event == "FuelScoop":
            ed_player.mothership.fuel_scooping(entry["Total"])
        elif event == "RefuelAll":
            ed_player.mothership.refuel()
        elif event == "RefuelPartial":
            ed_player.mothership.refuel(entry["Amount"])
        elif event == "RepairAll":
            ed_player.mothership.repair()
        elif event == "Repair":
            items = entry.get("Items", [entry.get("Item")])
            for item in items:
                if item: ed_player.mothership.repair(item)
        elif event == "RepairDrone":
            if entry.get("HullRepaired"): ed_player.mothership.hull_health = entry["HullRepaired"]
            if entry.get("CockpitRepaired"): ed_player.mothership.cockpit_health(entry["CockpitRepaired"])

    def handle_outfitting_events(self, player, entry):
        """Handle outfitting changes."""
        event = entry["event"]
        if event == "MassModuleStore":
            for item in entry["Items"]: player.mothership.remove_subsystem(item["Name"])
        elif event == "ModuleStore":
            player.mothership.remove_subsystem(entry["StoredItem"])
            if entry.get("ReplacementItem"): player.mothership.add_subsystem(entry["ReplacementItem"])
        elif event == "ModuleBuy":
            if entry.get("StoredItem"): player.mothership.remove_subsystem(entry["StoredItem"])
            elif entry.get("SellItem"): player.mothership.remove_subsystem(entry["SellItem"])
            player.mothership.add_subsystem(entry["BuyItem"])
        elif event == "ModuleSell":
            player.mothership.remove_subsystem(entry["SellItem"])
        elif event == "ModuleRetrieve":
            if entry.get("SwapOutItem"): player.mothership.remove_subsystem(entry["SwapOutItem"])
            player.mothership.add_subsystem(entry["RetrievedItem"])

    def handle_legal_fees(self, player, entry):
        """Handle fine and bounty payments."""
        if entry["event"] == "PayFines":
            if entry.get("AllFines"): player.paid_all_fines()
            else: player.paid_fine(entry)
        elif entry["event"] == "PayBounties":
            if entry.get("AllFines"): player.paid_all_bounties()
            else:
                player.paid_bounty(entry)
                true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0)/100.0)
                player.bounty = max(0, player.bounty - true_amount)

    def handle_scan_events(self, player, entry):
        """Handle ship scanning events."""
        if not entry.get("TargetLocked") or entry.get("ScanStage", 0) <= 0: return
        
        prefix, piloted, npc = None, False, False
        pilot_name = entry.get("PilotName", "")
        if pilot_name.startswith("$cmdr_decorate:#name="):
            prefix, piloted = "$cmdr_decorate:#name=", True
        elif pilot_name.startswith("$RolePanel2_unmanned; $cmdr_decorate:#name="):
            prefix = "$RolePanel2_unmanned; $cmdr_decorate:#name="
        elif pilot_name.startswith("$RolePanel2_crew; $cmdr_decorate:#name="):
            prefix, piloted = "$RolePanel2_crew; $cmdr_decorate:#name=", True
        elif pilot_name.startswith("$npc_name_decorate:#name="):
            prefix, piloted, npc = "$npc_name_decorate:#name=", True, True
        elif pilot_name in ["$ShipName_Police_Independent;", "$ShipName_Police_Federation;", "$ShipName_Police_Empire;", "$LUASC_Scenario_Warzone_NPC_WarzoneGeneral_Ind;", "$ShipName_Military_Federation;", "$ShipName_Military_Independent;", "$ShipName_SearchAndRescue;", "$ShipName_ATR_Federation;", "$ShipName_Military_Empire;", "$ShipName_PassengerLiner_Wedding;", "$ShipName_PassengerLiner_Cruise;"]:
            piloted, npc = True, True
        
        target_name = entry.get("PilotName_Localised", pilot_name)
        if prefix: target_name = pilot_name[len(prefix):-1]
        if target_name == player.name: return

        target = player.instanced_npc(target_name, rank=entry.get("PilotRank", "Unknown"), ship_internal_name=entry["Ship"], piloted=piloted) if npc else player.instanced_player(target_name, rank=entry.get("PilotRank", "Unknown"), ship_internal_name=entry["Ship"], piloted=piloted)
        target.sqid = entry.get("SquadronID")
        target.pledged_to(entry["Power"].replace(".", "") if "Power" in entry else None)
        if target.is_human(): self.edr_submit_contact(target, entry["timestamp"], "Ship targeted", player)

        if entry["ScanStage"] >= 2:
            if "ShieldHealth" in entry: target.vehicle.shield_health = entry["ShieldHealth"]
            if "HullHealth" in entry: target.vehicle.hull_health = entry["HullHealth"]

        if entry["ScanStage"] == 3:
            target.wanted = entry["LegalStatus"] in ["Wanted", "WantedEnemy", "Warrant"]
            target.enemy = entry["LegalStatus"] in ["Enemy", "WantedEnemy", "Hunter"]
            target.bounty = entry.get("Bounty", 0)
            if "Subsystem" in entry and "SubsystemHealth" in entry: target.vehicle.subsystem_health(entry["Subsystem"], entry["SubsystemHealth"])
            scan = {"cmdr": target.name, "ship": target.vehicle_type(), "wanted": target.wanted, "enemy": target.enemy, "bounty": target.bounty, "sqid": target.sqid}
            if target.power: scan["power"] = target.powerplay.canonicalize() if target.powerplay else ""
            elif not player.is_independent(): scan["power"] = "independent"
            if target.is_human(): self.edr_submit_scan(scan, entry["timestamp"], "Ship targeted [{}]".format(entry["LegalStatus"]), player)

        player.targeting(target, ship_internal_name=entry["Ship"])
        self.edr_client.target_guidance(entry)

    def handle_material_events(self, cmdr, entry, state):
        """Handle material and inventory events."""
        event = entry["event"]
        if event in ["Materials", "ShipLockerMaterials"] or (event in ["ShipLocker", "Backpack"] and len(entry.keys()) > 2):
            cmdr.inventory.initialize(entry)
        if cmdr.inventory.stale_or_incorrect(): cmdr.inventory.initialize_with_edmc(state)

        if event == "MaterialCollected": cmdr.inventory.collected(entry)
        elif event == "MaterialDiscarded": cmdr.inventory.discarded(entry)
        elif event == "EngineerContribution": cmdr.inventory.donated_engineer(entry)
        elif event == "ScientificResearch": cmdr.inventory.donated_science(entry)
        elif event in ["EngineerCraft", "TechnologyBroker", "Synthesis"]:
            cmdr.inventory.consumed(entry.get("Ingredients", entry.get("Materials")))
        elif event == "MaterialTrade": cmdr.inventory.traded(entry)
        elif event == "MissionCompleted":
            cmdr.inventory.rewarded(entry)
            self.edr_client.eval_mission(entry)
        elif event == "BackpackChange":
            cmdr.inventory.backpack_change(entry)
            if "Added" in entry:
                added = [cmdr.inventory.oneliner(item["Name"], True) for item in entry["Added"] if not (cmdr.engineers.is_useless(item["Name"]) or cmdr.engineers.is_unnecessary(item["Name"])) or "MissionID" in item]
                discardable = [cmdr.inventory.oneliner(item["Name"], True) for item in entry["Added"] if cmdr.engineers.is_useless(item["Name"]) and not cmdr.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
                unnecessary = [cmdr.inventory.oneliner(item["Name"], True) for item in entry["Added"] if cmdr.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
                details = [", ".join(added)]
                if discardable: details.append(_("Useless: {}").format(", ".join(discardable)))
                if unnecessary: details.append(_("Unnecessary: {}").format(", ".join(unnecessary)))
                self.edr_client.notify_with_details("Materials Info", details)
            elif "Removed" in entry: self.edr_client.eval_backpack(passive=True)
        elif event == "SellMicroResources":
            cmdr.inventory.sold(entry)
            self.edr_client.eval_locker(passive=True)
        elif event == "BuyMicroResources": cmdr.inventory.bought(entry)
        elif event == "TransferMicroResources":
            cmdr.inventory.bought(entry)
            self.edr_client.eval_backpack(passive=True)
        elif event == "TradeMicroResources":
            cmdr.inventory.traded(entry)
            self.edr_client.eval_locker(passive=True)

    def report_crime(self, cmdr, entry):
        """Report a crime to the EDR server."""
        player_one = self.edr_client.player
        event = entry["event"]
        if event in ["Interdicted", "EscapeInterdiction"]:
            interdictor = player_one.instanced_player(entry["Interdictor"]) if entry.get("IsPlayer") else player_one.instanced_npc(entry.get("Interdictor", "[N/A]"))
            player_one.interdicted(interdictor, event == "Interdicted")
            if entry.get("IsPlayer"): self.edr_submit_crime([interdictor], event, cmdr, entry["timestamp"])
        elif event == "Died":
            if "Killers" in entry:
                criminals = [player_one.instanced_player(k["Name"][5:], ship_internal_name=k["Ship"]) for k in entry["Killers"] if k["Name"].startswith("Cmdr ")]
                self.edr_submit_crime(criminals, "Murder", cmdr, entry["timestamp"])
            elif entry.get("KillerName", "").startswith("Cmdr "):
                criminal = player_one.instanced_player(entry["KillerName"][5:], ship_internal_name=entry.get("KillerShip"))
                self.edr_submit_crime([criminal], "Murder", cmdr, entry["timestamp"])
            player_one.killed()
        elif event == "Interdiction":
            offence = "Interdiction" if entry["Success"] else "Failed interdiction"
            interdicted = player_one.instanced_player(entry["Interdicted"]) if entry.get("IsPlayer") else player_one.instanced_npc(entry.get("Interdicted", "[N/A]"))
            player_one.interdiction(interdicted, entry["Success"])
            if entry.get("IsPlayer"): self.edr_submit_crime_self(cmdr, offence, interdicted, entry["timestamp"])
        elif event == "PVPKill":
            victim = player_one.instanced_player(entry["Victim"])
            victim.killed()
            self.edr_submit_crime_self(cmdr, "Murder", victim, entry["timestamp"])
            player_one.destroy(victim)
        elif event == "CrimeVictim" and "Offender" in entry:
            if not re.match(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$", entry["Offender"]) and player_one.is_instanced_with_player(entry["Offender"]) and entry["Offender"].lower() != player_one.name.lower() and not (player_one.is_wingmate(entry["Offender"]) or player_one.is_crewmate(entry["Offender"])):
                offender = player_one.instanced_player(entry["Offender"])
                if "Bounty" in entry: offender.bounty += entry["Bounty"]
                if "Fine" in entry: offender.fine += entry["Fine"]
                self.edr_submit_crime([offender], "{} (CrimeVictim)".format(entry["CrimeType"]), cmdr, entry["timestamp"])
        elif event == "CommitCrime" and "Victim" in entry and entry["Victim"].lower() != player_one.name.lower():
            if not re.match(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$", entry["Victim"]) and player_one.is_instanced_with_player(entry["Victim"]):
                victim = player_one.instanced_player(entry["Victim"])
                if "Bounty" in entry: player_one.bounty += entry["Bounty"]
                if "Fine" in entry: player_one.fine += entry["Fine"]
                self.edr_submit_crime_self(player_one, "{} (CommitCrime)".format(entry["CrimeType"]), victim, entry["timestamp"])

    def report_comms(self, player, entry):
        """Report communications with other commanders."""
        event = entry["event"]
        if event == "ReceiveText" and "Channel" in entry:
            channel, from_cmdr = entry["Channel"], self.plain_cmdr_name(entry["From"])
            if channel == "local":
                self.edr_submit_contact(player.instanced_player(from_cmdr), entry["timestamp"], "Received text (local)", player)
            elif channel == "player":
                if not (player.is_friend(from_cmdr) or player.is_wingmate(from_cmdr)) and player.from_genesis:
                    self.edr_submit_contact(player.instanced_player(from_cmdr), entry["timestamp"], "Received text (non wing/friend player)", player)
            elif channel == "starsystem":
                contact = EDPlayer(from_cmdr)
                contact.star_system = player.star_system
                self.edr_submit_contact(contact, entry["timestamp"], "Received text (starsystem channel)", player, system_wide=True)
            elif channel == "npc" and entry["From"] == "$CHAT_System;":
                m = re.match(r"^\$HumanoidEmote_TargetMessage:#player=\$cmdr_decorate:#name=(.+);:#targetedAction=\$HumanoidEmote_([a-zA-Z]+)_Action_Targeted;:#target=\$cmdr_decorate:#name=(.+);;$", entry.get("Message", ""))
                if m:
                    action, receiving_party = m.group(2), m.group(3)
                    self.edr_submit_contact(player.instanced_player(receiving_party), entry["timestamp"], "Emote sent (non wing/friend player)", player)
                    if action in ["wave", "point"] and self.edr_client.gesture_triggers: self.edr_client.who(receiving_party, autocreate=True)
                elif "$HumanoidEmote_" in entry.get("Message", ""):
                    if not self.edr_client.pointing_guidance(entry): self.edr_client.gesture(entry)
        elif event == "SendText" and entry.get("To") not in ["local", "wing", "starsystem", "squadron", "squadleaders"]:
            to_cmdr = self.plain_cmdr_name(entry["To"])
            if not (player.is_friend(to_cmdr) or player.is_wingmate(to_cmdr)) and player.from_genesis:
                self.edr_submit_contact(player.instanced_player(to_cmdr), entry["timestamp"], "Sent text (non wing/friend player)", player)
        
        m = re.findall(r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+)", entry.get("Message", ""), flags=re.IGNORECASE)
        if m: self.edr_client.linkable_status(m[0])

    def report_fight(self, player):
        """Report a fight to the EDR server."""
        if not player.in_open():
            self.edr_client.status = _("Fight reporting disabled in solo/private modes.")
            return
        self.edr_client.fight(player.json(with_target=True))

    def edr_update_cmdr_status(self, cmdr, reason, timestamp):
        """Update commander status on the EDR server."""
        if cmdr.in_solo() or cmdr.has_partial_status(): return
        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        report = {"cmdr": cmdr.name, "starSystem": cmdr.star_system, "place": cmdr.place, "timestamp": edt.as_js_epoch(), "source": reason, "reportedBy": cmdr.name, "mode": cmdr.game_mode, "dlc": cmdr.dlc_name, "group": cmdr.private_group}
        if cmdr.vehicle_type(): report["ship"] = cmdr.vehicle_type()
        elif cmdr.spacesuit_type(): report["suit"] = cmdr.spacesuit_type()
        if not self.edr_client.blip(cmdr.name, report): self.edr_client.status = _("blip failed.")

    def edr_submit_crime(self, criminals_cmdrs, offence, victim, timestamp):
        """Submit a crime report."""
        if not victim.in_open():
            self.edr_client.status = _("Crime reporting disabled in solo/private modes.")
            return
        criminals = []
        for c in criminals_cmdrs:
            b = {"name": c.name, "enemy": c.enemy, "wanted": c.wanted, "bounty": c.bounty, "fine": c.fine, "power": c.powerplay.canonicalize() if c.powerplay else ""}
            if c.vehicle_type(): b["ship"] = c.vehicle_type()
            elif c.spacesuit_type(): b["suit"] = c.spacesuit_type()
            criminals.append(b)
        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        report = {"starSystem": victim.star_system, "place": victim.place, "timestamp": edt.as_js_epoch(), "criminals": criminals, "offence": offence.capitalize(), "victim": victim.name, "reportedBy": victim.name, "victimPower": victim.powerplay.canonicalize() if victim.powerplay else "", "byPledge": victim.powerplay.canonicalize() if victim.powerplay else "", "mode": victim.game_mode, "dlc": victim.dlc_name, "group": victim.private_group}
        if victim.vehicle_type(): report["victimShip"] = victim.vehicle_type()
        elif victim.spacesuit_type(): report["victimSuit"] = victim.spacesuit_type()
        if not self.edr_client.crime(victim.star_system, report): self.edr_client.status = _("failed to report crime.")

    def edr_submit_crime_self(self, criminal_cmdr, offence, victim, timestamp):
        """Submit a report of a crime committed by the player."""
        if not criminal_cmdr.in_open():
            self.edr_client.status = _("Crime reporting disabled in solo/private modes.")
            return
        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        c_blob = {"name": criminal_cmdr.name, "wanted": criminal_cmdr.wanted, "bounty": criminal_cmdr.bounty, "fine": criminal_cmdr.fine, "power": criminal_cmdr.powerplay.canonicalize() if criminal_cmdr.powerplay else ""}
        if criminal_cmdr.vehicle_type(): c_blob["ship"] = criminal_cmdr.vehicle_type()
        elif criminal_cmdr.spacesuit_type(): c_blob["suit"] = criminal_cmdr.spacesuit_type()
        report = {"starSystem": criminal_cmdr.star_system, "place": criminal_cmdr.place, "timestamp": edt.as_js_epoch(), "criminals": [c_blob], "offence": offence.capitalize(), "victim": victim.name, "reportedBy": criminal_cmdr.name, "victimWanted": victim.wanted, "victimBounty": victim.bounty, "victimEnemy": victim.enemy, "victimPower": victim.powerplay.canonicalize() if victim.powerplay else "", "byPledge": victim.powerplay.canonicalize() if victim.powerplay else "", "mode": criminal_cmdr.game_mode, "dlc": criminal_cmdr.dlc_name, "group": criminal_cmdr.private_group}
        if victim.vehicle_type(): report["victimShip"] = victim.vehicle_type()
        elif victim.spacesuit_type(): report["victimSuit"] = victim.spacesuit_type()
        if not self.edr_client.crime(criminal_cmdr.star_system, report): self.edr_client.status = _("failed to report crime.")

    def edr_submit_contact(self, contact, timestamp, source, witness, system_wide=False):
        """Submit a contact report."""
        if witness.has_partial_status(): return
        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        report = {"cmdr": contact.name, "starSystem": witness.star_system, "place": witness.place, "timestamp": edt.as_js_epoch(), "source": source, "reportedBy": witness.name, "byPledge": witness.powerplay.canonicalize() if witness.powerplay else "", "mode": witness.game_mode, "dlc": witness.dlc_name, "group": witness.private_group}
        if contact.vehicle_type(): report["ship"] = contact.vehicle_type()
        elif contact.spacesuit_type(): report["suit"] = contact.spacesuit_type()
        if contact.sqid: report["sqid"] = contact.sqid
        if not self.edr_client.blip(contact.name, report, system_wide): self.edr_client.status = _("failed to report contact.")
        self.edr_submit_traffic(contact, timestamp, source, witness, system_wide)

    def edr_submit_scan(self, scan, timestamp, source, witness):
        """Submit a scan report."""
        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        report = scan.copy()
        report.update({"starSystem": witness.star_system, "place": witness.place, "timestamp": edt.as_js_epoch(), "source": source, "reportedBy": witness.name, "byPledge": witness.powerplay.canonicalize() if witness.powerplay else "", "mode": witness.game_mode, "dlc": witness.dlc_name, "group": witness.private_group})
        self.edr_client.scanned(scan["cmdr"], report)

    def edr_submit_traffic(self, contact, timestamp, source, witness, system_wide=False):
        """Submit a traffic report."""
        if not witness.in_open() and not system_wide:
            self.edr_client.status = _("Traffic reporting disabled in solo/private modes.")
            return
        if witness.has_partial_status(): return
        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        report = {"cmdr": contact.name, "starSystem": witness.star_system, "place": witness.place, "timestamp": edt.as_js_epoch(), "source": source, "reportedBy": witness.name, "byPledge": witness.powerplay.canonicalize() if witness.powerplay else "", "mode": witness.game_mode, "dlc": witness.dlc_name, "group": witness.private_group}
        if contact.vehicle_type(): report["ship"] = contact.vehicle_type()
        elif contact.spacesuit_type(): report["ship"] = contact.spacesuit_type()
        if not self.edr_client.traffic(witness.star_system, report, system_wide): self.edr_client.status = _("failed to report traffic.")

    def edr_submit_multicrew_session(self, player, report):
        """Submit a multicrew session report."""
        if not player.in_open() and not player.destroyed:
            self.edr_client.status = _("Multicrew reporting disabled in private mode.")
            return
        if not self.edr_client.crew_report(report): self.edr_client.status = _("failed to report multicrew session.")
