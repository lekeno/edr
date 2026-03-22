import re
import json
import datetime
import itertools
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.utils.edtime import EDTime
from edr.utils.clippy import copy
from edr.utils.edrutils import simplified_body_name, pretty_print_number
from edr.models.edsitu import EDPlanetaryLocation

class EDRNavigationManager:
    def __init__(self, edr_client):
        self.client = edr_client

    def try_custom_poi(self):
        """
        Attempt to set a custom POI as destination based on current attitude.
        """
        current = self.client.player.attitude
        if not current or not current.valid():
            return
        
        location = self.client.player.location
        body = self.client.edrsystems.body(location.star_system, location.body or location.place)
        radius = body.get("radius", None) if body else None

        star_system = location.star_system
        body_name = location.body or location.place
        if not star_system or not body_name:
            return
        
        poi = self.client.edrboi.closest_custom_point_of_interest(star_system, body_name, current, radius)
        if not poi:
            return

        self.client.player.planetary_destination = EDPlanetaryLocation(poi)
    
    def pointing_guidance(self, entry):
        """
        Provide guidance based on what the player is pointing at (Odyssey).

        Args:
            entry (dict): The journal event.

        Returns:
            bool: True if guidance was provided.
        """
        if (not self.client.gesture_triggers):
            EDR_LOG.info("Gestures setting is off, skipping processing")
            return True
        # TODO add the name of the thing in the header
        target = self.client.player.remlok_helmet.pointing_at(entry)
        if not target:
            return False
        details = []
        description = self.client.player.describe_item(target)
        inventory_description = self.client.player.inventory.oneliner(target, fallback=False)
        if inventory_description:
            details.append(inventory_description)
        if not description:
            return False

        details.extend(description)
        self.client._EDRClient__notify(_("Remlok Insights"), details, clear_before=True)
        
        return True
    
    def gesture(self, entry):
        """
        Handle gesture events (Odyssey emotes).

        Args:
            entry (dict): The journal event.
        """
        if (not self.client.gesture_triggers):
            EDR_LOG.info("Gestures setting is off, skipping processing")
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
            if not (self.client.player.body and self.client.player.star_system):
                EDR_LOG.info("Skipping point gesture: not on/near a body, or no system set")
                return

            if not (self.client.player.location.on_foot_location.on_planet):
                EDR_LOG.info("Skipping point gesture: not on a planet")
                return

            now = datetime.datetime.now()
            title = "POI ({})".format(now.strftime("%H:%M:%S"))
            if target:
                m = re.match(r"^\$Codex_Ent_([^_]+)_.+_Name[;]+$", target)
                if m:
                    title = "{} ({})".format(m.group(1), now.strftime("%H:%M:%S"))
            poi = {
                "title": title,
                "latitude": self.client.player.attitude.latitude,
                "longitude": self.client.player.attitude.longitude,
                "heading": self.client.player.attitude.heading
            }
            system_name = self.client.player.star_system
            body_name = self.client.player.body
            if not body_name or body_name.lower() == "unknown":
                return

            if self.client.edrboi.add_custom_poi(system_name, body_name, poi):
                details = [
                    _("Added a point of interest at the current position."),
                    _("Use the '!nav next' or '!nav previous! to select the next or previous POI."),
                    _("Use the 'stop' gesture or '!nav clear' to clear the current point of interest."),
                    _("Use the '!nav reset' to reset all custom POI for the current planet.")
                ]
                self.client._EDRClient__notify(_("EDR Navigation (pointing gesture)"), details)
            pass
        elif action == "wave":
            pass
        elif action == "agree":
            self.next_custom_poi()
            self.client._EDRClient__notify(_("EDR Navigation (thumb up gesture)"), [_("Switched to next POI.")])
        elif action == "disagree":
            self.previous_custom_poi()
            self.client._EDRClient__notify(_("EDR Navigation (thumb down gesture)"), [_("Switched to previous POI.")])
        elif action == "go":
            pass
        elif action == "stop":
            self.client.player.planetary_destination = None
            self.clear_current_custom_poi()
            self.client._EDRClient__notify(_("EDR Navigation (stop gesture)"), [_("Cleared current POI.")])
        elif action == "applaud":
            pass
        elif action == "salute":
            pass        
    
    def reset_custom_pois(self):
        """
        Reset custom Points of Interest (POIs) for the current body.
        """
        system_name = self.client.player.star_system
        body_name = self.client.player.body
        if not body_name or body_name.lower() == "unknown":
            EDR_LOG.warning("Can't reset custom POIs, no body name: {}".format(body_name))
            return

        self.client.edrboi.reset_custom_poi(system_name, body_name)
    
    def clear_current_custom_poi(self):
        """
        Clear the currently selected custom POI.
        """
        system_name = self.client.player.star_system
        body_name = self.client.player.body
        if not body_name or body_name.lower() == "unknown":
            EDR_LOG.warning("Can't clear current custom POI, no body name: {}".format(body_name))
            return

        self.client.edrboi.clear_current_custom_poi(system_name, body_name)
    
    def next_custom_poi(self):
        """
        Select the next custom POI.
        """
        return self.__next_previous_custom_poi(True)
    
    def previous_custom_poi(self):
        """
        Select the previous custom POI.
        """
        return self.__next_previous_custom_poi(False)

    def __next_previous_custom_poi(self, next):
        location = self.client.player.location
        
        poi = None
        if next:
            poi = self.client.edrboi.next_custom_point_of_interest(location.star_system, location.body or location.place)
        else:
            poi = self.client.edrboi.previous_custom_point_of_interest(location.star_system, location.body or location.place)
        
        if not poi:
            return

        self.client.player.planetary_destination = EDPlanetaryLocation(poi)

    def hyperspace_jump(self, system):
        """
        Handle Hyperspace Jump events.

        Args:
            system (str): The destination system name.
        """
        self.client.player.to_hyper_space()
        if self.client.player.piloted_vehicle:
            self.client.player.routenav.fsd_range(self.client.player.piloted_vehicle.max_jump_range)
        coords = self.client.edrsystems.system_coords(system)
        updates = self.client.player.routenav.update(system, coords)
        
        if updates["route_updated"]:
            if self.client.visual_feedback:
                self.client.IN_GAME_MSG.navroute(self.client.player.routenav)
            
        if updates["journey_updated"]:
            self.journey_show_waypoint()

    def update_star_system_if_obsolete(self, system, address=None):
        """
        Update the current star system if the stored one is obsolete.

        Args:
            system (str): The new system name.
            address (int, optional): The system address.

        Returns:
            bool: True if updated.
        """
        updated = self.client.player.update_star_system_if_obsolete(system, address)
        if updated:
            if self.client.player.piloted_vehicle:
                self.client.player.routenav.fsd_range(self.client.player.piloted_vehicle.max_jump_range)
            coords = self.client.edrsystems.system_coords(system)
            updates = self.client.player.routenav.update(system, coords)
            
        return updated

    def system_guidance(self, system_name, passive=False):
        """
        Provide guidance/intel about a system.

        Args:
            system_name (str): The system name.
            passive (bool): If True, suppresses output if no info.

        Returns:
            bool: True if info found/displayed.
        """
        description = self.client.edrsystems.describe_system(system_name, self.client.player.star_system == system_name)
        if not description:
            if not passive:
                self.client._EDRClient__notify(_("EDR System Search"), [_("No info on System called {}").format(system_name)], clear_before=True)
            return False

        header = "{}".format(system_name)
        self.client._EDRClient__notify(header, description, clear_before=True)
        return True

    def body_guidance(self, system_name, body_name, passive=False):
        """
        Provide guidance/intel about a body.

        Args:
            system_name (str): The system name.
            body_name (str): The body name.
            passive (bool): If True, suppresses output if no info.

        Returns:
            bool: True if info found/displayed.
        """
        description = self.client.edrsystems.describe_body(system_name, body_name, self.client.player.star_system == system_name)
        if not description:
            if not passive:
                self.client._EDRClient__notify(_("EDR System Search"), [_("No info on Body called {}").format(body_name)], clear_before=True)
            return False

        materials_info = self.client.edrsystems.materials_on(system_name, body_name)
        facts = self.client.edrresourcefinder.assess_materials_density(materials_info, self.client.player.inventory)
        if facts:
            description.extend(facts)
        bio_info = self.client.edrsystems.biology_on(system_name, body_name)
        if bio_info and bio_info.get("species", None):
            description.append(_("Expected Bio: {}").format(", ".join(bio_info["species"])))
            progress = self.__biome_progress_oneliner(system_name, body_name)
            if progress:
                description.append(progress)
        header = "{}".format(body_name)
        self.client._EDRClient__notify(header, description, clear_before=True)
        return True
        
