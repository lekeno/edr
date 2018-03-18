import os
import pickle

import datetime
import time
import collections
import operator

import edtime
import edrconfig
import edrlog
import lrucache
from edentities import EDBounty

EDRLOG = edrlog.EDRLog()

class EDRSystems(object):
    EDR_SYSTEMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/systems.v2.p')
    EDR_NOTAMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/notams.v2.p')
    EDR_SITREPS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/sitreps.v2.p')
    EDR_TRAFFIC_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/traffic.v2.p')
    EDR_CRIMES_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/crimes.v2.p')

    def __init__(self, server):
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


        self.reports_check_interval = edr_config.reports_check_interval()
        self.notams_check_interval = edr_config.notams_check_interval()
        self.timespan = edr_config.sitreps_timespan()
        self.server = server

    def system_id(self, star_system, may_create=False):
        if not star_system:
            return None
        sid = self.systems_cache.get(star_system.lower())
        if sid:
            EDRLOG.log(u"System {} is in the cache with id={}".format(star_system, sid), "DEBUG")
            return sid

        sid = self.server.system_id(star_system, may_create)
        if sid:
            self.systems_cache.set(star_system.lower(), sid)
            EDRLOG.log(u"Cached {}'s id={}".format(star_system, sid), "DEBUG")
            return sid

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

    def has_notams(self, star_system):
        self.__update_if_stale()
        sid = self.system_id(star_system)
        return self.notams_cache.has_key(sid)

    def __has_active_notams(self, system_id):
        self.__update_if_stale()
        if not self.notams_cache.has_key(system_id):
            return False
        return len(self.__active_notams_for_sid(system_id)) > 0

    def active_notams(self, star_system):
        if self.has_notams(star_system):
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
            if active:
                EDRLOG.log(u"Active NOTAM: {}".format(notam["text"]), "DEBUG")
                active_notams.append(notam["text"])
        return active_notams

    def systems_with_active_notams(self):
        summary = []
        self.__update_if_stale()
        systems_ids = self.notams_cache.keys()
        for sid in systems_ids:
            entry = self.notams_cache.get(sid)
            star_system = entry.get("name", None)
            if star_system and self.__has_active_notams(sid):
                summary.append(star_system)

        return summary

    def has_recent_activity(self, system_name):
        return self.has_recent_traffic(system_name) or self.has_recent_crimes(system_name) or self.has_recent_outlaws(system_name)

    def systems_with_recent_activity(self):
        systems_with_recent_crimes = {}
        systems_with_recent_traffic = {}
        systems_with_recent_outlaws = {}
        self.__update_if_stale()
        systems_ids = self.sitreps_cache.keys()
        for sid in systems_ids:
            sitrep = self.sitreps_cache.get(sid)
            star_system = sitrep.get("name", None)
            if self.has_recent_outlaws(star_system):
                systems_with_recent_outlaws[star_system] = sitrep["latestOutlaw"]
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
            summary[u"Outlaws"] = summary_outlaws

        summary_crimes = []
        systems_with_recent_crimes = sorted(systems_with_recent_crimes.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_crimes:
            summary_crimes.append(u"{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_crimes:
            summary[u"Crimes"] = summary_crimes

        summary_traffic = []
        systems_with_recent_traffic = sorted(systems_with_recent_traffic.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_traffic:
            summary_traffic.append(u"{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_traffic:
            summary[u"Traffic"] = summary_traffic

        return summary

    def has_recent_crimes(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if "latestCrime" not in system_reports:
                return False

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestCrime"],
                                  edr_config.crimes_recent_threshold())
        return False

    def has_recent_outlaws(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.system_id(star_system))
            if "latestOutlaw" not in system_reports:
                return False

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestOutlaw"],
                                  edr_config.outlaws_recent_threshold())
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
            if "latestTraffic" not in system_reports:
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

    def summarize_recent_activity(self, star_system):
        #TODO refactor/simplify this mess ;)
        summary = {}
        wanted_cmdrs = {}
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
                    bounty = EDBounty(traffic.get("bounty", 0))
                    if karma < 0 or bounty.is_significant():
                        wanted_cmdrs[traffic["cmdr"]] = [ traffic["timestamp"], karma ]
                    else:
                        summary_traffic[traffic["cmdr"]] = traffic["timestamp"]
                for cmdr in summary_traffic:
                    summary_sighted.append(u"{} {}".format(cmdr, edtime.EDTime.t_minus(summary_traffic[cmdr], short=True)))
                if summary_sighted:
                    summary[u"Sighted"] = summary_sighted
        
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
                            if previous_timestamp > crime["timestamp"]:
                                continue
                            karma = criminal.get("karma", 0)
                            bounty = EDBounty(traffic.get("bounty", 0))
                            if karma < 0 or bounty.is_significant():
                                wanted_cmdrs[criminal["name"]] = [ crime["timestamp"], karma]
                for criminal in summary_crimes:
                    if summary_crimes[criminal][1] == "Murder":
                        summary_destroyers.append(u"{} {}".format(criminal, edtime.EDTime.t_minus(summary_crimes[criminal][0], short=True)))
                    elif summary_crimes[criminal][1] in ["Interdicted", "Interdiction"]:
                        summary_interdictors.append(u"{} {}".format(criminal, edtime.EDTime.t_minus(summary_crimes[criminal][0], short=True)))
                if summary_interdictors:
                    summary[u"Interdictors"] = summary_interdictors
                if summary_destroyers:
                    summary[u"Destroyers"] = summary_destroyers
        
        wanted_cmdrs = sorted(wanted_cmdrs.items(), key=operator.itemgetter(1), reverse=True)
        if wanted_cmdrs:
            summary_wanted = []
            for wanted in wanted_cmdrs:
                summary_wanted.append(u"{} {}".format(wanted[0], edtime.EDTime.t_minus(wanted[1][0], short=True)))
            if summary_wanted:
                summary[u"Outlaws"] = summary_wanted

        return summary

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
            missing_seconds = self.timespan
            now = datetime.datetime.now()
            if self.notams_cache.last_updated:
                missing_seconds = min(self.timespan, (now - self.notams_cache.last_updated).total_seconds())

            notams = self.server.notams(missing_seconds)
            if notams:
                for system_id in notams:
                    self.notams_cache.set(system_id, notams[system_id])
            self.notams_cache.last_updated = now
            updated = True

        return updated
