# coding= utf-8
import datetime
import time
import os
import pickle

import lrucache
import edrconfig
import edrserver
import edrlog
import edtime

EDRLOG = edrlog.EDRLog()

class EDROutlaws(object):
    EDR_OUTLAWS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/outlaws.v2.p')

    def __init__(self, server):
        self.server = server
        
        config = edrconfig.EDRConfig()
        try:
            with open(self.EDR_OUTLAWS_CACHE, 'rb') as handle:
                self.sightings = pickle.load(handle)
        except:
            self.sightings = lrucache.LRUCache(config.lru_max_size(), config.outlaws_max_age())
        self.timespan = config.outlaws_recent_threshold()
        self.reports_check_interval = config.reports_check_interval()

    def persist(self):
        with open(self.EDR_OUTLAWS_CACHE, 'wb') as handle:
            pickle.dump(self.sightings, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def where(self, cmdr_name):
        self.__update_outlaws_if_stale()
        cname = cmdr_name.lower()
        report = self.sightings.get(cname)
        if not report:
            report = self.server.where(cmdr_name)
            if report:
                 self.sightings.set(cname, report)
        return self.__readable_outlaw_sighting(report)

    def recent_sightings(self):
        self.__update_outlaws_if_stale()
        if not self.sightings:
            EDRLOG.log(u"No recently sighted outlaws", "INFO")
            return None
        
        self.status = "recently sighted outlaws"
        EDRLOG.log(u"Got recently sighted outlaws", "INFO")
        summary = []
        for key in self.sightings.keys():
            #TODO bail out if too old?
            summary.append(self.__readable_outlaw_sighting(self.sightings.get(key), one_liner=True))
        return summary

    def __pretty_print_bounty(self, bounty):
        readable = ""
        if bounty >= 10000000000:
            readable = u"{}b".format(bounty / 1000000000)
        elif bounty >= 1000000000:
            readable = u"{:.1f}b".format(bounty / 1000000000.0)
        elif bounty >= 10000000:
            readable = u"{}m".format(bounty / 1000000)
        elif bounty > 1000000:
            readable = u"{:.1f}m".format(bounty / 1000000.0)
        elif bounty >= 10000:
            readable = u"{}k".format(bounty / 1000)
        elif bounty >= 1000:
            readable = u"{:.1f}k".format(bounty / 1000.0)
        else:
            readable = u"{}".format(bounty)
        return readable

    def __readable_outlaw_sighting(self, sighting, one_liner=False):
        EDRLOG.log(u"sighting: {}".format(sighting), "DEBUG")
        if not sighting:
            return None
        t_minus = edtime.EDTime.t_minus(sighting["timestamp"], short=True)
        if one_liner:
            cmdr = (sighting["cmdr"][:29] + u'…') if len(sighting["cmdr"]) > 30 else sighting["cmdr"]
            starSystem = (sighting["starSystem"][:50] + u'…') if len(sighting["starSystem"]) > 50 else sighting["starSystem"]    
            if sighting.get("bounty", None) > 0:
                neat_bounty = self.__pretty_print_bounty(sighting["bounty"])
                return u"T{:<2}: {} in {}, wanted for {}".format(t_minus, cmdr, starSystem, neat_bounty)
            else:
                return u"T{:<2}: {} in {}".format(t_minus, cmdr, starSystem)
        
        readable = []
        
        location = u"T{} {} sighted in {}".format(t_minus, sighting["cmdr"], sighting["starSystem"])
        if sighting["place"] and sighting["place"] != sighting["starSystem"]:
            if sighting["place"].startswith(sighting["starSystem"]+" "):
                location += u", {}".format(sighting["place"].partition(sighting["starSystem"]+" ")[2])
            else:
                location += u", {}".format(sighting["place"])
        readable.append(location)
        if sighting["ship"] != "Unknown":
            readable.append(u"Spaceship: {}".format(sighting["ship"]))
        if sighting.get("bounty", None) > 0:
            neat_bounty = self.__pretty_print_bounty(sighting["bounty"]) 
            readable.append(u"Wanted for {} credits".format(neat_bounty))
        return readable

    def __are_sightings_stale(self):
        if self.sightings.last_updated is None:
            return True
        now = datetime.datetime.now()
        epoch_now = time.mktime(now.timetuple())
        epoch_updated = time.mktime(self.sightings.last_updated.timetuple())
        return (epoch_now - epoch_updated) > self.reports_check_interval

    
    def __update_outlaws_if_stale(self):
        updated = False
        if self.__are_sightings_stale():
            now = datetime.datetime.now()
            missing_seconds = self.timespan
            if self.sightings.last_updated:
                missing_seconds = min(self.timespan, (now - self.sightings.last_updated).total_seconds())
            sightings = self.server.recent_outlaws(missing_seconds)
            if sightings:
                for sighting in sightings:
                    previous = self.sightings.get(sighting["cmdr"].lower())
                    if not previous or (previous and previous["timestamp"] < sighting["timestamp"]):
                        self.sightings.set(sighting["cmdr"].lower(), sighting)
            self.sightings.last_updated = now
            updated = True
        return updated