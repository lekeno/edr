import os
import pickle

import datetime
import time
import calendar

import edrconfig
import edrlog
import lrucache

EDRLOG = edrlog.EDRLog()

class EDRSystems(object):
    EDR_SYSTEMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/systems.p')

    EDR_NOTAMS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/notams.p')

    def __init__(self, server):
        edr_config = edrconfig.EDRConfig()

        try:
            with open(self.EDR_SYSTEMS_CACHE, 'rb') as handle:
                self.systems_cache = pickle.load(handle)
        except IOError:
            self.systems_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                   edr_config.systems_max_age())

        try:
            with open(self.EDR_NOTAMS_CACHE, 'rb') as handle:
                self.notams_cache = pickle.load(handle)
        except IOError:
            self.notams_cache = lrucache.LRUCache(edr_config.lru_max_size(),
                                                  edr_config.notams_max_age())

        #TODO use notams_cache
        #TODO keep track of last updated from the cache instead of always starting from scratch

        #TODO use a cache for reports, probably repurpose the systems_cache
        #TODO keep track of last updated from the cache instead of always starting from scratch

        self.reports_check_interval = edr_config.reports_check_interval()
        self.notams_check_interval = edr_config.notams_check_interval()
        self.timespan = edr_config.sitreps_timespan()
        self.reports_last_updated = None
        self.notams_last_updated = None
        self.reports = {}
        self.notams = {}
        self.server = server

    def system_id(self, star_system, may_create=False):
        sid = self.systems_cache.get(star_system.lower())
        if not sid is None:
            EDRLOG.log(u"System {} is in the cache with id={}".format(star_system, sid), "DEBUG")
            return sid

        sid = self.server.system_id(star_system, may_create)
        if not sid is None:
            self.systems_cache.set(star_system.lower(), sid)
            EDRLOG.log(u"Cached {}'s id={}".format(star_system, sid), "DEBUG")
            return sid

        return None

    def persist(self):
        with open(self.EDR_SYSTEMS_CACHE, 'wb') as handle:
            pickle.dump(self.systems_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_NOTAMS_CACHE, 'wb') as handle:
            pickle.dump(self.notams_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def timespan_s(self):
        return self.__pretty_print_timespan(self.timespan, short=True, verbose=True)

    def __pretty_print_timespan(self, timespan, short=False, verbose=False):
        remaining = timespan
        days = remaining / 86400
        remaining -= days * 86400

        hours = (remaining / 3600) % 24
        remaining -= hours * 3600

        minutes = (remaining / 60) % 60
        remaining -= minutes * 60

        seconds = (remaining % 60)

        readable = ""
        if days > 0:
            readable = u"{}{}".format(days, u"day(s)" if verbose else "d")
            if hours > 0 and not short:
                readable += u":{}{}".format(hours, u"hour(s)" if verbose else "h")
        elif hours > 0:
            readable = u"{}{}".format(hours, u"hour(s)" if verbose else "h")
            if minutes > 0 and not short:
                readable += ":{}{}".format(minutes, u"minute(s)" if verbose else "m")
        elif minutes > 0:
            readable = u"{}m".format(minutes)
            if seconds > 0 and not short:
                readable += ":{}{}".format(seconds, u"second(s)" if verbose else "s")
        else:
            readable = u"{}{}".format(seconds, u"second(s)" if verbose else "s")

        return readable

    def crimes_t_minus(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestCrime" in system_reports:
                return self.t_minus(system_reports["latestCrime"])
        return None


    def traffic_t_minus(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestTraffic" in system_reports:
                return self.t_minus(system_reports["latestTraffic"])
        return None

    def t_minus(self, js_epoch_then, short=False):
        now = datetime.datetime.now()
        py_epoch_now = time.mktime(now.timetuple())
        ago = int(py_epoch_now - js_epoch_then / 1000)
        if short:
            return u"-{}".format(self.__pretty_print_timespan(ago, short=True))
        return u"T-{}".format(self.__pretty_print_timespan(ago))
    
    def has_sitrep(self, star_system):
        self.__update_if_stale()
        sid = self.system_id(star_system)
        return sid in self.reports.keys()

    def has_notams(self, star_system):
        self.__update_if_stale()
        sid = self.system_id(star_system)
        return sid in self.notams.keys()

    def __has_active_notams(self, system_id):
        self.__update_if_stale()
        if not system_id in self.notams.keys():
            return False

        return len(self.__active_notams_for_sid(system_id)) > 0

    def active_notams(self, star_system):
        if self.has_notams(star_system):
            return self.__active_notams_for_sid(self.system_id(star_system))
        return None

    def __active_notams_for_sid(self, system_id):
        active_notams = []
        all_notams = self.notams[system_id].get("NOTAMs", None)
        now = datetime.datetime.now()
        js_epoch_now = time.mktime(now.timetuple()) * 1000
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
        for sid in self.notams:
            star_system = self.notams[sid].get("name", None)
            if star_system and self.__has_active_notams(sid):
                summary.append(star_system)

        return summary

    def systems_with_recent_activity(self):
        systems_with_recent_crimes = {}
        systems_with_recent_traffic = {}
        systems_with_recent_outlaws = {}
        self.__update_if_stale()
        for sid in self.reports:
            star_system = self.reports[sid].get("name", None)
            if star_system:
                if self.has_recent_outlaws(star_system):
                    systems_with_recent_outlaws[star_system] = self.reports[sid]["latestOutlaw"]
                elif self.has_recent_crimes(star_system):
                    systems_with_recent_crimes[star_system] = self.reports[sid]["latestCrime"]
                elif self.has_recent_traffic(star_system):
                    systems_with_recent_traffic[star_system] = self.reports[sid]["latestTraffic"]

        summary = {}
        summary_outlaws = []
        systems_with_recent_outlaws = sorted(systems_with_recent_outlaws.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_outlaws:
            summary_outlaws.append(u"{} {}".format(system[0], self.t_minus(system[1], short=True)))
        if summary_outlaws:
            summary[u"Outlaws"] = summary_outlaws

        summary_crimes = []
        systems_with_recent_crimes = sorted(systems_with_recent_crimes.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_crimes:
            summary_crimes.append(u"{} {}".format(system[0], self.t_minus(system[1], short=True)))
        if summary_crimes:
            summary[u"Crimes"] = summary_crimes

        summary_traffic = []
        systems_with_recent_traffic = sorted(systems_with_recent_traffic.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_traffic:
            summary_traffic.append(u"{} {}".format(system[0], self.t_minus(system[1], short=True)))
        if summary_traffic:
            summary[u"Traffic"] = summary_traffic

        return summary

    def has_recent_crimes(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestCrime" not in system_reports:
                return None

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestCrime"],
                                  edr_config.crimes_recent_threshold())

        return None

    def has_recent_outlaws(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestOutlaw" not in system_reports:
                return None

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestOutlaw"],
                                  edr_config.outlaws_recent_threshold())

        return None

    def recent_crimes(self, star_system):
        if self.has_recent_crimes(star_system):
            #TODO cache crimes and only fetch the missing timespan
            return self.server.recent_crimes(star_system, self.timespan)
        return None

    def has_recent_traffic(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestTraffic" not in system_reports:
                return None

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports["latestTraffic"],
                                  edr_config.traffic_recent_threshold())

        return None
    
    def summarize_recent_activity(self, star_system):
        #TODO refactor/simplify this mess ;)
        summary = {}
        wanted_cmdrs = {}
        if self.has_recent_traffic(star_system):
            summary_sighted = []
            #TODO cache traffic and only fetch the missing timespan
            recent_traffic = self.server.recent_traffic(self.system_id(star_system), self.timespan)
            if recent_traffic is not None:
                summary_traffic = {}
                for tid in recent_traffic:
                    traffic = recent_traffic[tid]
                    summary_traffic[traffic["cmdr"]] = max(traffic["timestamp"] , summary_traffic.get(traffic["cmdr"], None))
                    karma = traffic.get("karma", None)
                    if karma and karma < 0:
                        wanted_cmdrs[traffic["cmdr"]] = [ traffic["timestamp"], karma ]
                summary_traffic = sorted(summary_traffic.items(), key=lambda t: t[1], reverse=True)
                for traffic in summary_traffic:
                    summary_sighted.append(u"{} {}".format(traffic[0], self.t_minus(traffic[1], short=True)))
                summary[u"Sighted"] = summary_sighted
        
        if self.has_recent_crimes(star_system):
            summary_interdictors = []
            summary_destroyers = []
            #TODO cache traffic and only fetch the missing timespan
            recent_crimes = self.server.recent_crimes(self.system_id(star_system), self.timespan)
            if recent_crimes is not None:
                summary_crimes = {}
                for sid in recent_crimes:
                    crime = recent_crimes[sid]
                    if crime["criminals"][0]["name"] not in summary_crimes or crime["timestamp"] > summary_crimes[crime["criminals"][0]["name"]][0]: 
                        summary_crimes[crime["criminals"][0]["name"]] = [crime["timestamp"], crime["offence"]]
                        for criminal in crime["criminals"]:
                            karma = criminal.get("karma", None)
                            if karma and karma < 0:
                                wanted_cmdrs[criminal["name"]] = [ crime["timestamp"], karma]
                summary_crimes = sorted(summary_crimes.items(), key=lambda t: t[1][0], reverse=True)
                for crime in summary_crimes:
                    if crime[1][1] == "Murder":
                        summary_destroyers.append(u"{} {}".format(crime[0], self.t_minus(crime[1][0], short=True)))
                    elif crime[1][1] in ["Interdicted", "Interdiction"]:
                        summary_interdictors.append(u"{} {}".format(crime[0], self.t_minus(crime[1][0], short=True)))
                if summary_interdictors:
                    summary[u"Interdictors"] = summary_interdictors
                if summary_destroyers:
                    summary[u"Destroyers"] = summary_destroyers
        
        if wanted_cmdrs:
            wanted_cmdrs = sorted(wanted_cmdrs.items(), key=lambda t: t[1][0], reverse=True)
            summary_wanted = []
            for wanted in wanted_cmdrs:
                summary_wanted.append(u"{} {}".format(wanted[0], self.t_minus(wanted[1][0], short=True)))
            summary[u"Outlaws"] = summary_wanted

        return summary
    
    def has_recent_recon(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestRecon" not in system_reports.keys():
                return None

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports.get["latestRecon"],
                                  edr_config.recon_recent_threshold())

        return None

    def is_recent(self, timestamp, max_age):
        if timestamp is None:
            return False
        now = datetime.datetime.now()
        js_epoch_now = time.mktime(now.timetuple()) * 1000

        return (js_epoch_now - timestamp) / 1000 <= max_age

    def evict(self, star_system):
        try:
            del self.systems_cache[star_system]
        except KeyError:
            pass


    def __are_reports_stale(self):
        return self.__is_stale(self.reports_last_updated, self.reports_check_interval)

    def __are_notams_stale(self):
        return self.__is_stale(self.notams_last_updated, self.notams_check_interval)

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
            if not self.reports_last_updated is None:
                missing_seconds = self.timespan - (now - self.reports_last_updated).total_seconds()
            response = self.server.sitreps(missing_seconds)
            if not response is None:
                self.reports.update(response)
            self.reports_last_updated = now
            updated = True

        if self.__are_notams_stale():
            missing_seconds = self.timespan
            now = datetime.datetime.now()
            if not self.notams_last_updated is None:
                missing_seconds = self.timespan - (now - self.notams_last_updated).total_seconds()

            response = self.server.notams(missing_seconds)
            if not response is None:
                self.notams.update(response)
            self.notams_last_updated = now
            updated = True

        return updated
