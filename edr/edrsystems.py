#!/usr/bin/env python
# coding=utf-8

import os
import pickle
from math import sqrt, ceil

import datetime
import time
import collections
import operator
import threading

import edtime
import edrconfig
import edrlog
import lrucache
import edsmserver
from edentities import EDBounty
from edri18n import _, _c, _edr

EDRLOG = edrlog.EDRLog()

class EDRSystems(object):
    EDR_SYSTEMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/systems.v3.p')
    EDSM_SYSTEMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/edsm_systems.v3.p')
    EDSM_STATIONS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/edsm_stations.v1.p')
    EDSM_SYSTEMS_WITHIN_RADIUS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/edsm_systems_radius.v1.p')
    EDR_NOTAMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/notams.v2.p')
    EDR_SITREPS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/sitreps.v2.p')
    EDR_TRAFFIC_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/traffic.v2.p')
    EDR_CRIMES_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/crimes.v2.p')

    def __init__(self, server):
        self.reasonable_sc_distance = 1500
        self.reasonable_hs_radius = 20
        edr_config = edrconfig.EDRConfig()

        try:
            with open(self.EDR_SYSTEMS_CACHE, 'rb') as handle:
                self.systems_cache = pickle.load(handle)
        except:
            self.systems_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                   edr_config.systems_max_age())

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
            with open(self.EDSM_STATIONS_CACHE, 'rb') as handle:
                self.edsm_stations_cache = pickle.load(handle)
        except:
            self.edsm_stations_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_stations_max_age())

        try:
            with open(self.EDSM_SYSTEMS_WITHIN_RADIUS_CACHE, 'rb') as handle:
                self.edsm_systems_within_radius_cache = pickle.load(handle)
        except:
            self.edsm_systems_within_radius_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.edsm_systems_max_age())

         

        self.reports_check_interval = edr_config.reports_check_interval()
        self.notams_check_interval = edr_config.notams_check_interval()
        self.timespan = edr_config.sitreps_timespan()
        self.timespan_notams = edr_config.notams_timespan()
        self.server = server
        self.edsm_server = edsmserver.EDSMServer()

    def system_id(self, star_system, may_create=False):
        if not star_system:
            return None
        sid = self.systems_cache.get(star_system.lower())
        cached = self.systems_cache.has_key(star_system.lower())
        if cached or sid:
            EDRLOG.log(u"System {} is in the cache with id={}".format(star_system, sid), "DEBUG")
            return sid

        sid = self.server.system_id(star_system, may_create)
        if sid:
            self.systems_cache.set(star_system.lower(), sid)
            EDRLOG.log(u"Cached {}'s id={}".format(star_system, sid), "DEBUG")
            return sid

        self.systems_cache.set(star_system.lower(), None)
        EDRLOG.log(u"No match on EDR. Temporary entry to be nice on EDR's server.", "DEBUG")
        return None

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

        with open(self.EDR_NOTAMS_CACHE, 'wb') as handle:
            pickle.dump(self.notams_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDR_SITREPS_CACHE, 'wb') as handle:
            pickle.dump(self.sitreps_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.EDR_TRAFFIC_CACHE, 'wb') as handle:
            pickle.dump(self.traffic_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_CRIMES_CACHE, 'wb') as handle:
            pickle.dump(self.crimes_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_SYSTEMS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_systems_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_STATIONS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_stations_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDSM_SYSTEMS_WITHIN_RADIUS_CACHE, 'wb') as handle:
            pickle.dump(self.edsm_systems_within_radius_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

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
        
        raise ValueError('Unknown system')

    def transfer_time(self, origin, destination):
        dist = self.distance(origin, destination)
        return int(ceil(dist * 9.75 + 300))

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

    def has_notams(self, star_system, may_create=False):
        self.__update_if_stale()
        sid = self.system_id(star_system, may_create)
        return self.notams_cache.has_key(sid)

    def __has_active_notams(self, system_id):
        self.__update_if_stale()
        if not self.notams_cache.has_key(system_id):
            return False
        return len(self.__active_notams_for_sid(system_id)) > 0

    def active_notams(self, star_system, may_create=False):
        if self.has_notams(star_system, may_create):
            return self.__active_notams_for_sid(self.system_id(star_system))
        return None

    def __active_notams_for_sid(self, system_id):
        active_notams = []
        entry = self.notams_cache.get(system_id)
        all_notams = entry.get("NOTAMs", None)
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
        systems_ids = self.notams_cache.keys()
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
        systems_ids = self.sitreps_cache.keys()
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
                    previous_timestamp = summary_traffic.get(traffic["cmdr"], None)
                    if traffic["timestamp"] < previous_timestamp:
                        continue
                    karma = traffic.get("karma", 0)
                    if not karma > 0:
                        karma = min(karma, traffic.get("dkarma", 0))
                    bounty = EDBounty(traffic.get("bounty", 0))
                    enemy = traffic.get("enemy", False)
                    by_pledge = traffic.get("byPledge", None)
                    if karma < 0 or bounty.is_significant():
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
                            previous_timestamp = wanted_cmdrs[criminal["name"]][0] if criminal["name"] in wanted_cmdrs else None
                            previous_timestamp = max(previous_timestamp, enemies[criminal["name"]][0]) if criminal["name"] in enemies else None
                            if previous_timestamp > crime["timestamp"]:
                                continue
                            karma = criminal.get("karma", 0)
                            if not karma > 0:
                                karma = min(karma, criminal.get("dkarma", 0))
                            bounty = EDBounty(traffic.get("bounty", 0))
                            enemy = traffic.get("enemy", False)
                            by_pledge = traffic.get("byPledge", None)
                            if karma < 0 or bounty.is_significant():
                                wanted_cmdrs[criminal["name"]] = [ crime["timestamp"], karma]
                            elif powerplay and enemy and powerplay == by_pledge:
                                enemies[traffic["cmdr"]] = [traffic["timestamp"], karma]
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

    def search_interstellar_factors(self, star_system, callback, with_large_pad = True, override_radius = None, override_sc_distance = None, permits = []):
        if not (self.in_bubble(star_system) or self.in_colonia(star_system)):
            return None

        sc_distance = override_sc_distance or self.reasonable_sc_distance
        radius = override_radius or self.reasonable_hs_radius

        finder = InterstellarFactorsFinder(star_system, self, callback)
        finder.with_large_pad(with_large_pad)
        finder.within_radius(radius)
        finder.within_supercruise_distance(sc_distance)
        finder.permits_in_possesion(permits)
        finder.start()
        return None


    def systems_within_radius(self, star_system, override_radius = None):
        if not star_system:
            return None

        radius = override_radius or self.reasonable_hs_radius
        key = u"{}@{}".format(star_system.lower(), radius)
        systems = self.edsm_systems_within_radius_cache.get(key)
        cached = self.edsm_systems_within_radius_cache.has_key(key)
        if cached or systems:
            EDRLOG.log(u"Systems within {} of system {} are in the cache.".format(radius, star_system), "DEBUG")
            return systems

        systems = self.edsm_server.systems_within_radius(star_system, radius)
        if systems:
            self.edsm_systems_within_radius_cache.set(key, systems)
            EDRLOG.log(u"Cached systems within {} of {}".format(radius, star_system), "DEBUG")
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

    def in_bubble(self, system_name):
        return self.distance(system_name, 'Sol') <= 500
    
    def in_colonia(self, system_name):
        return self.distance(system_name, 'Colonia') <= 500

class InterstellarFactorsFinder(threading.Thread):

    def __init__(self, star_system, edr_systems, callback):
        self.star_system = star_system
        self.radius = 50
        self.sc_distance = 1500
        self.edr_systems = edr_systems
        self.callback = callback
        self.large_pad_required = True
        self.permits = []
        super(InterstellarFactorsFinder, self).__init__()

    def with_large_pad(self, required):
        self.large_pad_required = required

    def within_radius(self, radius):
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        self.sc_distance = sc_distance

    def permits_in_possesion(self, permits):
        self.permits = permits

    def run(self):
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.sc_distance, results)

    def nearby(self):
        ifactorsPrime = None
        ifactorsAlt = None
        
        system = self.edr_systems.system(self.star_system)
        if not system:
            return None

        system = system[0]
        system['distance'] = 0
        if not system.get('requirePermit', False) or (system['requirePermit'] and system['name'] in self.permits):
            candidate = self.__interstellar_factors_in_system(system)
            if candidate:
                check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
                check_landing_pads = self.__has_large_lading_pads(candidate['type']) if self.large_pad_required else True
                if check_sc_distance and check_landing_pads:
                    ifactorsPrime = system
                    ifactorsPrime['station'] = candidate
                    return ifactorsPrime
                else:
                    ifactorsAlt = system
                    ifactorsAlt['station'] = candidate
        else:
            print "skipping {} as it requires a missing permit".format(system['name'])

        sorted_systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)

        for system in sorted_systems:
            if system['requirePermit'] and not (system['name'] in self.permits):
                print "skipping {} as it requires a missing permit".format(system['name'])
                continue

            candidate = self.__interstellar_factors_in_system(system)
            if candidate:
                check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
                check_landing_pads = self.__has_large_lading_pads(candidate['type']) if self.large_pad_required else True
                if check_sc_distance and check_landing_pads:
                    trialed = system
                    trialed['station'] = candidate
                    closest = self.edr_systems.closest_destination(trialed, ifactorsPrime)
                    ifactorsPrime = closest
                else:
                    trialed = system
                    trialed['station'] = candidate
                    closest = self.edr_systems.closest_destination(trialed, ifactorsAlt)
                    ifactorsAlt = closest

            if ifactorsPrime:
                break

        return ifactorsPrime if ifactorsPrime else ifactorsAlt


    def closest_station_with_ifc(self, stations):
        overall = None
        with_large_landing_pads = None
        for station in stations:
            if (not station['otherServices'] or not 'Interstellar Factors Contact' in station['otherServices']):
                continue

            if overall == None:
                overall = station
            elif station['distanceToArrival'] < overall['distanceToArrival']:
                overall = station
            
            if self.__has_large_lading_pads(station['type']):
                with_large_landing_pads = station
        
        return with_large_landing_pads if self.large_pad_required and with_large_landing_pads else overall


    def __has_large_lading_pads(self, stationType):
        return stationType.lower() in ['coriolis starport', 'ocellus starport', 'orbis starport', 'planetary port', 'asteroid base', 'mega ship']

    def __interstellar_factors_in_system(self, system):
        if not system:
            return None
            
        if system.get('requirePermit', False) and not system['name'] in self.permits :
            return None

        all_stations = self.edr_systems.stations_in_system(system['name'])
        if not all_stations or not len(all_stations):
            return None

        return self.closest_station_with_ifc(all_stations)

    def close(self):
        # TODO
        return None