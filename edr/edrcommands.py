from edrlog import EDR_LOG
import random
import codecs

from edri18n import _


class EDRCommands(object):
    
    OVERLAY_DUMMY_COUNTER = 0

    def __init__(self, edr_client):
        self.edr_client = edr_client

    def process(self, text, recipient=None):
        command_parts = text.split(" ", 1)
        command = command_parts[0].lower()
        if not command:
            return False
        
        cmdr = self.edr_client.player
        if recipient is None:
            target = cmdr.target_pilot()
            recipient = target.name if target and target.is_human() else None

        if command[0] == "!":
            return self.handle_bang_commands(cmdr, command, command_parts)
        elif command[0] == "?":
            return self.handle_query_commands(cmdr, command, command_parts)
        elif command[0] == "#":
            return self.handle_hash_commands(command, command_parts, recipient)
        elif command[0] == "-":
            return self.handle_minus_commands(command, command_parts, recipient)
        elif command[0] == "@":
            return self.handle_at_commands(text, recipient)
        elif command == "o7":
            if recipient and not recipient in ["local", "voicechat", "wing", "friend", "starsystem", "squadron", "squadleaders"]:
                EDR_LOG.log(u"Implicit who command for {}".format(recipient), "INFO")
                to_cmdr = recipient
                if recipient.startswith("$cmdr_decorate:#name="):
                    to_cmdr = recipient[len("$cmdr_decorate:#name="):-1]
                return self.edr_client.who(to_cmdr, autocreate=True)
        return False

    def handle_bang_commands(self, cmdr, command, command_parts):
        if command == "!overlay":
            self.overlay_command("" if len(command_parts) == 1 else command_parts[1])
        elif command == "!audiocue" and len(command_parts) == 2:
            self.audiocue_command(command_parts[1])
        elif command in ["!who", "!w"]:
            target_cmdr = None
            if len(command_parts) == 2:
                target_cmdr = command_parts[1]
            else:
                target = self.edr_client.player.target_pilot()
                target_cmdr = target.name if target and target.is_human() else None
            if target_cmdr:
                EDR_LOG.log(u"Explicit who command for {}".format(target_cmdr), "INFO")
                self.edr_client.who(target_cmdr)
        elif command == "!crimes":
            self.crimes_command("" if len(command_parts) == 1 else command_parts[1])
        elif command == "!sitrep":
            system = cmdr.star_system if len(command_parts) == 1 else command_parts[1]
            EDR_LOG.log(u"Sitrep command for {}".format(system), "INFO")
            self.edr_client.check_system(system)
        elif command == "!sitreps":
            EDR_LOG.log(u"Sitreps command", "INFO")
            self.edr_client.sitreps()
        elif command == "!signals":
            EDR_LOG.log(u"Signals command", "INFO")
            self.edr_client.noteworthy_signals_in_system()
        elif command == "!notams":
            EDR_LOG.log(u"Notams command", "INFO")
            self.edr_client.notams()
        elif command == "!notam":
            system = cmdr.star_system if len(command_parts) == 1 else command_parts[1]
            EDR_LOG.log(u"Notam command for {}".format(system), "INFO")
            self.edr_client.notam(system)
        elif command == "!outlaws":
            EDR_LOG.log(u"Outlaws command", "INFO")
            self.edr_client.outlaws()
        elif command == "!enemies":
            EDR_LOG.log(u"Enemies command", "INFO")
            self.edr_client.enemies()
        elif command == "!where":
            target_cmdr = None
            if len(command_parts) == 2:
                target_cmdr = command_parts[1]
            else:
                target = self.edr_client.player.target_pilot()
                target_cmdr = target.name if target and target.is_human() else None
            if target_cmdr:
                EDR_LOG.log(u"Explicit where command for {}".format(target_cmdr), "INFO")
                self.edr_client.where(target_cmdr)
        elif command == "!search":
            resource = None
            system = cmdr.star_system
            if len(command_parts) == 2:
                better_parts = command_parts[1].split("@", 1)
                if len(better_parts) == 2:
                    system = better_parts[1].lstrip()
                resource = better_parts[0].rstrip()
            if resource:
                EDR_LOG.log(u"Search command for {}".format(resource), "INFO")
                self.edr_client.search(resource, system)
        elif command in ["!distance", "!d"] and len(command_parts) >= 2:
            EDR_LOG.log(u"Distance command", "INFO")
            systems = " ".join(command_parts[1:]).split(" > ", 1)
            if not systems:
                EDR_LOG.log(u"Aborting distance calculation (no params).", "DEBUG")
                return False
            from_sys = systems[0] if len(systems) == 2 else cmdr.star_system
            to_sys = systems[1] if len(systems) == 2 else systems[0]
            EDR_LOG.log(u"Distance command from {} to {}".format(from_sys, to_sys), "INFO")
            self.edr_client.distance(from_sys, to_sys)
        elif command == "!if":
            EDR_LOG.log(u"Interstellar Factors command", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.interstellar_factors_near(search_center, override_sc_dist)
        elif command == "!raw":
            EDR_LOG.log(u"Raw Material Trader command", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.raw_material_trader_near(search_center, override_sc_dist)
        elif command in ["!encoded", "!enc"]:
            EDR_LOG.log(u"Encoded Material Trader command", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.encoded_material_trader_near(search_center, override_sc_dist)
        elif command in ["!manufactured", "!man"]:
            EDR_LOG.log(u"Manufactured Material Trader command", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.manufactured_material_trader_near(search_center, override_sc_dist)
        elif command == "!staging":
            EDR_LOG.log(u"Looking for a staging station", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.staging_station_near(search_center, override_sc_dist)
        elif command == "!fc":
            if len(command_parts) < 2:
                return False
            callsign_or_name = " ".join(command_parts[1:]).upper()
            EDR_LOG.log(u"Looking for a Fleet Carrier in current system with {} in callsign or name".format(callsign_or_name), "INFO")
            self.edr_client.fc_in_current_system(callsign_or_name)
        elif command == "!station":
            if len(command_parts) < 2:
                return False
            station_name = " ".join(command_parts[1:]).upper()
            EDR_LOG.log(u"Looking for a Station in current system with {} in its name".format(station_name), "INFO")
            self.edr_client.station_in_current_system(station_name)
        elif command == "!rrrfc":
            EDR_LOG.log(u"Looking for a RRR Fleet Carrier", "INFO")
            search_center = cmdr.star_system
            override_radius = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_radius = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.rrr_fc_near(search_center, override_radius)
        elif command == "!rrr":
            EDR_LOG.log(u"Looking for a RRR Station", "INFO")
            search_center = cmdr.star_system
            override_radius = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_radius = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.rrr_near(search_center, override_radius)
        elif command == "!parking":
            search_center = cmdr.star_system
            override_rank = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("#", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_rank = int(parameters[1]) if len(parameters) > 1 else None
            EDR_LOG.log(u"Looking for a system to park a fleet carrier near {}".format(search_center), "INFO")
            self.edr_client.parking_system_near(search_center, override_rank)
        elif command in ["!htb", "!humantechbroker"]:
            EDR_LOG.log(u"Looking for a human tech broker", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.human_tech_broker_near(search_center, override_sc_dist)
        elif command in ["!gtb", "!guardiantechbroker"]:
            EDR_LOG.log(u"Looking for a guardian tech broker", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.guardian_tech_broker_near(search_center, override_sc_dist)
        elif command in ["!offbeat"]:
            EDR_LOG.log(u"Looking for an offbeat station", "INFO")
            search_center = cmdr.star_system
            override_sc_dist = None
            if len(command_parts) >= 2:
                parameters = [param.strip() for param in " ".join(command_parts[1:]).split("< ", 1)]
                search_center = parameters[0] or cmdr.star_system
                override_sc_dist = int(parameters[1]) if len(parameters) > 1 else None
            self.edr_client.offbeat_station_near(search_center, override_sc_dist)
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
                EDR_LOG.log(u"EDR Central for {} with {} not allowed (enough fuel)".format(service, message), "INFO")
                self.edr_client.notify_with_details("EDR Central", [_(u"Call rejected: you seem to have enough fuel."), _("Contact Cmdr LeKeno if this is inaccurate")])
                return False
            if service == "repair" and not cmdr.heavily_damaged():
                EDR_LOG.log(u"EDR Central for {} with {} not allowed (no serious damage)".format(service, message), "INFO")
                self.edr_client.notify_with_details("EDR Central", [_(u"Call rejected: you seem to have enough hull left."), _("Contact Cmdr LeKeno if this is inaccurate")])
                return False
            info = self.edr_client.player.json(fuel_info=(service == "fuel"))
            info["message"] = message
            EDR_LOG.log(u"Message to EDR Central for {} with {}".format(service, message), "INFO")
            self.edr_client.call_central(service, info)
        elif command == "!nav":
            if len(command_parts) < 2:
                EDR_LOG.log(u"Not enough parameters for navigation command", "INFO")
                return False
            if command_parts[1].lower() == "off":
                EDR_LOG.log(u"Clearing destination", "INFO")
                self.edr_client.player.planetary_destination = None
            elif command_parts[1].lower() == "set" and self.edr_client.player.attitude.valid():
                EDR_LOG.log(u"Setting destination", "INFO")
                attitude = self.edr_client.player.attitude
                name = command_parts[2:].lower() if len(command_parts) > 2 else "Navpoint"
                self.edr_client.navigation(attitude.latitude, attitude.longitude, name)
            elif command_parts[1].lower() == "next":
                EDR_LOG.log(u"Next custom POI", "INFO")
                self.edr_client.player.planetary_destination = None
                self.edr_client.next_custom_poi()
            elif command_parts[1].lower() == "previous":
                EDR_LOG.log(u"Previous custom POI", "INFO")
                self.edr_client.player.planetary_destination = None
                self.edr_client.previous_custom_poi()
            elif command_parts[1].lower() == "clear":
                EDR_LOG.log(u"Clearing POI", "INFO")
                self.edr_client.player.planetary_destination = None
                self.edr_client.clear_current_custom_poi()
            elif command_parts[1].lower() == "reset":
                EDR_LOG.log(u"Reset POIs", "INFO")
                self.edr_client.player.planetary_destination = None
                self.edr_client.reset_custom_pois()
            else:
                lat_long = command_parts[1].split(" ")
                if len(lat_long) != 2:
                    EDR_LOG.log(u"Invalid parameters for navigation command", "INFO")
                    return False
                try:
                    EDR_LOG.log(u"Navigation command", "INFO")
                    self.edr_client.navigation(float(lat_long[0]), float(lat_long[1]))
                except:
                    EDR_LOG.log(u"Couldn't convert parameters for navigation command to lat/long", "INFO")
                    return False
        elif command == "!ship" and len(command_parts) == 2:
            name_or_type = command_parts[1]
            EDR_LOG.log(u"Ship search command for {}".format(name_or_type), "INFO")
            self.edr_client.where_ship(name_or_type)
        elif command == "!eval" and len(command_parts) == 2:
            eval_type = command_parts[1]
            EDR_LOG.log(u"Eval command for {}".format(eval_type), "INFO")
            self.edr_client.eval(eval_type)
        elif command == "!contracts" and len(command_parts) == 1:
            EDR_LOG.log(u"Contracts command", "INFO")
            self.edr_client.contracts()
        elif command == "!contract":
            target_cmdr = cmdr.target
            reward = None
            if len(command_parts) >= 2:
                parts = [p.strip() for p in filter(len, " ".join(command_parts[1:]).split("$$$ ", 1))]
                target_cmdr = parts[0]
                if len(parts)>=2:
                    reward = int(parts[1])
            EDR_LOG.log(u"Contract command on {} with reward of {}".format(target_cmdr, reward), "INFO")
            if reward is None:
                self.edr_client.contract(target_cmdr)
            else:
                self.edr_client.contract_on(target_cmdr, reward)
        elif command == "!help":
            EDR_LOG.log(u"Help command", "INFO")
            self.edr_client.help("" if len(command_parts) == 1 else command_parts[1])
        elif command == "!tip" or command == "!tips":
            EDR_LOG.log(u"Tip command", "INFO")
            self.edr_client.tip("" if len(command_parts) == 1 else command_parts[1])
        elif command == "!clear":
            EDR_LOG.log(u"Clear command", "INFO")
            self.edr_client.clear()
        elif command == "!materials":
            if len(command_parts) == 2:
                profile = command_parts[1]
                EDR_LOG.log(u"Configure material profile with {}".format(profile), "INFO")
                self.edr_client.configure_resourcefinder(profile)
            else:
                self.edr_client.show_material_profiles()
                EDR_LOG.log(u"Listing material profiles", "INFO")
        elif command == "!biology":
            EDR_LOG.log(u"Biology info", "INFO")
            target = None
            if len(command_parts) >= 2:
                target = command_parts[1] or cmdr.body
            if target:
                self.edr_client.biology_on(target)
            else:
                self.edr_client.biology_spots(cmdr.star_system)
        elif command == "!journey":
            EDR_LOG.log(u"Journey command", "INFO")
            if len(command_parts) >= 2:
                better_parts = command_parts[1].split(" ", 1)
                if better_parts[0] == "next":
                    self.edr_client.journey_next()
                elif better_parts[0] == "previous":
                    self.edr_client.journey_previous()
                elif better_parts[0] == "clear":
                    self.edr_client.journey_clear()
                elif better_parts[0] == "fetch":
                    self.edr_client.journey_fetch()
                elif better_parts[0] == "load":
                    filename = better_parts[1] if len(better_parts) >= 2 else "journey.csv"
                    self.edr_client.journey_load(filename)
                elif better_parts[0] == "new":
                    if len(better_parts) >= 2:
                        self.edr_client.journey_new_adv(better_parts[1])
                    else:
                        self.edr_client.journey_new_adv()
                elif better_parts[0] == "overview":
                    self.edr_client.journey_show_overview()
                elif better_parts[0] == "waypoint":
                    self.edr_client.journey_show_waypoint()
                elif better_parts[0] == "bodies":
                    self.edr_client.journey_show_bodies()
                elif better_parts[0] == "check" and len(better_parts) >= 2 and better_parts[1]:
                    bodies_names = list(map(str.strip, better_parts[1].split(",")))
                    self.edr_client.journey_check_bodies(bodies_names)
            else:
                self.edr_client.journey_smart_behavior()
        else:
            return False
        return True

    def handle_query_commands(self, cmdr, command, command_parts):
        if command == "?outlaws":
            EDR_LOG.log(u"Outlaws alerts command", "INFO")
            param = "" if len(command_parts) == 1 else command_parts[1]
            if param == "":
                self.edr_client.outlaws_alerts_enabled(silent=False)
            elif param == "on": 
                EDR_LOG.log(u"Enabling Outlaws alerts", "INFO")
                self.edr_client.enable_outlaws_alerts()
            elif param == "off":
                EDR_LOG.log(u"Disabling Outlaws alerts", "INFO")
                self.edr_client.disable_outlaws_alerts()
            elif param.startswith("ly "):
                EDR_LOG.log(u"Max distance for Outlaws alerts", "INFO")
                self.edr_client.max_distance_outlaws_alerts(param[3:])
            elif param.startswith("cr "):
                EDR_LOG.log(u"Min bounty for Outlaws alerts", "INFO")
                self.edr_client.min_bounty_outlaws_alerts(param[3:])
            else:
                return False
            return True
        elif command == "?enemies":
            EDR_LOG.log(u"Enemies alerts command", "INFO")
            param = "" if len(command_parts) == 1 else command_parts[1]
            if param == "":
                self.edr_client.enemies_alerts_enabled(silent=False)
            elif param == "on": 
                EDR_LOG.log(u"Enabling enemies alerts", "INFO")
                self.edr_client.enable_enemies_alerts()
            elif param == "off":
                EDR_LOG.log(u"Disabling enemies alerts", "INFO")
                self.edr_client.disable_enemies_alerts()
            elif param.startswith("ly "):
                EDR_LOG.log(u"Max distance for Enemies alerts", "INFO")
                self.edr_client.max_distance_enemies_alerts(param[3:])
            else:
                return False
            return True
        return False
        
        
    def handle_hash_commands(self, command, command_parts, recipient):
        target_cmdr = EDRCommands.get_target_cmdr(command_parts, recipient, self.edr_client.player)
        if target_cmdr is None:
            EDR_LOG.log(u"Skipping tag command: no valid target", "WARNING")
            return False
        
        if (command == "#!" or command == "#outlaw"):
            EDR_LOG.log(u"Tag outlaw command for {}".format(target_cmdr), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, "outlaw")
        elif (command == "#?" or command == "#neutral"):
            EDR_LOG.log(u"Tag neutral command for {}".format(target_cmdr), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, "neutral")
        elif (command == "#+" or command == "#enforcer"):
            EDR_LOG.log(u"Tag enforcer command for {}".format(target_cmdr), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, "enforcer")
        elif (command == "#s!" or command == "#enemy"):
            EDR_LOG.log(u"Tag squadron enemy command for {}".format(target_cmdr), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, "enemy")
        elif (command == "#s+" or command == "#ally"):
            EDR_LOG.log(u"Tag squadron ally command for {}".format(target_cmdr), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, "ally")
        elif (command == "#=" or command == "#friend"):
            EDR_LOG.log(u"Tag friend command for {}".format(target_cmdr), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, "friend")
        elif (len(command) > 1 and command[0] == "#"):
            tag = command[1:]
            EDR_LOG.log(u"Tag command for {} with {}".format(target_cmdr, tag), "INFO")
            self.edr_client.tag_cmdr(target_cmdr, tag)
        else:
            return False
        return True

    def handle_minus_commands(self, command, command_parts, recipient):
        target_cmdr = EDRCommands.get_target_cmdr(command_parts, recipient, self.edr_client.player)
        if target_cmdr is None:
            EDR_LOG.log(u"Skipping untag command: no valid target", "WARNING")
            return False

        if command == "-#":
            EDR_LOG.log(u"Remove {} from dex".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, tag=None)
        elif command == "-#!" or command == "-#outlaw":
            EDR_LOG.log(u"Remove outlaw tag for {}".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, "outlaw")
        elif command == "-#?" or command == "-#neutral":
            EDR_LOG.log(u"Remove neutral tag for {}".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, "neutral")
        elif command == "-#+" or command == "-#enforcer":
            EDR_LOG.log(u"Remove enforcer tag for {}".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, "enforcer")
        elif command == "-#s!" or command == "-#enemy":
            EDR_LOG.log(u"Remove squadron enemy tag for {}".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, "enemy")
        elif command == "-#s+" or command == "-#ally":
            EDR_LOG.log(u"Remove squadron ally tag for {}".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, "ally")    
        elif command == "-#=" or command == "-#friend":
            EDR_LOG.log(u"Remove friend tag for {}".format(target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, "friend")
        elif (len(command) > 2 and command[0] == "-#"):
            tag = command[2:]
            EDR_LOG.log(u"Remove tag {} for {}".format(tag, target_cmdr), "INFO")
            self.edr_client.untag_cmdr(target_cmdr, tag)
        elif command == "-@#":
            EDR_LOG.log(u"Remove memo for {}".format(target_cmdr), "INFO")
            self.edr_client.clear_memo_cmdr(target_cmdr)
        else:
            return False
        return True
        

    def handle_at_commands(self, text, recipient):
        command_parts = text.split(" memo=", 1)
        command = command_parts[0].lower()
        target_cmdr = recipient
        
        if command == "@# ":
            if not recipient in ["local", "voicechat", "wing", "friend", "starsystem", "squadron", "squadleaders"]:
                prefix = "$cmdr_decorate:#name="
                target_cmdr = recipient[len(prefix):-1] if recipient.startswith(prefix) else recipient
                EDR_LOG.log(u"Memo command for tagged cmdr {}".format(target_cmdr), "INFO")
            else:
                target = self.edr_client.player.target_pilot()
                target_cmdr = target.name if target and target.is_human() else None
        elif command.startswith("@# ") and len(command)>2:
            target_cmdr = command[3:]
            EDR_LOG.log(u"Memo command for tagged cmdr {}".format(target_cmdr), "INFO")

        if target_cmdr:
            return self.edr_client.memo_cmdr(target_cmdr, command_parts[1])
        return False 


    def overlay_command(self, param):
        if param == "":
            EDR_LOG.log(u"Visual feedback is {}".format("enabled." if self.edr_client.visual_feedback
                                                    else "disabled."), "INFO")
            if not self.edr_client.IN_GAME_MSG:
                return False
            self.edr_client.IN_GAME_MSG.reconfigure()
            random.seed()
            r = random.random()
            if r < 0.5:
                self.edr_client.who(codecs.decode(random.choice(['yrxrab', 'Fgrs']), 'rot_13'))
            else:
                self.edr_client.who(codecs.decode(random.choice(['Qnatrebhf.pbz', 'Yrzna Ehff IV', 'qvrtb anpxl', 'Ahzvqn', 'Nyovab Fnapurm']), 'rot_13')) # top 5 for self reported kills in 2021
            self.edr_client.noteworthy_about_system({ "timestamp":"2021-10-22T12:34:56Z", "event":"FSDJump", "Taxi":False, "Multicrew":False, "StarSystem":"Deciat", "SystemAddress":6681123623626, "StarPos":[122.62500,-0.81250,-47.28125], "SystemAllegiance":"Independent", "SystemEconomy":"$economy_Industrial;", "SystemEconomy_Localised":"Industrial", "SystemSecondEconomy":"$economy_Refinery;", "SystemSecondEconomy_Localised":"Refinery", "SystemGovernment":"$government_Feudal;", "SystemGovernment_Localised":"Feudal", "SystemSecurity":"$SYSTEM_SECURITY_high;", "SystemSecurity_Localised":"High Security", "Population":31778844, "Body":"Deciat", "BodyID":0, "BodyType":"Star", "Powers":[ "A. Lavigny-Duval" ], "PowerplayState":"Exploited", "JumpDist":5.973, "FuelUsed":0.111415, "FuelLevel":8.000000, "Factions":[ { "Name":"Independent Deciat Green Party", "FactionState":"War", "Government":"Democracy", "Influence":0.109109, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand3;", "Happiness_Localised":"Discontented", "MyReputation":57.083599, "ActiveStates":[ { "State":"InfrastructureFailure" }, { "State":"War" } ] }, { "Name":"Kremata Incorporated", "FactionState":"Election", "Government":"Corporate", "Influence":0.105105, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":-6.000000, "ActiveStates":[ { "State":"Election" } ] }, { "Name":"Windri & Co", "FactionState":"War", "Government":"Corporate", "Influence":0.151151, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":-11.800000, "ActiveStates":[ { "State":"Boom" }, { "State":"War" } ] }, { "Name":"Deciat Flag", "FactionState":"None", "Government":"Dictatorship", "Influence":0.100100, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Deciat Corp.", "FactionState":"Election", "Government":"Corporate", "Influence":0.105105, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":-1.200000, "ActiveStates":[ { "State":"Election" } ] }, { "Name":"Deciat Blue Dragons", "FactionState":"None", "Government":"Anarchy", "Influence":0.010010, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":3.300000 }, { "Name":"Ryders of the Void", "FactionState":"Boom", "Government":"Feudal", "Influence":0.419419, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":93.099998, "PendingStates":[ { "State":"Expansion", "Trend":0 } ], "RecoveringStates":[ { "State":"CivilUnrest", "Trend":0 }, { "State":"PirateAttack", "Trend":0 } ], "ActiveStates":[ { "State":"Boom" } ] } ], "SystemFaction":{ "Name":"Ryders of the Void", "FactionState":"Boom" }, "Conflicts":[ { "WarType":"war", "Status":"active", "Faction1":{ "Name":"Independent Deciat Green Party", "Stake":"Carson Hub", "WonDays":2 }, "Faction2":{ "Name":"Windri & Co", "Stake":"Alonso Cultivation Estate", "WonDays":1 } }, { "WarType":"election", "Status":"active", "Faction1":{ "Name":"Kremata Incorporated", "Stake":"Folorunsho Military Enterprise", "WonDays":2 }, "Faction2":{ "Name":"Deciat Corp.", "Stake":"Amos Synthetics Moulding", "WonDays":1 } } ] })
            self.edr_client.check_system("Deciat")
            self.OVERLAY_DUMMY_COUNTER = (self.OVERLAY_DUMMY_COUNTER + 1) % 3
            if self.OVERLAY_DUMMY_COUNTER == 0:
                real_star_system = self.edr_client.player.star_system
                self.edr_client.player.star_system = "Deciat"
                self.edr_client.docking_guidance({ "timestamp":"2021-10-22T12:34:56Z", "event":"DockingGranted", "LandingPad":7, "MarketID":3229756160, "StationName":"Garay Terminal", "StationType":"Coriolis" })
                self.edr_client.player.star_system = real_star_system
            elif self.OVERLAY_DUMMY_COUNTER == 1:
                self.edr_client.player.mining_stats.dummify()
                self.edr_client.mining_guidance()
                self.edr_client.player.mining_stats.reset()
            else:
                self.edr_client.player.bounty_hunting_stats.dummify()
                self.edr_client.bounty_hunting_guidance() 
                self.edr_client.player.bounty_hunting_stats.reset()
        elif param == "on":
            EDR_LOG.log(u"Enabling visual feedback", "INFO")
            self.edr_client.visual_feedback = True
            self.edr_client.warmup()
        elif param == "off":
            EDR_LOG.log(u"Disabling visual feedback", "INFO")
            self.edr_client.notify_with_details("Visual Feedback System", ["disabling"])
            self.edr_client.visual_feedback = False
        else:
            return False
        return True

    def crimes_command(self, param):
        if param == "":
            EDR_LOG.log(u"Crimes report is {}".format("enabled." if self.edr_client.crimes_reporting
                                                    else "disabled."), "INFO")
            self.edr_client.notify_with_details("EDR crimes report",
                                        ["Enabled" if self.edr_client.crimes_reporting else "Disabled"])
        elif param == "on":
            EDR_LOG.log(u"Enabling crimes reporting", "INFO")
            self.edr_client.crimes_reporting = True
            self.edr_client.notify_with_details("EDR crimes report", ["Enabling"])
        elif param == "off":
            EDR_LOG.log(u"Disabling crimes reporting", "INFO")
            self.edr_client.crimes_reporting = False
            self.edr_client.notify_with_details("EDR crimes report", ["Disabling"])
        else:
            return False
        return True

    def audiocue_command(self, param):
        if param == "on":
            EDR_LOG.log(u"Enabling audio feedback", "INFO")
            self.edr_client.audio_feedback = True
            self.edr_client.notify_with_details("EDR audio cues", ["Enabling"])
        elif param == "off":
            EDR_LOG.log(u"Disabling audio feedback", "INFO")
            self.edr_client.audio_feedback = False
            self.edr_client.notify_with_details("EDR audio cues", ["Disabling"])
        elif param == "loud":
            EDR_LOG.log(u"Loud audio feedback", "INFO")
            self.edr_client.loud_audio_feedback()
            self.edr_client.audio_feedback = True
            self.edr_client.notify_with_details("EDR audio cues", ["Enabled", "Loud"])
        elif param == "soft":
            EDR_LOG.log(u"Soft audio feedback", "INFO")
            self.edr_client.soft_audio_feedback()
            self.edr_client.audio_feedback = True
            self.edr_client.notify_with_details("EDR audio cues", ["Enabled", "Soft"])
        else:
            return False
        return True

    @staticmethod
    def get_target_cmdr(command_parts, recipient, player):
        target_cmdr = command_parts[1] if len(command_parts) > 1 else None
        if target_cmdr is None:
            if not recipient in ["local", "voicechat", "wing", "friend", "starsystem", "squadron", "squadleaders"]:
                prefix = "$cmdr_decorate:#name="
                target_cmdr = recipient[len(prefix):-1] if recipient.startswith(prefix) else recipient
            else:
                target = player.target_pilot()
                target_cmdr = target.name if target and target.is_human() else None
        return target_cmdr
    