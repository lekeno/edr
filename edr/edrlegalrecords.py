
import datetime
import time
import os
from collections import deque

from lrucache import LRUCache
from edrconfig import EDRConfig
from edrlog import EDR_LOG
from edtime import EDTime
from edentities import EDFineOrBounty
from edri18n import _, _c


class EDRLegalRecords(object):
    EDR_LEGAL_RECORDS_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cache', 'legal_records.v3.p')
    
    def __init__(self, server):
        self.server = server
        
        self.timespan = None
        self.records_check_interval = None
        config = EDRConfig()

        self.records = LRUCache.load(
            file_path=self.EDR_LEGAL_RECORDS_CACHE,
            max_size=config.lru_max_size(),
            max_age_seconds=config.legal_records_max_age()
        )
        
        self.timespan = config.legal_records_recent_threshold()
        self.records_check_interval = config.legal_records_check_interval()
    
    def persist(self):
        if self.records:
            self.records.save(self.EDR_LEGAL_RECORDS_CACHE)
    
    def summarize(self, cmdr_id):
        if not cmdr_id:
            EDR_LOG.info(u"No cmdr_id, no records for {}".format(cmdr_id))
            return None
        
        self.__update_records_if_stale(cmdr_id)

        record_entry = self.records.peek(cmdr_id)
        records = record_entry.get("records") if record_entry and isinstance(record_entry, dict) else None
        
        if not records:
            EDR_LOG.info(u"No legal records for {}".format(cmdr_id))
            return None
        
        EDR_LOG.info(u"Got legal records for {}".format(cmdr_id))
        overview = None
        (clean, wanted, bounties, recent_stats) = self.__process(records)
        timespan = EDTime.pretty_print_timespan(self.timespan, short=True, verbose=True)
        maxB = u""
        lastB = u""
        
        if recent_stats["maxBounty"]:
            max_bounty = EDFineOrBounty(recent_stats["maxBounty"]).pretty_print()
            maxB = _(u", max={} cr").format(max_bounty)

        if "last" in recent_stats and recent_stats["last"].get("value", None) and (recent_stats["last"].get("starSystem", "") not in ["", "unknown", "Unknown"]):
            tminus = EDTime.t_minus(recent_stats["last"]["timestamp"], short=True)
            last_bounty = EDFineOrBounty(recent_stats["last"]["value"]).pretty_print()
            lastB = _(u", last: {} cr in {} {}").format(last_bounty, recent_stats["last"]["starSystem"], tminus)
        
        # Translators: this is an overview of a cmdr's recent legal history for the 'last {}' days, number of clean and wanted scans, and optionally max and last bounties
        overview = _(u"[Past {}] clean:{} / wanted:{}{}{}").format(timespan, recent_stats["clean"], recent_stats["wanted"], maxB, lastB)
        return {"overview": overview, "clean": clean, "wanted": wanted, "bounties": bounties}

    def __are_records_stale_for_cmdr(self, cmdr_id):
        record_entry = self.records.peek(cmdr_id)

        if record_entry is None:
            return True
        
        last_updated = record_entry.get("last_updated")

        if last_updated is None:
            return True
        
        now = datetime.datetime.now()
        time_since_update = (now - last_updated).total_seconds()
        return time_since_update > self.records_check_interval

    
    def __update_records_if_stale(self, cmdr_id):
        updated = False

        if self.__are_records_stale_for_cmdr(cmdr_id):
            
            try:
                records = self.server.legal_stats(cmdr_id)
                now = datetime.datetime.now() 
                self.records.set(cmdr_id, {"last_updated": now, "records": records})
                updated = True
            
            except Exception as e:
                EDR_LOG.exception(f"Failed to fetch/update records for {cmdr_id} - {e}")
        
        return updated

    def __process(self, legal_stats):
        last = self.__emptyMonthlyBag()
        clean = []
        wanted = []
        bounties = []       
        recent_stats = {"clean": 0, "wanted": 0, "maxBounty": 0, "last": {"value": 0, "timestamp": None, "starSystem": None}}
        now_date = datetime.datetime.now()
        currentYear = now_date.year
        currentMonth = now_date.month
        orderly = self.__orderlyMonthNo()
        monthSpan = int(min(12, round(1 + (self.timespan / (60*60*24) - now_date.day)/30)))
        
        for m in orderly:
            if (m not in legal_stats):
                clean.append(0)
                wanted.append(0)
                bounties.append(0)
                continue

            wayTooOld = int(legal_stats[m]["year"]) < currentYear-1
            tooOld = (int(legal_stats[m]["year"]) == currentYear-1) and int(m) <= currentMonth
            if (wayTooOld or tooOld):
                clean.append(0)
                wanted.append(0)
                bounties.append(0)
                continue
            
            if (m in orderly[12-monthSpan:]):
                recent_stats["clean"] += legal_stats[m]["clean"]
                recent_stats["wanted"] += legal_stats[m]["wanted"]
                if legal_stats[m]["max"]:
                    recent_stats["maxBounty"] = max(recent_stats["maxBounty"], legal_stats[m]["max"].get("value", 0))
                if legal_stats[m]["last"] and legal_stats[m]["last"].get("value", 0) >= recent_stats["last"]["value"]:
                    recent_stats["last"] = legal_stats[m]["last"]

            clean.append(legal_stats[m]["clean"])
            wanted.append(legal_stats[m]["wanted"])
            last[m] = legal_stats[m]["last"]
            bounties.append(legal_stats[m]["max"]["value"])

        return (clean, wanted, bounties, recent_stats)

    @staticmethod
    def __orderlyMonthNo():
        currentMonthIDX0 = datetime.datetime.now().month-1
        return [ str((((currentMonthIDX0 - i) %12) + 12)%12)  for i in range(11,-1,-1)]
    
    @staticmethod
    def __emptyMonthlyBag():
        return {
            '0': None, '1': None, '2': None, '3': None, '4': None, '5': None, 
            '6': None, '7': None, '8': None, '9': None, '10': None, '11': None
        }