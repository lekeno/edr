import json
import os
import datetime
from edr.utils.edrpath import edr_cache_path, edr_data_path
from edr.utils.lrucache import LRUCache
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c, _edr
from edr.utils import edtime
from edr.core import edrconfig

class EDRSysIntel:
    EDR_NOTAMS_CACHE = edr_cache_path('notams.v2.p')
    EDR_SITREPS_CACHE = edr_cache_path('sitreps.v3.p')
    EDR_TRAFFIC_CACHE = edr_cache_path('traffic.v2.p')
    EDR_CRIMES_CACHE = edr_cache_path('crimes.v2.p')
    EDSM_TRAFFIC_CACHE = edr_cache_path('edsm_traffic.v1.p')
    EDSM_DEATHS_CACHE = edr_cache_path('edsm_deaths.v1.p')

    def __init__(self, edrsystems):
        self.edrsystems = edrsystems
        self.server = edrsystems.server
        edr_config = edrconfig.EDR_CONFIG

        self.notams_cache = LRUCache.load(
            file_path=self.EDR_NOTAMS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.notams_max_age()
        )

        self.sitreps_cache = LRUCache.load(
            file_path=self.EDR_SITREPS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.sitreps_max_age()
        )

        self.crimes_cache = LRUCache.load(
            file_path=self.EDR_CRIMES_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.crimes_max_age()
        )

        self.traffic_cache = LRUCache.load(
            file_path=self.EDR_TRAFFIC_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.traffic_max_age()
        )

        self.edsm_traffic_cache = LRUCache.load(
            file_path=self.EDSM_TRAFFIC_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_traffic_max_age()
        )

        self.edsm_deaths_cache = LRUCache.load(
            file_path=self.EDSM_DEATHS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_deaths_max_age()
        )

        self.reports_check_interval = edr_config.reports_check_interval()
        self.notams_check_interval = edr_config.notams_check_interval()
        self.timespan = edr_config.sitreps_timespan()
        self.timespan_notams = edr_config.notams_timespan()

    def save(self):
        if self.notams_cache:
            self.notams_cache.save(self.EDR_NOTAMS_CACHE)
        if self.sitreps_cache:
            self.sitreps_cache.save(self.EDR_SITREPS_CACHE)
        if self.crimes_cache:
            self.crimes_cache.save(self.EDR_CRIMES_CACHE)
        if self.traffic_cache:
            self.traffic_cache.save(self.EDR_TRAFFIC_CACHE)
        if self.edsm_traffic_cache:
            self.edsm_traffic_cache.save(self.EDSM_TRAFFIC_CACHE)
        if self.edsm_deaths_cache:
            self.edsm_deaths_cache.save(self.EDSM_DEATHS_CACHE)

    def crimes_t_minus(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.edrsystems.system_id(star_system))
            if "latestCrime" in system_reports:
                return edtime.EDTime.t_minus(system_reports["latestCrime"])
        return None

    def traffic_t_minus(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.edrsystems.system_id(star_system))
            if "latestTraffic" in system_reports:
                return edtime.EDTime.t_minus(system_reports["latestTraffic"])
        return None

    def has_sitrep(self, star_system):
        if not star_system:
            return False
        self.update_if_stale()
        sid = self.edrsystems.system_id(star_system)
        return self.sitreps_cache.has_key(sid)

    def has_notams(self, star_system, may_create=False, coords=None):
        self.update_if_stale()
        sid = self.edrsystems.system_id(star_system, may_create, coords)
        return self.notams_cache.has_key(sid)

    def has_active_notams(self, system_id):
        self.update_if_stale()
        if not self.notams_cache.has_key(system_id):
            return False
        return len(self.active_notams_for_sid(system_id)) > 0

    def active_notams(self, star_system, may_create=False, coords=None):
        if self.has_notams(star_system, may_create, coords=None):
            return self.active_notams_for_sid(self.edrsystems.system_id(star_system))
        return None

    def active_notams_for_sid(self, system_id):
        active_notams = []
        entry = self.notams_cache.get(system_id)
        if not entry:
            return []
        all_notams = entry.get("NOTAMs", {})
        js_epoch_now = edtime.EDTime.js_epoch_now()
        for notam in all_notams:
            active = True
            if "from" in notam:
                active &= notam["from"] <= js_epoch_now
            if "until" in notam:
                active &= js_epoch_now <= notam["until"]
            if active and "text" in notam:
                EDR_LOG.debug("Active NOTAM: {}".format(notam["text"]))
                active_notams.append(_edr(notam["text"]))
            elif active and "l10n" in notam:
                EDR_LOG.debug("Active NOTAM: {}".format(notam["l10n"]["default"]))
                active_notams.append(_edr(notam["l10n"]))
        return active_notams

    def systems_with_active_notams(self):
        summary = []
        self.update_if_stale()
        systems_ids = list(self.notams_cache.keys()).copy()
        for sid in systems_ids:
            entry = self.notams_cache.get(sid)
            if not entry:
                continue 
            star_system = entry.get("name", None)
            if star_system and self.has_active_notams(sid):
                summary.append(star_system)
        return summary

    def has_recent_activity(self, system_name, pledged_to=None):
        return self.has_recent_traffic(system_name) or self.has_recent_crimes(system_name) or self.has_recent_outlaws(system_name) or (pledged_to and self.has_recent_enemies(system_name, pledged_to))

    def systems_with_recent_activity(self, pledged_to=None):
        systems_with_recent_crimes = {}
        systems_with_recent_traffic = {}
        systems_with_recent_outlaws = {}
        systems_with_recent_enemies = {}
        self.update_if_stale()
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
            summary_outlaws.append("{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_outlaws:
            summary[_c("sitreps section|✪ Outlaws")] = summary_outlaws
        
        if pledged_to:
            summary_enemies = []
            systems_with_recent_enemies = sorted(systems_with_recent_enemies.items(), key=lambda t: t[1], reverse=True)
            for system in systems_with_recent_enemies:
                summary_enemies.append("{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
            if summary_enemies:
                summary[_c("sitreps section|✪ Enemies")] = summary_enemies

        summary_crimes = []
        systems_with_recent_crimes = sorted(systems_with_recent_crimes.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_crimes:
            summary_crimes.append("{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_crimes:
            summary[_c("sitreps section|✪ Crimes")] = summary_crimes

        summary_traffic = []
        systems_with_recent_traffic = sorted(systems_with_recent_traffic.items(), key=lambda t: t[1], reverse=True)
        for system in systems_with_recent_traffic:
            summary_traffic.append("{} {}".format(system[0], edtime.EDTime.t_minus(system[1], short=True)))
        if summary_traffic:
            summary[_c("sitreps section|✪ Traffic")] = summary_traffic

        return summary

    def summarize_deaths_traffic(self, star_system):
        if not star_system:
            return None

        traffic = self.edsm_traffic_cache.get(star_system.lower())
        if not self.edsm_traffic_cache.has_key(star_system.lower()):
            traffic = self.edrsystems.edsm_server.traffic(star_system)
            self.edsm_traffic_cache.set(star_system.lower(), traffic)

        deaths = self.edsm_deaths_cache.get(star_system.lower())
        if not self.edsm_deaths_cache.has_key(star_system.lower()):
            deaths = self.edrsystems.edsm_server.deaths(star_system)
            self.edsm_deaths_cache.set(star_system.lower(), deaths)

        if not deaths and not traffic:
            return None
        
        from edr.utils.edrutils import pretty_print_number
        zero = {"total": 0, "week": 0, "day": 0}
        deaths = {s: pretty_print_number(v) for s, v in deaths.get("deaths", zero).items()}
        traffic = {s: pretty_print_number(v) for s, v in traffic.get("traffic", {}).items()}
        
        if traffic == {}:
            return None

        return "Deaths / Traffic: [Day {}/{}]   [Week {}/{}]  [All {}/{}]".format(deaths.get("day", 0), traffic.get("day"), deaths.get("week", 0), traffic.get("week"), deaths.get("total"), traffic.get("total"))

    def summarize_recent_activity(self, star_system, powerplay=None):
        import collections
        import operator
        from edr.models.edentities import EDFineOrBounty
        summary = {}
        wanted_cmdrs = {}
        enemies = {}
        if self.has_recent_traffic(star_system):
            summary_sighted = []
            recent_traffic = self.recent_traffic(star_system)
            if recent_traffic is not None:
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
                    summary_sighted.append("{} {}".format(cmdr, edtime.EDTime.t_minus(summary_traffic[cmdr], short=True)))
                if summary_sighted:
                    summary[_c("sitrep section|✪ Sighted")] = summary_sighted
        
        if self.has_recent_crimes(star_system):
            summary_interdictors = []
            summary_destroyers = []
            recent_crimes = self.recent_crimes(star_system)
            if recent_crimes is not None:
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
                        summary_destroyers.append("{} {}".format(criminal, edtime.EDTime.t_minus(summary_crimes[criminal][0], short=True)))
                    elif summary_crimes[criminal][1] in ["Interdicted", "Interdiction"]:
                        summary_interdictors.append("{} {}".format(criminal, edtime.EDTime.t_minus(summary_crimes[criminal][0], short=True)))
                if summary_interdictors:
                    summary[_c("sitrep section|✪ Interdictors")] = summary_interdictors
                if summary_destroyers:
                    summary[_c("sitreps section|✪ Destroyers")] = summary_destroyers
        
        wanted_cmdrs = sorted(wanted_cmdrs.items(), key=operator.itemgetter(1), reverse=True)
        if wanted_cmdrs:
            summary_wanted = []
            for wanted in wanted_cmdrs:
                summary_wanted.append("{} {}".format(wanted[0], edtime.EDTime.t_minus(wanted[1][0], short=True)))
            if summary_wanted:
                summary[_c("sitreps section|✪ Outlaws")] = summary_wanted
        
        enemies = sorted(enemies.items(), key=operator.itemgetter(1), reverse=True)
        if enemies:
            summary_enemies = []
            for enemy in enemies:
                summary_enemies.append("{} {}".format(enemy[0], edtime.EDTime.t_minus(enemy[1][0], short=True)))
            if summary_enemies:
                summary[_c("sitreps section|✪ Enemies")] = summary_enemies

        return summary

    def recent_outlaws(self, star_system, max_age=3600):
        from edr.models.edentities import EDFineOrBounty
        recent_traffic = self.recent_traffic(star_system)
        recent_crimes = self.recent_crimes(star_system)

        outlaws = {}
        age_ms = max_age * 1000

        if recent_traffic is not None:
            for traffic in recent_traffic:
                cmdr_name = traffic["cmdr"]
                timestamp = traffic["timestamp"]
                previous_timestamp = outlaws.get(cmdr_name, [0])[0]
                if timestamp < previous_timestamp:
                    continue
                if not self.is_recent(timestamp, age_ms):
                    continue
                karma = traffic.get("karma", 0)
                if not karma > 0:
                    karma = min(karma, traffic.get("dkarma", 0))
                bounty = EDFineOrBounty(traffic.get("bounty", 0))
                if karma <= -100 or bounty.is_significant():
                    outlaws[cmdr_name] = [timestamp, karma]
    
        if recent_crimes is not None:
            for crime in recent_crimes:
                for criminal in crime["criminals"]:
                    cmdr_name = criminal["name"]
                    timestamp = crime["timestamp"]
                    previous_timestamp = outlaws.get(cmdr_name, [0])[0]
                    if timestamp < previous_timestamp:
                        continue
                    if not self.is_recent(timestamp, age_ms):
                        continue
                    karma = criminal.get("karma", 0)
                    if not karma > 0:
                        karma = min(karma, criminal.get("dkarma", 0))
                    bounty = EDFineOrBounty(criminal.get("bounty", 0))
                    if karma <= -100 or bounty.is_significant():
                        outlaws[cmdr_name] = [timestamp, karma]
        
        import collections
        outlaws = collections.OrderedDict(sorted(outlaws.items(), key=lambda kv: kv[1][0], reverse=True))
        return list(outlaws.keys())

    def is_recent(self, timestamp, max_age):
        if timestamp is None:
            return False
        return (edtime.EDTime.js_epoch_now() - timestamp) / 1000 <= max_age

    def has_recent_crimes(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.edrsystems.system_id(star_system))
            if system_reports is None or "latestCrime" not in system_reports:
                return False

            edr_config = edrconfig.EDR_CONFIG
            return self.edrsystems.is_recent(system_reports["latestCrime"],
                                  edr_config.opponents_recent_threshold("outlaws"))
        return False

    def has_recent_outlaws(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.edrsystems.system_id(star_system))
            if system_reports is None or "latestOutlaw" not in system_reports:
                return False

            edr_config = edrconfig.EDR_CONFIG
            return self.edrsystems.is_recent(system_reports["latestOutlaw"],
                                  edr_config.opponents_recent_threshold("outlaws"))
        return False

    def has_recent_enemies(self, star_system, pledged_to):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.edrsystems.system_id(star_system))
            latestEnemy = "latestEnemy_{}".format(self.server.nodify(pledged_to))
            if system_reports is None or latestEnemy not in system_reports:
                return False

            edr_config = edrconfig.EDR_CONFIG
            return self.edrsystems.is_recent(system_reports[latestEnemy],
                                  edr_config.opponents_recent_threshold("enemies"))
        return False

    def recent_crimes(self, star_system):
        sid = self.edrsystems.system_id(star_system)
        if not sid:
            return None
        
        key = sid
        if self.crimes_cache.has_key(key) and not self.crimes_cache.is_stale(key):
            recent_crimes = self.crimes_cache.peek(key)
            if recent_crimes is not None:
                return recent_crimes
            self.crimes_cache.evict(key)
            
        updated_crimes = None
        stale_profile = self.crimes_cache.peek(key)
        
        if self.has_recent_crimes(star_system):
            try:
                EDR_LOG.info("Fetching recent crimes for {} (SID {}) from EDR server.".format(star_system, key))
                updated_crimes = self.server.recent_crimes(key, self.timespan) 
            except Exception as e:
                EDR_LOG.warning(f"Comms jammed/Failed to fetch crimes for {star_system}: {e}")
                if stale_profile is not None:
                    self.crimes_cache.refresh(key)
                    return stale_profile
        
        if updated_crimes is not None:
            self.crimes_cache.set(key, updated_crimes)
            return updated_crimes
        return None

    def has_recent_traffic(self, star_system):
        if self.has_sitrep(star_system):
            system_reports = self.sitreps_cache.get(self.edrsystems.system_id(star_system))
            if system_reports is None or "latestTraffic" not in system_reports:
                return False

            edr_config = edrconfig.EDR_CONFIG
            return self.edrsystems.is_recent(system_reports["latestTraffic"],
                                  edr_config.traffic_recent_threshold())
        return False

    def recent_traffic(self, star_system):
        sid = self.edrsystems.system_id(star_system)
        if not sid:
            return None
        
        key = sid
        if self.traffic_cache.has_key(key) and not self.traffic_cache.is_stale(key):
            recent_traffic = self.traffic_cache.peek(key)
            if recent_traffic is not None:
                return recent_traffic
            
        updated_traffic = None
        stale_profile = self.traffic_cache.peek(key)
        
        if self.has_recent_traffic(star_system):
            try:
                EDR_LOG.info("Fetching recent traffic for {} (SID {}) from EDR server.".format(star_system, key))
                updated_traffic = self.server.recent_traffic(key, self.timespan) 
            except Exception as e:
                EDR_LOG.warning(f"Comms jammed/Failed to fetch traffic for {star_system}: {e}")
                if stale_profile is not None:
                    self.traffic_cache.refresh(key)
                    return stale_profile
        
        if updated_traffic is not None:
            self.traffic_cache.set(key, updated_traffic)
            return updated_traffic
        return None

    def update_if_stale(self):
        updated = False
        if self.are_sitreps_stale():
            self.update_sitreps()
            updated = True
        if self.are_notams_stale():
            self.update_notams()
            updated = True
        return updated

    def are_sitreps_stale(self):
        return self.__is_stale(self.sitreps_cache.last_updated, self.reports_check_interval)

    def are_notams_stale(self):
        return self.__is_stale(self.notams_cache.last_updated, self.notams_check_interval)

    def __is_stale(self, last_updated, interval):
        if last_updated is None:
            return True
        now = datetime.datetime.now()
        return (now - last_updated).total_seconds() > interval

    def update_sitreps(self):
        now = datetime.datetime.now()
        try:
            missing_seconds = self.timespan
            if self.sitreps_cache.last_updated:
                missing_seconds = min(self.timespan, (now - self.sitreps_cache.last_updated).total_seconds())
            sitreps = self.server.sitreps(missing_seconds)
            if sitreps:
                for system_id in sitreps:
                    self.sitreps_cache.set(system_id, sitreps[system_id])
            self.sitreps_cache.last_updated = now
        except Exception as e:
            EDR_LOG.warning("Failed to fetch/update sitreps: {}".format(e))

    def update_notams(self):
        now = datetime.datetime.now()
        try:
            missing_seconds = self.timespan_notams
            if self.notams_cache.last_updated:
                missing_seconds = min(self.timespan_notams, (now - self.notams_cache.last_updated).total_seconds())
            notams = self.server.notams(missing_seconds)
            if notams:
                for system_id in notams:
                    self.notams_cache.set(system_id, notams[system_id])
            self.notams_cache.last_updated = now
        except Exception as e:
            EDR_LOG.warning("Failed to fetch/update notams: {}".format(e))
