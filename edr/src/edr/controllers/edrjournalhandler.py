from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _
from edr.utils.edtime import EDTime
from edr.models.edsitu import EDPlanetaryLocation

from edr.core.edrconfig import EDR_CONFIG
from edr.core.edrplayer import EDRPlayer
from edr.core.edrvehicle import EDVehicleFactory
from edr.core.edrrawdepletables import EDRRawDepletables

class EDRJournalHandler:
    def __init__(self, edr_client):
        self.edr_client = edr_client
        self.ed_player = edr_client.ed_player
        self.last_known_ship_name = ""
        self.snapshot = None
        self.first_run = True

        self.event_map = {
            "SupercruiseEntry": self._on_supercruise_entry,
            "SupercruiseExit": self._on_supercruise_exit,
            "FSDJump": self._on_fsd_jump,
            "StartJump": self._on_start_jump,
            "ApproachSettlement": self._on_approach_settlement,
            "ApproachBody": self._on_approach_body,
            "LeaveBody": self._on_leave_body,

            "FuelScoop": self._on_fuel_scoop,
            "RefuelAll": self._on_refuel_all,
            "RefuelPartial": self._on_refuel_partial,
            "Repair": self._on_repair,
            "RepairAll": self._on_repair_all,
            "AfmuRepairs": self._on_afmu_repairs,
            "RebootRepair": self._on_reboot_repair,
            "RepairDrone": self._on_repair_drone,

            "PayFines": self._on_pay_fines,
            "PayBounties": self._on_pay_bounties,

            "SendText": self._on_send_text,
            "ReceiveText": self._on_receive_text,

            "BookTaxi": self._on_book_taxi,
            "BookDropship": self._on_book_dropship,
            "CancelTaxi": self._on_cancel_taxi,
            "CancelDropship": self._on_cancel_dropship,

            "NavRoute": self._on_nav_route,
            "NavRouteClear": self._on_nav_route_clear,

            "ModuleInfo": self._on_module_info,

            "Cargo": self._on_cargo,
            "EjectCargo": self._on_eject_cargo,
            "CollectCargo": self._on_collect_cargo,

            "MissionAccepted": self._on_mission_accepted,

            "CarrierBuy": self._on_carrier_buy,
            "CarrierStats": self._on_carrier_stats,
            "CarrierSell": self._on_carrier_sell,
            "CarrierTrade": self._on_carrier_trade,
            "CarrierJumpRequested": self._on_carrier_jump_requested,
            "CarrierJumpCancelled": self._on_carrier_jump_cancelled,
            "CarrierJump": self._on_carrier_jump,
            "CarrierDecommission": self._on_carrier_decommission,
            "CarrierCancelDecommission": self._on_carrier_cancel_decommission,
            "CarrierDockingPermission": self._on_carrier_docking_permission,
            "CarrierTradeOrder": self._on_carrier_trade_order,
            "FCMaterials": self._on_fc_materials,
            
            "Music": self._on_music,

            "Shutdown": self._on_shutdown,
            "ShutDown": self._on_shutdown,
            "Resurrect": self._on_resurrect,
            "LoadGame": self._on_load_game,
            "Fileheader": self._on_fileheader,
            "Loadout": self._on_loadout,
            "SuitLoadout": self._on_suit_loadout,
            "SwitchSuitLoadout": self._on_switch_suit_loadout,
            "LaunchSRV": self._on_launch_srv,
            "DockSRV": self._on_dock_srv,
            "Disembark": self._on_disembark,
            "Embark": self._on_embark,
            "DropshipDeploy": self._on_dropship_deploy,

            "Friends": self._on_friends,
            
            "EngineerProgress": self._on_engineer_progress,
            
            "Powerplay": self._on_powerplay,
            "PowerplayDefect": self._on_powerplay_defect,
            "PowerplayJoin": self._on_powerplay_join,
            "PowerplayLeave": self._on_powerplay_leave,

            "MiningRefined": self._on_mining_refined,
            "ProspectedAsteroid": self._on_prospected_asteroid,

            "Bounty": self._on_bounty,
            "ShipTargeted": self._on_ship_targeted,

            "HullDamage": self._on_hull_damage,
            "UnderAttack": self._on_under_attack,
            "SRVDestroyed": self._on_srv_destroyed,
            "FighterDestroyed": self._on_fighter_destroyed,
            "HeatDamage": self._on_heat_damage,
            "ShieldState": self._on_shield_state,
            "CockpitBreached": self._on_cockpit_breached,
            "SelfDestruct": self._on_self_destruct,

            "MassModuleStore": self._on_mass_module_store,
            "ModuleStore": self._on_module_store,
            "ModuleSell": self._on_module_sell,
            "ModuleBuy": self._on_module_buy,
            "ModuleRetrieve": self._on_module_retrieve,

            "SetUserShipName": self._on_set_user_ship_name,
            "SellShipOnRebuy": self._on_sell_ship_on_rebuy,
            "ShipyardBuy": self._on_shipyard_buy,
            "ShipyardNew": self._on_shipyard_new,
            "ShipyardSell": self._on_shipyard_sell,
            "ShipyardTransfer": self._on_shipyard_transfer,
            "ShipyardSwap": self._on_shipyard_swap,
            "StoredShips": self._on_stored_ships,

            "WingAdd": self._on_wing_add,
            "WingJoin": self._on_wing_join,
            "WingLeave": self._on_wing_leave,
            "WingInvite": self._on_wing_invite,

            "CrewMemberJoins": self._on_crew_member_joins,
            "CrewMemberRoleChange": self._on_crew_member_role_change,
            "CrewLaunchFighter": self._on_crew_launch_fighter,
            "CrewMemberQuits": self._on_crew_member_quits,
            "KickCrewMember": self._on_kick_crew_member,
            "JoinACrew": self._on_join_a_crew,
            "QuitACrew": self._on_quit_a_crew,
            "EndCrewSession": self._on_end_crew_session,

            "Location": [self._on_location, self._fc_position_related_events],
            "Docked": [self._on_docked, self._fc_position_related_events],
            "Undocked": [self._on_undocked, self._fc_position_related_events],
            "DockingCancelled": [self._on_docking_cancelled, self._fc_position_related_events],
            "DockingDenied": [self._on_docking_denied, self._fc_position_related_events],
            "DockingGranted": [self._on_docking_granted, self._fc_position_related_events],
            "DockingRequested": [self._on_docking_requested, self._fc_position_related_events],
            "DockingTimeout": [self._on_docking_timeout, self._fc_position_related_events],
            
            "Touchdown": self._on_touchdown,
            "Liftoff": self._on_liftoff,

            "SAAScanComplete": self._on_saa_scan_complete,
            "SAASignalsFound": self._on_saa_signals_found,
            "FSSBodySignals": self._on_fss_body_signals,
            "FSSSignalDiscovered": self._on_fss_signal_discovered,
            "FSSDiscoveryScan": self._on_fss_discovery_scan,
            "FSSAllBodiesFound": self._on_fss_all_bodies_found,
            "NavBeaconScan": self._on_nav_beacon_scan,
            "Scan": self._on_scan,
            "ScanOrganic": self._on_scan,
            "CodexEntry": self._on_codex_entry,

            "Materials": self._on_materials,
            "MaterialCollected": self._on_material_collected,
            "MaterialDiscarded": self._on_material_discarded,
            "EngineerContribution": self._on_engineer_contribution,
            "EngineerCraft": self._on_engineer_craft,
            "MaterialTrade": self._on_material_trade,
            "MissionCompleted": self._on_mission_completed,
            "ScientificResearch": self._on_scientific_research,
            "TechnologyBroker": self._on_technology_broker,
            "Synthesis": self._on_synthesis,
            "Backpack": self._on_backpack,
            "BackpackChange": self._on_backpack_change,
            "BuyMicroResources": self._on_buy_micro_resources,
            "SellMicroResources": self._on_sell_micro_resources,
            "TransferMicroResources": self._on_transfer_micro_resources,
            "TradeMicroResources": self._on_trade_micro_resources,
            "ShipLockerMaterials": self._baseline_materials_events,
            "ShipLocker": self._baseline_materials_events,
            
            "Interdicted": self._on_interdicted,
            "EscapeInterdiction": self._on_escape_interdiction,
            "Interdiction": self._on_interdiction,
            "Died": self._on_died,
            "PVPKill": self._on_pvpkill,
            "CrimeVictim": self._on_crime_victim,
            "CommitCrime": self._on_commit_crime,
            "ShipTargeted": self._on_ship_targeted,

            "Statistics": self._on_statistics,
            
        }
    
    def _take_snapshot(self):
        """Captures the key state variables before an event is processed."""
        self.snapshot = {
            "star_system": self.ed_player.star_system,
            "place": self.ed_player.place,
            "body": self.ed_player.body,
            "docked": self.ed_player.is_docked,
            "vehicle": self.ed_player.vehicle_type()
        }

    def _should_report(self):
        """Compares current state to snapshot to see if a blip is needed."""
        if not self.snapshot:
            return True

        if self.ed_player.in_solo():
            return False

        if self.ed_player.has_partial_status():
            return False
            
        return (
            self.ed_player.star_system != self.snapshot["star_system"] or
            self.ed_player.place != self.snapshot["place"] or
            self.ed_player.body != self.snapshot["body"] or
            self.ed_player.is_docked != self.snapshot["docked"] or
            self.ed_player.vehicle_type() != self.snapshot["vehicle"]
        )

    def journal_entry(self, entry, state):
        self.edr_client.edrdiscord.process(entry)

        self._take_snapshot()
        
        event_type = entry.get("event")
        handlers = self.event_map.get(event_type)
        if isinstance(handlers, list):
            for handler in handlers:
                handler(entry, state)
        else:
            handlers(entry, state)

        self._finalize_and_report(entry)

    def _finalize_and_report(self, entry):
        self.ed_player.location.from_entry(entry)
        
        if self._should_report():
            self._update_cmdr_status(entry["event"], entry["timestamp"])

        if self.ed_player.maybe_in_a_pvp_fight():
            self.report_fight(self.ed_player)

    
    @staticmethod
    def _plain_cmdr_name(journal_cmdr_name):
        if journal_cmdr_name.startswith("$cmdr_decorate:#name="):
            return journal_cmdr_name[len("$cmdr_decorate:#name="):-1]
        return journal_cmdr_name

    def _on_cargo(self, entry, state):
        self.ed_player.piloted_vehicle.update_cargo()


    def _on_statistics(self, entry, state):
        if not self.ed_player.powerplay:
            # There should be a Powerplay event before the Statistics event
            # if not then the player is not pledged and we should reflect that on the server
            self.edr_client.pledged_to(None)

    def _on_stored_ships(self, entry, state):
        self.ed_player.update_fleet(entry)

    def _on_codex_entry(self, entry, state):
        self.edr_client.process_codex_entry(entry)


    def _on_saa_scan_complete(self, entry, state):
        self.edr_client.saa_scan_complete(entry)
        
    def _on_saa_signals_found(self, entry, state):
        self.edr_client.body_signals_found(entry)

    def _on_fss_body_signals(self, entry, state):
        self.edr_client.body_signals_found(entry)
        
    def _on_fss_signal_discovered(self, entry, state):
        self.edr_client.noteworthy_about_signal(entry)

    def _on_fss_discovery_scan(self, entry, state):
        if "SystemName" in entry:
            self.edr_client.update_star_system_if_obsolete(entry["SystemName"], entry.get("SystemAddress", None))
            # TODO progress not reflected from individual scans
            self.edr_client.reflect_fss_discovery_scan(entry)
            self.edr_client.system_value(entry["SystemName"])
        # Takes care of zero pop system with no signals (not even a nav beacon) and no fleet carrier
        self.edr_client.register_fss_signals(entry.get("SystemAddress", None), entry.get("SystemName", None), force_reporting=True)

    def _on_fss_all_bodies_found(self, entry, state):
        if "SystemName" in entry:
            self.ed_player.update_star_system_if_obsolete(entry["SystemName"], entry.get("SystemAddress", None))
            self.edr_client.reflect_fss_discovery_scan(entry)
            self.edr_client.system_value(entry["SystemName"])

    def _on_nav_beacon_scan(self, entry, state):
        if not entry.get("NumBodies", 0):
            return

        if "SystemAddress" in entry:
            self.ed_player.star_system_address = entry["SystemAddress"]
        self.edr_client.notify_with_details(_("System info acquired"), [_("Noteworthy material densities will be shown when approaching a planet.")])

    def _on_scan(self, entry, state):
        self.edr_client.process_scan(entry)
        if entry["ScanType"] in ["Detailed", "Basic"]: # removed AutoScan because spammy
            self.edr_client.noteworthy_about_scan(entry)

    def _on_touchdown(self, entry, state):
        # TODO take advantage of nearestdestination for the place, use that in the nav set blob too
        if entry.get("PlayerControlled", False) and entry.get("NearestDestination", False):
            depletables = EDRRawDepletables()
            depletables.visit(entry["NearestDestination"])

        body = entry.get("Body", "Unknown")
        self.ed_player.update_body_if_obsolete(body)
        self.ed_player.to_normal_space()
        if entry.get("PlayerControlled", False):
            self.ed_player.in_mothership()
    
    def _on_liftoff(self, entry, state):
        body = entry.get("Body", "Unknown")
        self.ed_player.update_body_if_obsolete(body)
        self.ed_player.to_normal_space()
        if entry.get("PlayerControlled", False):
            self.ed_player.in_mothership()

    def _on_ship_targeted(self, entry, state):
        if "ScanStage" in entry and entry["ScanStage"] > 0:
            handle_scan_events(ed_player, entry)
            handle_bounty_hunting_events(ed_player, entry)
        elif ("ScanStage" in entry and entry["ScanStage"] == 0) or ("TargetLocked" in entry and not entry["TargetLocked"]):
            self.ed_player.untarget()
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)

    def legacy_journal_entry(self, cmdr, is_beta, system, station, entry, state):
        status_outcome = {"updated": False, "reason": "Unspecified"}

        vehicle = None
        if ed_player.is_crew_member():
            vehicle = EDVehicleFactory.unknown_crew_vehicle()
        elif state.get("ShipType", None):
            vehicle = EDVehicleFactory.from_edmc_state(state)

        status_outcome["updated"] = ed_player.update_vehicle_if_obsolete(vehicle, piloted=False)
        status_outcome["updated"] |= self.edr_client.update_star_system_if_obsolete(system)
        
        if status_outcome["updated"]:
            edr_update_cmdr_status(ed_player, status_outcome["reason"], entry["timestamp"])
            if ed_player.in_a_crew():
                for member in ed_player.crew.members:
                    if member == ed_player.name:
                        continue
                    source = "Multicrew (captain)" if ed_player.is_captain(member) else "Multicrew (crew)"
                    crew_player = EDPlayer(member)
                    crew_player.mothership = vehicle
                    edr_submit_contact(crew_player, entry["timestamp"], source, ed_player)
        
        

    def _update_cmdr_status(self, reason_for_update, timestamp):
        """
        Send a status update for a given cmdr
        :param cmdr:
        :param reason_for_update:
        :return:
        """
        if self.ed_player.in_solo():
            EDR_LOG.error("Skipping cmdr update due to Solo mode")
            return

        if self.ed_player.has_partial_status():
            EDR_LOG.error("Skipping cmdr update due to partial status")
            return

        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        report = {
            "cmdr" : self.ed_player.name,
            "starSystem": self.ed_player.star_system,
            "place": self.ed_player.place,
            "timestamp": edt.as_js_epoch(),
            "source": reason_for_update,
            "reportedBy": self.ed_player.name,
            "mode": self.ed_player.game_mode,
            "dlc": self.ed_player.dlc_name,
            "group": self.ed_player.private_group
        }

        if self.ed_player.vehicle_type():
            report["ship"] = self.ed_player.vehicle_type()
        elif self.ed_player.spacesuit_type():
            report["suit"] = self.ed_player.spacesuit_type()

        EDR_LOG.debug("report: {}".format(report))

        if not self.edr_client.blip(self.ed_player.name, report):
            self.edr_client.status = _("blip failed.")
            return


    def edr_submit_crime(self, criminal_cmdrs, offence, victim, timestamp):
        """
        Send a crime/incident report
        :param criminal:
        :param offence:
        :param victim:
        :return:
        """
        #TODO sort out ship and suit...
        if not victim.in_open():
            EDR_LOG.info("Skipping submit crime due to unconfirmed Open mode")
            self.edr_client.status = _("Crime reporting disabled in solo/private modes.")
            return

        criminals = []
        for criminal_cmdr in criminal_cmdrs:
            EDR_LOG.debug(f"Appending criminal {criminal_cmdr.name} ",
                        f"with ship {criminal_cmdr.vehicle_type()}, ",
                        f"suit {criminal_cmdr.spacesuit_type()}")
            blob = {"name": criminal_cmdr.name, "enemy": criminal_cmdr.enemy, "wanted": criminal_cmdr.wanted, "bounty": criminal_cmdr.bounty, "fine": criminal_cmdr.fine}
            if criminal_cmdr.vehicle_type():
                blob["ship"] = criminal_cmdr.vehicle_type()
            elif criminal_cmdr.spacesuit_type():
                blob["suit"] = criminal_cmdr.spacesuit_type()
            blob["power"] = criminal_cmdr.powerplay.canonicalize() if criminal_cmdr.powerplay else ""
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
            "victimPower": victim.powerplay.canonicalize() if victim.powerplay else "",
            "byPledge": victim.powerplay.canonicalize() if victim.powerplay else "",
            "mode": victim.game_mode,
            "dlc": victim.dlc_name,
            "group": victim.private_group
        }

        if victim.vehicle_type():
            report["victimShip"] = victim.vehicle_type()
        elif victim.spacesuit_type():
            report["victimSuit"] = victim.spacesuit_type()

        if not self.edr_client.crime(victim.star_system, report):
            self.edr_client.status = _("failed to report crime.")
            self.edr_client.evict_system(victim.star_system)


    def edr_submit_crime_self(self, criminal_cmdr, offence, victim, timestamp):
        """
        Send a crime/incident report
        :param criminal_cmdr:
        :param offence:
        :param victim:
        :return:
        """
        if not criminal_cmdr.in_open():
            EDR_LOG.info("Skipping submit crime (self) due to unconfirmed Open mode")
            self.edr_client.status = _("Crime reporting disabled in solo/private modes.")
            return

        edt = EDTime()
        edt.from_journal_timestamp(timestamp)
        criminal_blob = {
            "name": criminal_cmdr.name,
            "wanted": criminal_cmdr.wanted,
            "bounty": criminal_cmdr.bounty,
            "fine": criminal_cmdr.fine,
            "power": criminal_cmdr.powerplay.canonicalize() if criminal_cmdr.powerplay else "",
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
            "victimPower": victim.powerplay.canonicalize() if victim.powerplay else "",
            "byPledge": victim.powerplay.canonicalize() if victim.powerplay else "",
            "mode": criminal_cmdr.game_mode,
            "dlc": criminal_cmdr.dlc_name,
            "group": criminal_cmdr.private_group
        }

        if victim.vehicle_type():
            report["victimShip"] = victim.vehicle_type()
        elif victim.spacesuit_type():
            report["victimSuit"] = victim.spacesuit_type()

        EDR_LOG.debug("Perpetrated crime: {}".format(report))

        if not self.edr_client.crime(criminal_cmdr.star_system, report):
            self.edr_client.status = _("failed to report crime.")
            self.edr_client.evict_system(criminal_cmdr.star_system)

    def report_fight(self, player):
        if not player.in_open():
            EDR_LOG.info("Skipping reporting fight due to unconfirmed Open mode")
            self.edr_client.status = _("Fight reporting disabled in solo/private modes.")
            return

        report = player.json(with_target=True)
        self.edr_client.fight(report)

    def edr_submit_contact(self, contact, timestamp, source, witness, system_wide=False):
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
            EDR_LOG.info("Skipping cmdr update due to partial status")
            return

        if not self.edr_client.blip(contact.name, report, system_wide):
            self.edr_client.status = _("failed to report contact.")
            
        edr_submit_traffic(contact, timestamp, source, witness, system_wide)

    def edr_submit_scan(self, scan, timestamp, source, witness):
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

        self.edr_client.scanned(scan["cmdr"], report)
            
    def edr_submit_traffic(self, contact, timestamp, source, witness, system_wide=False):
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
            EDR_LOG.info("Skipping submit traffic due to unconfirmed Open mode, and event not being system wide.")
            self.edr_client.status = _("Traffic reporting disabled in solo/private modes.")
            return

        if witness.has_partial_status():
            EDR_LOG.info("Skipping traffic update due to partial status")
            return

        # TODO opsec check
        if not self.edr_client.traffic(witness.star_system, report, system_wide):
            self.edr_client.status = _("failed to report traffic.")
            self.edr_client.evict_system(witness.star_system)

    def edr_submit_multicrew_session(self, player, report):
        if not player.in_open() and not player.destroyed:
            EDR_LOG.info("Skipping submit multicrew report: not in Open and not destroyed")
            self.edr_client.status = _("Multicrew reporting disabled in private mode.")
            return

        if not self.edr_client.crew_report(report):
            self.edr_client.status = _("failed to report multicrew session.")

    def _on_interdicted(self, entry, state):
        if entry["IsPlayer"]:
            interdictor = self.edr_client.player.instanced_player(entry["Interdictor"])
            self.edr_client.player.interdicted(interdictor, entry["event"] == "Interdicted")
            self.edr_submit_crime([interdictor], entry["event"], self.edr_client.player, entry["timestamp"])
        else:
            interdictor = self.edr_client.player.instanced_npc(entry.get("Interdictor", "[N/A]"))
            self.edr_client.player.interdicted(interdictor, entry["event"] == "Interdicted")

    def _on_escape_interdiction(self, entry, state):
        self._on_interdicted(entry, state)

    def _on_interdiction(self, entry, state):
        if entry["IsPlayer"]:
            offence = "Interdiction" if entry["Success"] else "Failed interdiction"
            interdicted = self.edr_client.player.instanced_player(entry["Interdicted"])
            self.edr_client.player.interdiction(interdicted, entry["Success"])
            self.edr_submit_crime_self(self.edr_client.player, offence, interdicted, entry["timestamp"])
        else:
            offence = "Interdiction" if entry["Success"] else "Failed interdiction"
            interdicted = self.edr_client.player.instanced_npc(entry.get("Interdicted", "[N/A]"))
            self.edr_client.player.interdiction(interdicted, entry["Success"])

    def _on_died(self, entry, state):
        if "Killers" in entry:
            criminal_cmdrs = []
            for killer in entry["Killers"]:
                if killer["Name"].startswith("Cmdr "):
                    criminal_cmdr = self.edr_client.player.instanced_player(killer["Name"][5:], ship_internal_name=killer["Ship"])
                    criminal_cmdrs.append(criminal_cmdr)
            self.edr_submit_crime(criminal_cmdrs, "Murder", self.edr_client.player, entry["timestamp"])
        elif "KillerName" in entry and entry["KillerName"].startswith("Cmdr "):
            criminal_cmdr = self.edr_client.player.instanced_player(entry["KillerName"][5:], ship_internal_name=entry["KillerShip"])
            self.edr_submit_crime([criminal_cmdr], "Murder", self.edr_client.player, entry["timestamp"])
        self.edr_client.player.killed()

    def _on_pvpkill(self, entry, state):
        EDR_LOG.info("PVPKill!")
        victim = self.edr_client.player.instanced_player(entry["Victim"])
        victim.killed()
        self.edr_submit_crime_self(self.edr_client.player, "Murder", victim, entry["timestamp"])
        self.edr_client.player.destroy(victim)

    def _on_crime_victim(self, entry, state):
        if "Offender" in entry and self.edr_client.player.name:
            irrelevant_pattern = re.compile(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$")
            wingmate = self.edr_client.player.is_wingmate(entry["Offender"])
            oneself = entry["Offender"].lower() == self.edr_client.player.name.lower()
            crewmate = self.edr_client.player.is_crewmate(entry["Offender"])
            instanced = self.edr_client.player.is_instanced_with_player(entry["Offender"])
            if not irrelevant_pattern.match(entry["Offender"]) and instanced and not oneself and not wingmate and not crewmate:
                offender = self.edr_client.player.instanced_player(entry["Offender"])
                if "Bounty" in entry:
                    offender.bounty += entry["Bounty"]
                if "Fine" in entry:
                    offender.fine += entry["Fine"]
                self.edr_submit_crime([offender], "{} (CrimeVictim)".format(entry["CrimeType"]), self.edr_client.player, entry["timestamp"])
            else:
                # TODO extract npc name, instance, etc.
                EDR_LOG.debug("Ignoring 'CrimeVictim' event: offender={}; instanced_with={}".format(entry["Offender"], self.edr_client.player.is_instanced_with_player(entry["Offender"])))

    def _on_commit_crime(self, entry, state):
        if "Victim" in entry and self.edr_client.player.name and (entry["Victim"].lower() != self.edr_client.player.name.lower()):
            irrelevant_pattern = re.compile(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$")
            if not irrelevant_pattern.match(entry["Victim"]) and self.edr_client.player.is_instanced_with_player(entry["Victim"]):
                victim = self.edr_client.player.instanced_player(entry["Victim"])
                if "Bounty" in entry:
                    self.ed_player.bounty += entry["Bounty"]
                if "Fine" in entry:
                    self.ed_player.fine += entry["Fine"]
                self.edr_submit_crime(self.ed_player, "{} (CommitCrime)".format(entry["CrimeType"]), victim, entry["timestamp"])
            else:
                # TODO extract npc name, instance, etc.
                EDR_LOG.debug("Ignoring 'CommitCrime' event: Victim={}; instanced_with={}".format(entry["Victim"], self.edr_client.player.is_instanced_with_player(entry["Victim"])))
    
    def _on_receive_text(self, entry, state):
        m = re.findall(r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+)", entry["Message"], flags=re.IGNORECASE)
        if m:
            self.edr_client.linkable_status(m[0])

        channel = entry.get("Channel", "N/A")
        if channel not in ["local", "player", "starsystem", "npc"]:
            return

        if channel == "local":
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            contact = player.instanced_player(from_cmdr)
            edr_submit_contact(contact, entry["timestamp"], "Received text (local)", player)
        elif channel == "player":
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            if self.ed_player.is_friend(from_cmdr) or player.is_wingmate(from_cmdr):
                EDR_LOG.debug(f"Text from {from_cmdr} friend / wing. Can't infer location")
            else:
                if self.ed_player.from_genesis:
                    EDR_LOG.debug(f"Text from {from_cmdr} (not friend/wing) == same location")
                    contact = self.ed_player.instanced_player(from_cmdr)
                    edr_submit_contact(contact, entry["timestamp"],
                                    "Received text (non wing/friend player)", self.ed_player)
                else:
                    EDR_LOG.debug(f"Received text from {from_cmdr}. Player not created from game start => can't infer location")
        elif channel == "starsystem":
            from_cmdr = entry["From"]
            if entry["From"].startswith("$cmdr_decorate:#name="):
                from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
            EDR_LOG.info("Text from {} in star system".format(from_cmdr))
            contact = EDPlayer(from_cmdr)
            contact.star_system = self.ed_player.star_system
            # TODO add blip to systemwideinstance ?
            edr_submit_contact(contact, entry["timestamp"],
                                "Received text (starsystem channel)", self.ed_player, system_wide = True)
        elif channel == "npc" and entry["From"] == "$CHAT_System;":
            emote_regex = r"^\$HumanoidEmote_TargetMessage:#player=\$cmdr_decorate:#name=(.+);:#targetedAction=\$HumanoidEmote_([a-zA-Z]+)_Action_Targeted;:#target=\$cmdr_decorate:#name=(.+);;$"
            m = re.match(emote_regex, entry.get("Message", ""))
            if m:
                action = m.group(2)
                receiving_party = m.group(3)
                EDR_LOG.info("Emote to {} (not friend/wing) == same location".format(receiving_party))
                contact = self.ed_player.instanced_player(receiving_party)
                edr_submit_contact(contact, entry["timestamp"], "Emote sent (non wing/friend player)", self.ed_player)
                if action in ["wave", "point"] and self.edr_client.gesture_triggers:
                    EDR_LOG.info("Implicit who emote-command for {}".format(receiving_party))
                    self.edr_client.who(receiving_party, autocreate=True)
            elif "$HumanoidEmote_TargetMessage:#player=$cmdr_decorate:#name=" in entry.get("Message", ""):
                # sometimes goes to the wing channel :/
                if not self.edr_client.pointing_guidance(entry):
                    self.edr_client.gesture(entry)
            elif "$HumanoidEmote_DefaultMessage:#player=$cmdr_decorate:#name=" in entry.get("Message", ""):
                self.edr_client.gesture(entry)


    def _on_hull_damage(self, entry, state):
        if entry.get("Fighter", False):
            if self.ed_player.slf:
                self.ed_player.slf.taking_hull_damage(entry["Health"] * 100.0) # HullDamage's Health is normalized to 0.0 ... 1.0
            else:
                EDR_LOG.warning("SLF taking hull damage but player has none...")
        else:
            self.ed_player.mothership.taking_hull_damage(entry["Health"] * 100.0)

    def _on_cockpit_breached(self, entry, state):
        self.ed_player.piloted_vehicle.cockpit_breached()

    def _on_shield_state(self, entry, state):
        if self.ed_player.piloted_vehicle:
            self.ed_player.piloted_vehicle.shield_state(entry["ShieldsUp"])
        else:
            # TODO on_foot case
            pass

    def _on_under_attack(self, entry, state):
        default = "SRV" # TODO to confirm but it seems to be the case
        self.ed_player.attacked(entry.get("Target", default))

    def _on_heat_damage(self, entry, state):
        if self.ed_player.piloted_vehicle:
            self.ed_player.piloted_vehicle.taking_heat_damage()

    def _on_srv_destroyed(self, entry, state):
        if self.ed_player.srv:
            self.ed_player.srv.destroy()
        else:
            EDR_LOG.warning("SRV got destroyed but player had none...")

    def _on_fighter_destroyed(self, entry, state):
        if self.ed_player.slf:
            self.ed_player.slf.destroy()
        else:
            EDR_LOG.warning("SLF got destroyed but player had none...")

    def _on_self_destruct(self, entry, state):
        if self.ed_player.piloted_vehicle:
            self.ed_player.piloted_vehicle.destroy() # TODO on foot case?
        else:
            EDR_LOG.warning("SelfDestruct but player had no vehicle...")

    def _on_fuel_scoop(self, entry, state):
        self.ed_player.mothership.fuel_scooping(entry["Total"])

    def _on_afmu_repairs(self, entry, state):
        self.ed_player.mothership.subsystem_health(entry["Module"], entry["Health"] * 100.0)

    def _on_refuel_all(self, entry, state):
        self.ed_player.mothership.refuel()

    def _on_refuel_partial(self, entry, state):
        self.ed_player.mothership.refuel(entry["Amount"])

    def _on_repair_all(self, entry, state):
        self.ed_player.mothership.repair()

    def _on_repair(self, entry, state):
        items = entry["Items"] if "Items" in entry else [entry["Item"]]
        for item in items:
            self.ed_player.mothership.repair(item)

    def _on_repair_drone(self, entry, state):
        if entry.get("HullRepaired", None):
            self.ed_player.mothership.hull_health = entry["HullRepaired"]
        if entry.get("CockpitRepaired", None):
            self.ed_player.mothership.cockpit_health(entry["CockpitRepaired"])

    def _on_reboot_repair(self, entry, state):
        # TODO not sure this exists and works
        self.ed_player.mothership.reboot_repair()

    def _on_mass_module_store(self, entry, state):
        for item in entry["Items"]:
            self.ed_player.mothership.remove_subsystem(item["Name"])

    def _on_module_store(self, entry, state):
        self.ed_player.mothership.remove_subsystem(entry["StoredItem"])
        if entry.get("ReplacementItem", None):
            self.ed_player.mothership.add_subsystem(entry["ReplacementItem"])

    def _on_module_sell(self, entry, state):
        self.ed_player.mothership.remove_subsystem(entry["SellItem"])

    def _on_module_buy(self, entry, state):
        if entry.get("StoredItem", None):
            self.ed_player.mothership.remove_subsystem(entry["StoredItem"])
        elif entry.get("SellItem", None):
            self.ed_player.mothership.remove_subsystem(entry["SellItem"])
        self.ed_player.mothership.add_subsystem(entry["BuyItem"])

    def _on_module_retrieve(self, entry, state):
        if entry.get("SwapOutItem", None):
            self.ed_player.mothership.remove_subsystem(entry["SwapOutItem"])
        self.ed_player.mothership.add_subsystem(entry["RetrievedItem"])

    def _on_pay_fines(self, entry, state):
        #TODO this should be on a ship whose id is in the entry rather than the player
        #TODO also use the Wanted flag on FSDJump, Docked + StationFaction, Location events and the status file's legalstate
        #TODO also use the "Hot" flag on Loadout event        
        if entry.get("AllFines", None):
            self.ed_player.paid_all_fines()
        else:
            self.ed_player.paid_fine(entry)

    def _on_pay_bounties(self, entry, state):
        #TODO this should be on a ship whose id is in the entry rather than the player
        #TODO also use the Wanted flag on FSDJump, Docked + StationFaction, Location events and the status file's legalstate
        #TODO also use the "Hot" flag on Loadout event        
        if entry.get("AllFines", None) or entry.get("AllBounties", None):
            self.ed_player.paid_all_bounties()
        else:
            self.ed_player.paid_bounty(entry)
            true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0)/100.0)
            self.ed_player.bounty = max(0, self.ed_player.bounty - true_amount)

    def handle_scan_events(self, entry):
        if not (entry["event"] == "ShipTargeted"):
            return False

        if not (entry["TargetLocked"]) or entry["ScanStage"] <= 0:
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)
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
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)
            return False
        
        target_name = entry.get("PilotName_Localised", entry["PilotName"])
        if prefix:
            target_name = entry["PilotName"][len(prefix):-1]
        
        if target_name == self.ed_player.name:
            # Happens when scanning one's unmanned ship, etc.
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)
            return False

        if self.ed_player.target_pilot() and target_name != self.ed_player.target_pilot().name:
            # clear previous guidance if any
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)

        target = None
        pilotrank = entry.get("PilotRank", "Unknown")
        if npc:
            target = self.ed_player.instanced_npc(target_name, rank=pilotrank, ship_internal_name=entry["Ship"], piloted=piloted)
        else:
            target = self.ed_player.instanced_player(target_name, rank=pilotrank, ship_internal_name=entry["Ship"], piloted=piloted)

        target.sqid = entry.get("SquadronID", None)
        nodotpower = entry["Power"].replace(".", "") if "Power" in entry else None
        target.pledged_to(nodotpower)
    
        if target.is_human():
            self.edr_submit_contact(target, entry["timestamp"], "Ship targeted", self.ed_player)

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
                scan["power"] = target.powerplay.canonicalize() if target.powerplay else ""
            elif not self.ed_player.is_independent():
                # Note: power is only present in shiptargeted events if the player is pledged
                # This means that we can only know that the target is independent if a player is pledged and the power attribute is missing
                scan["power"] = "independent"
        
            if target.is_human():
                self.edr_submit_scan(scan, entry["timestamp"], "Ship targeted [{}]".format(entry["LegalStatus"]), self.ed_player)

        self.ed_player.targeting(target, ship_internal_name=entry["Ship"])
        self.edr_client.target_guidance(entry)

        return True

    def _baseline_materials_events(self, entry, state):
        if entry["event"] in ["Materials", "ShipLockerMaterials"] or (entry["event"] == "ShipLocker" and len(entry.keys()) > 2) or (entry["event"] == "Backpack" and len(entry.keys()) > 2):
            self.ed_player.inventory.initialize(entry)

        # TODO auto eval of locker if on fleet carrier and shiplocker event kicks in, only if recently updated/different?
            
        if self.ed_player.inventory.stale_or_incorrect():
            self.ed_player.inventory.initialize_with_edmc(state)

    def _on_materials(self, entry, state):
        self._baseline_materials_events(entry, state)

    def _on_material_collected(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.collected(entry)

    def _on_materials_discarded(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.discarded(entry)

    def _on_engineer_contribution(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.donated_engineer(entry)

    def _on_scientific_research(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.donated_science(entry)

    def _on_engineer_craft(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.consumed(entry["Ingredients"])

    def _on_technology_broker(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.consumed(entry["Materials"])

    def _on_synthesis(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.consumed(entry["Materials"])

    def _on_material_trade(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.traded(entry)

    def _on_mission_completed(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.rewarded(entry)
        self.edr_client.eval_mission(entry)

    def _on_backpack_change(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.backpack_change(entry)
        if "Added" in entry:
            added = [self.ed_player.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if not(self.ed_player.engineers.is_useless(item["Name"]) or self.ed_player.engineers.is_unnecessary(item["Name"])) or "MissionID" in item]
            discardable = [self.ed_player.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if self.ed_player.engineers.is_useless(item["Name"]) and not self.ed_player.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
            unnecessary = [self.ed_player.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if self.ed_player.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
            details = [", ".join(added)]
            if discardable:
                details.append(_("Useless: {}").format(", ".join(discardable)))
            if unnecessary:
                details.append(_("Unnecessary: {}").format(", ".join(unnecessary)))
            self.edr_client.notify_with_details("Materials Info", details)
        elif "Removed" in entry:
            self.edr_client.eval_backpack(passive=True)

    def _on_sell_micro_resources(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.sold(entry)

    def _on_buy_micro_resources(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.bought(entry)

    def _on_transfer_micro_resources(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.bought(entry)
        self.edr_client.eval_backpack(passive=True)

    def _on_trade_micro_resources(self, entry, state):
        self._baseline_materials_events(entry, state)
        self.ed_player.inventory.traded(entry)
        self.edr_client.eval_locker(passive=True)

    def _on_send_text(self, entry, state):
        # Note: Channel can be missing... probably not safe to assume anything in that case
        # TODO npc instancing
        to_channel = entry.get("To", "")
        if not to_channel in ["local", "wing", "starsystem", "squadron", "squadleaders"]:            
            to_cmdr = to_channel
            if to_channel.startswith("$cmdr_decorate:#name="):
                to_cmdr = to_channel[len("$cmdr_decorate:#name="):-1]
            if self.ed_player.is_friend(to_cmdr) or self.ed_player.is_wingmate(to_cmdr):
                EDR_LOG.info("Sent text to {} friend/wing: can't infer location".format(to_cmdr))            
            else:
                if self.ed_player.from_genesis:
                    EDR_LOG.info(f"Sent text to {to_cmdr} (not friend/wing) == same location")
                    contact = self.ed_player.instanced_player(to_cmdr)
                    edr_submit_contact(contact, entry["timestamp"], "Sent text (non wing/friend player)",
                                    self.ed_player)
                else:
                    EDR_LOG.warning(f"Sent text to {to_cmdr}. Player not created from game start => can't infer location")

        m = re.findall(r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+)", entry["Message"], flags=re.IGNORECASE)
        if m:
            self.edr_client.linkable_status(m[0])

        self.edr_client.process_sent_message(entry)


    def _on_book_taxi(self, entry, state):
        self.ed_player.booked_shuttle(entry)

    def _on_book_dropship(self, entry, state):
        self.ed_player.booked_shuttle(entry)

    def _on_cancel_taxi(self, entry, state):
        self.ed_player.cancelled_shuttle(entry)

    def _on_cancel_dropship(self, entry, state):
        self.ed_player.cancelled_shuttle(entry)
    
    def _on_nav_route(self, entry, state):
        if state.get("NavRoute", None):
            self.edr_client.nav_route_set(state["NavRoute"])

    def _on_nav_route_clear(self, entry, state):
        self.edr_client.nav_route_clear()

    def _on_set_user_ship_name(self, entry, state):
        self.ed_player.fleet.rename(entry)
        self.ed_player.mothership.update_name(entry)
        self.last_known_ship_name = self.ed_player.mothership.name

    def _on_sell_ship_on_rebuy(self, entry, state):
        self.ed_player.fleet.sell(entry)

    def _on_shipyard_buy(self, entry, state):
        self.ed_player.fleet.buy(entry, self.ed_player.star_system, self.ed_player.mothership.name)

    def _on_shipyard_new(self, entry, state):
        self.ed_player.fleet.new(entry, self.ed_player.star_system)

    def _on_shipyard_sell(self, entry, state):
        self.ed_player.fleet.sell(entry)

    def _on_shipyard_transfer(self, entry, state):
        self.ed_player.fleet.transfer(entry, self.ed_player.star_system)

    def _on_shipyard_swap(self, entry, state):
        self.ed_player.fleet.swap(entry, self.ed_player.star_system, self.last_known_ship_name)
        self.last_known_ship_name = self.ed_player.mothership.name

    def _on_module_info(self, entry, state):
        self.ed_player.mothership.outfit_probably_changed(entry["timestamp"])

    def _on_eject_cargo(self, entry, state):
        self.ed_player.piloted_vehicle.cargo.eject(entry)

    def _on_collect_cargo(self, entry, state):
        self.ed_player.piloted_vehicle.cargo.collect(entry)

    def _on_mission_accepted(self, entry, state):
        self.edr_client.eval_mission(entry)

    def _on_wing_add(self, entry, state):
        wingmate = plain_cmdr_name(entry["Name"])
        self.ed_player.add_to_wing(wingmate)
        self.edr_client.status = _("added to wing: ").format(wingmate)
        EDR_LOG.info("Addition to wing: {}".format(self.ed_player.wing))
        self.edr_client.who(wingmate, autocreate=True)

    def _on_wing_join(self, entry, state):
        # TODO some inconsistency when other members leave the wing, and others come in...
        self.ed_player.join_wing(entry["Others"])
        self.edr_client.status = _("joined wing.")
        EDR_LOG.info("Joined a wing: {}".format(self.ed_player.wing))

    def _on_wing_leave(self, entry, state):
        self.ed_player.leave_wing()
        self.edr_client.status = _("left wing.")
        EDR_LOG.info(" Left the wing.")

    def _on_wing_invite(self, entry, state):
        requester = plain_cmdr_name(entry["Name"])
        self.edr_client.status = _("wing invite from: ").format(requester)
        EDR_LOG.info("Wing invite from: {}".format(requester))
        self.edr_client.who(requester, autocreate=True)

    def _on_crew_member_joins(self, entry, state):
        crew = plain_cmdr_name(entry["Crew"])
        success = self.ed_player.add_to_crew(crew)
        if success: # only show intel on the first add 
            self.edr_client.status = _(f"added to crew: {crew}")
            EDR_LOG.info(f"Addition to crew: {self.ed_player.crew.members}")
            self.edr_client.who(crew, autocreate=True)

    def _on_crew_member_role_change(self, entry, state):
        crew = plain_cmdr_name(entry["Crew"])
        success = self.ed_player.add_to_crew(crew)
        if success: # only show intel on the first add 
            self.edr_client.status = _(f"added to crew: {crew}")
            EDR_LOG.info(f"Addition to crew: {self.ed_player.crew.members}")
            self.edr_client.who(crew, autocreate=True)

    def _on_crew_launch_fighter(self, entry, state):
        crew = plain_cmdr_name(entry["Crew"])
        success = self.ed_player.add_to_crew(crew)
        if success: # only show intel on the first add 
            self.edr_client.status = _(f"added to crew: {crew}")
            EDR_LOG.info(f"Addition to crew: {self.ed_player.crew.members}")
            self.edr_client.who(crew, autocreate=True)

    def _on_crew_member_quits(self, entry, state):
        crew = plain_cmdr_name(entry["Crew"])
        duration = self.ed_player.crew_time_elapsed(crew)
        kicked = entry["event"] == "KickCrewMember"
        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        self.ed_player.remove_from_crew(crew)
        self.edr_client.status = _("{} left the crew.").format(crew)
        EDR_LOG.info("{} left the crew.".format(crew))
        edt = EDTime()
        edt.from_journal_timestamp(entry["timestamp"])
        report = {
            "captain": self.ed_player.crew.captain,
            "timestamp": edt.as_js_epoch(),
            "crew" : crew,
            "duration": duration,
            "kicked": kicked,
            "crimes": crimes,
            "destroyed":  self.ed_player.destroyed if self.ed_player.is_captain() else False
        }
        self.edr_submit_multicrew_session(self.ed_player, report)

    def _on_kick_crew_member(self, entry, state):
        crew = plain_cmdr_name(entry["Crew"])
        duration = self.ed_player.crew_time_elapsed(crew)
        kicked = entry["event"] == "KickCrewMember"
        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        self.ed_player.remove_from_crew(crew)
        self.edr_client.status = _("{} left the crew.").format(crew)
        EDR_LOG.info("{} left the crew.".format(crew))
        edt = EDTime()
        edt.from_journal_timestamp(entry["timestamp"])
        report = {
            "captain": self.ed_player.crew.captain,
            "timestamp": edt.as_js_epoch(),
            "crew" : crew,
            "duration": duration,
            "kicked": kicked,
            "crimes": crimes,
            "destroyed":  self.ed_player.destroyed if self.ed_player.is_captain() else False
        }
        self.edr_submit_multicrew_session(self.ed_player, report)

    def _on_join_a_crew(self, entry, state):
        captain = plain_cmdr_name(entry["Captain"])
        self.ed_player.join_crew(captain)
        self.edr_client.status = _("joined a crew.")
        EDR_LOG.info("Joined captain {}'s crew".format(captain))
        self.edr_client.who(captain, autocreate=True)

    def _on_quit_a_crew(self, entry, state):
        if not ed_player.crew:
            return

        for member in self.ed_player.crew.members:
            duration = self.ed_player.crew_time_elapsed(member)
            edt = EDTime()
            edt.from_journal_timestamp(entry["timestamp"])
            report = {
                "captain": self.ed_player.crew.captain,
                "timestamp": edt.as_js_epoch(),
                "crew" : member,
                "duration": duration,
                "kicked": False,
                "crimes": False,
                "destroyed": self.ed_player.destroyed if self.ed_player.is_captain() else False
            }    
            self.edr_submit_multicrew_session(self.ed_player, report)
        self.ed_player.leave_crew()
        self.edr_client.status = _("left crew.")
        EDR_LOG.info("Left the crew.")

    def _on_end_crew_session(self, entry, state):
        if  not self.ed_player.crew:
            return

        crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
        for member in self.ed_player.crew.members:
            duration = self.ed_player.crew_time_elapsed(member)
            edt = EDTime()
            edt.from_journal_timestamp(entry["timestamp"])
            report = {
                "captain": self.ed_player.crew.captain,
                "timestamp": edt.as_js_epoch(),
                "crew" : member,
                "duration": duration,
                "kicked": False,
                "crimes": crimes,
                "destroyed": self.ed_player.destroyed if self.ed_player.is_captain() else False
            }    
            self.edr_submit_multicrew_session(self.ed_player, report)
        self.ed_player.disband_crew()
        self.edr_client.status = _("crew disbanded.")
        EDR_LOG.info("Crew disbanded.")

    def _on_carrier_buy(self, entry, state):
        self.ed_player.fleet_carrier.bought(entry)

    def _on_carrier_stats(self, entry, state):
        self.ed_player.fleet_carrier.update_from_stats(entry)

    def _on_carrier_jump_requested(self, entry, state):
        self.edr_client.fc_jump_requested(entry)

    def _on_carrier_jump_cancelled(self, entry, state):
        self.edr_client.fc_jump_cancelled(entry)

    def _on_carrier_decommission(self, entry, state):
        self.ed_player.fleet_carrier.decommission_requested(entry)

    def _on_carrier_cancel_decommission(self, entry, state):
        self.ed_player.fleet_carrier.cancel_decommission(entry)

    def _on_carrier_docking_permission(self, entry, state):
        self.ed_player.fleet_carrier.update_docking_permissions(entry)

    def _on_carrier_trade_order(self, entry, state):
        self.edr_client.carrier_trade(entry)

    def _on_carrier_crew_services(self, entry, state):
        self.ed_player.fleet_carrier.tweak_crew_service(entry)

    def _on_fc_materials(self, entry, state):
        self.edr_client.fc_materials(entry)
        if not self.edr_client.eval_bar():
            self.edr_client.eval_bar(stock=False)
            
    def _on_fsd_jump(self, entry, state):
        self.ed_player.to_super_space()
        self.ed_player.wanted = entry.get("Wanted", False)
        
        place = "Supercruise" if entry["event"] == "FSDJump" else entry.get("StationName", "Unknown")
        self.ed_player.update_place_if_obsolete(place)
        self.ed_player.mothership.fuel_level = entry.get("FuelLevel", self.ed_player.mothership.fuel_level)
        self.ed_player.location.population = entry.get('Population', 0)
        self.ed_player.location.allegiance = entry.get('SystemAllegiance', 0)
        
        # UI Guidance
        self.edr_client.docking_guidance(entry)
        self.edr_client.noteworthy_about_system(entry)

    def _on_carrier_jump_requested(self, entry, state):
        self.edr_client.fc_jump_requested(entry)

    def _on_carrier_jump_cancelled(self, entry, state):
        self.edr_client.fc_jump_cancelled(entry)

    def _on_carrier_jump(self, entry, state):
        self.edr_client.fc_jumped(entry)

        place = entry.get("StationName", "Unknown")
        self.ed_player.update_place_if_obsolete(place)
        self.ed_player.wanted = entry.get("Wanted", False)
        self.ed_player.mothership.fuel_level = entry.get("FuelLevel", self.ed_player.mothership.fuel_level)
        self.ed_player.location.population = entry.get('Population', 0)
        self.ed_player.location.allegiance = entry.get('SystemAllegiance', 0)
        self.ed_player.to_normal_space()
        self.edr_client.docking_guidance(entry)
        self.edr_client.noteworthy_about_system(entry)

    def _on_supercruise_entry(self, entry, state):
        self.ed_player.to_super_space()

        if "SystemAddress" in entry:
            self.ed_player.star_system_address = entry["SystemAddress"]
        
        place = "Supercruise"
        self.ed_player.update_place_if_obsolete(place)
        self.edr_client.docking_guidance(entry)

    def _on_supercruise_exit(self, entry, state):
        self.ed_player.to_normal_space()

        body = entry.get("Body", "Unknown")
        self.ed_player.update_body_if_obsolete(body)
        self.ed_player.update_place_if_obsolete(body)
        
        if "SystemAddress" in entry:
            self.ed_player.star_system_address = entry["SystemAddress"]
        self.edr_client.register_fss_signals(entry.get("SystemAddress", None), entry.get("StarSystem", None))

    def _on_start_jump(self, entry, state):
        if  entry["JumpType"] != "Hyperspace":
            return

        self.ed_player.update_place_if_obsolete("Hyperspace")
        self.edr_client.hyperspace_jump(entry.get("StarSystem", None))
        self.edr_client.docking_guidance(entry)
        self.edr_client.check_system(entry["StarSystem"], may_create=True)
        self.edr_client.register_fss_signals()
        self.edr_client.edrfssinsights.reset(entry["timestamp"])

    def _on_approach_settlement(self, entry, state):
        place = entry["Name"]
        body = entry.get("BodyName", None)
        self.ed_player.update_place_if_obsolete(place)
        self.ed_player.update_body_if_obsolete(body)        
        
        self.edr_client.noteworthy_about_settlement(entry)

    def _on_approach_body(self, entry, state):
        body = entry.get("Body", "Unknown")
        self.ed_player.update_body_if_obsolete(body)
        self.ed_player.update_place_if_obsolete(body)
        
        noteworthy = self.edr_client.noteworthy_about_body(entry["StarSystem"], body)
        if noteworthy and self.ed_player.planetary_destination is None:
            poi = self.edr_client.closest_poi_on_body(entry["StarSystem"], body, self.ed_player.attitude)
            self.ed_player.planetary_destination = EDPlanetaryLocation(poi)

    def _on_leave_body(self, entry, state):
        body_name = entry.get("Body", None)
        star_system = entry.get("StarSystem", None)
        self.edr_client.leave_body(star_system, body_name)

    def handle_change_events(self, ed_player, entry):
        if entry["event"] in ["Touchdown", "Liftoff"]:
            body = entry.get("Body", "Unknown")
            outcome["updated"] |= ed_player.update_body_if_obsolete(body)
            ed_player.to_normal_space()
            if entry.get("PlayerControlled", False):
                ed_player.in_mothership()
                
            outcome["reason"] = "Touchdown/Liftoff events"
            EDR_LOG.info("Body changed: {}".format(body))

        ed_player.location.from_entry(entry)
        return outcome

    def _fc_position_related_events(self, entry):
        station_type = entry.get("StationType", None)
        if station_type and station_type != "FleetCarrier":
            return
        station_name = entry.get("StationName", None)
        market_id = entry.get("MarketID", 0)
        star_system = entry.get("StarSystem", self.ed_player.star_system)
        if not star_system:
            return
        self.ed_player.fleet_carrier.update_star_system_if_relevant(star_system, market_id, station_name)
        # TODO maybe update other things too, e.g. services?
        # { "timestamp":"2022-03-28T20:00:40Z", "event":"Location", "Docked":true, "StationName":"B6J-0HZ", "StationType":"FleetCarrier", "MarketID":3700480256, 
        # "StationServices":[ "dock", "autodock", "commodities", "contacts", "exploration", "outfitting", "crewlounge", "rearm", "refuel", "repair", "shipyard", "engineer", "flightcontroller", "stationoperations", "stationMenu", "carriermanagement", "carrierfuel", "livery", "voucherredemption", "socialspace", "bartender", "vistagenomics", "pioneersupplies" ], 
        # "Taxi":false, "Multicrew":false, "StarSystem":"Gurney Slade", "SystemAddress":182292842867, "StarPos":[70.21875,53.28125,81.00000], 
        # "SystemAllegiance":"Independent", "SystemEconomy":"$economy_Colony;", "SystemEconomy_Localised":"Colony", 
        # "SystemSecondEconomy":"$economy_Industrial;", "SystemSecondEconomy_Localised":"Industrial", "SystemGovernment":"$government_Democracy;", "SystemGovernment_Localised":"Democracy",
        #  "SystemSecurity":"$SYSTEM_SECURITY_low;", "SystemSecurity_Localised":"Low Security", "Population":66351, 
        # "Body":"Gurney Slade", "BodyID":0, "BodyType":"Star",
        #  "Powers":[ "Edmund Mahon" ], "PowerplayState":"Exploited", 
        # "Factions":[ { "Name":"Gurney Slade Republic Party", "FactionState":"None", "Government":"Democracy", "Influence":0.026000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Union of Jath for Equality", "FactionState":"War", "Government":"Democracy", "Influence":0.085000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000, "PendingStates":[ { "State":"Expansion", "Trend":0 } ], "ActiveStates":[ { "State":"War" } ] }, { "Name":"Partnership of Gurney Slade", "FactionState":"Bust", "Government":"Anarchy", "Influence":0.010000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000, "ActiveStates":[ { "State":"Bust" } ] }, { "Name":"Orrere Energy Company", "FactionState":"None", "Government":"Corporate", "Influence":0.146000, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Gurney Slade Dynasty", "FactionState":"War", "Government":"Feudal", "Influence":0.085000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000, "ActiveStates":[ { "State":"War" } ] }, { "Name":"Gurney Slade Blue General PLC", "FactionState":"Drought", "Government":"Corporate", "Influence":0.061000, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000, "ActiveStates":[ { "State":"Drought" } ] }, { "Name":"The Silverbacks", "FactionState":"CivilUnrest", "Government":"Democracy", "Influence":0.587000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000, "RecoveringStates":[ { "State":"PublicHoliday", "Trend":0 } ], "ActiveStates":[ { "State":"Boom" }, { "State":"CivilUnrest" } ] } ], "SystemFaction":{ "Name":"The Silverbacks", "FactionState":"CivilUnrest" }, "Conflicts":[ { "WarType":"war", "Status":"active", "Faction1":{ "Name":"Union of Jath for Equality", "Stake":"McCabe Cultivation Centre", "WonDays":1 }, "Faction2":{ "Name":"Gurney Slade Dynasty", "Stake":"Kopyl Metallurgic Installation", "WonDays":1 } } ] }

    def _on_location(self, entry, state):
        body = entry.get("Body", None)
        self.ed_player.update_body_if_obsolete(body)
        self.ed_player.update_place_if_obsolete(entry["Body"])
        EDR_LOG.info("Body changed: {} (location event)".format(body))
        self.ed_player.to_normal_space()
        self.ed_player.wanted = entry.get("Wanted", False)
        self.ed_player.location_security(entry.get("SystemSecurity", None))
        self.ed_player.location.population = entry.get("Population", None)
        self.ed_player.location.allegiance = entry.get("SystemAllegiance", None)
        if "StarSystem" in entry:
            self.edr_client.update_star_system_if_obsolete(entry["StarSystem"], entry.get("SystemAddress", None))
        
        if entry["Docked"]:
            place = entry["StationName"]
            self.ed_player.update_place_if_obsolete(place)
            EDR_LOG.info("Place changed: {} (location event)".format(place))
            self.edr_client.docked_at(entry)
        self.edr_client.process_location_event(entry)

        self._fc_position_related_events(entry)

    def _on_docking_related_events(self, entry, state):
        place = entry.get("StationName", "Unknown")
        self.ed_player.update_place_if_obsolete(place)
        self.ed_player.to_normal_space()
        self.edr_client.docking_guidance(entry)

    def _on_docked(self, entry, state):
        self._on_docking_related_events(entry, state)
        self.ed_player.docked_at(entry)
        self.ed_player.wanted = entry.get("Wanted", False)
        self.ed_player.mothership.update_cargo()
        if self.ed_player.mothership.could_use_limpets():
            limpets = self.ed_player.mothership.cargo.how_many("drones")
            capacity = self.ed_player.mothership.cargo_capacity
            self.edr_client.notify_with_details(_(U"Restock reminder"), [_("Don't forget to restock on limpets before heading out."), _("Limpets: {}/{}").format(limpets, capacity)])
    
        self._fc_position_related_events(entry)

    def _on_undocked(self, entry, state):
        self._on_docking_related_events(entry, state)
        self.edr_client.ack_station_pending_reports()
        self.ed_player.docked(False)
        self.ed_player.reset_stats()
        
        self._fc_position_related_events(entry)

    def _on_docking_cancelled(self, entry, state):
        self._on_docking_related_events(entry, state)
        self._fc_position_related_events(entry)

    def _on_docking_denied(self, entry, state):
        self._on_docking_related_events(entry, state)
        self._fc_position_related_events(entry)

    def _on_docking_granted(self, entry, state):
        self._on_docking_related_events(entry, state)
        self._fc_position_related_events(entry)

    def _on_docking_requested(self, entry, state):
        self._on_docking_related_events(entry, state)
        self._fc_position_related_events(entry)

    def _on_docking_timeout(self, entry, state):
        self._on_docking_related_events(entry, state)
        self._fc_position_related_events(entry)

    def _on_music(self, entry, state):
        # TODO another map to shed the ifs
        if entry["MusicTrack"] in ["Supercruise", "NoTrack"]:
            # music event happens after the chain of FSS signals discovered events on a jump
            # TODO wrong system...
            self.edr_client.register_fss_signals()
            return

        if entry["MusicTrack"] == "MainMenu" and not self.ed_player.is_crew_member():
            # Checking for 'is_crew_member' because "MainMenu" shows up when joining a multicrew session
            # Assumption: being a crew member while main menu happens means that a multicrew session is about to start.
            # { "timestamp":"2018-06-19T13:06:04Z", "event":"QuitACrew", "Captain":"Dummy" }
            # { "timestamp":"2018-06-19T13:06:16Z", "event":"Music", "MusicTrack":"MainMenu" }
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            self.edr_client.game_mode(None)
            self.ed_player.leave_wing()
            self.ed_player.leave_crew()
            self.ed_player.leave_vehicle()
            self.ed_player.in_game = False
            EDR_LOG.debug("Player is on the main menu.")
            return
        
        self.ed_player.in_game = True
        if entry["MusicTrack"] == "Combat_Dogfight":
            if self.ed_player.mothership:
                self.ed_player.mothership.skirmish() # TODO check music event for on foot combat
            return
        
        if entry["MusicTrack"] == "Combat_LargeDogFight":
            if self.ed_player.mothership:
                self.ed_player.mothership.battle()  # TODO check music event for on foot combat
            return
        
        if entry["MusicTrack"] == "Combat_SRV":
            if self.ed_player.srv:
                self.ed_player.srv.skirmish()
            return
        
        if entry["MusicTrack"] in ["Supercruise", "Exploration", "NoTrack"] and self.ed_player.in_a_fight():
            self.ed_player.in_danger(False)
            return
        
        if entry["MusicTrack"] == "SystemMap":
            self.edr_client.noteworthy_signals_in_system()
            return
        
        if entry["MusicTrack"] == "OnFoot":
            self.ed_player.in_spacesuit()
            return
        
        if entry["MusicTrack"] == "FleetCarrier_Managment":
            # typo intentional
            self.edr_client.fleet_carrier_update()

    def _on_shutdown(self, entry, state):
        EDR_LOG.info("Shutting down in-game features...")
        self.edr_client.edrfssinsights.reset()
        self.edr_client.shutdown()

    def _on_resurrect(self, entry, state):
        self.edr_client.clear()
        self.edr_client.edrfssinsights.reset()
        self.ed_player.resurrect(entry["Option"] in ["rebuy", "recover"])
        EDR_LOG.debug("Player has been resurrected.")

    def _on_fileheader(self, entry, state):
        if  entry["part"] != 1:
            return

        self.edr_client.clear()
        self.edr_client.edrfssinsights.reset()
        self.ed_player.inception(genesis=True)
        self.edr_client.status = _("initialized.")
        EDR_LOG.debug("Journal player got created: accurate picture of friends/wings.")

    def _on_load_game(self, entry, state):
        from_genesis = False
        
        if self.first_run:
            self.first_run = False
            # TODO update this now that we are passing the parameters
            from_genesis = (cmdr and system is None and station is None)

        if self.ed_player.inventory.stale_or_incorrect():
            self.ed_player.inventory.initialize_with_edmc(state)
        self.edr_client.clear()
        self.edr_client.edrfssinsights.reset()
        self.ed_player.inception(genesis=from_genesis)
        if from_genesis:
            EDR_LOG.debug("Heuristics genesis: probably accurate picture of friends/wings.")
        if entry.get("Odyssey", False):
            self.edr_client.set_dlc("Odyssey")
            EDR_LOG.debug("DLC is Odyssey")
        elif entry.get("Horizons", False):
            self.edr_client.set_dlc("Horizons")
            EDR_LOG.debug("DLC is Horizons")
        
        self.edr_client.game_mode(entry["GameMode"], entry.get("Group", None))
            
        self.ed_player.update_vehicle_or_suit_if_obsolete(entry)
        EDR_LOG.debug("Game mode is {}".format(entry["GameMode"]))
        self.edr_client.warmup()
            
    def _on_loadout(self, entry, state):
        EDR_LOG.debug(f"Loadout event {entry}")
        # Sometimes it's not a ship but the spacesuit, maybe the srv too :/
        if self.ed_player.mothership.id == entry.get("ShipID", -1):
            EDR_LOG.debug(f"updating current vehicle {ed_player.mothership.type}")
            self.ed_player.mothership.update_from_loadout(entry)
            self.ed_player.mothership.update_cargo()
            if self.ed_player.mothership.could_use_limpets() and self.ed_player.is_docked:
                limpets = self.ed_player.mothership.cargo.how_many("drones")
                capacity = self.ed_player.mothership.cargo_capacity
                self.edr_client.notify_with_details(_(U"Restock reminder"), [_("Don't forget to restock on limpets before heading out."), _("Limpets: {}/{}").format(limpets, capacity)])
            self.last_known_ship_name = self.ed_player.mothership.name
            EDR_LOG.debug(f"new current vehicle {self.ed_player.mothership.name}")
        else:
            updated = ed_player.update_vehicle_if_obsolete(EDVehicleFactory.from_load_game_event(entry), piloted=True)
            EDR_LOG.debug(f"udpate current vehicle if obsolete: {updated}, {self.ed_player.mothership.type}")
    
    def _on_suit_loadout(self, entry, state):
        EDR_LOG.debug(f"Suit loadout event {entry}")
        self.ed_player.update_suit_if_obsolete(entry)

    def _on_switch_suit_loadout(self, entry, state):
        EDR_LOG.debug(f"Switch suit loadout event {entry}")
        self.ed_player.update_suit_if_obsolete(entry)

    def _on_launch_srv(self, entry, state):
        if not entry.get("PlayerControlled", False):
            return

        EDR_LOG.debug(f"Launch SRV event {entry}")
        self.ed_player.in_srv()
    
    def _on_dock_srv(self, entry, state):
        EDR_LOG.debug(f"Dock SRV event {entry}")
        self.ed_player.in_mothership()

    def _on_disembark(self, entry, state):
        EDR_LOG.debug(f"Disembark event {entry}")
        self.ed_player.disembark(entry)

    def _on_embark(self, entry, state):
        EDR_LOG.debug(f"Embark event {entry}")
        self.ed_player.embark(entry)

    def _on_dropship_deploy(self, entry, state):
        EDR_LOG.debug(f"Dropship deploy event {entry}")
        self.ed_player.dropship_deployed(entry)

    def _on_friends(self, entry, state):
        if entry["Status"] == "Requested":
            requester = plain_cmdr_name(entry["Name"])
            self.edr_client.who(requester, autocreate=True)
        elif entry["Status"] == "Offline":
            self.ed_player.deinstanced_player(entry["Name"])

    def _on_engineer_progress(self, entry, state):
        self.ed_player.engineers.update(entry)

    def _on_powerplay(self, entry, state):
        EDR_LOG.debug("Initial powerplay event: {}".format(entry))
        self.edr_client.pledged_to(entry["Power"], entry["TimePledged"])

    def _on_powerplay_defect(self, entry, state):
        self.edr_client.pledged_to(entry["ToPower"])

    def _on_powerplay_join(self, entry, state):
        self.edr_client.pledged_to(entry["Power"])

    def _on_powerplay_leave(self, entry, state):
        self.edr_client.pledged_to(None)        

    def _on_mining_refined(self, entry, state):
        self.ed_player.refined(entry)
        self.edr_client.mining_guidance()

    def _on_prospected_asteroid(self, entry, state):
        self.ed_player.prospected(entry)
        self.edr_client.mining_guidance()

    def _on_bounty(self, entry, state):
        if not entry.get("Rewards", False):
            return

        self.ed_player.bounty_awarded(entry)
        self.edr_client.bounty_hunting_guidance()

    def _on_ship_targeted(self, entry, state):
        if entry["TargetLocked"] and entry["ScanStage"] >= 3 and entry.get("Bounty", 0) > 0:
            self.ed_player.bounty_scanned(entry)
            self.edr_client.bounty_hunting_guidance()
        else:
            self.edr_client.bounty_hunting_guidance(turn_off=True)