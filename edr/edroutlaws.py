#!/usr/bin/env python
# coding=utf-8

import datetime
import time
import os
import pickle

import lrucache
from collections import deque 
import edrconfig
import edrserver
import edrlog
import edtime
from edentities import EDBounty
from edri18n import _, _c

EDRLOG = edrlog.EDRLog()

class EDROutlaws(object):
    EDR_OUTLAWS_SIGHTINGS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/outlaws_sigthings.p')

    EDR_OUTLAWS_RECENTS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/outlaws_recents.p')

    def __init__(self, server):
        self.server = server
        config = edrconfig.EDRConfig()
        try:
            with open(self.EDR_OUTLAWS_SIGHTINGS_CACHE, 'rb') as handle:
                self.sightings = pickle.load(handle)
        except:
            self.sightings = lrucache.LRUCache(config.lru_max_size(), config.outlaws_max_age())

        try:
            with open(self.EDR_OUTLAWS_RECENTS_CACHE, 'rb') as handle:
                self.recents = pickle.load(handle)
        except:
            self.recents = deque(maxlen=config.outlaws_max_recents())

        self.timespan = config.outlaws_recent_threshold()
        self.reports_check_interval = config.reports_check_interval()

    def persist(self):
        with open(self.EDR_OUTLAWS_SIGHTINGS_CACHE, 'wb') as handle:
            pickle.dump(self.sightings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.EDR_OUTLAWS_RECENTS_CACHE, 'wb') as handle:
            pickle.dump(self.recents, handle, protocol=pickle.HIGHEST_PROTOCOL)

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
        if not self.recents:
            EDRLOG.log(u"No recently sighted outlaws", "INFO")
            return None
        
        EDRLOG.log(u"Got recently sighted outlaws", "INFO")
        summary = []
        now = datetime.datetime.now()
        js_epoch_now = 1000 * time.mktime(now.timetuple())
        processed = []
        for sighting in self.recents:
            if (js_epoch_now - sighting["timestamp"]) / 1000 > self.timespan:
                continue
            if sighting["cmdr"] not in processed:
                summary.append(self.__readable_outlaw_sighting(sighting, one_liner=True))
                processed.append(sighting["cmdr"])
        return summary

    def __readable_outlaw_sighting(self, sighting, one_liner=False):
        EDRLOG.log(u"sighting: {}".format(sighting), "DEBUG")
        if not sighting:
            return None
        t_minus = edtime.EDTime.t_minus(sighting["timestamp"], short=True)
        if one_liner:
            cmdr = (sighting["cmdr"][:29] + u'…') if len(sighting["cmdr"]) > 30 else sighting["cmdr"]
            starSystem = (sighting["starSystem"][:50] + u'…') if len(sighting["starSystem"]) > 50 else sighting["starSystem"]    
            if sighting.get("bounty", None) > 0:
                neat_bounty = EDBounty(sighting["bounty"]).pretty_print()
                # Translators: this is a one-liner for the recently sighted outlaws; Keep it short! T{t:<2} is to show how long ago e.g. T-4H (4 hours ago) 
                return _(u"T{t:<2}: {name} in {system}, wanted for {bounty}").format(t=t_minus, name=cmdr, system=starSystem, bounty=neat_bounty)
            else:
                # Translators: this is a one-liner for the recently sighted outlaws; Keep it short! T{t:<2} is to show how long ago e.g. T-4H (4 hours ago) 
                return _(u"T{t:<2}: {name} in {system}").format(t=t_minus, name=cmdr, system=starSystem)
        
        readable = []
        
        # Translators: this is for a recently sighted outlaw; T{t} is to show how long ago, e.g. T-2h43m 
        location = _(u"T{t} {name} sighted in {system}").format(t=t_minus, name=sighting["cmdr"], system=sighting["starSystem"])
        if sighting["place"] and sighting["place"] != sighting["starSystem"]:
            if sighting["place"].startswith(sighting["starSystem"]+" "):
                # Translators: this is a continuation of the previous item (location of recently sighted outlaw) and shows a place in the system (e.g. supercruise, Cleve Hub) 
                location += _(u", {place}").format(place=sighting["place"].partition(sighting["starSystem"]+" ")[2])
            else:
                location += _(u", {place}").format(place=sighting["place"])
        readable.append(location)
        if sighting["ship"] != "Unknown":
            # Translators: this is for the recently sighted outlaw feature; it shows which ship they were flying at the time
            readable.append(_(u"Spaceship: {}").format(sighting["ship"]))
        if sighting.get("bounty", None) > 0:
            neat_bounty = EDBounty(sighting["bounty"]).pretty_print()
            # Translators: this is for the recently sighted outlaw feature; it shows their bounty if any
            readable.append(_(u"Wanted for {} credits").format(neat_bounty))
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
                missing_seconds = int(min(self.timespan, (now - self.sightings.last_updated).total_seconds()))
            sightings = self.server.recent_outlaws(missing_seconds)
            self.sightings.last_updated = now
            if sightings:
                updated = True
                #TODO can we just append the whole thing?
                sightings = sorted(sightings, key=lambda t: t["timestamp"], reverse=False)
                for sighting in sightings:
                    previous = self.sightings.get(sighting["cmdr"].lower())
                    if not previous or (previous and previous["timestamp"] < sighting["timestamp"]):
                        self.sightings.set(sighting["cmdr"].lower(), sighting)
                    self.recents.appendleft(sighting)
        return updated