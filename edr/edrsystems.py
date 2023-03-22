#!/usr/bin/env python
# coding=utf-8

import os
import pickle
import re
from math import sqrt, ceil

import datetime
from re import S
import sys
import time
import collections
import operator

import edtime
import edrconfig
import edrlog
import lrucache
import edsmserver
from edentities import EDFineOrBounty
from edentities import pretty_print_number
from edri18n import _, _c, _edr
import edrservicecheck
import edrservicefinder
import edrparkingsystemfinder
import utils2to3

EDRLOG = edrlog.EDRLog()

class EDRSystems(object):
    EDR_SYSTEMS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'systems.v5.p')
    EDR_RAW_MATERIALS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'raw_materials.v1.p')
    EDSM_BODIES_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_bodies.v1.p')
    EDSM_SYSTEMS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_systems.v3.p')
    EDSM_STATIONS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_stations.v1.p')
    EDSM_SYSTEMS_WITHIN_RADIUS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_systems_radius.v2.p')
    EDSM_FACTIONS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_factions.v1.p')
    EDSM_TRAFFIC_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_traffic.v1.p')
    EDSM_DEATHS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_deaths.v1.p')
    EDSM_MARKETS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_markets.v1.p')
    EDSM_SHIPYARDS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_shipyards.v1.p')
    EDSM_OUTFITTING_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_outfitting.v1.p')
    EDSM_SYSTEM_VALUES_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'edsm_system_values.v1.p')
    EDR_NOTAMS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'notams.v2.p')
    EDR_SITREPS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'sitreps.v3.p')
    EDR_TRAFFIC_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'traffic.v2.p')
    EDR_CRIMES_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'crimes.v2.p')
    EDR_FC_REPORTS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'fc_reports.v1.p')
    EDR_FC_PRESENCE_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'fc_presence.v1.p')
    EDR_FC_MATERIALS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'fc_materials.v1.p')
    EDR_FCS_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'fcs.v1.p')

    def __init__(self, server):
        self.reasonable_sc_distance = 1500
        self.reasonable_hs_radius = 50
        edr_config = edrconfig.EDRConfig()

        try:
            with open(self.EDR_SYSTEMS_CACHE, 'rb') as handle:
                self.systems_cache = pickle.load(handle)
        except:
            self.systems_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                   edr_config.systems_max_age())

        try:
            with open(self.EDR_RAW_MATERIALS_CACHE, 'rb') as handle:
                self.materials_cache = pickle.load(handle)
        except:
            self.materials_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                   edr_config.materials_max_age())
        
        try:
            with open(self.EDR_NOTAMS_CACHE, 'rb') as handle:
                self.notams_cache = pickle.load(handle)
        except:
            self.notams_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.notams_max_age())

        try:
            with open(self.EDR_SITREPS_CACHE, 'rb') as handle:
                self.sitreps_cache = pickle.load(handle) 
        except:
            self.sitreps_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.sitreps_max_age())

        try:
            with open(self.EDR_CRIMES_CACHE, 'rb') as handle:
                self.crimes_cache = pickle.load(handle)
        except:
            self.crimes_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.crimes_max_age())

        try:
            with open(self.EDR_FC_REPORTS_CACHE, 'rb') as handle:
                self.fc_reports_cache = pickle.load(handle)
        except:
            self.fc_reports_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                              edr_config.fc_reports_max_age())

        try:
            with open(self.EDR_FC_PRESENCE_CACHE, 'rb') as handle:
                self.fc_presence_cache = pickle.load(handle)
        except:
            self.fc_presence_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                              edr_config.fc_presence_max_age())

        try:
            with open(self.EDR_FC_MATERIALS_CACHE, 'rb') as handle:
                self.fc_materials_cache = pickle.load(handle)
        except:
            self.fc_materials_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                              edr_config.fc_materials_max_age())
            
        try:
            with open(self.EDR_FCS_CACHE, 'rb') as handle:
                self.fcs_cache = pickle.load(handle)
        except:
            self.fcs_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                              edr_config.fc_max_age())
            
        try:
            with open(self.EDR_TRAFFIC_CACHE, 'rb') as handle:
                self.traffic_cache = pickle.load(handle)
        except:
            self.traffic_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.traffic_max_age())

        try:
            with open(self.EDSM_SYSTEMS_CACHE, 'rb') as handle:
                self.edsm_systems_cache = pickle.load(handle)
        except:
            self.edsm_systems_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_systems_max_age())

        try:
            with open(self.EDSM_BODIES_CACHE, 'rb') as handle:
                self.edsm_bodies_cache = pickle.load(handle)
        except:
            self.edsm_bodies_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_bodies_max_age())
                                            
        try:
            with open(self.EDSM_STATIONS_CACHE, 'rb') as handle:
                self.edsm_stations_cache = pickle.load(handle)
        except:
            self.edsm_stations_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_stations_max_age())

        try:
            with open(self.EDSM_FACTIONS_CACHE, 'rb') as handle:
                self.edsm_factions_cache = pickle.load(handle)
        except:
            self.edsm_factions_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_factions_max_age())
        
        try:
            with open(self.EDSM_SYSTEMS_WITHIN_RADIUS_CACHE, 'rb') as handle:
                self.edsm_systems_within_radius_cache = pickle.load(handle)
        except:
            self.edsm_systems_within_radius_cache = lrucache.LRUCache(edr_config.edsm_within_radius_max_size(),
                                                  edr_config.edsm_systems_max_age())

        try:
            with open(self.EDSM_TRAFFIC_CACHE, 'rb') as handle:
                self.edsm_traffic_cache = pickle.load(handle)
        except:
            self.edsm_traffic_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_traffic_max_age())

        try:
            with open(self.EDSM_MARKETS_CACHE, 'rb') as handle:
                self.edsm_markets_cache = pickle.load(handle)
        except:
            self.edsm_markets_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_markets_max_age())

        try:
            with open(self.EDSM_SHIPYARDS_CACHE, 'rb') as handle:
                self.edsm_shipyards_cache = pickle.load(handle)
        except:
            self.edsm_shipyards_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_shipyards_max_age())

        try:
            with open(self.EDSM_OUTFITTING_CACHE, 'rb') as handle:
                self.edsm_outfitting_cache = pickle.load(handle)
        except:
            self.edsm_outfitting_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_outfitting_max_age())

        try:
            with open(self.EDSM_SYSTEM_VALUES_CACHE, 'rb') as handle:
                self.edsm_system_values_cache = pickle.load(handle)
        except:
            self.edsm_system_values_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_bodies_max_age()) # TODO proper max age value
        
        try:
            with open(self.EDSM_DEATHS_CACHE, 'rb') as handle:
                self.edsm_deaths_cache = pickle.load(handle)
        except:
            self.edsm_deaths_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_deaths_max_age())

         

        self.reports_check_interval = edr_config.reports_check_interval()
        self.notams_check_interval = edr_config.notams_check_interval()
        self.timespan = edr_config.sitreps_timespan()
        self.timespan_notams = edr_config.notams_timespan()
        self.server = server
        self.edsm_server = edsmserver.EDSMServer()
        self.dlc_name = None

    def set_dlc(self, name):
        self.dlc_name = name

    def system_id(self, star_system, may_create=False, coords=None):
        if not star_system:
            return None
        system = self.systems_cache.get(star_system.lower())
        cached = self.systems_cache.has_key(star_system.lower())
        if cached and system is None:
            EDRLOG.log(u"Temporary entry for System {} in the cache".format(star_system), "DEBUG")
            return None

        if cached and system:
            sid = list(system)[0]
            if may_create and coords and not "coords" in system[sid]:
                EDRLOG.log(u"System {} is in the cache with id={} but missing coords".format(star_system, sid), "DEBUG")
                system = self.server.system(star_system, may_create, coords)
                if system:
                    self.systems_cache.set(star_system.lower(), system)
                sid = list(system)[0]
            return sid

        system = self.server.system(star_system, may_create, coords)
        if system:
            self.systems_cache.set(star_system.lower(), system)
            sid = list(system)[0]
            EDRLOG.log(u"Cached {}'s info with id={}".format(star_system, sid), "DEBUG")
            return sid

        self.systems_cache.set(star_system.lower(), None)
        EDRLOG.log(u"No match on EDR. Temporary entry to be nice on EDR's server.", "DEBUG")
        return None

    def fc_id(self, callsign, name, star_system, may_create=False):
        if not callsign:
            return None
        fc = self.fcs_cache.get(callsign.lower())
        cached = self.fcs_cache.has_key(callsign.lower())
        if cached and fc is None:
            EDRLOG.log(u"Temporary entry for FC {} in the cache".format(callsign), "DEBUG")
            return None

        if cached and fc:
            fcid = list(fc)[0]
            return fcid

        fc = self.server.fc(callsign, name, star_system,  may_create)
        if fc:
            self.fcs_cache.set(callsign.lower(), fc)
            fcid = list(fc)[0]
            EDRLOG.log(u"Cached {}'s info with id={}".format(callsign, fcid), "DEBUG")
            return fcid

        self.fcs_cache.set(callsign.lower(), None)
        EDRLOG.log(u"No match on EDR. Temporary entry to be nice on EDR's server.", "DEBUG")
        return None

    def are_stations_stale(self, star_system):
        if not star_system:
            return False
        return self.edsm_stations_cache.is_stale(star_system.lower())
        
    def station(self, star_system, station_name, station_type):
        stations = self.stations_in_system(star_system)
        if not stations:
            return None
            
        for station in stations:
            if station["name"] == station_name:
                return station
        
        worth_retrying_age = 60*60*6 
        if station_type == "FleetCarrier" and self.edsm_stations_cache.is_older_than(star_system.lower(), worth_retrying_age):
            # FleetCarrier are a bit more dynamic, so evict a lukewarm entry and get a new fresh one in case the info has been reflected since last time
            self.edsm_stations_cache.evict(star_system.lower())
            stations = self.stations_in_system(star_system)
            for station in stations:
                if station["name"] == station_name:
                    return station
        
        return None

    def fuzzy_stations(self, star_system, station_name):
        if station_name is None or station_name == "":
            return []

        stations = self.stations_in_system(star_system)
        if not stations:
            return []
        
        return [station for station in stations if (station_name.lower() in station["name"].lower())]
        

    def fleet_carrier(self, star_system, callsign):
        return self.station(star_system, callsign, "FleetCarrier")

    def stations_in_system(self, star_system):
        if not star_system:
            return None
        stations = self.edsm_stations_cache.get(star_system.lower())
        cached = self.edsm_stations_cache.has_key(star_system.lower())
        if cached or stations:
            EDRLOG.log(u"Stations for system {} are in the cache.".format(star_system), "DEBUG")
            return stations

        stations = self.edsm_server.stations_in_system(star_system)
        if stations:
            self.edsm_stations_cache.set(star_system.lower(), stations)
            EDRLOG.log(u"Cached {}'s stations".format(star_system), "DEBUG")
            return stations

        self.edsm_stations_cache.set(star_system.lower(), None)
        EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None

    def persist(self):
        with open(self.EDR_SYSTEMS_CACHE, 'wb') as handle:
            pickle.dump(self.systems_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_RAW_MATERIALS_CACHE, 'wb') as handle:
            pickle.dump(self.materials_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_NOTAMS_CACHE, 'wb') as handle:
            pickle.dump(self.notams_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDR_SITREPS_CACHE, 'wb') as handle:
            pickle.dump(self.sitreps_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDR_TRAFFIC_CACHE, 'wb') as handle:
            pickle.dump(self.traffic_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_CRIMES_CACHE, 'wb') as handle:
            pickle.dump(self.crimes_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_FC_REPORTS_CACHE, 'wb') as handle:
            pickle.dump(self.fc_reports_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_FC_MATERIALS_CACHE, 'wb') as handle:
            pickle.dump(self.fc_materials_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDR_FC_PRESENCE_CACHE, 'wb') as handle:
            pickle.dump(self.fc_presence_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_FCS_CACHE, 'wb') as handle:
            pickle.dump(self.fcs_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_SYSTEMS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_systems_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDSM_BODIES_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_bodies_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDSM_SYSTEM_VALUES_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_system_values_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_STATIONS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_stations_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_SYSTEMS_WITHIN_RADIUS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_systems_within_radius_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_FACTIONS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_factions_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_TRAFFIC_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_traffic_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_DEATHS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_deaths_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def distance(self, source_system, destination_system):
        if source_system == destination_system:
            return 0
        source = self.system(source_system)
        destination = self.system(destination_system)
 
        if source and destination:
            source_coords = source[0]["coords"]
            dest_coords = destination[0]["coords"] 
            return sqrt((dest_coords["x"] - source_coords["x"])**2 + (dest_coords["y"] - source_coords["y"])**2 + (dest_coords["z"] - source_coords["z"])**2)
        raise ValueError('Unknown system')

    def distance_with_coords(self, source_system, dest_coords):
        source = self.system(source_system)
        
        if source:
            source_coords = source[0]["coords"]
            return sqrt((dest_coords["x"] - source_coords["x"])**2 + (dest_coords["y"] - source_coords["y"])**2 + (dest_coords["z"] - source_coords["z"])**2)
        raise ValueError('Unknown system')

    def update_fc_presence(self, fc_report):
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
        if not self.fc_reports_cache.has_key(sid):
            return True

        if self.fc_reports_cache.is_stale(sid):
            return True
        last_fc_report = self.fc_reports_cache.get(sid)
        different_count = (fc_report["fcCount"] != last_fc_report["fcCount"])
        different_fcs = (fc_report.get("fc", None) != last_fc_report.get("fc", None))
        return different_count or different_fcs

    def __novel_enough_fc_materials(self, fcid, fc_materials):
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
        if not name:
            return None

        the_system = self.edsm_systems_cache.get(name.lower())
        if the_system:
            return the_system

        the_system = self.edsm_server.system(name)
        if the_system:
            self.edsm_systems_cache.set(name.lower(), the_system)
            return the_system
        
        return None

    def describe_system(self, name, current_system=True):
        the_system = self.system(name)
        if not the_system:
            return None
        the_system = the_system[0]
        details = []
        if "primaryStar" in the_system:
            details.extend(self.__describe_primary_star(the_system["primaryStar"], name, current_system))

        if "information" in the_system:
            info = ""
            info += _("Gvt: {}  ").format(the_system["information"]["government"]) if the_system["information"].get("government", None) else ""
            info += _("Alg: {}  ").format(the_system["information"]["allegiance"]) if the_system["information"].get("allegiance", None) else ""
            population = the_system["information"].get("population", None)
            if population != None:
                population = pretty_print_number(population)
                info += _("Pop: {}  ").format(population)
    
            if info:
                details.append(info)
            
            info = ""
            info += _("Sec: {}  ").format(the_system["information"]["security"]) if the_system["information"].get("security", None) else ""
            
            economy = the_system["information"].get("economy", None)
            second_economy = the_system["information"].get("secondEconomy", None)
            if second_economy:
                if economy:
                    info += _("Eco: {}/{}  ").format(economy, second_economy)
                else:
                    info += _("Eco: -/{}  ").format(second_economy)
            elif economy:
                info += _("Eco: {}  ").format(economy)
                
            
            info += _("Res: {}  ").format(the_system["information"]["reserve"]) if the_system["information"].get("reserve", None) else ""
            
            if info:
                details.append(info)
            
            info = ""
            info += _("Sta: {}  ").format(the_system["information"]["factionState"]) if the_system["information"].get("factionState", None) else ""
            info += _("Fac: {}  ").format(the_system["information"]["faction"]) if the_system["information"].get("faction", None) else ""
            if info:
                details.append(info)

        return details

    def __describe_star(self, star, system_name):
        raw_type = star.get("subType", "???")
        star_type = self.__star_type_lut(raw_type)
        star_info = []
        star_info.append(_("Star: {} [Fuel]").format(star_type) if star.get("isScoopable", False) else _("Star: {}").format(star_type))
        value = self.body_value(system_name, star.get("name", ""))
        if value:
            star_info.append(_("Max value: {} cr @ {} LS").format(pretty_print_number(value["valueMax"]), pretty_print_number(value["distance"])))
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
        
        return type_lut.get(star_type.lower(), star_type)
        

    def __describe_primary_star(self, star, system_name, current_system=True):
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

    def station(self, star_system, station_name, station_type):
        stations = self.stations_in_system(star_system)
        if not stations:
            return None
            
        for station in stations:
            if station["name"] == station_name:
                return station
        
        worth_retrying_age = 60*60*6 
        if station_type == "FleetCarrier" and self.edsm_stations_cache.is_older_than(star_system.lower(), worth_retrying_age):
            # FleetCarrier are a bit more dynamic, so evict a lukewarm entry and get a new fresh one in case the info has been reflected since last time
            self.edsm_stations_cache.evict(star_system.lower())
            stations = self.stations_in_system(star_system)
            for station in stations:
                if station["name"] == station_name:
                    return station
        
        return None


    def market(self, marketId):
        marketInfo = self.edsm_markets_cache.get(marketId)
        cached = self.edsm_markets_cache.has_key(marketId)
        if cached or marketInfo:
            EDRLOG.log(u"Market info for marketId {} is in the cache.".format(marketId), "DEBUG")
            return marketInfo

        marketInfo = self.edsm_server.market(marketId)
        if marketInfo:
            self.edsm_markets_cache.set(marketId, marketInfo)
            EDRLOG.log(u"Cached {}'s market info".format(marketId), "DEBUG")
            return marketInfo

        self.edsm_markets_cache.set(marketId, None)
        EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None

    def shipyard(self, shipyardId):
        shipyardInfo = self.edsm_shipyards_cache.get(shipyardId)
        cached = self.edsm_shipyards_cache.has_key(shipyardId)
        if cached or shipyardInfo:
            EDRLOG.log(u"shipyard info for shipyardId {} is in the cache.".format(shipyardId), "DEBUG")
            return shipyardInfo

        shipyardInfo = self.edsm_server.shipyard(shipyardId)
        if shipyardInfo:
            self.edsm_shipyards_cache.set(shipyardId, shipyardInfo)
            EDRLOG.log(u"Cached {}'s shipyard info".format(shipyardId), "DEBUG")
            return shipyardInfo

        self.edsm_shipyards_cache.set(shipyardId, None)
        EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None

    def outfitting(self, outfittingId):
        outfittingInfo = self.edsm_outfittings_cache.get(outfittingId)
        cached = self.edsm_outfittings_cache.has_key(outfittingId)
        if cached or outfittingInfo:
            EDRLOG.log(u"outfitting info for outfittingId {} is in the cache.".format(outfittingId), "DEBUG")
            return outfittingInfo

        outfittingInfo = self.edsm_server.outfitting(outfittingId)
        if outfittingInfo:
            self.edsm_outfittings_cache.set(outfittingId, outfittingInfo)
            EDRLOG.log(u"Cached {}'s outfitting info".format(outfittingId), "DEBUG")
            return outfittingInfo

        self.edsm_outfittings_cache.set(outfittingId, None)
        EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None


    def station(self, star_system, station_name, station_type):
        stations = self.stations_in_system(star_system)
        if not stations:
            return None
            
        for station in stations:
            if station["name"] == station_name:
                return station
        
        worth_retrying_age = 60*60*6 
        if station_type == "FleetCarrier" and self.edsm_stations_cache.is_older_than(star_system.lower(), worth_retrying_age):
            # FleetCarrier are a bit more dynamic, so evict a lukewarm entry and get a new fresh one in case the info has been reflected since last time
            self.edsm_stations_cache.evict(star_system.lower())
            stations = self.stations_in_system(star_system)
            for station in stations:
                if station["name"] == station_name:
                    return station
        
        return None

    def materials_info(self, system_name, body_name, info):
        if not system_name or not body_name:
            return None

        self.materials_cache.set(u"{}:{}".format(system_name.lower(), body_name.lower()), info)

    def describe_body(self, system_name, body_name, current_system=True):
        belt = bool(re.match(r"^(.*) \S+ (?:Belt Cluster [0-9]+)$", body_name))
        ring = body_name.endswith("Ring") # TODO check if this one also has "Ring Cluster/something number"
        adj_body_name = body_name
        if belt or ring:
            m = re.match(r"^(.*) \S+ (?:Belt Cluster [0-9]+|Ring)$", body_name)
            adj_body_name = m.group(1) if m else body_name

        the_body = self.body(system_name, adj_body_name)
        if not the_body:
            return None
        details = []
        body_type = the_body.get("type", "")
        if belt and "belts" in the_body:
            details.extend(self.__describe_belt(the_body, body_name))
        elif ring and "rings" in the_body:
            details.extend(self.__describe_ring(the_body, body_name))
        elif body_type == "Star":
            if current_system:
                details.extend(self.__describe_star(the_body, system_name))
            else:
                details.extend(self.describe_system(system_name, current_system))
        elif body_type == "Planet":
            details.extend(self.__describe_planet(the_body, system_name))
        else:
            pass

        if "updateTime" in the_body:
            details.append(_("as of {}  ").format(the_body["updateTime"]))
        
        return details

    @staticmethod
    def __planet_walkable(planet):
        landable = planet.get("isLandable", False)
        walkable = planet.get("surfaceTemperature", 1000) < 800 and planet.get("gravity", 3) < 2.7 and (planet.get("surfacePressure", None) and planet.get("surfacePressure", 1) < 0.1)
        return landable and walkable
    
    def __describe_planet(self, planet, system_name):
        details = []
        info = ""
        body_type = planet.get("type", None)
        sub_type = planet.get("subType", None)
        if sub_type:
            if body_type:
                info += _("{}/{}  ").format(body_type, sub_type)
            else:
                info += _("-/{}  ").format(sub_type)
        elif body_type:
            info += _("{}  ").format(body_type)

        if planet.get("isLandable", False):
            gravity = "{:0.2f}".format(planet["gravity"]) if "gravity" in planet else "-" #TODO not really G? but earth G? verify other field for conversions too
            temperature = "{:0.0f}".format(planet["surfaceTemperature"]) if "surfaceTemperature" in planet else "-"
            land_or_walk =  _("[LAND: {}G; {}K]").format(gravity, temperature)
            if EDRSystems.__planet_walkable(planet):
                land_or_walk = _("[WALK: {}G; {}K]").format(gravity, temperature)
            info += land_or_walk

        if info:
            details.append(info)

        info = ""
        if planet.get("atmosphereType", "No atmosphere") != "No atmosphere":
            atm = " @{:0.1f}".format(planet["atmospherePressure"]) if "atmospherePressure" in planet else ""
            info += "Atm: {}{}  ".format(planet["atmosphereType"], atm)
        
        if planet.get("volcanismType", "No volcanism") != "No volcanism":
            info += _("[{}]").format(planet["volcanismType"])
        
        if info:
            details.append(info)

        value = self.body_value(system_name, planet.get("name", ""))
        if value:
            details.append(_("Max value: {} cr @ {} LS").format(pretty_print_number(value["valueMax"]), pretty_print_number(value["distance"])))

        return details

    def __parent_star(self, system_name, body):
        parents = body.get("parents", [])
        star_parent_id = None
        if not parents:
            return None
        for p in parents:
            if "Star" not in p:
                continue
            star_parent_id = p["Star"]
            break
    
        if star_parent_id is None:
            return None
        return self.__body_with_id(system_name, star_parent_id)
    
    def __body_with_id(self, system_name, body_id):
        if not system_name:
            return None

        bodies = self.edsm_bodies_cache.get(system_name.lower())
        if not bodies:
            bodies = self.edsm_server.bodies(system_name)
            if bodies:
                self.edsm_bodies_cache.set(system_name.lower(), bodies)

        if not bodies:
            return None

        for body in bodies:
            if body.get("bodyId", -1) == body_id:
                return body
        return None
    
    def body_name_with_id(self, system_name, body_id):
        body = self.__body_with_id(system_name, body_id)
        if body:
            return body.get("name", "Unknown")
        return None

    def __maybe_append(self, biome, genuses, species, genus, detected_genuses):
        if detected_genuses is not None and len(detected_genuses) == 0:
            # Scanned but no genuses detected => donn't append anything
            return

        CGENUS_LUT = {
            "aleoids": "$Codex_Ent_Aleoids_Genus_Name;",
            "anemone": "$Codex_Ent_Sphere_Genus_Name;",
            "bacterium": "$Codex_Ent_Bacterial_Genus_Name;",
            "bark mound": "$Codex_Ent_Cone_Genus_Name;",
            "seed": "$Codex_Ent_Seed_Genus_Name;",
            "cactoids": "$Codex_Ent_Cactoid_Genus_Name;",
            "clypeus": "$Codex_Ent_Clypeus_Genus_Name;",
            "conchas": "$Codex_Ent_Conchas_Genus_Name;",
            "electricae": "$Codex_Ent_Electricae_Genus_Name;",
            "fonticulus": "$Codex_Ent_Fonticulus_Genus_Name;",
            "shrubs": "$Codex_Ent_Shrubs_Genus_Name;",
            "fumerolas": "$Codex_Ent_Fumerolas_Genus_Name;",
            "fungoids": "$Codex_Ent_Fungoids_Genus_Name;",
            "osseus": "$Codex_Ent_Osseus_Genus_Name;",
            "recepta": "$Codex_Ent_Recepta_Genus_Name;",
            "sinuous tuber": "$Codex_Ent_Tube_Genus_Name;",
            "stratum": "$Codex_Ent_Stratum_Genus_Name;",
            "tubus": "$Codex_Ent_Tubus_Genus_Name;",
            "tussocks": "$Codex_Ent_Tussocks_Genus_Name;",
            "crystalline shard": "$Codex_Ent_Ground_Struct_Ice_Name;",
            "amphora": "$Codex_Ent_Vents_Name;"
        }
        cgenus = CGENUS_LUT.get(genus.lower(), "unknown")
        if cgenus not in genuses:
            genuses.append(cgenus)

        if not detected_genuses:
            biome.append(species)
        elif cgenus == "unknown":
            EDRLOG.log("Unknown genus: {}".format(genus), "WARNING")
            biome.append(species)
        else:
            for g in detected_genuses:
                if cgenus in g["Genus"]:
                    biome.append(species)
                    break

    def __add_missing_genuses(self, biome, genuses, detected_genuses):
        if detected_genuses is None or len(detected_genuses) == 0:
            return
        
        GENUS_LUT = {
            "$Codex_Ent_Aleoids_Genus_Name;": _("Aleoids"),
            "$Codex_Ent_Sphere_Genus_Name;": _("Anemone"),
            "$Codex_Ent_Bacterial_Genus_Name;": _("Bacterium"),
            "$Codex_Ent_Cone_Genus_Name;": _("Bark mound"),
            "$Codex_Ent_Seed_Genus_Name;": _("Seed"),
            "$Codex_Ent_Cactoid_Genus_Name;": _("Cactoids"),
            "$Codex_Ent_Clypeus_Genus_Name;": _("Clypeus"),
            "$Codex_Ent_Conchas_Genus_Name;": _("Conchas"),
            "$Codex_Ent_Electricae_Genus_Name;": _("Electricae"),
            "$Codex_Ent_Fonticulus_Genus_Name;": _("Fonticulus"),
            "$Codex_Ent_Shrubs_Genus_Name;": _("Shrubs"),
            "$Codex_Ent_Fumerolas_Genus_Name;": _("Fumerolas"),
            "$Codex_Ent_Fungoids_Genus_Name;": _("Fungoids"),
            "$Codex_Ent_Osseus_Genus_Name;": _("Osseus"),
            "$Codex_Ent_Recepta_Genus_Name;": _("Recepta"),
            "$Codex_Ent_Tube_Genus_Name;": _("Sinuous tuber"),
            "$Codex_Ent_Stratum_Genus_Name;": _("Stratum"),
            "$Codex_Ent_Tubus_Genus_Name;": _("Tubus"),
            "$Codex_Ent_Tussocks_Genus_Name;": _("Tussocks"),
            "$Codex_Ent_Ground_Struct_Ice_Name;": _("Crystalline shards"),
            "$Codex_Ent_Vents_Name;": _("Amphora")
        }

        predicted = set(genuses)

        for g in detected_genuses:
            if g["Genus"] not in GENUS_LUT:
                continue
            readable_genus = GENUS_LUT[g["Genus"]]
            if g["Genus"] not in predicted:
                biome.append(readable_genus)


    def __expected_bio_on_planet(self, planet, system_name):
        EDRLOG.log("Expected bio on planet {} in system {}".format(planet.get("name", "???"), system_name), "INFO")
        species = []
        detected_genuses = planet.get("genuses", None)
        genuses = []
        EDRLOG.log("Detected genuses: {}".format(detected_genuses), "INFO")
        atmosphere = planet.get("atmosphereType", "No atmosphere")
        if atmosphere.lower().startswith("thin "):
            atmosphere = atmosphere[len("thin "):]
        atmosphere = atmosphere.replace(" ", "")
        atmosphere = atmosphere.replace("-", "")
        atmosphere = atmosphere.lower()
        EDRLOG.log("Atm: {}".format(atmosphere), "INFO")
        gravity = planet.get("gravity", 100) / 9.81
        EDRLOG.log("Gravity: {}".format(gravity), "INFO")
        mean_temperature = planet.get("surfaceTemperature", 1000)
        EDRLOG.log("Temperature: {}".format(mean_temperature), "INFO")
        planet_class = planet.get("subType", "Unknown").lower()
        planet_class = planet_class.replace("world", "")
        planet_class = planet_class.replace("body", "")
        planet_class = planet_class.replace(" ", "")
        EDRLOG.log("Class: {}".format(planet_class), "INFO")
        luminosity = "???"
        parent_star = self.__parent_star(system_name, planet)
        star_type = "???"
        distance_from_parent_star = planet.get("distanceToArrival", 0)
        if parent_star:
            raw_type = parent_star.get("subType", "???")
            star_type = self.__star_type_lut(raw_type)
            distance_from_parent_star = planet.get("distanceToArrival", 0) - parent_star.get("distanceToArrival", 0)
            luminosity = planet.get("luminosity", "???")
        
        EDRLOG.log("parent star type: {}".format(star_type), "INFO")
        EDRLOG.log("distance from parent star: {}".format(distance_from_parent_star), "INFO")

        if atmosphere == "noatmosphere":
            '''
            Amphora Plant also needs one the following planets types present in the system:
            Earth-Like World
            Ammoniac
            Gas Giant with water based life
            Gas Giant with ammonia based life
            Water Giant
            '''
            if star_type == "A" and planet_class == "metalrich":
                self.__maybe_append(species, genuses, _("Amphora(?)"), "amphora", detected_genuses)
            
            if star_type in ["O", "B"]:
                self.__maybe_append(species, genuses, _("Anemones"), "anemone", detected_genuses)
                
            if star_type in ["A"]:
                self.__maybe_append(species, genuses, _("Anemones(?)"), "anemone", detected_genuses)

            '''
            Planets types: planets with no atmosphere
            In or near a nebula (less than 150 Ly from the centre of the nebula)
            '''
            # species.append(_("Bark mounds(?)"))

            if star_type in ["A", "F", "G", "K", "M", "S"]:
                if mean_temperature < 273 and distance_from_parent_star > 12000:
                    '''
                    TODO check for the presence of any of these:
                        Earth-Like World
                        Ammoniac
                        Gas Giant with water based life
                        Gas Giant with ammonia based life
                        Water Giant
                    '''        
                    self.__maybe_append(species, genuses, _("Crystalline shard(?)"), "crystalline shard", detected_genuses)

            if (planet.get("volcanism","")): 
                '''
                TODO complex, rare....
                Believed to be located near Guardian ruins.
                Type of planet, temperature, presence of an Earth-like world, or a gas giant with water-based life are also extra factors...
                '''
                # species.append(_("Brain trees(??)"))
                
                if planet.get("volcanism", ""):
                    self.__maybe_append(species, genuses, _("Sinuous Tubers(?)"), "sinuous tuber", detected_genuses)
                    
            self.__add_missing_genuses(species, genuses, detected_genuses)
            return {
                "spieces": species,
                "genuses": genuses,
            }
        
        if not EDRSystems.__planet_walkable(planet):
            EDRLOG.log("High gravity or not landable => no bio expected", "INFO")
            self.__add_missing_genuses(species, genuses, detected_genuses)
            return {
                "spieces": species,
                "genuses": genuses,
            }
        
        # TODO color variation (mats or parent star?)
        
        if atmosphere in ["water", "waterrich"]:
            self.__maybe_append(species, genuses, _("Bacterium Cerbrus"), "Bacterium", detected_genuses)
            self.__maybe_append(species, genuses, _("Concha Renibus"), "Conchas", detected_genuses)
            # TODO redo the combos in a constructed manner
            fungoidas = _("Fungoida Gelata")
            fungoidas += "/" + _("Stabitis")
            self.__maybe_append(species, genuses, fungoidas, "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Cactoida Vermis"), "Cactoids", detected_genuses)

            if mean_temperature >= 165:
                if planet_class == "rocky":
                    self.__maybe_append(species, genuses, _("Stratum Paleas"), "Stratum", detected_genuses)
                else:
                    self.__maybe_append(species, genuses, _("Stratum Tectonicas"), "Stratum", detected_genuses)

            
            if mean_temperature >= 190:
                clypeus = _("Clypeus Lacrimam")
                clypeus += "/" + _("Margaritus")
                if parent_star and distance_from_parent_star > 2500:
                    clypeus += "/" + _("Speculumi")
                self.__maybe_append(species, genuses, clypeus, "Clypeus", detected_genuses)

            if planet_class == "rocky":
                self.__maybe_append(species, genuses, _("Frutexa Sponsae"), "Shrubs", detected_genuses)
                self.__maybe_append(species, genuses, _("Osseus Discus"), "Osseus", detected_genuses)
                self.__maybe_append(species, genuses, _("Tussock Virgam"), "tussocks", detected_genuses)
            elif planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses, _("Fumerola Aquatis"), "Fumerolas", detected_genuses)
            elif planet_class == "highmetalcontent":
                self.__maybe_append(species, genuses, _("Osseus Discus"), "Osseus", detected_genuses)
                self.__maybe_append(species, genuses, _("Tussock Virgam"), "tussocks", detected_genuses) # example: Hangu C 2
        elif atmosphere == "helium":
            self.__maybe_append(species, genuses, _("Bacterium Nebulus"), "Bacterium", detected_genuses)
            if star_type == "A" and luminosity.startswith("V"):
                self.__maybe_append(species, genuses, _("Electricae Pluma"), "Electricae", detected_genuses)
            '''
            Electricae radialem (Nebulae)
            '''
        elif atmosphere in ["neon", "neonrich"]:
            self.__maybe_append(species, genuses, _("Fonticulua segmentatus"), "Fonticulus", detected_genuses)
            bacterium = _("Bacterium Acies")
            if planet.get("volcanism","") == "Water":
                bacterium += "/" + _("Verrata")
            elif planet.get("volcanism","") in ["Nitrogen", "Ammonia"]:
                bacterium += "/" + _("Omentum")
            elif planet.get("volcanism","") in ["Carbon", "Methane"]:
                bacterium += "/" + _("Scopulum")
            self.__maybe_append(species, genuses, bacterium, "Bacterium", detected_genuses)

            if star_type == "A" and luminosity.startswith("V"):
                self.__maybe_append(species, genuses, _("Electricae Pluma"), "Electricae", detected_genuses)
            '''
            Electricae radialem (Nebulae)            
            '''
        elif atmosphere in ["argon", "argonrich"]:
            self.__maybe_append(species, genuses, _("Bacterium Vesicula"), "Bacterium", detected_genuses)
            self.__maybe_append(species, genuses, _("Fungoida Bullarum"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Osseus Pumice"), "Osseus", detected_genuses)
            if planet_class == "rocky":
                self.__maybe_append(species, genuses, _("Tussock Capillum"), "tussocks", detected_genuses)
            if atmosphere == "argon" and planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses, _("Fonticulua Campestris"), "Fonticulus", detected_genuses)
            elif atmosphere == "argonrich" and planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses, _("Fonticulua Upupam"), "Fonticulus", detected_genuses)
            if star_type == "A" and luminosity.startswith("V"):
                self.__maybe_append(species, genuses, _("Electricae Pluma"), "Electricae", detected_genuses)
            '''
            Electricae radialem (Nebulae)
            '''
        elif atmosphere in ["methane", "methanerich"]:
            self.__maybe_append(species, genuses, _("Fungoida Setisis"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Osseus Pumice"), "Osseus", detected_genuses)
            self.__maybe_append(species, genuses, _("Bacterium Bullaris"), "Bacterium", detected_genuses)
            if planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses, _("Fonticulua Digitos"), "Fonticulus", detected_genuses)
            elif planet_class == "rocky":
                self.__maybe_append(species, genuses, _("Tussock Capillum"), "tussocks", detected_genuses)
        elif atmosphere == "nitrogen":
            self.__maybe_append(species, genuses, _("Concha Biconcavis"), "Conchas", detected_genuses)
            self.__maybe_append(species, genuses, _("Bacterium Informem"), "Bacterium", detected_genuses)
            if planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses, _("Fonticulua Lapida"), "Fonticulus", detected_genuses)
        elif atmosphere == "oxygen":
            self.__maybe_append(species, genuses, _("Bacterium Volu"), "Bacterium", detected_genuses)
            if planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses, _("Fonticulua Fluctus"), "Fonticulus", detected_genuses)
            elif planet_class == "highmetalcontent" and mean_temperature > 165:
                self.__maybe_append(species, genuses, _("Stratum Tectonicas"), "Stratum", detected_genuses)
        elif atmosphere == "ammonia" and planet_class == "rocky":
            aleoidas = _("Aleoida Laminiae")
            aleoidas += "/" + _("Spica")
            self.__maybe_append(species, genuses, aleoidas, "Aleoids", detected_genuses)
            cactoidas = _("Cactoida Lapis")
            cactoidas += "/" + _("Peperatis")
            self.__maybe_append(species, genuses, cactoidas, "Cactoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Concha Aureolas"), "Conchas", detected_genuses)
            shrubs = _("Frutexa Flabellum")
            shrubs += "/" + _("Flammasis")
            self.__maybe_append(species, genuses, shrubs, "shrubs", detected_genuses)
            self.__maybe_append(species, genuses, _("Fungoida Setisis"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Osseus Spiralis"), "Osseus", detected_genuses)
            tussocks = _("Tussock Catena")
            tussocks += "/" + _("Cultro")
            tussocks += "/" + _("Divisa")
            self.__maybe_append(species, genuses, tussocks, "Tussocks", detected_genuses)
            self.__maybe_append(species, genuses, _("Bacterium Alcyoneum"), "Bacterium", detected_genuses)
            if gravity < 0.15:
                self.__maybe_append(species, genuses, _("Tubus Rosarium"), "Tubus", detected_genuses)
            if mean_temperature > 165:
                stratums = _("Stratum Paleas")
                stratums += "/" + _("Laminamus")
                self.__maybe_append(species, genuses, stratums, "Stratum", detected_genuses)
        elif atmosphere == "ammonia" and planet_class == "highmetalcontent":
            self.__maybe_append(species, genuses, _("Bacterium Alcyoneum"), "Bacterium", detected_genuses)
            aleoidas = _("Aleoida Laminiae")
            aleoidas += "/" + _("Spica")
            self.__maybe_append(species, genuses, aleoidas, "Aleoids", detected_genuses)
            cactoidas = _("Cactoida Lapis")
            cactoidas += "/" + _("Peperatis")
            self.__maybe_append(species, genuses, cactoidas, "Cactoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Concha Aureolas"), "Conchas", detected_genuses)
            self.__maybe_append(species, genuses, _("Frutexa Metallicum"), "Shrubs", detected_genuses)
            self.__maybe_append(species, genuses, _("Fungoida Setisis"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses, _("Osseus Spiralis"), "Osseus", detected_genuses)
            if gravity < 0.15:
                self.__maybe_append(species, genuses, _("Tubus Sororibus"), "Tubus", detected_genuses)
            if mean_temperature > 165:
                self.__maybe_append(species, genuses, _("Stratum Tectonicas"), "Stratum", detected_genuses)
        elif atmosphere in ["carbondioxide", "carbondioxiderich"] and planet_class == "rocky":
            self.__maybe_append(species, genuses, _("Bacterium Aurasus"), "Bacterium", detected_genuses)
            conchas = _("Concha Labiata")
            shrubs = _("Frutexa Acus")
            shrubs += "/" + _("Fera")
            self.__maybe_append(species, genuses, shrubs, "shrubs", detected_genuses)
            tussocks = _("Tussock Propagito")
            tussocks += "/" + _("Pennatis")
            if mean_temperature > 145 and mean_temperature < 155:
                tussocks += "/" + _("Pennata")
            elif mean_temperature > 155 and mean_temperature < 160:
                tussocks += "/" + _("Ventusa")
            elif mean_temperature > 160 and mean_temperature < 170:
                tussocks += "/" + _("Ignis")
            elif mean_temperature > 170 and mean_temperature < 175:
                tussocks += "/" + _("Serrati")
            elif mean_temperature > 175 and mean_temperature < 180:
                tussocks += "/" + _("Albata")
                self.__maybe_append(species, genuses, _("Aleoida Arcus"), "Aleoids", detected_genuses)
            elif mean_temperature > 180 and mean_temperature < 190:
                self.__maybe_append(species, genuses, _("Aleoida Coronamus"), "Aleoids", detected_genuses)
                self.__maybe_append(species, genuses, _("Cactoida Cortexum"), "Cactoids", detected_genuses)
                cactoidas = _("Cactoida Cortexum")
                cactoidas += "/" + _("Pullulanta")
                self.__maybe_append(species, genuses, cactoidas, "cactoids", detected_genuses)
                conchas += "/" + _("Renibus")
                osseuses = _("Osseus Fractus")
                osseuses += "/" + _("Cornibus")
                self.__maybe_append(species, genuses, osseuses, "osseus", detected_genuses)
                tussocks += "/" + _("Caputus")
                fungoidas = _("Fungoida Gelata")
                fungoidas += "/" + _("Stabitis")
                self.__maybe_append(species, genuses, fungoidas, "Fungoids", detected_genuses)
            elif mean_temperature > 180 and mean_temperature < 195:
                cactoidas = _("Cactoida Cortexum")
                cactoidas += "/" + _("Pullulanta")
                self.__maybe_append(species, genuses, cactoidas, "cactoids", detected_genuses)
                conchas += "/" + "Renibus"
                self.__maybe_append(species, genuses, _("Osseus Cornibus"), "Osseus", detected_genuses)
                tussocks += "/" + _("Caputus")
                fungoidas = _("Fungoida Gelata")
                fungoidas += "/" + _("Stabitis")
                self.__maybe_append(species, genuses, fungoidas, "Fungoids", detected_genuses)
            
            if mean_temperature > 160 and mean_temperature < 190 and gravity < 0.15:
                tubus = _("Tubus Cavas")
                tubus += "/" + _("Compagibus")
                tubus += "/" + _("Conifer")
                self.__maybe_append(species, genuses, tubus, "tubus", detected_genuses)
            
            if mean_temperature > 190:
                clypeuses = _("Clypeus Lacrimam")
                clypeuses += "/" + _("Margaritus")
                if distance_from_parent_star > 2500:
                    clypeuses += "/" + _("Speculumi")
                self.__maybe_append(species, genuses, clypeuses, "clypeus", detected_genuses)

                if mean_temperature < 195:
                    self.__maybe_append(species, genuses, _("Aleoida Gravis"), "Aleoids", detected_genuses)
                    self.__maybe_append(species, genuses, _("Osseus Pellebantus"), "Osseus", detected_genuses)
                    self.__maybe_append(species, genuses, _("Aleoida Gravis"), "Aleoids", detected_genuses)
                    tussocks += "/" + _("Triticum")
            
            if mean_temperature > 165:
                stratums = _("Stratum Paleas")
                if  mean_temperature < 190:
                    stratums += "/" + _("Stratum Excutitus")
                else:
                    stratums += "/" + _("Stratum Limaxus")
                    stratums += "/" + _("Stratum Frigus")
                    stratums += "/" + _("Stratum Cucumisis")

            self.__maybe_append(species, genuses, tussocks, "tussocks", detected_genuses)
            self.__maybe_append(species, genuses, conchas, "conchas", detected_genuses)
        elif atmosphere in ["carbondioxide", "carbondioxiderich"] and planet_class == "highmetalcontent":
            self.__maybe_append(species, genuses, _("Bacterium Aurasus"), "Bacterium", detected_genuses)
            self.__maybe_append(species, genuses, _("Frutexa Metallicum"), "Shrubs", detected_genuses)
            if mean_temperature > 175 and mean_temperature < 180:
                self.__maybe_append(species, genuses, _("Aleoida Arcus"), "Aleoids", detected_genuses)
            elif mean_temperature > 180 and mean_temperature < 190:
                self.__maybe_append(species, genuses, _("Aleoida Coronamus"), "Aleoids", detected_genuses)
            elif mean_temperature > 190 and mean_temperature < 195:
                self.__maybe_append(species, genuses, _("Aleoida Gravis"), "Aleoids", detected_genuses)
            
            if mean_temperature > 180 and  mean_temperature < 195:
                cactoidas = _("Cactoida Cortexum")
                cactoidas += "/" + _("Pullulanta")
                self.__maybe_append(species, genuses, cactoidas, "Cactoids", detected_genuses)                
            
            conchas = None
            if mean_temperature > 180 and mean_temperature < 195:
                conchas = _("Concha Renibus")
                fungoidas = _("Fungoida Gelata")
                fungoidas += "/" + _("Stabitis")
                self.__maybe_append(species, genuses, fungoidas, "fungoids", detected_genuses)

            if mean_temperature < 190:
                if conchas:
                    conchas += "/" + _("Labiata")
                else:
                    conchas = _("Concha Labiata")
            if conchas:
                self.__maybe_append(species, genuses, conchas, "conchas", detected_genuses)

            osseuses = None
            if mean_temperature > 180:
                if mean_temperature < 195:
                    osseuses = _("Osseus Cornibus")
                    if mean_temperature > 190:
                        osseuses += "/" + _("Pellebantus")
                if mean_temperature < 190:
                    if osseuses:
                        osseuses = _("Osseus Fractus")
                    else:
                        osseuses += "/" + _("Fractus")
            if osseuses:
                self.__maybe_append(species, genuses, osseuses, "osseus", detected_genuses)
            
            if mean_temperature > 160 and mean_temperature < 190 and gravity < 0.15:
                self.__maybe_append(species, genuses, _("Tubus Sororibus"), "tubus", detected_genuses)

            if mean_temperature > 190:
                clypeuses = _("Clypeus Lacrimam")
                clypeuses += "/" + _("Margaritus")
                if distance_from_parent_star > 2500:
                    clypeuses += "/" + _("Speculumi")
                self.__maybe_append(species, genuses, clypeuses, "clypeus", detected_genuses)
            
            if mean_temperature > 165:
                self.__maybe_append(species, genuses, _("Stratum Tectonicas"), "stratum", detected_genuses)
        elif atmosphere == "sulphurdioxide" and planet_class in ["icy", "rockyice"]:
            receptas = _("Recepta Umbrux")
            receptas += "/" + _("Conditivus")
            self.__maybe_append(species, genuses, receptas, "Recepta", detected_genuses)
            self.__maybe_append(species, genuses, _("Bacterium Cerbrus"), "Bacterium", detected_genuses)
        elif atmosphere == "sulphurdioxide" and planet_class in ["icy", "rockyice"]:
            self.__maybe_append(species, genuses, _("Frutexa Collum"), "Shrubs", detected_genuses)
            receptas = _("Recepta Deltahedronix")
            receptas += "/" + _("Umbrux")
            self.__maybe_append(species, genuses, receptas, "Recepta", detected_genuses)
            self.__maybe_append(species, genuses, _("Tussock Stigmasis"), "tussocks", detected_genuses)
            bacterium = _("Bacterium Cerbrus")
            if mean_temperature > 165:
                self.__maybe_append(species, genuses, _("Stratum Araneamus"), "Stratum", detected_genuses)
                if mean_temperature <  190:
                    bacterium += "/" + _("Excutitus")
                    bacterium += "/" + _("Limaxus")
                if mean_temperature > 190:
                    bacterium += "/" + _("Frigus")
                    bacterium += "/" + _("Cucumisis")
            self.__maybe_append(species, genuses, bacterium, "Bacterium", detected_genuses)
        elif atmosphere == "sulphurdioxide" and planet_class == "highmetalcontent":
            receptas = _("Recepta Deltahedronix")
            receptas += "/" + _("Umbrux")
            self.__maybe_append(species, genuses, receptas, "Recepta", detected_genuses)
            self.__maybe_append(species, genuses, _("Bacterium Cerbrus"), "Bacterium", detected_genuses)
            if mean_temperature > 165:
                self.__maybe_append(species, genuses, _("Stratum Tectonicas"), "Stratum", detected_genuses)

        self.__add_missing_genuses(species, genuses, detected_genuses)
        
        EDRLOG.log("Species: {}".format(species), "INFO")
        EDRLOG.log("Genuses: {}".format(genuses), "INFO")
        
        return {
            "species": species,
            "genuses": genuses,
        }


    def __describe_belt(self, body, belt_full_name):
        # TODO not really working yet
        # TODO rings are within a given body's bag of stuff under "belts"
        belts = body.get("belts", [])
        the_belt = None
        for b in belts:
            if b.get("name", "").lower().endswith("belt"):
                if belt_full_name.startswith(b.get("name", "NO NAME FOR THAT BELT")):
                    the_belt = b
                    break
            else:
                if b.get("name", None) == belt_full_name:
                    the_belt = b
                    break
            
        if not the_belt:
            return [_("Unknown belt")]
        return [_("Type: {}").format(the_belt.get("type", "???"))]

    def __describe_ring(self, body, ring_full_name):
        # TODO not really working yet, that said it doesn't look possible to target a ring...
        # TODO rings are within a given body's bag of stuff under "rings"        
        rings = body.get("rings", [])
        the_ring = None
        for r in rings:
            if rings[r].get("name", None) == ring_full_name:
                the_ring = rings[r]
                break
        if not the_ring:
            return [_("Unknown ring")]
        return [_("Type: {} {}").format(the_ring.get("type", "???"), the_ring.get("reserveLevel", ""))]


    def materials_on(self, system_name, body_name):
        if not system_name or not body_name:
            return None

        materials = self.materials_cache.get(u"{}:{}".format(system_name.lower(), body_name.lower()))
        if not materials:
            the_body = self.body(system_name, body_name)
            if not the_body:
                return None
            raw_materials = the_body.get("materials", None)
            if raw_materials:
                materials = [{"Name": key, "Percent": value} for key,value in raw_materials.items()]
                self.materials_info(system_name, body_name, materials)
            else:
                return None
            
        return materials

    def biology_on(self, system_name, body_name):
        if not system_name or not body_name:
            return None

        the_body = self.body(system_name, body_name)
        if not the_body:
            EDRLOG.log("No body for biology on: {}".format(system_name, body_name), "INFO")
            return {}
        return self.__expected_bio_on_planet(the_body, system_name)
        

    def reflect_scan(self, system_name, body_name, scan):
        if "belt cluster" in body_name.lower():
            return
        
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = []
        
        the_body = None
        for b in bodies:
            if b.get("name", "").lower() == body_name.lower():
                the_body = b
                break
                
        new_body = the_body is None
        if new_body:
            the_body = {}
        
        kv_lut = {
            "DistanceFromArrivalLS": {"k": "distanceToArrival", "v": lambda v: v},
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "event": None,
            "ScanType": None,
            "BodyName": {"k": "name", "v": lambda v: v},
            "BodyID": {"k": "bodyId", "v": lambda v: v},
            "StarSystem": None,
            "SystemAddress": None,
            "StarType": {"k": "type", "v": lambda v: v},
            "StellarMass": {"k": "solarMasses", "v": lambda v: v},
            "Age_MY": {"k": "age", "v": lambda v: v},
            "Luminosity": None,
            "SemiMajorAxis": {"k": "semiMajorAxis", "v": lambda v: v/149597870700},
            "Eccentricity": {"k": "orbitalEccentricity", "v": lambda v: v},
            "Periapsis": {"k": "argOfPeriapsis", "v": lambda v: v},
            "OrbitalPeriod": {"k": "orbitalPeriod", "v": lambda v: v/86400},
            "RotationPeriod": {"k": "rotationalPeriod", "v": lambda v: v/86400},
            "Landable": {"k": "isLandable", "v": lambda v: v},
            "Materials": {"k": "materials", "v": lambda v: {np["Name"]: np["Percent"] for np in v}},
            "AtmosphereComposition": {"k": "atmosphereComposition", "v": lambda v: {np["Name"]: np["Percent"] for np in v}},
            "SurfaceGravity": {"k": "gravity", "v": lambda v: v/9.79761064137},
            "MassEM":  {"k": "earthMasses", "v": lambda v: v},
            "TidalLock":  {"k": "rotationalPeriodTidallyLocked", "v": lambda v: v},
            "TerraformState": {"k": "terraformingState", "v": lambda v: v if v else "Not terraformable"},
            "Volcanism": {"k": "volcanismType", "v": lambda v: v if v else "No volcanism"},
            "AtmosphereType": {"k": "atmosphereType", "v": lambda v: v if v and v != "None" else "No atmosphere"},
            "Composition": {"k": "solidComposition", "v": lambda v: {m:p*100 for m,p in v.items()} if v else None},
            "PlanetClass": {"k": "subType", "v": lambda v: v},
            "StarType": {"k": "subType", "v": lambda v: v},
            "SurfacePressure": {"k": "surfacePressure", "v": lambda v: v/101325},
            "WasDiscovered": {"k": "wasDiscovered", "v": lambda v: v},
            "WasMapped": {"k": "wasMapped", "v": lambda v: v},
        }
        # TODO rings
        adj_kv = lambda k: kv_lut[k] if k in kv_lut else ({"k": k[:1].lower() + k[1:], "v": lambda v: v} if k else None)
        
        for key in scan:
            new_kv = adj_kv(key)
            if new_kv:
                the_body[new_kv["k"]] = new_kv["v"](scan[key])

        the_body["scanned"] = True

        if "PlanetClass" in scan:
            the_body["type"] = "Planet"
            the_body["radius"] = scan["Radius"]/1000 if scan.get("Radius", None) else None
        elif "StarType" in scan:
            the_body["type"] = "Star"
            the_body["isScoopable"] = the_body.get("subType", "") in ["O","B","A", "F", "G", "K", "M"]
            the_body["solarRadius"] = scan["Radius"]/695500000 if scan.get("Radius", None) else None
        if new_body:
            bodies.append(the_body)
        else:
            pass
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def reflect_organic_scan(self, system_name, body_id, scan):
        if scan["event"] != "ScanOrganic" and scan["ScanType"] != "Analyse":
            return
        
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = []
        
        the_body = None
        for b in bodies:
            if b.get("bodyId", -1) == body_id:
                the_body = b
                break
                
        new_body = the_body is None
        if new_body:
            the_body = {}

        kv_lut = {
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "event": None,
            "ScanType": None,
            "Body": {"k": "bodyId", "v": lambda v: v},
            "SystemAddress": None,
            "Genus": None,
            "Genus_Localised": None,
            "Species": None,
            "Species_Localised": None
        }
        adj_kv = lambda k: kv_lut[k] if k in kv_lut else ({"k": k[:1].lower() + k[1:], "v": lambda v: v} if k else None)
        
        for key in scan:
            new_kv = adj_kv(key)
            if new_kv:
                the_body[new_kv["k"]] = new_kv["v"](scan[key])

        if "species" not in the_body:
            the_body["species"] = {}
        
        the_body["species"][scan["Species"]] = {"genus": scan["Genus"], "genusLocalised": scan["Genus_Localised"], "speciesLocalised": scan["Species_Localised"]}
        
        if new_body:
            bodies.append(the_body)
        else:
            pass
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)
    
    def analyzed_biome(self, star_system, body_id_or_name):
        planet = self.__body_with_id(star_system, body_id_or_name) or self.body(star_system, body_id_or_name)
        if not planet:
            return
        
        body_name = planet.get("name", None)
        if body_name is None:
            return
        biome = self.biology_on(star_system, body_name)
        detected_genuses = len(planet.get("genuses", []))
        expected_genuses = len(biome.get("genuses", [])) 
        actual_genuses = set()
        actual_species = set()
        species = planet.get("species", {})
        for s in species:
            actual_genuses.add(species[s]["genusLocalised"])
            actual_species.add(species[s]["speciesLocalised"])
        analyzed_genuses = len(actual_genuses)
        analyzed_species = len(actual_species)
        
        return {
            "genuses": {
                "detected": detected_genuses,
                "expected": expected_genuses,
                "analyzed": analyzed_genuses,
                "localized": actual_genuses
            },
            "species": {
                "analyzed": analyzed_species,
                "localized": actual_species
            }
        }


    def body(self, system_name, body_name):
        if not system_name or not body_name:
            return None

        bodies = self.edsm_bodies_cache.get(system_name.lower())
        if not bodies:
            bodies = self.edsm_server.bodies(system_name)
            if bodies:
                self.edsm_bodies_cache.set(system_name.lower(), bodies)

        if not bodies:
            return None

        for body in bodies:
            if body.get("name", "").lower() == body_name.lower():
                return body
        return None

    def bodies(self, system_name):
        if not system_name:
            return None

        bodies = self.edsm_bodies_cache.get(system_name.lower())
        if not bodies:
            bodies = self.edsm_server.bodies(system_name)
            if bodies:
                self.edsm_bodies_cache.set(system_name.lower(), bodies)

        return bodies

    def fss_discovery_scan_update(self, scan):
        system_name = scan["SystemName"]
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        kv_lut = {
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "event": None,
            "Progress": {"k": "progress", "v": lambda v: v},
            "BodyCount": {"k": "bodyCount", "v": lambda v: v},
            "NonBodyCount": {"k": "nonBodyCount", "v": lambda v: v},
            "SystemName": None,
            "SystemAddress": None,
            "Count": {"k": "bodyCount", "v": lambda v: v},
        }
        adj_kv = lambda k: kv_lut[k] if k in kv_lut else ({"k": k[:1].lower() + k[1:], "v": lambda v: v} if k else None)
        
        for key in scan:
            new_kv = adj_kv(key)
            if new_kv:
                bodies[0][new_kv["k"]] = new_kv["v"](scan[key])

        if scan["event"] == "FSSAllBodiesFound":
            bodies[0]["progress"] = 1.0
            bodies[0]["bodyCount"] = scan["Count"]

        self.edsm_bodies_cache.set(system_name.lower(), bodies)
        
    def saa_scan_complete(self, system_name, scan):
        body_name = scan.get("BodyName", None)
        if not body_name:
            return
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = []
        
        the_body = None
        for b in bodies:
            if b.get("name", "").lower() == body_name.lower():
                the_body = b
                break
                
        new_body = the_body is None
        if new_body:
            the_body = {}
        
        kv_lut = {
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "event": None,
            "BodyName": {"k": "name", "v": lambda v: v},
            "BodyID": {"k": "bodyId", "v": lambda v: v},
            "SystemAddress": None,
        }
        
        adj_kv = lambda k: kv_lut[k] if k in kv_lut else ({"k": k[:1].lower() + k[1:], "v": lambda v: v} if k else None)
        
        for key in scan:
            new_kv = adj_kv(key)
            if new_kv:
                the_body[new_kv["k"]] = new_kv["v"](scan[key])

        the_body["wasEfficient"] = scan["ProbesUsed"] <= scan["EfficiencyTarget"]
        the_body["mapped"] = True
        
        if new_body:
            bodies.append(the_body)
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def saa_signals_found(self, system_name, scan):
        body_name = scan.get("BodyName", None)
        if not body_name:
            return
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = []
        
        the_body = None
        for b in bodies:
            if b.get("name", "").lower() == body_name.lower():
                the_body = b
                break
                
        new_body = the_body is None
        if new_body:
            the_body = {}
        
        kv_lut = {
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "event": None,
            "BodyName": {"k": "name", "v": lambda v: v},
            "BodyID": {"k": "bodyId", "v": lambda v: v},
            "SystemAddress": None,
        }
        
        adj_kv = lambda k: kv_lut[k] if k in kv_lut else ({"k": k[:1].lower() + k[1:], "v": lambda v: v} if k else None)
        
        for key in scan:
            new_kv = adj_kv(key)
            if new_kv:
                the_body[new_kv["k"]] = new_kv["v"](scan[key])

        if new_body:
            bodies.append(the_body)
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)


    def are_factions_stale(self, star_system):
        if not star_system:
            return False
        return self.edsm_factions_cache.is_stale(star_system.lower())

    def __factions(self, star_system):
        if not star_system:
            return None
        factions = self.edsm_factions_cache.get(star_system.lower())
        cached = self.edsm_factions_cache.has_key(star_system.lower())
        if cached or factions:
            EDRLOG.log(u"Factions for system {} are in the cache.".format(star_system), "DEBUG")
            return factions

        EDRLOG.log(u"Factions for system {} are NOT in the cache.".format(star_system), "DEBUG")
        factions = self.edsm_server.factions_in_system(star_system)
        if factions:
            self.edsm_factions_cache.set(star_system.lower(), factions)
            EDRLOG.log(u"Cached {}'s factions".format(star_system), "DEBUG")
            return factions

        self.edsm_factions_cache.set(star_system.lower(), None)
        EDRLOG.log(u"No match on EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None

    def system_state(self, star_system):
        factions = self.__factions(star_system)
        if not factions:
            return (None, None)
        
        if not factions.get('controllingFaction', None) or not factions.get('factions', None):
            EDRLOG.log(u"Badly formed factions data for system {}.".format(star_system), "INFO")
            return (None, None)

        controlling_faction_id = factions['controllingFaction']['id']
        all_factions = factions['factions']
        state = None
        updated = None
        for faction in all_factions:
            if faction['id'] == controlling_faction_id:
                state = faction['state']
                updated = faction['lastUpdate']
                break

        return (state, updated)

    def system_value(self, system_name):
        value = self.edsm_system_values_cache.get(system_name.lower())
        if not value:
            value = self.edsm_server.system_value(system_name)
            if value:
                self.edsm_system_values_cache.set(system_name.lower(), value)
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        body_values = {b["bodyName"]: b for b in value.get("valuableBodies", [])}
        totalMappedValue = 0
        totalHonkValue = 0
        for body in bodies:
            valueMax = None
            valueScanned = None
            if body.get("type", "").lower() == "star":
                valueMax = self.__star_value(body)
                valueScanned = valueMax
            else:
                valueMax = self.__body_value(body)
                valueScanned = self.__body_value(body, False)
            body_name = body.get("name", None)
            if body_name and valueMax is not None:
                if body_name in body_values:
                    body_values[body_name]["valueMax"] = valueMax
                    body_values[body_name]["valueScanned"] = valueScanned
                else:
                    body_values[body_name] = {
                        "bodyId":body.get("bodyId", None),
                        "bodyName": body_name,
                        "distance": round(body.get("distanceToArrival", None)),
                        "valueMax": valueMax,
                        "valueScanned": valueScanned,
                    }
                flags = {key: value for key, value in body.items() if key in ["wasDiscovered", "wasMapped", "mapped", "scanned"]}
                body_values[body_name].update(flags)
                totalMappedValue += valueMax
            
            if valueScanned is not None:
                totalHonkValue += valueScanned

        valuable_bodies = sorted(body_values.values(), key=lambda s: s['valueMax'], reverse=True)
        if value:
            value["estimatedValue"] = max(value["estimatedValue"], totalHonkValue)
            value["estimatedValueMapped"] = max(value["estimatedValueMapped"], totalMappedValue)
            value["valuableBodies"] = valuable_bodies
        else:
            value = {
                "name": system_name,
                "estimatedValue": totalHonkValue,
                "estimatedValue": totalMappedValue,
                "valuableBodies": valuable_bodies,
            }

        if "bodyCount" in bodies[0]:
            value["bodyCount"] = max(bodies[0]["bodyCount"], len(bodies))
            if "progress" in bodies[0]:
                value["progress"] = bodies[0]["progress"]

        return value

    def body_value(self, system_name, body_name):
        system_value = self.system_value(system_name)
        if not system_value:
            return None
        
        value = None
        for body in system_value.get("valuableBodies", []):
            # if body.get("bodyName", None) == body_name:
            if body.get("name", None) == body_name:
                value = body

        if value is None:
            value={}
        
        the_body = self.body(system_name, body_name)
        if the_body:
            valueMax = "?"
            if the_body.get("type", "").lower() == "star":
                valueMax = self.__star_value(the_body)
                value["valueScanned"] = valueMax
            else:
                valueMax = self.__body_value(the_body)
                value["valueScanned"] = self.__body_value(the_body, False)
            
            
            value["bodyId"] = the_body.get("bodyId", None)
            value["bodyName"] = body_name
            value["distance"] = round(the_body.get("distanceToArrival", None))
            value["valueMax"] = valueMax

            if "wasDiscovered" in the_body:
                value["wasDiscovered"] = the_body["wasDiscovered"]

            if "wasMapped" in the_body:
                value["wasMapped"] = the_body["wasMapped"]

            if "wasEfficient" in the_body:
                value["wasEfficient"] = the_body["wasEfficient"]
        return value
        
    @staticmethod
    def __star_value(the_body, bonus=True):
        type = the_body.get("subType", "")
        mass = the_body.get("solarMasses", 0)
        first_discoverer = not the_body.get("wasDiscovered", False)
        
        if not type:
            return None
        if "white dwarf" in type.lower() or type.lower in ["d", "da", "dab", "dao", "daz", "dav", "db", "dbz", "dbv", "do", "dov", "dq", "dc", "dcv", "dx"]:
            type = "white dwarf"
        elif type.lower() == "n":
            type = "neutron star"
        elif type.lower() == "h" or type.lower() == "supermassiveblackhole":
            type = "black hole"
        k_lut = {"black hole": 22628, "neutron star": 22628, "white dwarf": 14057}
        k = k_lut.get(type.lower(), 1200)
        honk_bonus_value = 0
        if bonus:
            q = 0.56591828
            honk_bonus_value = max(500,(k + k * q * pow(mass,0.2)) / 3 )
            honk_bonus_value *= 2.6 if first_discoverer else 1
        value = round((k + (mass * k / 66.25)) + honk_bonus_value)
        return value

    def __body_value(self, the_body, override_mapped=True):
        type = the_body.get("subType", "")
        mass = the_body.get("earthMasses", 0)
        terraformability = 1.0 if the_body.get("terraformingState", "") == "Terraformed" else 0.0
        first_discoverer = not the_body.get("wasDiscovered", False)
        
        mapped = override_mapped
        first_mapped = not the_body.get("wasMapped", False) if mapped else False
        efficiency_bonus = the_body.get("wasEfficient", True) if mapped else False
        k_lut = {
                "metal-rich body": 21790,
                "metal rich body": 21790,
                "ammonia world": 96932,
                "sudarsky class i gas giant": 1656,
                "sudarsky class ii gas giant": 9654 + terraformability * 100677,
                "class i gas giant": 1656,
                "class ii gas giant": 9654 + terraformability * 100677,
                "high metal content world":  9654 + terraformability * 100677,
                "high metal content body":  9654 + terraformability * 100677,
                "water world": 64831 + terraformability * 116295,
                "earth-like world": 64831 + terraformability * 116295,
                "earthlike body": 64831 + terraformability * 116295
        }
        k = 300 + terraformability * 93328
        k = k_lut.get(type.lower(), k)
        q = 0.56591828
        mapping_multiplier = 1
        if mapped:
            if first_discoverer and first_mapped:
                mapping_multiplier = 3.699622554
            elif first_mapped:
                mapping_multiplier = 8.0956
            else:
                mapping_multiplier = 3.3333333333
        value = (k + k * q * pow(mass,0.2)) * mapping_multiplier
        
        if mapped:
            if self.dlc_name and self.dlc_name.lower()  == "odyssey":
                value += max(value * 0.3, 555)
                
            
            if efficiency_bonus:
                value *= 1.25
                
        value = max(500, value)
        if first_discoverer:
            value *= 2.6
            
        value = round(value)
        return value


    def system_allegiance(self, star_system):
        factions = self.__factions(star_system)
        if not factions:
            return None
        
        if not factions.get('controllingFaction', None):
            EDRLOG.log(u"Badly formed factions data for system {}.".format(star_system), "INFO")
            return None

        return factions['controllingFaction'].get('allegiance', None)

    def transfer_time(self, origin, destination):
        dist = self.distance(origin, destination)
        return edtime.EDTime.transfer_time(dist)

    def jumping_time(self, origin, destination, jump_range, seconds_per_jump = 55):
        dist = self.distance(origin, destination)
        return int(ceil(dist / jump_range) * seconds_per_jump)

    def timespan_s(self):
        return edtime.EDTime.pretty_print_timespan(self.timespan, short=True, verbose=True)

    def crimes_t_minus(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if "latestCrime" in system_reports:
                return edtime.EDTime.t_minus(system_reports["latestCrime"])
        return None

    def traffic_t_minus(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if "latestTraffic" in system_reports:
                return edtime.EDTime.t_minus(system_reports["latestTraffic"])
        return None
    
    def has_sitrep(self, star_system):
        if not star_system:
            return False
        self.__update_if_stale()
        sid = self.system_id(star_system)
        return self.sitreps_cache.has_key(sid)

    def has_notams(self, star_system, may_create=False, coords=None):
        self.__update_if_stale()
        sid = self.system_id(star_system, may_create, coords)
        return self.notams_cache.has_key(sid)

    def __has_active_notams(self, system_id):
        self.__update_if_stale()
        if not self.notams_cache.has_key(system_id):
            return False
        return len(self.__active_notams_for_sid(system_id)) > 0

    def active_notams(self, star_system, may_create=False, coords=None):
        if self.has_notams(star_system, may_create, coords=None):
            return self.__active_notams_for_sid(self.system_id(star_system))
        return None

    def __active_notams_for_sid(self, system_id):
        active_notams = []
        entry = self.notams_cache.get(system_id)
        all_notams = entry.get("NOTAMs", {})
        js_epoch_now = edtime.EDTime.js_epoch_now()
        for notam in all_notams:
            active = True
            if "from" in notam:
                active &= notam["from"] <= js_epoch_now
            if "until" in notam:
                active &= js_epoch_now <= notam["until"]
            if active and "text" in notam:
                EDRLOG.log(u"Active NOTAM: {}".format(notam["text"]), "DEBUG")
                active_notams.append(_edr(notam["text"]))
            elif active and "l10n" in notam:
                EDRLOG.log(u"Active NOTAM: {}".format(notam["l10n"]["default"]), "DEBUG")
                active_notams.append(_edr(notam["l10n"]))
        return active_notams

    def systems_with_active_notams(self):
        summary = []
        self.__update_if_stale()
        systems_ids = list(self.notams_cache.keys()).copy()
        for sid in systems_ids:
            entry = self.notams_cache.get(sid)
            if not entry:
                continue 
            star_system = entry.get("name", None)
            if star_system and self.__has_active_notams(sid):
                summary.append(star_system)

        return summary

    def has_recent_activity(self, system_name, pledged_to=None):
        return self.has_recent_traffic(system_name) or self.has_recent_crimes(system_name) or self.has_recent_outlaws(system_name) or pledged_to and self.has_recent_enemies(system_name, pledged_to)

    def systems_with_recent_activity(self, pledged_to=None):
        systems_with_recent_crimes = {}
        systems_with_recent_traffic = {}
        systems_with_recent_outlaws = {}
        systems_with_recent_enemies = {}
        self.__update_if_stale()
        systems_ids = (list(self.sitreps_cache.keys())).copy()
        for sid in systems_ids:
            sitrep = self.sitreps_cache.get(sid)
            star_system = sitrep.get("name", None) if sitrep else None
            if self.has_recent_outlaws(star_system):
                systems_with_recent_outlaws[star_system] = sitrep["latestOutlaw"]
            elif pledged_to and self.has_recent_enemies(star_system, pledged_to):
                latestEnemy = "latestEnemy_{}".format(self.server.nodify(pledged_to))
                systems_with_recent_enemies[star_system] = sitrep[latestEnemy]
            elif self.has_recent_crimes(star_system):
                systems_with_recent_crimes[star_system] = sitrep["latestCrime"]
            elif self.has_recent_traffic(star_system):
                systems_with_recent_traffic[star_system] = sitrep["latestTraffic"]

        summary = {}
        summary_outlaws = []
        systems_with_recent_outlaws = sorted(systems_with_recent_outlaws.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_outlaws:
            summary_outlaws.append(u"{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_outlaws:
            # Translators: this is for the sitreps feature; it's the title of a section to show systems with sighted outlaws 
            summary[_c(u"sitreps section|✪ Outlaws")] = summary_outlaws
        
        if pledged_to:
            summary_enemies = []
            systems_with_recent_enemies = sorted(systems_with_recent_enemies.items(), key=lambda t: t[1], reverse=True)
            for system in systems_with_recent_enemies:
                summary_enemies.append(u"{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
            if summary_enemies:
                # Translators: this is for the sitreps feature; it's the title of a section to show systems with sighted enemies (powerplay) 
                summary[_c(u"sitreps section|✪ Enemies")] = summary_enemies

        summary_crimes = []
        systems_with_recent_crimes = sorted(systems_with_recent_crimes.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_crimes:
            summary_crimes.append(u"{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_crimes:
            # Translators: this is for the sitreps feature; it's the title of a section to show systems with reported crimes
            summary[_c(u"sitreps section|✪ Crimes")] = summary_crimes

        summary_traffic = []
        systems_with_recent_traffic = sorted(systems_with_recent_traffic.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_traffic:
            summary_traffic.append(u"{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_traffic:
            # Translators: this is for the sitreps feature; it's the title of a section to show systems with traffic
            summary[_c(u"sitreps section|✪ Traffic")] = summary_traffic

        return summary

    def has_recent_crimes(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if system_reports is None or "latestCrime" not in system_reports:
                return False

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestCrime"],
                                  edr_config.crimes_recent_threshold())
        return False

    def has_recent_outlaws(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if system_reports is None or "latestOutlaw" not in system_reports:
                return False

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestOutlaw"],
                                  edr_config.opponents_recent_threshold("outlaws"))
        return False
    
    def has_recent_enemies(self, star_system, pledged_to):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            latestEnemy = "latestEnemy_{}".format(self.server.nodify(pledged_to))
            if system_reports is None or latestEnemy not in system_reports:
                return False

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports[latestEnemy],
                                  edr_config.opponents_recent_threshold("enemies"))
        return False

    def recent_crimes(self, star_system):
        sid = self.system_id(star_system)
        if not sid:
            return None
        recent_crimes = None
        if self.has_recent_crimes(star_system):
            if not self.crimes_cache.has_key(sid) or (self.crimes_cache.has_key(sid) and self.crimes_cache.is_stale(sid)):
                recent_crimes = self.server.recent_crimes(sid, self.timespan)
                if recent_crimes:
                    self.crimes_cache.set(sid, recent_crimes)
            else:
                recent_crimes = self.crimes_cache.get(sid)
        return recent_crimes

    def has_recent_traffic(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if system_reports is None or "latestTraffic" not in system_reports:
                return False

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestTraffic"],
                                  edr_config.traffic_recent_threshold())
        return False

    def recent_traffic(self, star_system):
        sid = self.system_id(star_system)
        if not sid:
            return None
        recent_traffic = None
        if self.has_recent_traffic(star_system):
            if not self.traffic_cache.has_key(sid) or (self.traffic_cache.has_key(sid) and self.traffic_cache.is_stale(sid)):
                recent_traffic = self.server.recent_traffic(sid, self.timespan)
                if recent_traffic:
                    self.traffic_cache.set(sid, recent_traffic)
            else:
                recent_traffic = self.traffic_cache.get(sid)
        return recent_traffic

    def summarize_deaths_traffic(self, star_system):
        if not star_system:
            return None

        traffic = self.edsm_traffic_cache.get(star_system.lower())
        if traffic is None:
            traffic = self.edsm_server.traffic(star_system)
        self.edsm_traffic_cache.set(star_system.lower(), traffic)

        deaths = self.edsm_deaths_cache.get(star_system.lower())
        if deaths is None:
            deaths = self.edsm_server.deaths(star_system)
        self.edsm_deaths_cache.set(star_system.lower(), traffic)

        if not deaths and not traffic:
            return None
        
        zero = {"total": 0, "week": 0, "day": 0}
        deaths = {s: pretty_print_number(v) for s, v in deaths.get("deaths", zero).items()}
        traffic = {s: pretty_print_number(v) for s, v in traffic.get("traffic", {}).items()}
        
        if traffic == {}:
            return None

        return "Deaths / Traffic: [Day {}/{}]   [Week {}/{}]  [All {}/{}]".format(deaths.get("day", 0), traffic.get("day"), deaths.get("week", 0), traffic.get("week"), deaths.get("total"), traffic.get("total"))

    def summarize_recent_activity(self, star_system, powerplay=None):
        #TODO refactor/simplify this mess ;)
        summary = {}
        wanted_cmdrs = {}
        enemies = {}
        if self.has_recent_traffic(star_system):
            summary_sighted = []
            recent_traffic = self.recent_traffic(star_system)
            if recent_traffic is not None: # Should always be true... simplify. TODO
                summary_traffic = collections.OrderedDict()
                for traffic in recent_traffic:
                    previous_timestamp = summary_traffic.get(traffic["cmdr"], 0)
                    if traffic["timestamp"] < previous_timestamp:
                        continue
                    karma = traffic.get("karma", 0)
                    if not karma > 0:
                        karma = min(karma, traffic.get("dkarma", 0))
                    bounty = EDFineOrBounty(traffic.get("bounty", 0))
                    enemy = traffic.get("enemy", False)
                    by_pledge = traffic.get("byPledge", None)
                    if karma <= -100 or bounty.is_significant():
                        wanted_cmdrs[traffic["cmdr"]] = [ traffic["timestamp"], karma ]
                    elif powerplay and enemy and powerplay == by_pledge:
                        enemies[traffic["cmdr"]] = [traffic["timestamp"], karma]
                    else:
                        summary_traffic[traffic["cmdr"]] = traffic["timestamp"]
                for cmdr in summary_traffic:
                    summary_sighted.append(u"{} {}".format(cmdr, edtime.EDTime.t_minus(summary_traffic[cmdr], short=True)))
                if summary_sighted:
                    # Translators: this is for the sitrep feature; it's a section to show sighted cmdrs in the system of interest
                    summary[_c(u"sitrep section|✪ Sighted")] = summary_sighted
        
        if self.has_recent_crimes(star_system):
            summary_interdictors = []
            summary_destroyers = []
            recent_crimes = self.recent_crimes(star_system)
            if recent_crimes is not None: # Should always be true... simplify. TODO
                summary_crimes = collections.OrderedDict()
                for crime in recent_crimes:
                    lead_name = crime["criminals"][0]["name"]
                    if lead_name not in summary_crimes or crime["timestamp"] > summary_crimes[lead_name][0]: 
                        summary_crimes[lead_name] = [crime["timestamp"], crime["offence"]]
                        for criminal in crime["criminals"]:
                            previous_timestamp = wanted_cmdrs[criminal["name"]][0] if criminal["name"] in wanted_cmdrs else 0
                            previous_timestamp = max(previous_timestamp, enemies[criminal["name"]][0]) if criminal["name"] in enemies else 0
                            if previous_timestamp > crime["timestamp"]:
                                continue
                            karma = criminal.get("karma", 0)
                            if not karma > 0:
                                karma = min(karma, criminal.get("dkarma", 0))
                            bounty = EDFineOrBounty(criminal.get("bounty", 0))
                            enemy = criminal.get("enemy", False)
                            by_pledge = crime.get("victimPower", None)
                            if karma <= -100 or bounty.is_significant():
                                wanted_cmdrs[criminal["name"]] = [ crime["timestamp"], karma]
                            elif powerplay and enemy and powerplay == by_pledge:
                                enemies[criminal["name"]] = [crime["timestamp"], karma]
                for criminal in summary_crimes:
                    if summary_crimes[criminal][1] == "Murder":
                        summary_destroyers.append(u"{} {}".format(criminal, edtime.EDTime.t_minus(summary_crimes[criminal][0], short=True)))
                    elif summary_crimes[criminal][1] in ["Interdicted", "Interdiction"]:
                        summary_interdictors.append(u"{} {}".format(criminal, edtime.EDTime.t_minus(summary_crimes[criminal][0], short=True)))
                if summary_interdictors:
                    # Translators: this is for the sitrep feature; it's a section to show cmdrs who have been reported as interdicting another cmdr in the system of interest
                    summary[_c(u"sitrep section|✪ Interdictors")] = summary_interdictors
                if summary_destroyers:
                    # Translators: this is for the sitrep feature; it's a section to show cmdrs who have been reported as responsible for destroying the ship of another cmdr in the system of interest; use a judgement-neutral term
                    summary[_c(u"sitreps section|✪ Destroyers")] = summary_destroyers
        
        wanted_cmdrs = sorted(wanted_cmdrs.items(), key=operator.itemgetter(1), reverse=True)
        if wanted_cmdrs:
            summary_wanted = []
            for wanted in wanted_cmdrs:
                summary_wanted.append(u"{} {}".format(wanted[0], edtime.EDTime.t_minus(wanted[1][0], short=True)))
            if summary_wanted:
                # Translators: this is for the sitrep feature; it's a section to show wanted cmdrs who have been sighted in the system of interest
                summary[_c(u"sitreps section|✪ Outlaws")] = summary_wanted
        
        enemies = sorted(enemies.items(), key=operator.itemgetter(1), reverse=True)
        if enemies:
            summary_enemies = []
            for enemy in enemies:
                summary_enemies.append(u"{} {}".format(enemies[0], edtime.EDTime.t_minus(enemies[1][0], short=True)))
            if summary_enemies:
                # Translators: this is for the sitrep feature; it's a section to show enemy cmdrs who have been sighted in the system of interest
                summary[_c(u"sitreps section|✪ Enemies")] = summary_enemies

        return summary

    def recent_outlaws(self, star_system, max_age=3600):
        outlaws = {}
        if self.has_recent_traffic(star_system):
            recent_traffic = self.recent_traffic(star_system)
            if recent_traffic is not None: # Should always be true... simplify. TODO
                for traffic in recent_traffic:
                    previous_timestamp = outlaws[traffic["cmdr"]][0] if traffic["cmdr"] in outlaws else 0
                    if traffic["timestamp"] < previous_timestamp:
                        continue
                    if not self.is_recent(traffic["timestamp"], max_age*1000):
                        continue
                    karma = traffic.get("karma", 0)
                    if not karma > 0:
                        karma = min(karma, traffic.get("dkarma", 0))
                    bounty = EDFineOrBounty(traffic.get("bounty", 0))
                    if karma <= -100 or bounty.is_significant():
                        outlaws[traffic["cmdr"]] = [ traffic["timestamp"], karma ]
        
        if self.has_recent_crimes(star_system):
            recent_crimes = self.recent_crimes(star_system)
            if recent_crimes is not None: # Should always be true... simplify. TODO
                for crime in recent_crimes:
                    for criminal in crime["criminals"]:
                        previous_timestamp = outlaws[criminal["name"]][0] if criminal["name"] in outlaws else 0
                        if previous_timestamp > crime["timestamp"]:
                            continue
                        if not self.is_recent(crime["timestamp"], max_age*1000):
                            continue
                        karma = criminal.get("karma", 0)
                        if not karma > 0:
                            karma = min(karma, criminal.get("dkarma", 0))
                        bounty = EDFineOrBounty(criminal.get("bounty", 0))
                        if karma <= -100 or bounty.is_significant():
                            outlaws[criminal["name"]] = [ crime["timestamp"], karma]
                
        outlaws = collections.OrderedDict(sorted(outlaws.items(), key=lambda kv: kv[1][0], reverse=True))
        return outlaws.keys()

    def search_interstellar_factors(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationServiceCheck('Interstellar Factors Contact')
        checker.name = 'Interstellar Factors Contact'
        checker.hint = 'Look for low security systems, or stations run by an anarchy faction regardless of system security'
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_raw_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRRawTraderCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_encoded_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDREncodedTraderCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_manufactured_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRManufacturedTraderCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_black_market(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRBlackMarketCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_staging_station(self, star_system, callback, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStagingCheck(15)
        self.__search_a_service(star_system, callback, checker, with_large_pad = True, with_medium_pad = False, override_radius = 15, override_sc_distance = override_sc_distance, permits = permits, exclude_center = True)

    def search_parking_system(self, star_system, callback, override_rank = None):
        self.__search_a_parking(star_system, callback, override_radius = 25, override_rank = override_rank)

    def search_rrr_fc(self, star_system, callback, override_radius = None, permits = []):
        radius = override_radius if override_radius is not None and override_radius >= 0 else 0
        sc_dist = 10000
        checker = edrservicecheck.EDRFleetCarrierRRRCheck(radius, sc_dist)
        self.__search_a_service(star_system, callback, checker, override_radius = radius, permits = permits, shuffle_stations=True, override_sc_distance=sc_dist)

    def search_rrr(self, star_system, callback, override_radius = None, permits = []):
        radius = override_radius if override_radius is not None and override_radius >= 0 else 0
        sc_dist = 10000
        checker = edrservicecheck.EDRStationRRRCheck(radius, sc_dist)
        self.__search_a_service(star_system, callback, checker, override_radius = radius, permits = permits, shuffle_stations=True, override_sc_distance=sc_dist)

    def search_shipyard(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationFacilityCheck('Shipyard')
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_outfitting(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationFacilityCheck('Outfitting')
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_market(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationFacilityCheck('Market')
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_human_tech_broker(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRHumanTechBrokerCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_guardian_tech_broker(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRGuardianTechBrokerCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_offbeat_station(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = 100, override_sc_distance = 100000, permits = []):
        checker = edrservicecheck.EDROffBeatStationCheck(override_sc_distance)
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits, shuffle_systems=True, shuffle_stations=True, exclude_center=True)

    def __search_a_service(self, star_system, callback, checker, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = [], shuffle_systems=False, shuffle_stations=False, exclude_center=False):
        sc_distance = override_sc_distance or self.reasonable_sc_distance
        sc_distance = max(250, sc_distance)
        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        radius = min(100, radius)

        finder = edrservicefinder.EDRServiceFinder(star_system, checker, self, callback)
        finder.with_large_pad(with_large_pad)
        finder.with_medium_pad(with_medium_pad)
        finder.within_radius(radius)
        finder.within_supercruise_distance(sc_distance)
        finder.permits_in_possesion(permits)
        finder.shuffling(shuffle_systems, shuffle_stations)
        finder.ignore_center(exclude_center)
        finder.set_dlc(self.dlc_name)
        finder.start()

    def __search_a_parking(self, star_system, callback, override_radius = None, override_rank = None):
        rank = override_rank or 0
        rank = max(0, rank)
        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        radius = min(100, radius)

        finder = edrparkingsystemfinder.EDRParkingSystemFinder(star_system, self, callback)
        finder.within_radius(radius)
        finder.nb_to_pick(rank)
        finder.start()

    def systems_within_radius(self, star_system, override_radius = None):
        if not star_system:
            return None

        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        key = u"{}@{}".format(star_system.lower(), radius)
        systems = self.edsm_systems_within_radius_cache.get(key)
        cached = self.edsm_systems_within_radius_cache.has_key(key)
        if cached:
            if not systems:
                EDRLOG.log(u"Systems within {} of system {} are not available for a while.".format(radius, star_system), "DEBUG")
                return None
            else:
                EDRLOG.log(u"Systems within {} of system {} are in the cache.".format(radius, star_system), "DEBUG")
                return sorted(systems, key = lambda i: i['distance'])

        systems = self.edsm_server.systems_within_radius(star_system, radius)
        if systems:
            systems = sorted(systems, key = lambda i: i['distance']) 
            self.edsm_systems_within_radius_cache.set(key, systems)
            EDRLOG.log(u"Cached systems within {}LY of {}".format(radius, star_system), "DEBUG")
            return systems

        self.edsm_systems_within_radius_cache.set(key, None)
        EDRLOG.log(u"No results from EDSM. Temporary entry to be nice on EDSM's server.", "DEBUG")
        return None

    def is_recent(self, timestamp, max_age):
        if timestamp is None:
            return False
        return (edtime.EDTime.js_epoch_now() - timestamp) / 1000 <= max_age

    def evict(self, star_system):
        try:
            del self.systems_cache[star_system]
        except KeyError:
            pass


    def __are_reports_stale(self):
        return self.__is_stale(self.sitreps_cache.last_updated, self.reports_check_interval)

    def __are_notams_stale(self):
        return self.__is_stale(self.notams_cache.last_updated, self.notams_check_interval)

    def __is_stale(self, updated_at, max_age):
        if updated_at is None:
            return True
        now = datetime.datetime.now()
        epoch_now = time.mktime(now.timetuple())
        epoch_updated = time.mktime(updated_at.timetuple())

        return (epoch_now - epoch_updated) > max_age

    def __update_if_stale(self):
        updated = False
        if self.__are_reports_stale():
            missing_seconds = self.timespan
            now = datetime.datetime.now()
            if self.sitreps_cache.last_updated:
                missing_seconds = min(self.timespan, (now - self.sitreps_cache.last_updated).total_seconds())
            sitreps = self.server.sitreps(missing_seconds)
            if sitreps:
                for system_id in sitreps:
                    self.sitreps_cache.set(system_id, sitreps[system_id])
            self.sitreps_cache.last_updated = now
            updated = True

        if self.__are_notams_stale():
            missing_seconds = self.timespan_notams
            now = datetime.datetime.now()
            if self.notams_cache.last_updated:
                missing_seconds = min(self.timespan_notams, (now - self.notams_cache.last_updated).total_seconds())

            notams = self.server.notams(missing_seconds)
            if notams:
                for system_id in notams:
                    self.notams_cache.set(system_id, notams[system_id])
            self.notams_cache.last_updated = now
            updated = True

        return updated

    def closest_destination(self, sysAndSta1, sysAndSta2, override_sc_distance = None):
        if not sysAndSta1:
            return sysAndSta2

        if not sysAndSta2:
            return sysAndSta1

        sc_distance = override_sc_distance or self.reasonable_sc_distance 

        if sysAndSta1['station']['distanceToArrival'] > sc_distance and sysAndSta2['station']['distanceToArrival'] > sc_distance:
            if abs(sysAndSta1['distance'] - sysAndSta2['distance']) < 5:
                return sysAndSta1 if sysAndSta1['station']['distanceToArrival'] < sysAndSta2['station']['distanceToArrival'] else sysAndSta2
            else:
                return sysAndSta1 if sysAndSta1['distance'] < sysAndSta2['distance'] else sysAndSta2
    
        if sysAndSta1['station']['distanceToArrival'] > sc_distance:
            return sysAndSta2
    
        if sysAndSta2['station']['distanceToArrival'] > sc_distance:
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