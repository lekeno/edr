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

class EDRLegalRecords(object):
    EDR_LEGAL_RECORDS_CACHE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'cache/legal_records.p')
    
    def __init__(self, server):
        self.server = server
        
        self.timespan = None
        self.records_last_updated = None
        self.records_check_interval = None
        config = edrconfig.EDRConfig()
        self.records = lrucache.LRUCache(config.lru_max_size(), config.legal_records_max_age())
        self.summaries = lrucache.LRUCache(config.lru_max_size(), config.legal_records_max_age())
        self.__apply_config()
    
    def __apply_config(self):
        config = edrconfig.EDRConfig()
        self.timespan = config.legal_records_recent_threshold()
        self.reports_check_interval = config.legal_records_check_interval()

    def load(self):
        try:
            with open(self.EDR_LEGAL_RECORDS_CACHE, 'rb') as handle:
                tmp_edr_legal_records = pickle.load(handle)
                self.__dict__.clear()
                self.__dict__.update(tmp_edr_legal_records)
                self.__apply_config()
        except:
            pass

    def persist(self):
        with open(self.EDR_LEGAL_RECORDS_CACHE, 'wb') as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def summarize_recents(self, cmdr_id):
        self.__update_records_if_stale(cmdr_id)
        records = self.records.get(cmdr_id)
        if not records:
            EDRLOG.log(u"No recent legal records for {}".format(cmdr_id), "INFO")
            return None
        
        self.status = "Got recent legal records"
        EDRLOG.log(u"Got recent legal records for {}".format(cmdr_id), "INFO")
        summary = []
        counters = {"clean": 0, "wanted": 0}
        legal_history = u""
        for record in records:
            counters["wanted"] += record["counters"]["wanted"]
            counters["clean"] += record["counters"]["clean"]
            legal_history += u"■" if record["counters"]["wanted"] else u"□"
        summary.append(u"Wanted ■ scans: {0:.0f}%".format(float(counters["wanted"]) / (counters["wanted"] + counters["clean"])*100.0))
        summary.append(u"Scan history: {}".format(legal_history))
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
        if self.records_last_updated is None:
            return True
        now = datetime.datetime.now()
        epoch_now = time.mktime(now.timetuple())
        epoch_updated = time.mktime(self.records_last_updated.timetuple())
        return (epoch_now - epoch_updated) > self.records_check_interval

    
    def __update_records_if_stale(self, cmdr_id):
        updated = False
        if self.__are_records_stale():
            missing_seconds = self.timespan
            now = datetime.datetime.now()
            if self.records_last_updated:
                missing_seconds = min(self.timespan, (now - self.records_last_updated).total_seconds())
            
            records = self.server.legal_records(cmdr_id, missing_seconds)
            prev_records = self.records.get(cmdr_id)
            if prev_records:
                records.update(prev_records)
            self.records.set(cmdr_id, records)
            self.reports_last_updated = now
            updated = True
        return updated