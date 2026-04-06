import os
import re
from math import sqrt, ceil

import datetime
import time
import collections
import operator
import json

from edr.utils import edtime
from edr.core import edrconfig
from edr.core.edrlog import EDR_LOG
from edr.utils.lrucache import LRUCache
from edr.models.edentities import EDFineOrBounty
from edr.utils.edrpath import edr_cache_path, edr_data_path
from edr.utils.edrutils import pretty_print_number
from edr.core.edri18n import _, _c, _edr
from . import edrservicecheck
from . import edrsysplacheck
from . import edrsyssetlcheck
from . import edrservicefinder
from . import edrparkingsystemfinder
from . import edrplanetfinder
from . import edrsettlementfinder
from .edrbiology import EDRBiology
from .edrscout import EDRScout
from .edrsysintel import EDRSysIntel
from .edrstation import EDRStation
from .edrbody import EDRBody


class EDRSystems:
    """
    Manages system information, including EDSM data, caches, and fleet carrier details.
    """
    EDR_SYSTEMS_CACHE = edr_cache_path('systems.v5.p')
    EDSM_SYSTEMS_CACHE = edr_cache_path('edsm_systems.v3.p')
    EDSM_OUTFITTING_CACHE = edr_cache_path('edsm_outfitting.v1.p')
    EDR_FC_REPORTS_CACHE = edr_cache_path('fc_reports.v1.p')
    EDR_FC_PRESENCE_CACHE = edr_cache_path('fc_presence.v1.p')
    EDR_FC_MATERIALS_CACHE = edr_cache_path('fc_materials.v1.p')
    EDR_FCS_CACHE = edr_cache_path('fcs.v1.p')
    NEBULAE = json.loads(open(edr_data_path('nebulae.json')).read())

    def __init__(self, server, edsm_server, factions):
        self.reasonable_sc_distance = 1500
        self.reasonable_hs_radius = 50
        self.edsm_systems_within_radius_blocklist = set()
        edr_config = edrconfig.EDR_CONFIG

        # --- EDR Caches ---
        self.systems_cache = LRUCache.load(
            file_path=self.EDR_SYSTEMS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.systems_max_age()
        )

        self.reports_check_interval = edr_config.reports_check_interval()
        self.server = server
        self.edsm_server = edsm_server
        self.factions = factions
        
        # --- Managers ---
        self.scout = EDRScout(self)
        self.intel = EDRSysIntel(self)
        self.station_manager = EDRStation(self)
        self.body_manager = EDRBody(self)
        self.biology = EDRBiology(self)
        
        # --- EDR Fleet Carrier (FC) Caches ---
        self.fc_reports_cache = LRUCache.load(
            file_path=self.EDR_FC_REPORTS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_reports_max_age()
        )

        self.fc_presence_cache = LRUCache.load(
            file_path=self.EDR_FC_PRESENCE_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_presence_max_age()
        )

        self.fc_materials_cache = LRUCache.load(
            file_path=self.EDR_FC_MATERIALS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_materials_max_age()
        )

        self.fcs_cache = LRUCache.load(
            file_path=self.EDR_FCS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_max_age()
        )

        # --- EDSM Caches ---
        self.edsm_systems_cache = LRUCache.load(
            file_path=self.EDSM_SYSTEMS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_systems_max_age()
        )

        self.EDSM_DEATHS_CACHE = edr_cache_path('edsm_deaths.v1.p')
        self.edsm_deaths_cache = LRUCache.load(
            file_path=self.EDSM_DEATHS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_deaths_max_age()
        )
        self.dlc_name = None

    def set_dlc(self, name):
        """
        Set the DLC name.
        """
        self.dlc_name = name

    def system_id(self, star_system, may_create=False, coords=None):
        """
        Get the system ID for a given star system.

        Args:
            star_system: The name of the star system.
            may_create: Whether to create the system on the server if not found.
            coords: Optional coordinates of the system.

        Returns:
            The system ID or None if not found.
        """
        if not star_system:
            return None

        key = star_system.lower()
        profile = None
        call_server = False

        # --- Step 1: Cache Check (Decision-Making Block) ---
        if self.systems_cache.has_key(key) and not self.systems_cache.is_stale(key):
            profile = self.systems_cache.peek(key)

            if profile is None:
                EDR_LOG.debug("Negative cache entry for System {} is fresh.".format(star_system))
                return profile

            sid = self._get_and_validate_sid(profile, star_system)
            if not sid:
                self.systems_cache.evict(key)
                EDR_LOG.error("Cached system {} had an invalid SID. Evicting cache entry.".format(star_system))
                call_server = True
            elif may_create and coords and "coords" not in profile.get(sid, {}):
                EDR_LOG.error("Cached system {} is missing coordinates. Forcing update.".format(star_system))
                call_server = True
            else:
                EDR_LOG.debug("System {} is in the cache with id={}".format(star_system, sid))
                return sid
        else:
            # Data is missing, stale, or evicted. Must call server.
            call_server = True
            if self.systems_cache.has_key(key):
                # Peek the profile for potential fallback.
                profile = self.systems_cache.peek(key)

        # --- Step 2: Server Call (Action-Taking Block) ---
        updated_system = None
        if call_server:
            EDR_LOG.info("Fetching system info for {} from EDR server.".format(star_system))
            try:
                updated_system = self.server.system(star_system, may_create, coords)
            except Exception as e:
                EDR_LOG.warning(f"Comms jammed/Failed to fetch system ID for {star_system}: {e}")

                # Stale Fallback Logic: Use 'profile' peeked in step 1 if server fails.
                if profile and profile is not None:
                    self.systems_cache.refresh(key)
                    EDR_LOG.info("Server failed. Re-using and refreshing stale system info.")
                    # Need to validate the stale profile again before returning it
                    return self._get_and_validate_sid(profile, star_system)

        # --- Step 3: Success / Negative Caching Logic ---

        if updated_system:
            # Server succeeded. Cache new data and return validated SID.
            self.systems_cache.set(key, updated_system)
            sid = self._get_and_validate_sid(updated_system, star_system)

            if sid:
                EDR_LOG.debug("Cached {}'s info with id={}".format(star_system, sid))
                return sid
            else:
                # Server returned data, but it failed validation (e.g., mismatched name, odd ID).
                EDR_LOG.error("Server returned a system for {} but the ID was invalid. Treating as no match.".format(
                    star_system))
                # Fall through to negative cache

        # Final cleanup: Cache failure/no match as None (Negative Caching)
        self.systems_cache.set(key, None)
        EDR_LOG.debug("No match on EDR/Server failed. Setting temporary None entry.")
        return None

    # Helper function to safely extract and validate the system ID
    def _get_and_validate_sid(self, system_dict, star_system_name):
        """
        Safely extract and validate the system ID.

        Args:
            system_dict: The dictionary containing system info.
            star_system_name: The expected name of the star system.

        Returns:
            The validated system ID or None.
        """
        if not system_dict or not isinstance(system_dict, dict):
            return None

        # The expected ID is the only key
        sid = list(system_dict.keys())[0] if system_dict.keys() else None

        if not sid:
            return None

        # 1. Check if the key is the literal system name (an unexpected placeholder)
        if sid.lower() == star_system_name.lower():
            EDR_LOG.warning("Rejected potential system ID (matches system name): {}".format(sid))
            return None

        # 2. Check if the key looks like an internal/common field name
        if sid.lower() in ["name", "id", "system"]:
            EDR_LOG.warning("Rejected potential system ID (matches internal field): {}".format(sid))
            return None

        return sid

    def fc_id(self, callsign, name, star_system, may_create=False):
        """
        Get the ID for a fleet carrier.

        Args:
            callsign: The fleet carrier callsign.
            name: The fleet carrier name.
            star_system: The current star system.
            may_create: Whether to create the FC entry on the server if not found.

        Returns:
            The fleet carrier ID or None.
        """
        if not callsign:
            return None

        key = callsign.lower()

        # --- Step 1: Cache Check (Decision-Making Block) ---
        if self.fcs_cache.has_key(key):

            # Check for freshness first. If fresh, handle it immediately.
            if not self.fcs_cache.is_stale(key):
                profile = self.fcs_cache.peek(key)

                if profile is None:
                    # A. Fresh Negative Cache Hit (FC known not to exist). Immediate return.
                    EDR_LOG.debug("Negative cache entry for FC {} is fresh.".format(callsign))
                    return None  # Returns None (the FC ID equivalent of "no match")

                # B. Fresh FC data hit. Extract and return the ID.
                fcid = list(profile.keys())[0] if profile.keys() else None
                if fcid:
                    EDR_LOG.debug("FC {} is in the cache with id={}".format(callsign, fcid))
                    return fcid

                # If fresh but contains invalid data (no key/ID), fall through to server call.
                EDR_LOG.error("Cached FC {} had an invalid ID format. Forcing server lookup.".format(callsign))
                self.fcs_cache.evict(key)  # Evict the bad data

        # --- Step 2: Server Call (Action-Taking Block) ---

        # Note: If cache check above returned, we skip this block entirely.
        # Otherwise, data is missing, stale, or was invalid.

        updated_fc = None
        stale_profile = self.fcs_cache.peek(key)  # Get stale profile for potential fallback

        try:
            EDR_LOG.info("Fetching FC info for {} from EDR server.".format(callsign))
            updated_fc = self.server.fc(callsign, name, star_system, may_create)
        except Exception as e:
            EDR_LOG.warning(f"Comms jammed/Failed to fetch FC ID for {callsign}: {e}")

            # Stale Fallback Logic: Use 'stale_profile' if server fails.
            if stale_profile and stale_profile is not None:
                self.fcs_cache.refresh(key)
                fcid = list(stale_profile.keys())[0] if stale_profile.keys() else None
                if fcid:
                    EDR_LOG.info("Server failed. Re-using and refreshing stale FC info for ID={}".format(fcid))
                    return fcid

        # --- Step 3: Success / Negative Caching Logic ---

        if updated_fc:
            # Server succeeded. Cache new data and return validated ID.
            self.fcs_cache.set(key, updated_fc)
            fcid = list(updated_fc.keys())[0] if updated_fc.keys() else None

            if fcid:
                EDR_LOG.debug("Cached {}'s info with id={}".format(callsign, fcid))
                return fcid
            else:
                EDR_LOG.error(
                    "Server returned FC data for {} but no ID was found. Treating as no match.".format(callsign))
                # Fall through to negative cache

        # Final cleanup: Cache failure/no match as None (Negative Caching)
        self.fcs_cache.set(key, None)
        EDR_LOG.debug("No match on EDR/Server failed. Setting temporary None entry.")
        return None

    def are_bodies_stale(self, star_system):
        """
        Check if bodies cache for a system is stale.
        """
        if not star_system:
            return False
        return self.edsm_bodies_cache.is_stale(star_system.lower())

    def are_stations_stale(self, star_system):
        """
        Check if stations cache for a system is stale.
        """
        if not star_system:
            return False
        return self.edsm_stations_cache.is_stale(star_system.lower())

    def are_settlements_stale(self, star_system):
        """
        Check if settlements cache for a system is stale.
        """
        return self.are_stations_stale(star_system)

    def stations_in_system(self, star_system):
        return self.station_manager.stations_in_system(star_system)

    def fuzzy_stations(self, star_system, station_name):
        return self.station_manager.fuzzy_stations(star_system, station_name)

    def fleet_carrier(self, star_system, callsign):
        return self.station(star_system, callsign, "FleetCarrier")

        self.edsm_stations_cache.set(star_system.lower(), None)
        EDR_LOG.debug("No match on EDSM. Temporary entry to be nice on EDSM's server.")
        return None

    def persist(self):
        if self.systems_cache:
            self.systems_cache.save(self.EDR_SYSTEMS_CACHE)
        if self.fc_reports_cache:
            self.fc_reports_cache.save(self.EDR_FC_REPORTS_CACHE)
        if self.fc_materials_cache:
            self.fc_materials_cache.save(self.EDR_FC_MATERIALS_CACHE)
        if self.fc_presence_cache:
            self.fc_presence_cache.save(self.EDR_FC_PRESENCE_CACHE)
        if self.fcs_cache:
            self.fcs_cache.save(self.EDR_FCS_CACHE)

        self.station_manager.save()
        self.body_manager.save()
        self.intel.save()
        self.scout.save()

        if self.edsm_systems_cache:
            self.edsm_systems_cache.save(self.EDSM_SYSTEMS_CACHE)
        if self.edsm_deaths_cache:
            self.edsm_deaths_cache.save(self.EDSM_DEATHS_CACHE)

    def distance(self, source_system, destination_system):
        """
        Calculate the distance between two systems.
        """
        if source_system == destination_system:
            return 0
        source = self.system(source_system)
        destination = self.system(destination_system)

        if source and destination:
            source_coords = source[0]["coords"]
            dest_coords = destination[0]["coords"]
            return sqrt((dest_coords["x"] - source_coords["x"]) ** 2 + (dest_coords["y"] - source_coords["y"]) ** 2 + (
                        dest_coords["z"] - source_coords["z"]) ** 2)
        raise ValueError('Unknown system')

    def distance_with_coords(self, source_system, dest_coords):
        """
        Calculate the distance between a system and a set of coordinates.
        """
        source = self.system(source_system)

        if source:
            source_coords = source[0]["coords"]
            return sqrt((dest_coords["x"] - source_coords["x"]) ** 2 + (dest_coords["y"] - source_coords["y"]) ** 2 + (
                        dest_coords["z"] - source_coords["z"]) ** 2)
        raise ValueError('Unknown system')

    def near_nebula(self, system_name):
        """
        Check if the system is near a known nebula.
        """
        distanceSol = self.distance("sol", system_name)

        for nbatch in EDRSystems.NEBULAE:
            if "rangeSol" in nbatch and abs(distanceSol - nbatch["rangeSol"]) <= 500:
                for n in nbatch:
                    if self.distance_with_coords(system_name, nbatch[n]["coords"]) < nbatch[n]["range"]:
                        return True

        return False

    def has_planet_type(self, system_name, planet_types):
        """
        Check if the system has a planet of the given type.
        """
        if not system_name:
            return False

        bodies = self.bodies(system_name)
        if not bodies:
            return False

        for b in bodies:
            subType = self.canonical_planet_class(b)
            if subType in planet_types:
                return True
        return False

    def update_fc_presence(self, fc_report):
        """
        Update fleet carrier presence in a system.
        """
        star_system = fc_report.get("starSystem", None)
        if star_system is None:
            return False
        sid = self.system_id(star_system, may_create=True)
        if not sid:
            return False
        if self.__novel_enough_fc_report(sid, fc_report):
            success = self.server.report_fcs(sid, fc_report)
            if success:
                self.fc_reports_cache.set(sid, fc_report)
                self.fc_presence_cache.evict(sid)
                return True
        return False

    def update_fc_materials(self, star_system, fc_materials):
        """
        Update fleet carrier materials (market/barman/shipyard/outfitting).
        """
        if star_system is None:
            return False

        callsign = fc_materials.get("callsign", None)
        if callsign is None:
            return False

        name = fc_materials.get("name", None)
        fcid = self.fc_id(callsign, name, star_system, may_create=True)
        if not fcid:
            return False

        fc_materials["starSystem"] = star_system
        if self.__novel_enough_fc_materials(fcid, fc_materials):
            success = self.server.report_fc_materials(fcid, fc_materials)
            if success:
                self.fc_materials_cache.set(fcid, fc_materials)
                self.fc_presence_cache.evict(fcid)
                return True
        return False

    def __novel_enough_fc_report(self, sid, fc_report):
        """
        Check if the FC report is different enough from the cached one.
        """
        if not self.fc_reports_cache.has_key(sid):
            return True

        if self.fc_reports_cache.is_stale(sid):
            return True
        last_fc_report = self.fc_reports_cache.get(sid)
        different_count = (fc_report["fcCount"] != last_fc_report["fcCount"])
        different_fcs = (fc_report.get("fc", None) != last_fc_report.get("fc", None))
        return different_count or different_fcs

    def __novel_enough_fc_materials(self, fcid, fc_materials):
        """
        Check if the FC materials are different enough from the cached ones.
        """
        if not self.fc_materials_cache.has_key(fcid):
            return True

        if self.fc_materials_cache.is_stale(fcid):
            return True
        last_fc_materials = self.fc_materials_cache.get(fcid)
        different_system = (fc_materials["starSystem"] != last_fc_materials["starSystem"])
        different_name = (fc_materials["name"] != last_fc_materials["name"])
        different_items_count = len(fc_materials.get("items", {})) != len(last_fc_materials.get("items", {}))
        if different_system or different_items_count or different_name:
            return True

        items = fc_materials.get("items", {})
        for item in items:
            previous_items = last_fc_materials.get("items", {})
            if item not in previous_items:
                return True
            listing = items[item]
            previous_listing = previous_items[item]
            different_price = listing["price"] != previous_listing["price"]
            different_stock = listing["stock"] != previous_listing["stock"]
            different_demand = listing["demand"] != previous_listing["demand"]
            if different_price or different_stock or different_demand:
                return True
        return False

    def fleet_carriers(self, star_system):
        """
        Get all fleet carriers in a star system.
        """
        if star_system is None:
            return {}
        sid = self.system_id(star_system)
        if not sid:
            return {}
        if self.fc_presence_cache.has_key(sid) and not self.fc_presence_cache.is_stale(sid):
            fc_report = self.fc_presence_cache.get(sid)
            return fc_report or {}
        if not self.fc_presence_cache.has_key(sid) or (self.fc_presence_cache.has_key(sid) and self.fc_presence_cache.is_stale(sid)):
            fc_report = self.server.fc_presence(star_system)
            self.fc_presence_cache.set(sid, fc_report)
            return fc_report or {}
        return {}

    
    def system(self, name):
        """
        Get EDSM system details.
        """
        if not name:
            return None

        the_system = self.edsm_systems_cache.get(name.lower())
        if self.edsm_systems_cache.has_key(name.lower()):
            EDR_LOG.debug("System {} is in the cache, and is known to EDSM: {}".format(name, the_system is not None))
            return the_system

        the_system = self.edsm_server.system(name)
        self.edsm_systems_cache.set(name.lower(), the_system)
        return the_system

    def system_coords(self, name):
        """
        Get coordinates for a system.
        """
        system = self.system(name)
        if not system:
            return None

        return system[0]["coords"] 

    def system_primary_star_oneliner(self, name, current_system=True):
        """
        Get a one-line description of the system's primary star.

        Args:
            name: The system name.
            current_system: Whether this is the current system.

        Returns:
            str: A one-line description of the primary star.
        """
        the_system = self.system(name)
        if not the_system:
            return None
        the_system = the_system[0]
        if "primaryStar" not in the_system:
            return None

        star = the_system["primaryStar"]
        raw_type = star.get("type", "???")
        star_type = self.__star_type_lut(raw_type)
        return _("Star: {} [Fuel]").format(star_type) if star.get("isScoopable", False) else _("Star: {}").format(star_type)

    def describe_system(self, name, current_system=True):
        """
        Get a detailed description of the system, including government, allegiance, economy, etc.

        Args:
            name: The system name.
            current_system: Whether this is the current system.

        Returns:
            list: A list of description strings.
        """
        the_system = self.system(name)
        if not the_system:
            return None
        the_system = the_system[0]
        details = []
        if "primaryStar" in the_system:
            details.extend(self.__describe_primary_star(the_system["primaryStar"], name, current_system))

        if "information" in the_system:
            info = ""
            info += _("Gvt: {}  ").format(the_system["information"]["government"]) if the_system["information"].get(
                "government", None) else ""
            info += _("Alg: {}  ").format(the_system["information"]["allegiance"]) if the_system["information"].get(
                "allegiance", None) else ""
            population = the_system["information"].get("population", None)
            if population is not None:
                population = pretty_print_number(population)
                info += _("Pop: {}  ").format(population)

            if info:
                details.append(info)

            info = ""
            info += _("Sec: {}  ").format(the_system["information"]["security"]) if the_system["information"].get(
                "security", None) else ""

            economy = the_system["information"].get("economy", None)
            second_economy = the_system["information"].get("secondEconomy", None)
            if second_economy:
                if economy:
                    info += _("Eco: {}/{}  ").format(economy, second_economy)
                else:
                    info += _("Eco: -/{}  ").format(second_economy)
            elif economy:
                info += _("Eco: {}  ").format(economy)

            info += _("Res: {}  ").format(the_system["information"]["reserve"]) if the_system["information"].get(
                "reserve", None) else ""

            if info:
                details.append(info)

            info = ""
            info += _("Sta: {}  ").format(the_system["information"]["factionState"]) if the_system["information"].get(
                "factionState", None) else ""
            factionName = the_system["information"].get("faction", None)
            if factionName:
                faction = self.factions.get(factionName, name)
                if faction and faction.isPMF:
                    info += _("Fac: {}  PMF: {}").format(factionName, "●" if faction.isPMF else "◌")
                else:
                    info += _("Fac: {}  ").format(factionName)

            if info:
                details.append(info)

        return details

    def __describe_star(self, star, system_name):
        """
        Helper to describe a star.
        """
        raw_type = star.get("subType", "???")
        star_type = self.__star_type_lut(raw_type)
        star_info = []
        star_info.append(_("Star: {} [Fuel]").format(star_type) if star.get("isScoopable", False) else _(
            "Star: {}").format(star_type))
        value = self.body_value(system_name, star.get("name", ""))
        if value:
            star_info.append(_("Max value: {} cr @ {} LS").format(pretty_print_number(value["valueMax"]),
                                                                  pretty_print_number(value["distance"])))
        return star_info

    def __star_type_lut(self, star_type):
        type_lut = {
            "o (blue-white) star": "O",
            "b (blue-white) star": "B",
            "b (blue-white super giant) star": "B+",
            "a (blue-white) star": "A",
            "a (blue-white super giant)": "A+",
            "f (white) star": "F",
            "f (white super giant) star": "F+",
            "g (white-yellow) star": "G",
            "g (white-yellow super giant) star": "G+",
            "k (yellow-orange) star": "K",
            "k (yellow-orange giant) star": "K+",
            "m (red dwarf) star": "M",
            "m (red giant) star": "M",
            "m (red super giant) star": "M+",
            "l (brown dwarf) star": "Brown Dwarf (L)",
            "t (brown dwarf) star": "Brown Dwarf (T)",
            "y (brown dwarf) star": "Brown Dwarf (Y)",
            "t tauri star": "T Tauri",
            "herbig ae/be star": "Herbig Ae/Be",
            "wolf-rayet star": "Wolf-Rayet",
            "wolf-rayet n star": "Wolf-Rayet N",
            "wolf-rayet nc star": "Wolf-Rayet NC",
            "wolf-rayet c star": "Wolf-Rayet C",
            "wolf-rayet o star": "Wolf-Rayet O",
            "c star": "C",
            "cn star": "CN",
            "cj star": "CJ",
            "ms-type star": "MS",
            "s-type star": "S",
            "white dwarf (d) star": "White Dwarf (D)",
            "white dwarf (da) star": "White Dwarf (DA)",
            "white dwarf (dab) star": "White Dwarf (DAB)",
            "white dwarf (daz) star": "White Dwarf (DAZ)",
            "white dwarf (dav) star": "White Dwarf (DAV)",
            "white dwarf (db) star": "White Dwarf (DB)",
            "white dwarf (dbz) star": "White Dwarf (DBZ)",
            "white dwarf (dbv) star": "White Dwarf (DBV)",
            "white dwarf (dq) star": "White Dwarf (DQ)",
            "white dwarf (dc) star": "White Dwarf (DC)",
            "white dwarf (dcv) star": "White Dwarf (DCV)",
            "neutron star": "Neutron",
            "black hole": "Black Hole",
            "supermassive black hole": "Supermassive Black Hole",
        }

        common_star_classes = "o,b,a,f,g,k,m,n,l,t,tts,s,w,x,y,h".split(",")
        
        if star_type.lower() not in type_lut and star_type.lower() not in common_star_classes:
            EDR_LOG.warning("Unrecognized star type: {}.".format(star_type))
        return type_lut.get(star_type.lower(), star_type)
        

    def __describe_primary_star(self, star, system_name, current_system=True):
        """
        Helper to describe the primary star.
        """
        raw_type = star.get("type", "???")
        star_type = self.__star_type_lut(raw_type)
        star_info = []
        star_info.append(_("Star: {} [Fuel]").format(star_type) if star.get("isScoopable", False) else _("Star: {}").format(star_type))
        value = None
        if current_system:
            value = self.body_value(system_name, star.get("name", ""))
            if value:
                star_info.append(_("Max value: {} cr @ {} LS").format(pretty_print_number(value["valueMax"]), pretty_print_number(value["distance"])))
        else:
            value = self.system_value(system_name)
            if value:
                estimatedValue = pretty_print_number(value["estimatedValue"]) if "estimatedValue" in value else "?"
                estimatedValueMapped = pretty_print_number(value["estimatedValueMapped"]) if "estimatedValueMapped" in value else "?"
                if estimatedValueMapped != estimatedValue:
                    star_info.append(_("Scanned: {}, Mapped: {}").format(estimatedValue, estimatedValueMapped))
                else:
                    star_info.append(_("Scanned: {}").format(estimatedValue))
                if "progress" in value and value["progress"] < 1.0 and value.get("bodyCount", None):
                    body_count = value["bodyCount"]
                    scanned_body_count = round(body_count * value["progress"])
                    progress = int(value["progress"]*100.0)
                    star_info.append(_("Discovered {}/{} {}%").format(scanned_body_count, body_count, progress))
        return star_info

    def market(self, marketId):
        return self.station_manager.market(marketId)

    def shipyard(self, shipyardId):
        return self.station_manager.shipyard(shipyardId)

    def outfitting(self, outfittingId):
        return self.station_manager.outfitting(outfittingId)


    def station(self, star_system, station_name, station_type, pad_count_override=None):
        return self.station_manager.station(star_system, station_name, station_type, pad_count_override)
    
    def materials_info(self, system_name, body_name, info):
        self.body_manager.materials_info(system_name, body_name, info)

    def describe_body(self, system_name, body_name, current_system=True):
        return self.body_manager.describe_body(system_name, body_name, current_system)

    def __body_with_id(self, system_name, body_id):
        return self.body_manager._EDRBody__body_with_id(system_name, body_id)

    def parent_star_type(self, system_name, body):
        return self.body_manager.parent_star_type(system_name, body)

    def parent_star_distance(self, system_name, body):
        return self.body_manager.parent_star_distance(system_name, body)

    def parent_star_luminosity(self, system_name, body):
        return self.body_manager.parent_star_luminosity(system_name, body)
    
    def materials_on(self, system_name, body_name):
        return self.body_manager.materials_on(system_name, body_name)

    @staticmethod
    def canonical_planet_class(planet):
        return EDRBody.canonical_planet_class(planet)

    @staticmethod
    def canonical_atmosphere(planet):
        return EDRBody.canonical_atmosphere(planet)

    @staticmethod
    def meets_biome_conditions(planet):
        return EDRBiology.meets_biome_conditions(planet)


    def analyzed_biome(self, star_system, body_id_or_name):
        return self.body_manager.analyzed_biome(star_system, body_id_or_name)

    def bodies(self, system_name):
        return self.body_manager.bodies(system_name)

    def body(self, system_name, body_name):
        return self.body_manager.body(system_name, body_name)

    def body_name_with_id(self, system_name, body_id):
        return self.body_manager.body_name_with_id(system_name, body_id)

    def body_count(self, system_name):
        return self.body_manager.body_count(system_name)

    def reflect_scan(self, system_name, body_name, scan):
        self.body_manager.reflect_scan(system_name, body_name, scan)

    def reflect_organic_scan(self, system_name, body_id, scan):
        self.body_manager.reflect_organic_scan(system_name, body_id, scan)

    def body_signals_found(self, system_name, scan):
        self.body_manager.body_signals_found(system_name, scan)

    def fss_discovery_scan_update(self, scan):
        self.body_manager.fss_discovery_scan_update(scan)

    def saa_scan_complete(self, scan):
        self.body_manager.saa_scan_complete(scan)

    def system_value(self, system_name):
        return self.scout.system_value(system_name)

    def body_value(self, system_name, body_name):
        return self.scout.body_value(system_name, body_name)
    
    def jumping_time(self, origin, destination, jump_range, seconds_per_jump = 55):
        dist = self.distance(origin, destination)
        return int(ceil(dist / jump_range) * seconds_per_jump)

    def search_interstellar_factors(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_interstellar_factors(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_raw_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_raw_trader(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_encoded_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_encoded_trader(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_manufactured_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_manufactured_trader(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_black_market(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_black_market(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_staging_station(self, star_system, callback, override_sc_distance = None, permits = []):
        self.station_manager.search_staging_station(star_system, callback, override_sc_distance, permits)

    def search_parking_system(self, star_system, callback, override_rank = None):
        self.station_manager.search_parking_system(star_system, callback, override_rank)

    def search_rrr_fc(self, star_system, callback, override_radius = None, permits = []):
        self.station_manager.search_rrr_fc(star_system, callback, override_radius, permits)

    def search_rrr(self, star_system, callback, override_radius = None, permits = []):
        self.station_manager.search_rrr(star_system, callback, override_radius, permits)

    def search_shipyard(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_shipyard(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_outfitting(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_outfitting(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_market(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_market(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_human_tech_broker(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_human_tech_broker(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_guardian_tech_broker(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        self.station_manager.search_guardian_tech_broker(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_offbeat_station(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = 100, override_sc_distance = 100000, permits = []):
        self.station_manager.search_offbeat_station(star_system, callback, with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_planet_with_genus(self, star_system, genus, callback, override_radius = 100, override_sc_distance = 100000, permits = []):
        self.body_manager.search_planet_with_genus(star_system, genus, callback, override_radius, override_sc_distance, permits)

    def search_settlement(self, star_system, settlement, callback, override_radius = 100, override_sc_distance = 100000, permits = []):
        self.station_manager.search_settlement(star_system, settlement, callback, override_radius, override_sc_distance, permits)
    
    def systems_within_radius(self, star_system, override_radius = None):
        if not star_system:
            return None

        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        key = "{}@{}".format(star_system.lower(), radius)

        if key in self.edsm_systems_within_radius_blocklist:
            EDR_LOG.info("Systems within radius for {} is in the blocklist.".format(key))
            return None

        systems = self.edsm_systems_within_radius_cache.get(key)
        cached = self.edsm_systems_within_radius_cache.has_key(key)
        if cached:
            if not systems:
                EDR_LOG.debug("Systems within {} of system {} are not available for a while.".format(radius, star_system))
                return None
            else:
                EDR_LOG.debug("Systems within {} of system {} are in the cache.".format(radius, star_system))
                return sorted(systems, key = lambda i: i['distance'])

        systems = self.edsm_server.systems_within_radius(star_system, radius)
        if systems is None:
            self.edsm_systems_within_radius_blocklist.add(key)
            EDR_LOG.debug("No results from EDSM. Temporary entry to be nice on EDSM's server. Added to blocklist.".format(key))
            return None
        
        systems = sorted(systems, key = lambda i: i['distance']) 
        self.edsm_systems_within_radius_cache.set(key, systems)
        EDR_LOG.debug("Cached systems within {}LY of {}".format(radius, star_system))
        return systems



    def evict(self, star_system):
        try:
            del self.systems_cache[star_system]
        except KeyError:
            pass

    def closest_station(self, sysAndSta1, sysAndSta2, override_sc_distance = None):
        return self.__closest_destination("station", sysAndSta1, sysAndSta2, override_sc_distance)

    def closest_planet(self, sysAndPla1, sysAndPla2, override_sc_distance = None):
        return self.__closest_destination("planet", sysAndPla1, sysAndPla2, override_sc_distance)
    
    def closest_settlement(self, sysAndPla1, sysAndPla2, override_sc_distance = None):
        return self.__closest_destination("settlement", sysAndPla1, sysAndPla2, override_sc_distance)
    
    def __closest_destination(self, key, sysAndSta1, sysAndSta2, override_sc_distance = None):
        if not sysAndSta1:
            return sysAndSta2

        if not sysAndSta2:
            return sysAndSta1

        sc_distance = override_sc_distance or self.reasonable_sc_distance 

        if sysAndSta1[key]['distanceToArrival'] > sc_distance and sysAndSta2[key]['distanceToArrival'] > sc_distance:
            if abs(sysAndSta1['distance'] - sysAndSta2['distance']) < 5:
                return sysAndSta1 if sysAndSta1[key]['distanceToArrival'] < sysAndSta2[key]['distanceToArrival'] else sysAndSta2
            else:
                return sysAndSta1 if sysAndSta1['distance'] < sysAndSta2['distance'] else sysAndSta2
    
        if sysAndSta1[key]['distanceToArrival'] > sc_distance:
            return sysAndSta2
    
        if sysAndSta2[key]['distanceToArrival'] > sc_distance:
            return sysAndSta1

        return sysAndSta1 if sysAndSta1['distance'] < sysAndSta2['distance'] else sysAndSta2
    
    def in_bubble(self, system_name, max_dist=1800):
        try:
            return self.distance(system_name, 'Sol') <= max_dist
        except ValueError:
            return False

    def in_colonia(self, system_name, max_dist=500):
        try:
            return self.distance(system_name, 'Colonia') <= max_dist
        except ValueError:
            return False