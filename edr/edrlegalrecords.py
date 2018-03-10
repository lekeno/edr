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
from collections import deque

EDRLOG = edrlog.EDRLog()

class EDRLegalRecords(object):
    EDR_LEGAL_RECORDS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/legal_records.p')
    
    def __init__(self, server):
        self.server = server
        
        self.timespan = None
        self.records_last_updated = None
        self.records_check_interval = None
        config = edrconfig.EDRConfig()
        try:
            with open(self.EDR_LEGAL_RECORDS_CACHE, 'rb') as handle:
                self.records = pickle.load(handle)
        except:
            self.records = lrucache.LRUCache(config.lru_max_size(), config.legal_records_max_age())
        
        self.timespan = config.legal_records_recent_threshold()
        self.reports_check_interval = config.legal_records_check_interval()
    
    def persist(self):
        with open(self.EDR_LEGAL_RECORDS_CACHE, 'wb') as handle:
            pickle.dump(self.records, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def summarize_recents(self, cmdr_id):
        self.__update_records_if_stale(cmdr_id)
        records = self.records.get(cmdr_id)
        if not records:
            EDRLOG.log(u"No recent legal records for {}".format(cmdr_id), "INFO")
            return None
        
        self.status = "Got legal records"
        EDRLOG.log(u"Got legal records for {}".format(cmdr_id), "INFO")
        summary = None
        counters = {"clean": 0, "wanted": 0}
        bounties = { "max": None, "last": {"value": None, "starSystem": None, "timestamp": None}}
        for record in records:
            counters["wanted"] += record["counters"]["wanted"]
            counters["clean"] += record["counters"]["clean"]
            bounties["max"] = max(record["bounties"]["max"], bounties["max"])
            if (record["bounties"]["last"]["timestamp"] >= bounties["last"]["timestamp"]):
                bounties["last"] = record["bounties"]["last"]
        timespan = edtime.EDTime.pretty_print_timespan(self.timespan, short=True, verbose=True)
        if bounties["last"]["value"]:
            tminus = edtime.EDTime.t_minus(bounties["last"]["timestamp"], short=True)
            max_bounty = self.__pretty_print_bounty(bounties["max"])
            last_bounty = self.__pretty_print_bounty(bounties["last"]["value"])
            summary = u"[Last {}] clean:{} / wanted:{} - max={} cr, last={} in {} {}".format(timespan, counters["clean"], counters["wanted"], max_bounty, last_bounty, bounties["last"]["starSystem"], tminus)
        else:
            summary = u"[Last {}] clean:{} / wanted:{}".format(timespan, counters["clean"], counters["wanted"])
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

    def __are_records_stale(self):
        if self.records.last_updated is None:
            return True
        now = datetime.datetime.now()
        epoch_now = time.mktime(now.timetuple())
        epoch_updated = time.mktime(self.records.last_updated.timetuple())
        return (epoch_now - epoch_updated) > self.records_check_interval

    
    def __update_records_if_stale(self, cmdr_id):
        updated = False
        if self.__are_records_stale():
            missing_seconds = self.timespan
            now = datetime.datetime.now()
            if self.records.last_updated:
                missing_seconds = min(self.timespan, (now - self.records.last_updated).total_seconds())
            
            records = self.server.legal_records(cmdr_id, missing_seconds)
            records = sorted(records, key=lambda t: t["timestamp"], reverse=False)
            recent_records = self.records.get(cmdr_id)
            if recent_records is None:
                recent_records = deque(maxlen=10)
            for record in records:
                recent_records.appendleft(record)

            self.records.set(cmdr_id, recent_records)
            self.records.last_updated = now
            updated = True
        return updated