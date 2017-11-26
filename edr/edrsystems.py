import os
import pickle

import datetime
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

    def system_id(self, star_system):
        sid = self.systems_cache.get(star_system)
        if not sid is None:
            EDRLOG.log(u"System {} is in the cache with id={}".format(star_system, sid), "DEBUG")
            return sid

        sid = self.server.system_id(star_system)
        if not sid is None:
            self.systems_cache.set(star_system, sid)
            EDRLOG.log(u"Cached {}'s id={}".format(star_system, sid), "DEBUG")
            return sid

        return None

    def persist(self):
        with open(self.EDR_SYSTEMS_CACHE, 'wb') as handle:
            pickle.dump(self.systems_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.EDR_NOTAMS_CACHE, 'wb') as handle:
            pickle.dump(self.notams_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def timespan_s(self):
        return self.__pretty_print_timespan(self.timespan)

    def __pretty_print_timespan(self, timespan):
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
            readable = u"{}d".format(days)
            if hours > 0:
                readable += u":{}h".format(hours)
        elif hours > 0:
            readable = u"{}h".format(hours)
            if minutes > 0:
                readable += ":{}m".format(minutes)
        elif minutes > 0:
            readable = u"{}m".format(minutes)
            if seconds > 0:
                readable += ":{}s".format(seconds)
        else:
            readable = u"{}s".format(seconds)

        return readable

    def crimes_t_minus(self, star_system):
        #TODO needs last_crime_timestamp
        now = datetime.datetime.now()
        return "T-01h30m"

    def traffic_t_minus(self, star_system):
        #TODO needs last_blip_timestamp
        now = datetime.datetime.now()
        return "T-01h30m"

    def has_sitrep(self, star_system):
        self.__update_if_stale()
        sid = self.system_id(star_system)

        return sid in self.reports.keys()

    def has_notams(self, star_system):
        self.__update_if_stale()
        sid = self.system_id(star_system)

        return sid in self.notams.keys()

    def active_notams(self, star_system):
        if self.has_notams(star_system):
            active_notams = []
            all_notams = self.notams[self.system_id(star_system)].get("NOTAMs", None)
            now = datetime.datetime.now()
            js_epoch_now = calendar.timegm(now.timetuple()) * 1000
            for notam in all_notams:
                active = True
                if "from" in notam:
                    active = notam["from"] <= js_epoch_now
                if "until" in notam:
                    active = js_epoch_now <= notam["until"]
                if active:
                    active_notams.append(notam["text"])
            return active_notams

        return None

    def has_recent_crimes(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestCrime" not in system_reports.keys():
                return None

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports.get["latestCrime"],
                                  edr_config.crimes_recent_threshold())

        return None

    def crimes(self, star_system):
        #TODO run crimes request
        return None

    def has_recent_traffic(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.reports[self.system_id(star_system)]
            if "latestBlip" not in system_reports.keys():
                return None

            edr_config = edrconfig.EDRConfig()
            return self.is_recent(system_reports.get["latestBlip"],
                                  edr_config.traffic_recent_threshold())

        return None

    def traffic_reports(self, star_system):
        #TODO run traffic request
        return None

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
        js_epoch_now = calendar.timegm(now.timetuple()) * 1000

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
        epoch_now = calendar.timegm(now.timetuple())
        epoch_updated = calendar.timegm(updated_at.timetuple())

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

        if self.__are_NOTAMs_stale():
            missing_seconds = self.timespan
            now = datetime.datetime.now()
            if not self.notams_last_updated is None:
                missing_seconds = self.timespan - (now - self.notams_last_updated).total_seconds()

            response = self.server.NOTAMs(missing_seconds)
            if not response is None:
                self.notams.update(response)
            self.notams_last_updated = now
            updated = True

        return updated
