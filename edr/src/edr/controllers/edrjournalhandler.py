from edr.core.edrlog import EDR_LOG
from edr.core.edrconfig import EDR_CONFIG
from edr.core.edrplayer import EDRPlayer
from edr.core.edrvehicle import EDVehicleFactory
from edr.core.edrrawdepletables import EDRRawDepletables
from edr.core.edrutils import _

class EDRJournalHandler:
    def __init__(self, edr_client):
        self.edr_client = edr_client
        self.last_known_ship_name = ""

    def journal_entry(self, cmdr, is_beta, system, station, entry, state):
        self.edr_client.edrdiscord.process(entry)

        if entry["event"] in ["Shutdown", "ShutDown", "Music", "Resurrect", "Fileheader", "LoadGame", "Loadout", "SuitLoadout", "SwitchSuitLoadout", "LaunchSRV", "DockSRV", "Disembark", "Embark", "DropShipDeploy"]:
            from_genesis = False
            if "first_run" not in journal_entry.__dict__:
                journal_entry.first_run = False
                from_genesis = (entry["event"] == "LoadGame") and (cmdr and system is None and station is None)
            handle_lifecycle_events(ed_player, entry, state, from_genesis)

        if entry["event"] in ["BookTaxi", "BookDropship", "CancelTaxi", "CancelDropship"]:
            handle_shuttle_events(entry)
        
        if entry["event"] in ["NavRoute", "NavRouteClear"]:
            handle_nav_route_events(entry, state)

        if entry["event"] in ["SetUserShipName", "SellShipOnRebuy", "ShipyardBuy", "ShipyardNew", "ShipyardSell", "ShipyardTransfer", "ShipyardSwap"]:
            handle_fleet_events(entry)

        if entry["event"] in ["ModuleInfo"]:
            handle_modules_events(ed_player, entry)

        if entry["event"] in ["Cargo"]:
            ed_player.piloted_vehicle.update_cargo()

        if entry["event"] in ["EjectCargo", "CollectCargo"]:
            handle_cargo_events(ed_player, entry)

        
        if entry["event"].startswith("Powerplay"):
            EDR_LOG.info("Powerplay event: {}".format(entry))
            handle_powerplay_events(ed_player, entry)
        
        if entry["event"] == "Statistics" and not ed_player.powerplay:
            # There should be a Powerplay event before the Statistics event
            # if not then the player is not pledged and we should reflect that on the server
            self.edr_client.pledged_to(None)

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

        if entry["event"] in ["CarrierJump", "CarrierBuy", "CarrierStats", "CarrierJumpRequest", "CarrierJumpCancelled", "CarrierDecommission", "CarrierCancelDecommission", "CarrierDockingPermission", "CarrierTradeOrder", "FCMaterials"]:
            handle_carrier_events(ed_player, entry)

        status_outcome = {"updated": False, "reason": "Unspecified"}

        vehicle = None
        if ed_player.is_crew_member():
            vehicle = EDVehicleFactory.unknown_crew_vehicle()
        elif state.get("ShipType", None):
            vehicle = EDVehicleFactory.from_edmc_state(state)

        status_outcome["updated"] = ed_player.update_vehicle_if_obsolete(vehicle, piloted=False)
        status_outcome["updated"] |= self.edr_client.update_star_system_if_obsolete(system)
            
        if entry["event"] in ["Location", "Undocked", "Docked", "DockingCancelled", "DockingDenied",
                            "DockingGranted", "DockingRequested", "DockingTimeout", "Touchdown", "Liftoff"]:
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
        
        # TODO take advantage of nearestdestination for the place, use that in the nav set blob too
        if entry["event"] == "Touchdown" and entry.get("PlayerControlled", None) and entry.get("NearestDestination", None):
            depletables = EDRRawDepletables()
            depletables.visit(entry["NearestDestination"])
            
        if entry["event"] == "SAAScanComplete":
            self.edr_client.saa_scan_complete(entry)
        
        if entry["event"] in ["SAASignalsFound", "FSSBodySignals"]:
            self.edr_client.body_signals_found(entry)
        
        if entry["event"] in ["FSSSignalDiscovered"]:
            self.edr_client.noteworthy_about_signal(entry)

        if entry["event"] in ["FSSDiscoveryScan"]:
            if "SystemName" in entry:
                self.edr_client.update_star_system_if_obsolete(entry["SystemName"], entry.get("SystemAddress", None))
                # TODO progress not reflected from individual scans
                self.edr_client.reflect_fss_discovery_scan(entry)
                self.edr_client.system_value(entry["SystemName"])
            self.edr_client.register_fss_signals(entry.get("SystemAddress", None), entry.get("SystemName", None), force_reporting=True) # Takes care of zero pop system with no signals (not even a nav beacon) and no fleet carrier

        if entry["event"] in ["FSSAllBodiesFound"]:
            if "SystemName" in entry:
                ed_player.update_star_system_if_obsolete(entry["SystemName"], entry.get("SystemAddress", None))
                self.edr_client.reflect_fss_discovery_scan(entry)
                self.edr_client.system_value(entry["SystemName"])

        if entry["event"] in ["NavBeaconScan"] and entry.get("NumBodies", 0):
            if "SystemAddress" in entry:
                ed_player.star_system_address = entry["SystemAddress"]
            self.edr_client.notify_with_details(_("System info acquired"), [_("Noteworthy material densities will be shown when approaching a planet.")])

        if entry["event"] in ["Scan", "ScanOrganic"]:
            self.edr_client.process_scan(entry)
            if entry["ScanType"] in ["Detailed", "Basic"]: # removed AutoScan because spammy
                self.edr_client.noteworthy_about_scan(entry)


        if entry["event"] == "CodexEntry":
            self.edr_client.process_codex_entry(entry)
            
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
                self.edr_client.target_guidance(entry, turn_off=True)
                self.edr_client.bounty_hunting_guidance(turn_off=True)
        
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

        if entry["event"] == "MissionAccepted":
            handle_mission_events(ed_player, entry)

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
        
        if ed_player.maybe_in_a_pvp_fight():
            report_fight(ed_player)

    def edr_update_cmdr_status(self, cmdr, reason_for_update, timestamp):
        """
        Send a status update for a given cmdr
        :param cmdr:
        :param reason_for_update:
        :return:
        """
        if cmdr.in_solo():
            EDR_LOG.error("Skipping cmdr update due to Solo mode")
            return

        if cmdr.has_partial_status():
            EDR_LOG.error("Skipping cmdr update due to partial status")
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

        EDR_LOG.debug("report: {}".format(report))

        if not self.edr_client.blip(cmdr.name, report):
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

    def report_crime(self, cmdr, entry):
        """
        Report a crime to the server
        :param cmdr:
        :param entry:
        :return:
        """
        # TODO opsec check

        player_one = self.edr_client.player
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
            EDR_LOG.info("PVPKill!")
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
                edr_submit_crime([offender], "{} (CrimeVictim)".format(entry["CrimeType"]), cmdr, entry["timestamp"])
            else:
                # TODO extract npc name, instance, etc.
                EDR_LOG.debug("Ignoring 'CrimeVictim' event: offender={}; instanced_with={}".format(entry["Offender"], player_one.is_instanced_with_player(entry["Offender"])))
        elif entry["event"] == "CommitCrime" and "Victim" in entry and player_one.name and (entry["Victim"].lower() != player_one.name.lower()):
            irrelevant_pattern = re.compile(r"^(\$([A-Za-z0-9]+_)+[A-Za-z0-9]+;)$")
            if not irrelevant_pattern.match(entry["Victim"]) and player_one.is_instanced_with_player(entry["Victim"]):
                victim = player_one.instanced_player(entry["Victim"])
                if "Bounty" in entry:
                    player_one.bounty += entry["Bounty"]
                if "Fine" in entry:
                    player_one.fine += entry["Fine"]
                edr_submit_crime_self(player_one, "{} (CommitCrime)".format(entry["CrimeType"]), victim, entry["timestamp"])
            else:
                # TODO extract npc name, instance, etc.
                EDR_LOG.debug("Ignoring 'CommitCrime' event: Victim={}; instanced_with={}".format(entry["Victim"], player_one.is_instanced_with_player(entry["Victim"])))


    def report_comms(self, player, entry):
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
                    EDR_LOG.debug(f"Text from {from_cmdr} friend / wing. Can't infer location")
                else:
                    if player.from_genesis:
                        EDR_LOG.debug(f"Text from {from_cmdr} (not friend/wing) == same location")
                        contact = player.instanced_player(from_cmdr)
                        edr_submit_contact(contact, entry["timestamp"],
                                        "Received text (non wing/friend player)", player)
                    else:
                        EDR_LOG.debug(f"Received text from {from_cmdr}. Player not created from game start => can't infer location")
            elif entry["Channel"] in ["starsystem"]:
                from_cmdr = entry["From"]
                if entry["From"].startswith("$cmdr_decorate:#name="):
                    from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
                EDR_LOG.info("Text from {} in star system".format(from_cmdr))
                contact = EDPlayer(from_cmdr)
                contact.star_system = player.star_system
                # TODO add blip to systemwideinstance ?
                edr_submit_contact(contact, entry["timestamp"],
                                    "Received text (starsystem channel)", player, system_wide = True)
            elif entry["Channel"] in ["npc"] and entry["From"] == "$CHAT_System;":
                emote_regex = r"^\$HumanoidEmote_TargetMessage:#player=\$cmdr_decorate:#name=(.+);:#targetedAction=\$HumanoidEmote_([a-zA-Z]+)_Action_Targeted;:#target=\$cmdr_decorate:#name=(.+);;$"
                m = re.match(emote_regex, entry.get("Message", ""))
                if m:
                    action = m.group(2)
                    receiving_party = m.group(3)
                    EDR_LOG.info("Emote to {} (not friend/wing) == same location".format(receiving_party))
                    contact = player.instanced_player(receiving_party)
                    edr_submit_contact(contact, entry["timestamp"], "Emote sent (non wing/friend player)", player)
                    if action in ["wave", "point"] and self.edr_client.gesture_triggers:
                        EDR_LOG.info("Implicit who emote-command for {}".format(receiving_party))
                        self.edr_client.who(receiving_party, autocreate=True)
                elif "$HumanoidEmote_TargetMessage:#player=$cmdr_decorate:#name=" in entry.get("Message", ""):
                    # sometimes goes to the wing channel :/
                    if not self.edr_client.pointing_guidance(entry):
                        self.edr_client.gesture(entry)
                elif "$HumanoidEmote_DefaultMessage:#player=$cmdr_decorate:#name=" in entry.get("Message", ""):
                    self.edr_client.gesture(entry)
        elif entry["event"] == "SendText" and not entry["To"] in ["local", "wing", "starsystem", "squadron", "squadleaders"]:
            to_cmdr = entry["To"]
            if entry["To"].startswith("$cmdr_decorate:#name="):
                to_cmdr = entry["To"][len("$cmdr_decorate:#name="):-1]
            if player.is_friend(to_cmdr) or player.is_wingmate(to_cmdr):
                EDR_LOG.info("Sent text to {} friend/wing: can't infer location".format(to_cmdr))            
            else:
                if player.from_genesis:
                    EDR_LOG.info(f"Sent text to {to_cmdr} (not friend/wing) == same location")
                    contact = player.instanced_player(to_cmdr)
                    edr_submit_contact(contact, entry["timestamp"], "Sent text (non wing/friend player)",
                                    player)
                else:
                    EDR_LOG.warning(f"Sent text to {to_cmdr}. Player not created from game start => can't infer location")

        m = re.findall(r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+)", entry["Message"], flags=re.IGNORECASE)
        if m:
            self.edr_client.linkable_status(m[0])

    def handle_damage_events(self, ed_player, entry):
        if not entry["event"] in ["HullDamage", "UnderAttack", "SRVDestroyed", "FighterDestroyed", "HeatDamage", "ShieldState", "CockpitBreached", "SelfDestruct"]:
            return False

        if entry["event"] == "HullDamage":
            if entry.get("Fighter", False):
                if ed_player.slf:
                    ed_player.slf.taking_hull_damage(entry["Health"] * 100.0) # HullDamage's Health is normalized to 0.0 ... 1.0
                else:
                    EDR_LOG.warning("SLF taking hull damage but player has none...")
            else:
                # TODO this could be the SRV too...
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
            default = "SRV" # TODO to confirm but it seems to be the case
            ed_player.attacked(entry.get("Target", default))
        elif entry["event"] == "HeatDamage" and ed_player.piloted_vehicle:
            ed_player.piloted_vehicle.taking_heat_damage()
        elif entry["event"] == "SRVDestroyed":
            if ed_player.srv:
                ed_player.srv.destroy()
            else:
                EDR_LOG.warning("SRV got destroyed but player had none...")
        elif entry["event"] == "FighterDestroyed":
            if ed_player.slf:
                ed_player.slf.destroy()
            else:
                EDR_LOG.warning("SLF got destroyed but player had none...")
        elif entry["event"] == "SelfDestruct" and ed_player.piloted_vehicle:
            ed_player.piloted_vehicle.destroy() # TODO on foot case?
        else:
            return False
        return True

    def handle_fixing_events(self, ed_player, entry):
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

    def handle_outfitting_events(self, player, entry):
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

    def handle_legal_fees(self, player, entry):
        if entry["event"] not in ["PayFines", "PayBounties"]:
            return False
        
        #TODO this should be on a ship whose id is in the entry rather than the player
        #TODO also use the Wanted flag on FSDJump, Docked + StationFaction, Location events and the status file's legalstate
        #TODO also use the "Hot" flag on Loadout event
        if entry["event"] == "PayFines":
            if entry.get("AllFines", None):
                player.paid_all_fines()
            else:
                player.paid_fine(entry)
        elif entry["event"] == "PayBounties":
            if entry.get("AllFines", None):
                player.paid_all_bounties()
            else:
                player.paid_bounty(entry)
                true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0)/100.0)
                player.bounty = max(0, player.bounty - true_amount)

    def handle_scan_events(player, entry):
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
        
        if target_name == player.name:
            # Happens when scanning one's unmanned ship, etc.
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)
            return False

        if player.target_pilot() and target_name != player.target_pilot().name:
            # clear previous guidance if any
            self.edr_client.target_guidance(entry, turn_off=True)
            self.edr_client.bounty_hunting_guidance(turn_off=True)

        target = None
        pilotrank = entry.get("PilotRank", "Unknown")
        if npc:
            target = player.instanced_npc(target_name, rank=pilotrank, ship_internal_name=entry["Ship"], piloted=piloted)
        else:
            target = player.instanced_player(target_name, rank=pilotrank, ship_internal_name=entry["Ship"], piloted=piloted)

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
                scan["power"] = target.powerplay.canonicalize() if target.powerplay else ""
            elif not player.is_independent():
                # Note: power is only present in shiptargeted events if the player is pledged
                # This means that we can only know that the target is independent if a player is pledged and the power attribute is missing
                scan["power"] = "independent"
        
            if target.is_human():
                edr_submit_scan(scan, entry["timestamp"], "Ship targeted [{}]".format(entry["LegalStatus"]), player)

        player.targeting(target, ship_internal_name=entry["Ship"])
        self.edr_client.target_guidance(entry)

        return True

    def handle_material_events(self, cmdr, entry, state):
        if entry["event"] in ["Materials", "ShipLockerMaterials"] or (entry["event"] == "ShipLocker" and len(entry.keys()) > 2) or (entry["event"] == "Backpack" and len(entry.keys()) > 2):
            cmdr.inventory.initialize(entry)

        # TODO auto eval of locker if on fleet carrier and shiplocker event kicks in, only if recently updated/different?
            
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
            self.edr_client.eval_mission(entry)
        elif entry["event"] == "BackpackChange":
            cmdr.inventory.backpack_change(entry)
            if "Added" in entry:
                added = [cmdr.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if not(cmdr.engineers.is_useless(item["Name"]) or cmdr.engineers.is_unnecessary(item["Name"])) or "MissionID" in item]
                discardable = [cmdr.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if cmdr.engineers.is_useless(item["Name"]) and not cmdr.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
                unnecessary = [cmdr.inventory.oneliner(item["Name"], from_backpack=True) for item in entry["Added"] if cmdr.engineers.is_unnecessary(item["Name"]) and "MissionID" not in item]
                details = [", ".join(added)]
                if discardable:
                    details.append(_("Useless: {}").format(", ".join(discardable)))
                if unnecessary:
                    details.append(_("Unnecessary: {}").format(", ".join(unnecessary)))
                self.edr_client.notify_with_details("Materials Info", details)
            elif "Removed" in entry:
                self.edr_client.eval_backpack(passive=True)
        elif entry["event"] == "SellMicroResources":
            cmdr.inventory.sold(entry)
            self.edr_client.eval_locker(passive=True)
        elif entry["event"] == "BuyMicroResources":
            cmdr.inventory.bought(entry)
        elif entry["event"] == "TransferMicroResources":
            cmdr.inventory.bought(entry)
            self.edr_client.eval_backpack(passive=True)
        elif entry["event"] == "TradeMicroResources":
            cmdr.inventory.traded(entry)
            self.edr_client.eval_locker(passive=True)

    def handle_commands(self, cmdr, entry):
        if not entry["event"] == "SendText":
            return

        return self.edr_client.process_sent_message(entry)
        
    def handle_shuttle_events(self, entry):
        if entry["event"]  not in ["BookTaxi", "BookDropship", "CancelTaxi", "CancelDropship"]:
            return
        ed_player = self.edr_client.player
        if entry["event"] in ["BookTaxi", "BookDropship"]:
            ed_player.booked_shuttle(entry)
        elif entry["event"] in ["CancelTaxi", "CancelDropship"]:
            ed_player.cancelled_shuttle(entry)

    def handle_nav_route_events(self, entry, state):
        if entry["event"] not in ["NavRoute", "NavRouteClear"]:
            return
        
        if entry["event"] == "NavRouteClear":
            self.edr_client.nav_route_clear()
        elif entry["event"] == "NavRoute" and state.get("NavRoute", None):
            self.edr_client.nav_route_set(state["NavRoute"])


    def handle_fleet_events(self, entry):
        if entry["event"] not in ["SetUserShipName", "SellShipOnRebuy", "ShipyardBuy", "ShipyardNew", "ShipyardSell", "ShipyardTransfer", "ShipyardSwap"]:
            return
        ed_player = self.edr_client.player
        if entry["event"] == "SetUserShipName":
            ed_player.fleet.rename(entry)
            ed_player.mothership.update_name(entry)
            self.last_known_ship_name = ed_player.mothership.name
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
            ed_player.fleet.swap(entry, ed_player.star_system, self.last_known_ship_name)
            self.last_known_ship_name = ed_player.mothership.name

    def handle_modules_events(self, ed_player, entry):
        if entry["event"] == "ModuleInfo":
            EDR_LOG.debug("ModuleInfo event")
            ed_player.mothership.outfit_probably_changed(entry["timestamp"])

    def handle_cargo_events(self, ed_player, entry):
        if entry["event"] == "EjectCargo":
            ed_player.piloted_vehicle.cargo.eject(entry)
        elif entry["event"] == "CollectCargo":
            ed_player.piloted_vehicle.cargo.collect(entry)

    def handle_mission_events(self, ed_player, entry):
        if entry["event"] == "MissionAccepted":
            self.edr_client.eval_mission(entry)

    
    def plain_cmdr_name(self, journal_cmdr_name):
        if journal_cmdr_name.startswith("$cmdr_decorate:#name="):
                return journal_cmdr_name[len("$cmdr_decorate:#name="):-1]
        return journal_cmdr_name

    def handle_wing_events(self, ed_player, entry):
        if entry["event"] in ["WingAdd"]:
            wingmate = plain_cmdr_name(entry["Name"])
            ed_player.add_to_wing(wingmate)
            self.edr_client.status = _("added to wing: ").format(wingmate)
            EDR_LOG.info("Addition to wing: {}".format(ed_player.wing))
            self.edr_client.who(wingmate, autocreate=True)
        elif entry["event"] in ["WingJoin"]:
            # TODO some inconsistency when other members leave the wing, and others come in...
            ed_player.join_wing(entry["Others"])
            self.edr_client.status = _("joined wing.")
            EDR_LOG.info("Joined a wing: {}".format(ed_player.wing))
        elif entry["event"] in ["WingLeave"]:
            ed_player.leave_wing()
            self.edr_client.status = _("left wing.")
            EDR_LOG.info(" Left the wing.")
        elif entry["event"] in ["WingInvite"]:
            requester = plain_cmdr_name(entry["Name"])
            self.edr_client.status = _("wing invite from: ").format(requester)
            EDR_LOG.info("Wing invite from: {}".format(requester))
            self.edr_client.who(requester, autocreate=True)


    def handle_multicrew_events(self, ed_player, entry):
        if entry["event"] in ["CrewMemberJoins", "CrewMemberRoleChange", "CrewLaunchFighter"]:
            crew = plain_cmdr_name(entry["Crew"])
            success = ed_player.add_to_crew(crew)
            if success: # only show intel on the first add 
                self.edr_client.status = _("added to crew: ").format(crew)
                EDR_LOG.info("Addition to crew: {}".format(ed_player.crew.members))
                self.edr_client.who(crew, autocreate=True)

        if entry["event"] in ["CrewMemberQuits", "KickCrewMember"]:
            crew = plain_cmdr_name(entry["Crew"])
            duration = ed_player.crew_time_elapsed(crew)
            kicked = entry["event"] == "KickCrewMember"
            crimes = False if not "OnCrimes" in entry else entry["OnCrimes"]
            ed_player.remove_from_crew(crew)
            self.edr_client.status = _("{} left the crew.").format(crew)
            EDR_LOG.info("{} left the crew.".format(crew))
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
            self.edr_client.status = _("joined a crew.")
            EDR_LOG.info("Joined captain {}'s crew".format(captain))
            self.edr_client.who(captain, autocreate=True)

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
            self.edr_client.status = _("left crew.")
            EDR_LOG.info("Left the crew.")

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
            self.edr_client.status = _("crew disbanded.")
            EDR_LOG.info("Crew disbanded.")

    def handle_carrier_events(self, ed_player, entry):
        if entry["event"] == "CarrierBuy":
            ed_player.fleet_carrier.bought(entry)
        elif entry["event"] == "CarrierStats":
            ed_player.fleet_carrier.update_from_stats(entry)
        elif entry["event"] == "CarrierJumpRequest":
            self.edr_client.fc_jump_requested(entry)
        elif entry["event"] == "CarrierJumpCancelled":
            self.edr_client.fc_jump_cancelled(entry)
        elif entry["event"] == "CarrierDecomission":
            ed_player.fleet_carrier.decommission_requested(entry)
        elif entry["event"] == "CarrierCancelDecommission":
            ed_player.fleet_carrier.cancel_decommission(entry)
        elif entry["event"] == "CarrierDockingPermission":
            ed_player.fleet_carrier.update_docking_permissions(entry)
        elif entry["event"] == "CarrierJump":
            self.edr_client.fc_jumped(entry)
        elif entry["event"] == "CarrierTradeOrder":
            self.edr_client.carrier_trade(entry)
        elif entry["event"] == "CarrierCrewServices":
            ed_player.fleet_carrier.tweak_crew_service(entry)
        elif entry["event"] == "FCMaterials":
            self.edr_client.fc_materials(entry)
            if not self.edr_client.eval_bar():
                self.edr_client.eval_bar(stock=False)
            

    def handle_movement_events(self, ed_player, entry):
        outcome = {"updated": False, "reason": None}
        place = "Unknown"

        if entry["event"] in ["SupercruiseExit"]:
            body = entry["Body"]
            outcome["updated"] |= ed_player.update_body_if_obsolete(body)
            outcome["updated"] |= ed_player.update_place_if_obsolete(body)
            outcome["reason"] = "Supercruise exit"
            ed_player.to_normal_space()
            if "SystemAddress" in entry:
                ed_player.star_system_address = entry["SystemAddress"]
            self.edr_client.register_fss_signals(entry.get("SystemAddress", None), entry.get("StarSystem", None))
            # TODO probably should be cleared to avoid keeping old FC around?
            EDR_LOG.info("Body changed: {}".format(body))
        elif entry["event"] in ["FSDJump", "CarrierJump"]:
            place = "Supercruise" if entry["event"] == "FSDJump" else entry.get("StationName", "Unknown")
            outcome["updated"] |= ed_player.update_place_if_obsolete(place)
            ed_player.wanted = entry.get("Wanted", False)
            ed_player.mothership.fuel_level = entry.get("FuelLevel", ed_player.mothership.fuel_level)
            ed_player.location.population = entry.get('Population', 0)
            ed_player.location.allegiance = entry.get('SystemAllegiance', 0)
            outcome["reason"] = entry["event"]
            if entry["event"] == "FSDJump":
                ed_player.to_super_space()
            else:
                ed_player.to_normal_space()
            EDR_LOG.info("Place changed: {}".format(place))
            self.edr_client.docking_guidance(entry)
            self.edr_client.noteworthy_about_system(entry)
        elif entry["event"] in ["SupercruiseEntry"]:
            if "SystemAddress" in entry:
                ed_player.star_system_address = entry["SystemAddress"]
            place = "Supercruise"
            outcome["updated"] |= ed_player.update_place_if_obsolete(place)
            outcome["reason"] = "Jump events"
            ed_player.to_super_space()
            self.edr_client.docking_guidance(entry)
            EDR_LOG.info("Place changed: {}".format(place))
        elif entry["event"] == "StartJump" and entry["JumpType"] == "Hyperspace":
            place = "Hyperspace"
            outcome["updated"] |= ed_player.update_place_if_obsolete(place)
            outcome["reason"] = "Hyperspace"
            self.edr_client.hyperspace_jump(entry.get("StarSystem", None))
            EDR_LOG.info("Place changed: {}".format(place))
            self.edr_client.docking_guidance(entry)
            self.edr_client.check_system(entry["StarSystem"], may_create=True)
            self.edr_client.register_fss_signals()
            self.edr_client.edrfssinsights.reset(entry["timestamp"])
        elif entry["event"] in ["ApproachSettlement"]:
            place = entry["Name"]
            body = entry.get("BodyName", None)
            outcome["updated"] |= ed_player.update_place_if_obsolete(place)
            outcome["updated"] |= ed_player.update_body_if_obsolete(body)        
            EDR_LOG.info("Place/Body changed: {}, {}".format(place, body))
            outcome["reason"] = "Approach event"
            self.edr_client.noteworthy_about_settlement(entry)
        elif entry["event"] in ["ApproachBody"]:
            body = entry["Body"]
            outcome["updated"] |= ed_player.update_body_if_obsolete(body)
            outcome["updated"] |= ed_player.update_place_if_obsolete(body)
            EDR_LOG.info("Body & place changed: {}".format(body))
            outcome["reason"] = "Approach event"
            if self.edr_client.noteworthy_about_body(entry["StarSystem"], entry["Body"]) and ed_player.planetary_destination is None:
                poi = self.edr_client.closest_poi_on_body(entry["StarSystem"], entry["Body"], ed_player.attitude)
                ed_player.planetary_destination = EDPlanetaryLocation(poi)
        
        ed_player.location.from_entry(entry)
        
        if entry["event"] in ["LeaveBody"]:
            body_name = entry.get("Body", None)
            star_system = entry.get("StarSystem", None)
            outcome["updated"] |= self.edr_client.leave_body(star_system, body_name)
            EDR_LOG.info("Place changed: Supercruise, body cleared")
            outcome["reason"] = "Leave event"

        return outcome

    def handle_change_events(self, ed_player, entry):
        outcome = {"updated": False, "reason": None}
        if entry["event"] in ["Location"]:
            body = entry.get("Body", None)
            outcome["updated"] |= ed_player.update_body_if_obsolete(body)
            outcome["updated"] |= ed_player.update_place_if_obsolete(entry["Body"])
            EDR_LOG.info("Body changed: {} (location event)".format(body))
            ed_player.to_normal_space()
            ed_player.wanted = entry.get("Wanted", False)
            ed_player.location_security(entry.get("SystemSecurity", None))
            ed_player.location.population = entry.get("Population", None)
            ed_player.location.allegiance = entry.get("SystemAllegiance", None)
            if "StarSystem" in entry:
                self.edr_client.update_star_system_if_obsolete(entry["StarSystem"], entry.get("SystemAddress", None))
            
            if entry["Docked"]:
                place = entry["StationName"]
                outcome["updated"] |= ed_player.update_place_if_obsolete(place)
                EDR_LOG.info("Place changed: {} (location event)".format(place))
                self.edr_client.docked_at(entry)
            self.edr_client.process_location_event(entry)
            outcome["reason"] = "Location event"

        if entry["event"] in ["Undocked", "Docked", "DockingCancelled", "DockingDenied",
                            "DockingGranted", "DockingRequested", "DockingTimeout"]:
            place = entry.get("StationName", "Unknown")
            outcome["updated"] |= ed_player.update_place_if_obsolete(place)
            ed_player.to_normal_space()
            self.edr_client.docking_guidance(entry)
            if entry["event"] == "Docked":
                ed_player.docked_at(entry)
                ed_player.wanted = entry.get("Wanted", False)
                ed_player.mothership.update_cargo()
                if ed_player.mothership.could_use_limpets():
                    limpets = ed_player.mothership.cargo.how_many("drones")
                    capacity = ed_player.mothership.cargo_capacity
                    self.edr_client.notify_with_details(_(U"Restock reminder"), [_("Don't forget to restock on limpets before heading out."), _("Limpets: {}/{}").format(limpets, capacity)])
            elif entry["event"] == "Undocked":
                self.edr_client.ack_station_pending_reports()
                ed_player.docked(False)
                ed_player.reset_stats()
            outcome["reason"] = "Docking events"
            EDR_LOG.info("Place changed: {}".format(place))
        
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

    def handle_fc_position_related_events(self, ed_player, entry):
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

    def handle_lifecycle_events(self, ed_player, entry, state, from_genesis=False):
        if entry["event"] == "Music":
            if entry["MusicTrack"] in ["Supercruise", "NoTrack"]:
                # music event happens after the chain of FSS signals discovered events on a jump
                # TODO wrong system...
                self.edr_client.register_fss_signals()

            if entry["MusicTrack"] == "MainMenu" and not ed_player.is_crew_member():
                # Checking for 'is_crew_member' because "MainMenu" shows up when joining a multicrew session
                # Assumption: being a crew member while main menu happens means that a multicrew session is about to start.
                # { "timestamp":"2018-06-19T13:06:04Z", "event":"QuitACrew", "Captain":"Dummy" }
                # { "timestamp":"2018-06-19T13:06:16Z", "event":"Music", "MusicTrack":"MainMenu" }
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
                self.edr_client.noteworthy_signals_in_system()
                return
            elif entry["MusicTrack"] == "OnFoot":
                ed_player.in_spacesuit()
                return
            elif entry["MusicTrack"] == "FleetCarrier_Managment":
                # typo intentional
                self.edr_client.fleet_carrier_update()


        if entry["event"] == "Shutdown":
            EDR_LOG.info("Shutting down in-game features...")
            self.edr_client.edrfssinsights.reset()
            self.edr_client.shutdown()
            return

        if entry["event"] == "Resurrect":
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            ed_player.resurrect(entry["Option"] in ["rebuy", "recover"])
            EDR_LOG.debug("Player has been resurrected.")
            return

        if entry["event"] in ["Fileheader"] and entry["part"] == 1:
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            ed_player.inception(genesis=True)
            self.edr_client.status = _("initialized.")
            EDR_LOG.debug("Journal player got created: accurate picture of friends/wings.")
            return

        if entry["event"] in ["LoadGame"]:
            if ed_player.inventory.stale_or_incorrect():
                ed_player.inventory.initialize_with_edmc(state)
            self.edr_client.clear()
            self.edr_client.edrfssinsights.reset()
            ed_player.inception(genesis=from_genesis)
            if from_genesis:
                EDR_LOG.debug("Heuristics genesis: probably accurate picture of friends/wings.")
            if entry.get("Odyssey", False):
                self.edr_client.set_dlc("Odyssey")
                EDR_LOG.debug("DLC is Odyssey")
            elif entry.get("Horizons", False):
                self.edr_client.set_dlc("Horizons")
                EDR_LOG.debug("DLC is Horizons")
            self.edr_client.game_mode(entry["GameMode"], entry.get("Group", None))
            
            ed_player.update_vehicle_or_suit_if_obsolete(entry)
            EDR_LOG.debug("Game mode is {}".format(entry["GameMode"]))
            self.edr_client.warmup()
            return

        if entry["event"] in ["Loadout"]:
            EDR_LOG.debug(f"Loadout event {entry}")
            # Sometimes it's not a ship but the spacesuit, maybe the srv too :/
            if ed_player.mothership.id == entry.get("ShipID", -1):
                EDR_LOG.debug(f"updating current vehicle {ed_player.mothership.type}")
                ed_player.mothership.update_from_loadout(entry)
                ed_player.mothership.update_cargo()
                if ed_player.mothership.could_use_limpets() and ed_player.is_docked:
                    limpets = ed_player.mothership.cargo.how_many("drones")
                    capacity = ed_player.mothership.cargo_capacity
                    self.edr_client.notify_with_details(_(U"Restock reminder"), [_("Don't forget to restock on limpets before heading out."), _("Limpets: {}/{}").format(limpets, capacity)])
                self.last_known_ship_name = ed_player.mothership.name
                EDR_LOG.debug(f"new current vehicle {ed_player.mothership.name}")
            else:
                updated = ed_player.update_vehicle_if_obsolete(EDVehicleFactory.from_load_game_event(entry), piloted=True)
                EDR_LOG.debug(f"udpate current vehicle if obsolete: {updated}, {ed_player.mothership.type}")
            return

        if entry["event"] in ["SuitLoadout", "SwitchSuitLoadout"]:
            ed_player.update_suit_if_obsolete(entry)
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

    def handle_friends_events(self, ed_player, entry):
        if entry["event"] != "Friends":
            return

        if entry["Status"] == "Requested":
            requester = plain_cmdr_name(entry["Name"])
            self.edr_client.who(requester, autocreate=True)
        elif entry["Status"] == "Offline":
            ed_player.deinstanced_player(entry["Name"])

    def handle_engineer_progress(self, ed_player, entry):
        if entry["event"] != "EngineerProgress":
            return
        ed_player.engineers.update(entry)

    def handle_powerplay_events(self, ed_player, entry):
        if entry["event"] == "Powerplay":
            EDR_LOG.debug("Initial powerplay event: {}".format(entry))
            self.edr_client.pledged_to(entry["Power"], entry["TimePledged"])
        elif entry["event"] == "PowerplayDefect":
            self.edr_client.pledged_to(entry["ToPower"])
        elif entry["event"] == "PowerplayJoin":
            self.edr_client.pledged_to(entry["Power"])
        elif entry["event"] == "PowerplayLeave":
            self.edr_client.pledged_to(None)        

    def handle_mining_events(self, ed_player, entry):
        if entry["event"] not in ["MiningRefined", "ProspectedAsteroid"]:
            return
        if entry["event"] == "ProspectedAsteroid":
            ed_player.prospected(entry)
        elif entry["event"] == "MiningRefined":
            ed_player.refined(entry)
        self.edr_client.mining_guidance()

    def handle_bounty_hunting_events(self, ed_player, entry):
        if entry["event"] not in ["Bounty", "ShipTargeted"]:
            return
        if entry["event"] == "Bounty" and entry.get("Rewards", None):
            ed_player.bounty_awarded(entry)
            self.edr_client.bounty_hunting_guidance()
        elif entry["event"] == "ShipTargeted":
            if entry["TargetLocked"] and entry["ScanStage"] >= 3 and entry.get("Bounty", 0) > 0:
                ed_player.bounty_scanned(entry)
                self.edr_client.bounty_hunting_guidance()
            else:
                self.edr_client.bounty_hunting_guidance(turn_off=True) 
