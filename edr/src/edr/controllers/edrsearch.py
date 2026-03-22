import re
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.utils.edtime import EDTime
from edr.utils.clippy import copy
from edr.utils.edrutils import simplified_body_name, pretty_print_number
from .edrsysplacheck import EDRGenusCheckerFactory
from .edrsyssetlcheck import EDRSettlementCheckerFactory

class EDRSearchManager:
    def __init__(self, edr_client):
        self.client = edr_client
        self.searching = {'active': False, 'timestamp': None}
    def __search_prerequisites(self, star_system):
        if not star_system:
            return False

        if self.__is_searching_recently():
            self.client._EDRClient__notify(_("EDR Search"), [_("Already searching for something, please wait...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
            return False
        
        if not (self.client.edrsystems.in_bubble(star_system) or self.client.edrsystems.in_colonia(star_system)):
            self.client._EDRClient__notify(_("EDR Search"), [_("Search features only work in the bubble or Colonia.")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.failed()
            return False
        return True

    def interstellar_factors_near(self, star_system, override_sc_distance = None):
        """
        Search for Interstellar Factors near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_interstellar_factors(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("I.Factors: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Interstellar Factors: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("I.Factors: failed")
            self.client.notify_with_details(_("EDR Search"), [_("Unknown system")])

    def raw_material_trader_near(self, star_system, override_sc_distance = None):
        """
        Search for Raw Material Traders near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_raw_trader(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("Raw mat. trader: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Raw material trader: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Raw mat. trader: failed")
            self.client.notify_with_details(_("EDR Search"), [_("Unknown system")])
        
    def encoded_material_trader_near(self, star_system, override_sc_distance = None):
        """
        Search for Encoded Material Traders near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_encoded_trader(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("Encoded data trader: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Encoded data trader: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Encoded data trader: failed")
            self.client.notify_with_details(_("EDR Search"), [_("Unknown system")])


    def manufactured_material_trader_near(self, star_system, override_sc_distance = None):
        """
        Search for Manufactured Material Traders near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return
        
        try:
            self.client.edrsystems.search_manufactured_trader(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("Manufactured mat. trader: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Manufactured material trader: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Manufactured mat. trader: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)


    def staging_station_near(self, star_system, override_sc_distance = None):
        """
        Search for a staging station (shipyard+outfitting) near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_staging_station(star_system, self.__staoi_found, override_sc_distance=override_sc_distance)
            self.__searching()
            self.client.status = _("Staging station: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Staging station: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Staging station: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def parking_system_near(self, star_system, override_rank = None):
        """
        Search for a parking system (for Fleet Carriers) near a system.

        Args:
            star_system (str): The reference system.
            override_rank (int, optional): Min security rank? (context specific).
        """
        self.client.feature_ads["parking"]["advertised"] = True # no need to advertise since the user clearly knows about it
        if not self.__search_prerequisites(star_system):
            return

        self.client.register_fss_signals() # we might as well gets this out in case it's useful

        try:
            self.client.edrsystems.search_parking_system(star_system, self.__parking_found, override_rank=override_rank)
            self.__searching()
            self.client.status = _("Parking system: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Parking system: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Parking system: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def rrr_fc_near(self, star_system, override_radius = None):
        """
        Search for a RRR (Refuel, Repair, Restock) Fleet Carrier near a system.

        Args:
            star_system (str): The reference system.
            override_radius (int, optional): Max search radius.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_rrr_fc(star_system, self.__staoi_found, override_radius=override_radius)
            self.__searching()
            self.client.status = _("RRR Fleet Carrier: searching...")
            details = [_("RRR Fleet Carrier: searching in {}...").format(star_system), _("If there are no results, try: !rrrfc {} < 15").format(star_system)]
            if override_radius:
                details = [_("RRR Fleet Carrier: searching within {} LY of {}...").format(override_radius, star_system)]
            self.client._EDRClient__notify(_("EDR Search"), details, clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("RRR Fleet Carrier: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def rrr_near(self, star_system, override_radius = None):
        """
        Search for a RRR (Refuel, Repair, Restock) station near a system.

        Args:
            star_system (str): The reference system.
            override_radius (int, optional): Max search radius.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_rrr(star_system, self.__staoi_found, override_radius=override_radius)
            self.__searching()
            self.client.status = _("RRR Station: searching...")
            details = [_("RRR Station: searching in {}...").format(star_system), _("If there are no results, try: !rrr {} < 15").format(star_system)]
            if override_radius:
                details = [_("RRR Station: searching within {} LY of {}...").format(override_radius, star_system)]
            self.client._EDRClient__notify(_("EDR Search"), details, clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("RRR Station: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def fc_in_current_system(self, callsign_or_name):
        """
        Find a Fleet Carrier in the current system.

        Args:
            callsign_or_name (str): The callsign or name to search for.
        """
        fcs = self.client.edrfssinsights.fuzzy_match_fleet_carriers(callsign_or_name)
        callsign = callsign_or_name
        fc_name = "Fleet Carrier"
        if len(fcs) == 1:
            callsign = next(iter(fcs))
            fc_name = fcs[callsign]
        elif len(fcs) > 1:
            self.client._EDRClient__notify(_("EDR Fleet Carrier Local Search"), [_("{} fleet carriers have {} in their callsign or name").format(len(fcs), callsign_or_name), _("Try something more specific, or the full callsign.")], clear_before=True)
            return
        
        fc_regexp = r"^([A-Z0-9]{3}-[A-Z0-9]{3})$"
        if not re.match(fc_regexp, callsign):
            self.client._EDRClient__notify(_("EDR Fleet Carrier Local Search"), [_("Couldn't find a fleet carrier with {} in its callsign or name").format(callsign_or_name), _("{} is not a valid callsign").format(callsign), _("Try a more specific term, the full callsign, or honk your discovery scanner first.")], clear_before=True)
            return

        fc = self.client.edrsystems.fleet_carrier(self.client.player.star_system, callsign)
        if fc is None:
            self.client._EDRClient__notify(_("EDR Fleet Carrier Local Search"), [_("No info on fleet carrier with {} callsign").format(callsign)], clear_before=True)
            return
        
        header = "{} ({})".format(fc_name, fc["name"])
        details = self.describe_fleet_carrier(fc)
        self.client._EDRClient__notify(header, details, clear_before=True)

    def describe_fleet_carrier(self, fc):
        """
        Format Fleet Carrier details.

        Args:
            fc (dict): The FC data.

        Returns:
            list: List of descriptive strings.
        """
        fc_other_services = (fc.get("otherServices", []) or []) 
        details = []
        
        a = "â—" if fc.get("haveOutfitting", False) else "â—Œ"
        b = "â—" if fc.get("haveShipyard", False) else "â—Œ"
        details.append(_("Outfit:{}   Shipyard:{}").format(a,b))
        
        a = "â—" if "Refuel" in fc_other_services else "â—Œ"
        b = "â—" if "Repair" in fc_other_services else "â—Œ"
        c = "â—" if "Restock" in fc_other_services else "â—Œ"
        details.append(_("Refuel:{}   Repair:{}   Restock:{}").format(a,b,c))
        
        a = "â—" if fc.get("haveMarket", False) else "â—Œ"
        b = "â—" if "Black Market" in fc_other_services else "â—Œ"
        details.append(_("Market:{}   B.Market:{}").format(a,b))
        
        a = "â—" if "Universal Cartographics" in fc_other_services else "â—Œ"
        b = "â—" if "Vista Genomics" in fc_other_services else "â—Œ"
        if a == "â—" or b == "â—":
             details.append(_("U.Cart:{}   Vista G:{}").format(a,b))
        
        a = "â—" if "Pioneer Supplies" in fc_other_services else "â—Œ"
        b = "â—" if "Contacts" in fc_other_services else "â—Œ"
        c = "â—" if "Crew Lounge" in fc_other_services else "â—Œ"
        if a == "â—" or b == "â—" or c == "â—":
            details.append(_("Redempt.O:{}   Pioneer S:{}   Lounge:{}").format(a,b,c))

        updated= EDTime()
        updated.from_edsm_timestamp(fc['updateTime']['information'])
        details.append(_("as of {date}").format(date=updated.as_local_timestamp()))
        return details

    def station_in_current_system(self, station_name, passive=False):
        """
        Find a Station in the current system.

        Args:
            station_name (str): The station name.
            passive (bool): If True, suppresses output if not found.

        Returns:
            bool: True if found.
        """
        stations = self.client.edrsystems.fuzzy_stations(self.client.player.star_system, station_name)
        if stations is None:
            if not passive:
                self.client._EDRClient__notify(_("EDR Station Local Search"), [_("No info on Station with {} in its name").format(station_name)], clear_before=True)
            return False

        if len(stations) > 1:
            if passive:
                return False
            self.client._EDRClient__notify(_("EDR Station Local Search"), [_("{} stations have {} in their name").format(len(stations), station_name), _("Try something more specific, or the full name.")], clear_before=True)
            return True
        elif len(stations) == 0:
            if not passive:
                self.client._EDRClient__notify(_("EDR Station Local Search"), [_("No Station with {} in their name").format(station_name)], clear_before=True)
            return False
        
        station = stations[0]
                
        economy = "{}/{}".format(station["economy"], station["secondEconomy"]) if station["secondEconomy"] else station["economy"]
        header = "{} ({})".format(station["name"], economy)

        faction = None
        if station and "controllingFaction" in station:
            controllingFaction = station["controllingFaction"]
            factionName = controllingFaction.get("name", "???")
            faction = self.client.edrfactions.get(factionName, self.client.player.star_system)
        details = self.client.describe_station(station, faction)
        self.client._EDRClient__notify(header, details, clear_before=True)
        return True

    def human_tech_broker_near(self, star_system, override_sc_distance = None):
        """
        Search for Human Tech Brokers near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_human_tech_broker(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("Human tech broker: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Human tech broker: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Human tech broker: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)
    
    def guardian_tech_broker_near(self, star_system, override_sc_distance = None):
        """
        Search for Guardian Tech Brokers near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_guardian_tech_broker(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("Guardian tech broker: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Guardian tech broker: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Guardian tech broker: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def offbeat_station_near(self, star_system, override_sc_distance = None):
        """
        Search for offbeat/rare stations (e.g. asteroid bases) near a system.

        Args:
            star_system (str): The reference system.
            override_sc_distance (int, optional): Max supercruise distance.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_offbeat_station(star_system, self.__staoi_found, with_large_pad=self.client.player.needs_large_landing_pad(), with_medium_pad=self.client.player.needs_medium_landing_pad(), override_sc_distance = override_sc_distance)
            self.__searching()
            self.client.status = _("Offbeat station: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Offbeat station: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Offbeat station: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def search_genus_near(self, genus, star_system):
        """
        Search for planets with a specific biology genus.

        Args:
            genus (str): The genus name.
            star_system (str): The reference system.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_planet_with_genus(star_system, genus, self.__plaoi_found)
            self.__searching()
            self.client.status = _("Biofit planet: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Biofit planet: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Biofit planet: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)

    def search_settlement_near(self, settlement, star_system):
        """
        Search for a specific settlement type or name.

        Args:
            settlement (str): The settlement query.
            star_system (str): The reference system.
        """
        if not self.__search_prerequisites(star_system):
            return

        try:
            self.client.edrsystems.search_settlement(star_system, settlement, self.__settloi_found)
            self.__searching()
            self.client.status = _("Settlement: searching...")
            self.client._EDRClient__notify(_("EDR Search"), [_("Settlement: searching...")], clear_before = True, sfx=False)
            if self.client.audio_feedback:
                self.client.SFX.searching()
        except ValueError:
            self.__searching(False)
            self.client.status = _("Settlement: failed")
            self.client._EDRClient__notify(_("EDR Search"), [_("Unknown system")], clear_before = True)


    def __staoi_found(self, reference, radius, sc, soi_checker, result):
        self.__searching(False)
        details = []
        if result and "station" in result:
            sc_distance = result['station']['distanceToArrival']
            distance = result['distance']
            pretty_dist = _("{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _("{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _("{dist}LS").format(dist=int(sc_distance))
            updated = EDTime()
            updated.from_edsm_timestamp(result['station']['updateTime']['information'])
            details.append(_("{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            details.append(_("{station} ({type}), {sc_dist}").format(station=result['station']['name'], type=result['station']['type'], sc_dist=pretty_sc_dist))
            details.append(_("as of {date} {ci}").format(date=updated.as_local_timestamp(),ci=result['station'].get('comment', '')))
            self.client.status = "{item}: {system}, {dist} - {station} ({type}), {sc_dist}".format(item=soi_checker.name, system=result['name'], dist=pretty_dist, station=result['station']['name'], type=result['station']['type'], sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            if result and 'station' not in result:
                EDR_LOG.error("Unsupported search result: {}".format(result))
            
            self.client.status = _("{}: nothing within [{}LY, {}LS] of {}").format(soi_checker.name, int(radius), int(sc), reference)
            checked = _("checked {} systems").format(soi_checker.systems_counter) 
            if soi_checker.stations_counter: 
                checked = _("checked {} systems and {} stations").format(soi_checker.systems_counter, soi_checker.stations_counter) 
            details.append(_("nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if soi_checker.hint:
                details.append(soi_checker.hint)
        self.client._EDRClient__notify(_("{} near {}").format(soi_checker.name, reference), details, clear_before = True)

    def __plaoi_found(self, reference, radius, sc, plaoi_checker, result):
        self.__searching(False)
        details = []
        if result:
            sc_distance = result['planet']['distanceToArrival']
            distance = result['distance']
            pretty_dist = _("{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _("{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _("{dist}LS").format(dist=int(sc_distance))
            planet_name = simplified_body_name(result['name'], result['planet']['name'])
            updated = EDTime()
            updated.from_edsm_timestamp(result['planet']['updateTime'])
            details.append(_("{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            details.append(_("{planet} ({type}, {atm}), {sc_dist}").format(planet=planet_name, type=result['planet']['subType'], atm=result['planet']['atmosphereType'], sc_dist=pretty_sc_dist))
            details.append(_("as of {date}").format(date=updated.as_local_timestamp()))
            self.client.status = "{item}: {system}, {dist} - {planet}, {sc_dist}".format(item=plaoi_checker.name, system=result['name'], dist=pretty_dist, planet=planet_name, sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            self.client.status = _("{}: nothing within [{}LY, {}LS] of {}").format(plaoi_checker.name, int(radius), int(sc), reference)
            checked = _("checked {} systems").format(plaoi_checker.systems_counter)
            if plaoi_checker.planets_counter: 
                checked = _("checked {} systems and {} planets").format(plaoi_checker.systems_counter, plaoi_checker.planets_counter)
            details.append(_("nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if plaoi_checker.hint:
                details.append(plaoi_checker.hint)
        self.client._EDRClient__notify(_("{} near {}").format(plaoi_checker.name, reference), details, clear_before = True)

    def __settloi_found(self, reference, radius, sc, settloi_checker, result):
        self.__searching(False)
        details = []
        if result and 'settlement' in result:
            settlement = result['settlement']
            sc_distance = settlement['distanceToArrival']
            distance = result['distance']
            pretty_dist = _("{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _("{dist}LY").format(dist=int(distance))
            pretty_sc_dist = _("{dist}LS").format(dist=int(sc_distance))
            updated = EDTime()
            updated.from_edsm_timestamp(settlement['updateTime']['information'])
            details.append(_("{system}, {dist}").format(system=result['name'], dist=pretty_dist))
            if 'body' in settlement:
                bodyName = settlement['body']['name']
                adjBodyName = simplified_body_name(result['name'], bodyName, " 0")
                details.append(_("{settlement} ({eco}), {body}, {sc_dist}").format(settlement=settlement['name'], eco=settlement["economy"], body=adjBodyName, sc_dist=pretty_sc_dist))
            else:
                details.append(_("{settlement} ({eco}), {sc_dist}").format(settlement=settlement['name'], eco=settlement["economy"], sc_dist=pretty_sc_dist))
            
            if 'controllingFaction' in settlement:
                faction = self.client.edrfactions.get(result["name"], settlement['controllingFaction']['name'])
                if faction:
                    updated = faction.lastUpdated
                    if faction.state != None:
                        details.append(_("{faction} ({bgs}, {gvt}, {alg})").format(faction=faction.name, bgs=faction.state, gvt=faction.government, alg=faction.allegiance))
                    else:
                        details.append(_("{faction} ({gvt}, {alg})").format(faction=settlement['controllingFaction']['name'], gvt=settlement['government'], alg=settlement['allegiance']))
                else:
                    if 'state' in settlement["controllingFaction"]:
                        details.append(_("{faction} ({bgs}, {gvt}, {alg})").format(faction=settlement['controllingFaction']['name'], bgs=settlement['controllingFaction']['state'], gvt=settlement['government'], alg=settlement['allegiance']))
                    else:
                        details.append(_("{faction} ({gvt}, {alg})").format(faction=settlement['controllingFaction']['name'], gvt=settlement['government'], alg=settlement['allegiance']))
            details.append(_("as of {date} {ci}").format(date=updated.as_local_timestamp(),ci=settlement.get('comment', '')))
            self.client.status = "{system}, {dist} - {settlement}, {sc_dist}".format(system=result['name'], dist=pretty_dist, settlement=settlement['name'], sc_dist=pretty_sc_dist)
            copy(result["name"])
        else:
            self.client.status = _("{}: nothing within [{}LY, {}LS] of {}").format(settloi_checker.name, int(radius), int(sc), reference)
            checked = _("checked {} systems").format(settloi_checker.systems_counter) 
            if settloi_checker.settlements_counter: 
                checked = _("checked {} systems and {} settlements").format(settloi_checker.systems_counter, settloi_checker.settlements_counter) 
            details.append(_("nothing found within [{}LY, {}LS], {}.").format(int(radius), int(sc), checked))
            if settloi_checker.hint:
                details.append(settloi_checker.hint)
        self.client._EDRClient__notify(_("Settlement near {}").format(reference), details, clear_before = True)

    def __parking_found(self, reference, radius, rank, result):
        self.__searching(False)
        details = []
        if result:
            distance = result['distance']
            pretty_dist = "0LY"
            if distance > 0:
                pretty_dist = _("{dist:.3g}LY").format(dist=distance) if distance < 50.0 else _("{dist}LY").format(dist=int(distance))
                details.append(_("{system}, {dist} from {ref} [#{rank}]").format(system=result['name'], dist=pretty_dist, ref=reference, rank=rank))
            else:
                details.append(_("{system} [#{rank}]").format(system=result['name'], rank=rank))
            fc = self.client.edrsystems.fleet_carriers(result['name'])
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
                    plusminus = "Â±{}".format(plus)
                else:
                    if plus > 0:
                        plusminus = "+{}".format(plus)
                        if minus > 0:
                            plusminus += " -{}".format(minus)
                    elif minus > 0:
                        plusminus = "-{}".format(minus)

                
                if len(plusminus):
                    details.append(_("Slots â‰ˆ {} ({}) / {} (as of {})").format(remaining, plusminus, result['parking']['slots'], tminus))
                else:
                    details.append(_("Slots â‰ˆ {} / {} (as of {})").format(remaining, result['parking']['slots'], tminus))
            else:
                details.append(_("Slots: ???/{} (no intel)").format(result['parking']['slots']))
            stats = result['parking']['info']['all']['stats']
            stars_stats = result['parking']['info']['stars']['stats']
            if stats["count"] > 1 and stats["count"] > stars_stats["count"]:
                bodyCount = _("{nb} bodies").format(nb=stats["count"]) if stats["count"] > 0 else _("{nb} body").format(nb=stats["count"])
                median = pretty_print_number(int(stats['median']))
                avg = pretty_print_number(int(stats['avg']))
                max_v = pretty_print_number(int(stats['max']))
                details.append(_("{} (LS): median={}, avg={}, max={}").format(bodyCount, median, avg, max_v))
            
            starCount = _("{nb} stars").format(nb=stars_stats["count"]) if stars_stats["count"] > 0 else _("{nb} stars").format(nb=stars_stats["count"])
            stars_median = pretty_print_number(int(stars_stats['median']))
            stars_avg = pretty_print_number(int(stars_stats['avg']))
            stars_max = pretty_print_number(int(stars_stats['max']))
            if stars_stats["count"] > 1:
                details.append(_("{} (LS): median={}, avg={}, max={}").format(starCount, stars_median, stars_avg, stars_max))
            elif stars_stats["count"] == 1:
                details.append(_("1 star (no gravity well)"))

            if reference == self.client.player.star_system:
                details.append(_("If full, try the next one with !parking #{}.").format(int(rank+1)))
            else:
                details.append(_("If full, try the next one with !parking {} #{}.").format(reference, int(rank+1)))
            
            self.client.status = "FC Parking: {system}, {dist}".format(system=result['name'], dist=pretty_dist)
            copy(result["name"])
        else:
            self.client.status = _("FC Parking: no #{} system within [{}LY] of {}").format(int(rank), int(radius), reference)
            details.append(_("No #{} system found within [{}LY].").format(int(rank), int(radius)))
            if rank > 0:
                if reference == self.client.player.star_system:
                    details.append(_("Try !parking #{}").format(int(rank-1)))
                else:
                    details.append(_("Try !parking {} #{}").format(reference, int(rank-1), int(rank-1)))
        self.client._EDRClient__notify(_("FC Parking near {}").format(reference), details, clear_before = True)
        self.__searching(False)

    def configure_resourcefinder(self, raw_profile):
        """
        Configure the resource finder profile.

        Args:
            raw_profile (str): The profile name.

        Returns:
            bool: True if successfully configured.
        """
        canonical_raw_profile = raw_profile.lower()
        adjusted_profile = None if canonical_raw_profile == "default" else canonical_raw_profile
        result = self.client.edrresourcefinder.configure(adjusted_profile)
        if not result:
            self.client._EDRClient__notify(_("Unrecognized materials profile"), [_("To see a list of profiles, send: !materials")], clear_before = True)
            return result
        
        if adjusted_profile:
            self.client._EDRClient__notify(_("Using materials profile '{}'").format(raw_profile), [_("Revert to default profile by sending: !materials default")], clear_before = True)
        else:
            self.client._EDRClient__notify(_("Using default materials profile"), [_("See the list of profiles by sending: !materials")], clear_before = True)
        return result

    def show_material_profiles(self):
        """
        List available material profiles.
        """
        profiles = self.client.edrresourcefinder.profiles()
        self.client._EDRClient__notify(_("Available materials profiles"), [" ;; ".join(profiles)], clear_before=True)

    def __searching(self, active=True):
        self.searching["active"] = active
        self.searching["timestamp"] = EDTime.py_epoch_now()
    
    def __is_searching_recently(self):
        if not self.searching["active"] or not self.searching["timestamp"]:
            return False
        
        threshold = 60*60*5
        if EDTime.py_epoch_now() - self.searching["timestamp"] < threshold:
            return self.searching["active"]

        EDR_LOG.debug("Resetting searching state due to no completion in {} seconds".format(threshold))
        self.__searching(False)
        return False
        
    def search(self, thing, star_system):
        """
        General search entry point (resource, genus, settlement, etc).

        Args:
            thing (str): The search query.
            star_system (str): The reference system.
        """
        cresource = self.client.edrresourcefinder.canonical_name(thing)
        if EDRGenusCheckerFactory.recognized_genus(thing):
            self.search_genus_near(thing, star_system)
        elif EDRSettlementCheckerFactory.recognized_settlement(thing):
            self.search_settlement_near(thing, star_system)
        elif cresource:
            self.search_resource(thing, star_system)
        else:
            matches = EDRGenusCheckerFactory.recognized_candidates(thing)
            matches.extend(self.client.edrresourcefinder.recognized_candidates(thing))
            matches.extend(EDRSettlementCheckerFactory.recognized_candidates(thing))
            if matches:
                self.client._EDRClient__notify(_("EDR Search: suggested terms"), [" ;; ".join(matches)], clear_before=True)
            else:
                self.client._EDRClient__notify(_("EDR Search"), [_("{}: not supported.").format(thing), _("To learn how to use the feature, send: !help search")], clear_before = True)
        

    def search_resource(self, resource, star_system):
        """
        Search for a materials/resource.

        Args:
            resource (str): The resource name.
            star_system (str): The reference system.
        """
        if not star_system:
            return
        
        if self.__is_searching_recently():
            self.client._EDRClient__notify(_("EDR Search"), [_("Already searching for something, please wait...")], clear_before = True)
            return

        if not (self.client.edrsystems.in_bubble(star_system) or self.client.edrsystems.in_colonia(star_system)):
            self.client._EDRClient__notify(_("EDR Search"), [_("Search features only work in the bubble or Colonia.")], clear_before = True)
            return

        cresource = self.client.edrresourcefinder.canonical_name(resource)
        if cresource is None:
            self.client.status = _("{}: not supported.").format(resource)
            self.client._EDRClient__notify(_("EDR Search"), [_("{}: not supported.").format(resource), _("To learn how to use the feature, send: !help search")], clear_before = True)
            return

        try:
            outcome = self.client.edrresourcefinder.resource_near(resource, star_system, self.__resource_found)
            if outcome == True:
                self.__searching()
                self.client.status = _("{}: searching...").format(cresource)
                self.client._EDRClient__notify(_("EDR Search"), [_("{}: searching...").format(cresource)], clear_before = True, sfx=False)
                if self.client.audio_feedback:
                    self.client.SFX.searching()
            elif outcome == False or outcome == None:
                self.client.status = _("{}: failed...").format(cresource)
                self.client._EDRClient__notify(_("EDR Search"), [_("{}: failed...").format(cresource), _("To learn how to use the feature, send: !help search")], clear_before = True)
            else:
                self.client.status = _("{}: found").format(cresource)
                self.client._EDRClient__notify("{}".format(cresource), outcome, clear_before = True)
        except ValueError:
            self.__searching(False)
            self.client.status = _("{}: failed...").format(cresource)
            self.client._EDRClient__notify(_("EDR Search"), [_("{}: failed...").format(cresource), _("To learn how to use the feature, send: !help search")], clear_before = True)

    def __resource_found(self, resource, reference, radius, checker, result, grade):
        self.__searching(False)
        details = []
        if result:
            distance = result['distance']
            pretty_dist = _("{dist:.3g}").format(dist=distance) if distance < 50.0 else _("{dist}").format(dist=int(distance))
            details.append(_("{} ({}LY, {})").format(result['name'], pretty_dist, '+' * grade))
            edt = EDTime()
            if 'updateTime' in result:
                edt.from_js_epoch(result['updateTime'] * 1000)
                details.append(_("as of {}").format(edt.as_local_timestamp()))
            if checker.hint():
                details.append(checker.hint())
            self.client.status = "{}: {} ({}LY)".format(checker.name, result['name'], pretty_dist)
            copy(result["name"])
        else:
            self.client.status = _("{}: nothing within [{}LY] of {}").format(checker.name, int(radius), reference)
            checked = _("checked {} systems").format(checker.systems_counter) 
            if checker.systems_counter: 
                checked = _("checked {} systems").format(checker.systems_counter)
            details.append(_("nothing found within {}LY, {}.").format(int(radius), checked))
            if checker.hint():
                details.append(checker.hint())
        self.client._EDRClient__notify(_("{} near {}").format(checker.name, reference), details, clear_before = True)

