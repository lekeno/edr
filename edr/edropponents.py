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
import edrrealtime
import edrlog
import edtime
from edentities import EDBounty
from edri18n import _, _c

EDRLOG = edrlog.EDRLog()

class EDROpponents(object):
    OUTLAWS = "Outlaws"
    ENEMIES = "Enemies"

    EDR_OPPONENTS_SIGHTINGS_CACHES = {
        "Outlaws": os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache/outlaws_sigthings.p'),
        "Enemies": os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache/enemies_sigthings.p')
    }

    EDR_OPPONENTS_RECENTS_CACHES = {
        "Outlaws": os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache/outlaws_recents.p'),
        "Enemies": os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache/enemies_recents.p')
    }

    def __init__(self, server, opponent_kind, client_callback):
        self.server = server
        self.kind = opponent_kind
        self.powerplay = None
        self.realtime_callback = client_callback
        self.realtime = None

        config = edrconfig.EDRConfig()
        try:
            with open(self.EDR_OPPONENTS_SIGHTINGS_CACHES[opponent_kind], 'rb') as handle:
                self.sightings = pickle.load(handle)
        except:
            self.sightings = lrucache.LRUCache(config.lru_max_size(), config.opponents_max_age(self.kind))

        try:
            with open(self.EDR_OPPONENTS_RECENTS_CACHES[opponent_kind], 'rb') as handle:
                self.recents = pickle.load(handle)
        except:
            self.recents = deque(maxlen=config.opponents_max_recents(self.kind))

        self.timespan = config.opponents_recent_threshold(self.kind)
        self.reports_check_interval = config.reports_check_interval()

    def persist(self):
        with open(self.EDR_OPPONENTS_SIGHTINGS_CACHES[self.kind], 'wb') as handle:
            pickle.dump(self.sightings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.EDR_OPPONENTS_RECENTS_CACHES[self.kind], 'wb') as handle:
            pickle.dump(self.recents, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def pledged_to(self, power, time_pledged):
        if self.kind is not EDROpponents.ENEMIES:
            return
        if not power or self.powerplay is not power:
            config = edrconfig.EDRConfig()
            self.recents = deque(maxlen=config.opponents_max_recents(self.kind))
            self.sightings = lrucache.LRUCache(config.lru_max_size(), config.opponents_max_age(self.kind))
        self.powerplay = power

    def is_comms_link_up(self):
        return self.realtime and self.realtime.is_live()

    def establish_comms_link(self):
        self.shutdown_comms_link()
        if self._invalid_state():
            return False
        endpoint = "{}{}".format(self.server.EDR_SERVER, self._node())
        self.realtime = edrrealtime.EDRRealtimeUpdates(self.realtime_callback, self.kind, endpoint, self.server.auth_token)
        self.realtime.start()
        return True

    def shutdown_comms_link(self):
        if self.realtime and self.realtime.is_live():
            self.realtime.shutdown()

    def where(self, cmdr_name):
        if self._invalid_state():
            return None
        self.__update_opponents_if_stale()
        cname = cmdr_name.lower()
        report = self.sightings.get(cname)
        if not report:
            report = self.server.where(cmdr_name, self.powerplay)
            if report:
                 self.sightings.set(cname, report)
        return self.__readable_opponent_sighting(report)

    def recent_sightings(self):
        self.__update_opponents_if_stale()
        if not self.recents:
            EDRLOG.log(u"No recently sighted {}".format(self.kind), "INFO")
            return None
        
        EDRLOG.log(u"Got recently sighted {}".format(self.kind), "INFO")
        summary = []
        now = datetime.datetime.now()
        js_epoch_now = 1000 * time.mktime(now.timetuple())
        processed = []
        for sighting in self.recents:
            if (js_epoch_now - sighting["timestamp"]) / 1000 > self.timespan:
                continue
            if sighting["cmdr"] not in processed:
                summary.append(self.__readable_opponent_sighting(sighting, one_liner=True))
                processed.append(sighting["cmdr"])
        return summary

    def __readable_opponent_sighting(self, sighting, one_liner=False):
        EDRLOG.log(u"sighting: {}".format(sighting), "DEBUG")
        if not sighting:
            return None
        t_minus = edtime.EDTime.t_minus(sighting["timestamp"], short=True)
        if one_liner:
            cmdr = (sighting["cmdr"][:29] + u'…') if len(sighting["cmdr"]) > 30 else sighting["cmdr"]
            starSystem = (sighting["starSystem"][:50] + u'…') if len(sighting["starSystem"]) > 50 else sighting["starSystem"]    
            if sighting.get("bounty", None) > 0:
                neat_bounty = EDBounty(sighting["bounty"]).pretty_print()
                # Translators: this is a one-liner for the recently sighted opponents; Keep it short! T{t:<2} is to show how long ago e.g. T-4H (4 hours ago) 
                return _(u"T{t:<2}: {name} in {system}, wanted for {bounty}").format(t=t_minus, name=cmdr, system=starSystem, bounty=neat_bounty)
            else:
                # Translators: this is a one-liner for the recently sighted opponents; Keep it short! T{t:<2} is to show how long ago e.g. T-4H (4 hours ago) 
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
   
    def __update_opponents_if_stale(self):
        updated = False
        if self.__are_sightings_stale():
            now = datetime.datetime.now()
            missing_seconds = self.timespan
            if self.sightings.last_updated:
                missing_seconds = int(min(self.timespan, (now - self.sightings.last_updated).total_seconds()))
            sightings = None
            if self.kind is EDROpponents.OUTLAWS:
                sightings = self.server.recent_outlaws(missing_seconds)
            elif self.kind is EDROpponents.OUTLAWS:
                sightings = self.server.recent_enemies(missing_seconds, self.powerplay)
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

    def _realtime_callback(self, kind, events):
        if events not in ["cancel", "auth_revoked"]:
            for report in events.values():
                previous = self.sightings.get(report["cmdr"].lower())
                if not previous or (previous and previous["timestamp"] < report["timestamp"]):
                    self.sightings.set(report["cmdr"].lower(), report)
                self.recents.appendleft(report)
            self.sightings.last_updated = datetime.datetime.now()
        self.realtime_callback(kind, events)

    def _node(self):
        if self.kind is self.OUTLAWS:
            return "/v1/outlaws/.json"
        elif self.kind is self.ENEMIES and self.powerplay:
            return "/v1/powerplay/{}/enemies/.json".format(self.server.nodify(self.powerplay))
        else:
            return None

    def _invalid_state(self):
        return self.kind is EDROpponents.ENEMIES and not self.powerplay