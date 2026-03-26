import math
import gettext
from edr.core.edri18n import _, _c
from edr.core.edrlog import EDR_LOG
from edr.utils.edrutils import pretty_print_number
from edr.models.edentities import EDFineOrBounty
from edr.models.edsitu import EDPlanetaryLocation

class EDRGuidance:
    """
    Handles evaluation, assessments, and guidance presentation for the EDR Client.
    Extracted from EDRClient to improve modularity and maintainability.
    """

    def __init__(self, edr_client):
        """
        Initialize the EDR Guidance service.
        
        Args:
            edr_client (EDRClient): The main EDRClient instance to get player state, UI, etc.
        """
        self.client = edr_client

    @property
    def player(self):
        return self.client.player
        
    @property
    def visual_feedback(self):
        return self.client.visual_feedback
        
    @property
    def audio_feedback(self):
        return self.client.audio_feedback
        
    @property
    def SFX(self):
        return self.client.SFX
        
    @property
    def IN_GAME_MSG(self):
        return self.client.IN_GAME_MSG

    def set_status(self, status):
        self.client.status = status

    def notify(self, header, details, clear_before=True):
        self.client._EDRClient__notify(header, details, clear_before)

    def biology_guidance(self):
        """
        Provide guidance for exobiological sampling.
        """
        current = self.player.attitude
        if not current or not current.valid():
            return
        
        genetic_sampler = self.player.closet.genetic_sampler
        locations = genetic_sampler.samples_locations()
        ccr = genetic_sampler.clonal_colony_range()
        species = genetic_sampler.species_tracked()
        credits = genetic_sampler.tracked_species_credits()
        
        location = self.player.location
        body = self.client.edrsystems.body(location.star_system, location.body or location.place)
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
                EDR_LOG.debug("No distance info out of System:{}, Body:{}, Place: {}, Radius:{}".format(location.star_system, location.body, location.place, radius))
                continue
            distances.append(distance)
            distances_summary += _(" [{loc_index}]: {dist}m  >{head:03}<").format(loc_index=i, dist=math.floor(distance), head=bearing)
            bearings.append(bearing)
            i += 1
        
        if self.visual_feedback:
            self.IN_GAME_MSG.biology_guidance(species, ccr, credits, distances,  bearings)
            if self.audio_feedback:
                self.SFX.biology()
        self.set_status(_("Value: {} cr; Gene diversity: +{}m => {}").format(pretty_print_number(credits), ccr, distances_summary))

    def mining_guidance(self):
        """
        Provide guidance for mining activities.
        """
        if self.visual_feedback:
            self.IN_GAME_MSG.mining_guidance(self.player.mining_stats)
            if self.audio_feedback:
                self.SFX.mining()
        
        if len(self.player.mining_stats.last["minerals_stats"]) > 0 and self.player.mining_stats.last["proportion"]:
            self.set_status(_("[Yield: {:.2f}%]   [Items: {} ({:.0f}/hour)]").format(self.player.mining_stats.last["proportion"], self.player.mining_stats.refined_nb, self.player.mining_stats.item_per_hour()))

    def bounty_hunting_guidance(self, turn_off=False):
        """
        Provide guidance for bounty hunting.

        Args:
            turn_off (bool): Whether to clear the guidance.
        """
        if self.visual_feedback:
            if turn_off:
                self.IN_GAME_MSG.clear_bounty_hunting_guidance()
                return
            self.IN_GAME_MSG.bounty_hunting_guidance(self.player.bounty_hunting_stats)
            if self.audio_feedback:
                self.SFX.bounty_hunting()
        
        bounty = EDFineOrBounty(self.player.bounty_hunting_stats.last["bounty"])
        credits_per_hour = EDFineOrBounty(int(self.player.bounty_hunting_stats.credits_per_hour()))
        self.set_status(_("[Last: {} cr [{}]]   [Totals: {} cr/hour ({} awarded)]").format(bounty.pretty_print(), self.player.bounty_hunting_stats.last["name"], self.player.bounty_hunting_stats.awarded_nb, credits_per_hour.pretty_print()))

    def target_guidance(self, target_event, turn_off=False):
        """
        Provide guidance about the current target.

        Args:
            target_event (dict): The ship target journal event.
            turn_off (bool): Whether to clear the guidance.
        """
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
            EDR_LOG.debug("Target info is not that interesting, skipping")
            return False

        shield_label = "{:.4g}".format(tgt.shield_health) if tgt.shield_health else "-"
        hull_label = "{:.4g}".format(tgt.hull_health) if tgt.hull_health else "-"
        
        if subsys_details:
            self.set_status(_("S/H %: {}/{} - {} %: {:.4g}").format(shield_label, hull_label, subsys_details["shortname"], subsys_details["stats"].last_value()))
        else:
            self.set_status(_("S/H %: {}/{}").format(shield_label, hull_label))
        
        if self.visual_feedback:
            self.IN_GAME_MSG.target_guidance(self.player.target_pilot(), subsys_details)
            if self.audio_feedback:
                self.SFX.target()

    def eval_mission(self, entry, passive=True):
        """
        Evaluate a mission for potential rewards or items.

        Args:
            entry (dict): The mission journal event.
            passive (bool): If True, suppresses output if nothing noteworthy.
        """
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
                    self.__notify(_("Mission Eval"), [_("Nothing noteworthy to share")], clear_before=True)
                return
            
            inventory_description = self.player.inventory.oneliner(commodity)
            details = []
            header = _("Eval of mission item : {}").format(localized_commodity)
            if inventory_description:
                header = _("Eval of mission item")
                details.append(inventory_description)
            details.extend(description)
            self.notify(header, details, clear_before=True)
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
                self.notify(_("Mission rewards eval"), details, clear_before=True)
            elif not passive:
                self.notify(_("Mission rewards eval"), [_("Nothing noteworthy to share")], clear_before=True)

    def eval(self, eval_type):
        """
        Evaluate items, loadouts, or other categories.

        Args:
            eval_type (str): The type of evaluation (e.g. 'power', 'backpack').
        """
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
                self.__notify(_("EDR Evals"), details, clear_before=True)
            else:
                self.__notify(_("EDR Evals"), [_("Yo dawg, I don't do evals for '{}'").format(eval_type), _("Try {} instead.").format(", ".join(canonical_commands)), _("Or specific materials (e.g. '!eval surveillance equipment').")], clear_before=True)
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
        """
        Evaluate ship build/loadout (power priorities).
        """
        if not self.player.mothership.update_modules():
            self.notify(_("Loadout information is stale"), [_("Congrats, yo've found a bug in Elite!"), _("The modules info isn't updated right away :("), _("Try again after moving around or relog and check your modules.")])
            return

        vehicle = self.player.mothership
        if not vehicle.modules:
            self.__notify(_("Basic Power Assessment"), [_("Yo dawg, U sure that you got modules on this?")], clear_before=True)
            return

        if vehicle.module_info_timestamp and vehicle.slots_timestamp < vehicle.module_info_timestamp:
            self.__notify(_("Basic Power Assessment"), [_("Yo dawg, the info I got from FDev might be stale."), _("Try again later after a bunch of random actions."), _("Or try this: relog, look at your modules, try again.")], clear_before=True)
            return
        
        build_master = EDRXzibit(vehicle)
        assessment = build_master.assess_power_priorities()
        if not assessment:
            self.__notify(_("Basic Power Assessment"), [_("Yo dawg, sorry but I can't help with dat.")], clear_before=True)
            return
        formatted_assessment = []
        grades = ['F', 'E', 'D', 'C', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
        for fraction in sorted(assessment):
            grade = grades[int(assessment[fraction]["grade"]*(len(grades)-1))]
            powered = _("⚡: {}").format(assessment[fraction]["annotation"]) if assessment[fraction]["annotation"] else ""
            formatted_assessment.append(_("{}: {}\t{}").format(grade, assessment[fraction]["situation"], powered))
            recommendation = _("   ⚑: {}").format(assessment[fraction]["recommendation"]) if "recommendation" in assessment[fraction] else ""
            praise = _("  ✓: {}").format(assessment[fraction]["praise"]) if "praise" in assessment[fraction] else ""
            formatted_assessment.append(_("{}{}").format(recommendation, praise))
        self.__notify(_("Basic Power Assessment (β; oddities? relog, look at your modules)"), formatted_assessment, clear_before=True)

    def eval_backpack(self, passive=False):
        """
        Evaluate backpack contents for usefulness (Odyssey).

        Args:
            passive (bool): If True, suppresses output if nothing noteworthy.
        """
        micro_resources = dict(sorted(self.player.inventory.all_in_backpack().items(), key=lambda item: item[1], reverse=True))
        if micro_resources:
            details = self.__eval_micro_resources(micro_resources, from_backpack=True)
            if details:
                self.__notify(_("Backpack assessment"), details, clear_before=True)
            elif not passive:
                self.__notify(_("Backpack assessment"), [_("Nothing superfluous")], clear_before = True)
        elif not passive:
            self.__notify(_("Backpack assessment"), [_("Empty backpack?")], clear_before=True)

    def eval_locker(self, passive=False):
        """
        Evaluate ship locker contents (Odyssey).

        Args:
            passive (bool): If True, suppresses output if nothing noteworthy.
        """
        micro_resources = dict(sorted(self.player.inventory.all_in_locker().items(), key=lambda item: item[1], reverse=True))
        if micro_resources:
            details = self.__eval_micro_resources(micro_resources)
            if details:
                self.__notify(_("Storage assessment"), details, clear_before=True)
            elif not passive:
                self.__notify(_("Storage assessment"), [_("Nothing superfluous")], clear_before=True)
        elif not passive:
            self.__notify(_("Storage assessment"), [_("Empty ship locker?")], clear_before=True)

    def eval_bar(self, stock=True):
        """
        Evaluate Carrier Bar stock or demand.

        Args:
            stock (bool): If True checks stock, else checks demand.

        Returns:
            bool: True if evaluation was successful/noteworthy.
        """
        header = _("Bar: stock assessment") if stock else _("Bar: demand assessment")
        if not self.player.last_station or not self.player.last_station.type == "FleetCarrier" or not self.player.last_station.bar:
            self.__notify(header, [_("Unexpected state: either no fleet carrier, or no bar?")], clear_before = True)
            return False

        bar = self.player.last_station.bar
        items = bar.items_in_stock() if stock else bar.items_in_demand()
        if items:
            details = self.__eval_good_micro_resources(items) if stock else self.__eval_bad_micro_resources(items)
            if details:
                legend = [_("Kind: best items (b=blueprint, u=upgrades, x=trading, e=eng. unlocks)")] if stock else [_("Kind: worst items (b=blueprint, u=upgrades, x=trading, e=eng. unlocks)")]
                self.__notify(header, legend + details, clear_before=True)
                return True
            else:
                self.__notify(header, [_("Nothing noteworthy")], clear_before = True)
                return False

    def __eval_micro_resources(self, micro_resources, from_backpack=False):
        discardable = [self.player.inventory.oneliner(name, from_backpack) for name in micro_resources if (self.player.engineers.is_useless(name) and self.player.inventory.count(name, from_backpack=from_backpack, from_locker=not from_backpack))]
        unnecessary = [self.player.inventory.oneliner(name, from_backpack) for name in micro_resources if (self.player.engineers.is_unnecessary(name) and self.player.inventory.count(name, from_backpack=from_backpack, from_locker=not from_backpack))]
        details = []
        discardable = discardable[0:min(len(discardable), 3)]
        unnecessary = unnecessary[0:min(len(unnecessary), 3)]
        if discardable:
            details.append(_("Useless: {}").format(", ".join(discardable)))
        if unnecessary:
            details.append(_("Unnecessary: {}").format(", ".join(unnecessary)))
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
            details.append(_("Unlocks: {}").format(", ".join(self_unlocking)))
        if sorted_engineering_assets:
            details.append(_("Assets: {}").format(", ".join([pair[0] for pair in sorted_engineering_assets])))
        if sorted_engineering_goods:
            details.append(_("Goods: {}").format(", ".join([pair[0] for pair in sorted_engineering_goods])))
        if sorted_engineering_data:
            details.append(_("Data: {}").format(", ".join([pair[0] for pair in sorted_engineering_data])))
        if other_unlocking:
            details.append(_("Unlocked: {}").format(", ".join(other_unlocking)))
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
            details.append(_("Assets: {}").format(", ".join([pair[0] for pair in sorted_engineering_assets])))
        if sorted_engineering_goods:
            details.append(_("Goods: {}").format(", ".join([pair[0] for pair in sorted_engineering_goods])))
        if sorted_engineering_data:
            details.append(_("Data: {}").format(", ".join([pair[0] for pair in sorted_engineering_data])))
        if other_unlocking:
            details.append(_("Unlocked: {}").format(", ".join(other_unlocking)))
        return details

