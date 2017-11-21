import datetime
import calendar

import edrserver
import edrconfig
import edrlog
import edrserver

EDRLOG = edrlog.EDRLog()

class EDRSitReps(object):
    def __init__(self, server):
        config = edrconfig.EDRConfig()
        self.reports_max_age = config.sitreps_max_age()
        self.reports_timespan = config.sitreps_timespan()
        self.last_updated = None
        self.reports = {}
        self.server = server

    def updateIfStale(self):
        if self.last_updated is None or self.isRecent(self.last_updated, self.reports_max_age):
            now = datetime.datetime.now()
            missing_seconds = self.reports_timespan - (now - self.last_updated).total_seconds()
            response = self.server.sitreps(missing_seconds)
            if not response is None:
                self.reports.update(response)
            self.last_updated = now
            return True

        return False

    def hasSitRep(self, system_id):
        self.updateIfStale()

        return system_id in self.reports.keys()

    def NOTSMs(self, system_id):
        if self.hasSitRep(system_id):
            return self.reports[system_id].get("NOTSM", None)

        return None

    def recentCrimes(self, system_id, max_age):
        if self.hasSitRep(system_id):
            system_reports = self.reports[system_id]
            if "latestCrime" not in system_reports.keys():
                return None
            return self.isRecent(system_reports.get["latestCrime"], max_age)
    
        return None

    def crimes(self, system_id):
        #TODO run crimes request
        return None

    def recentTraffic(self, system_id, max_age):
        if self.hasSitRep(system_id):
            system_reports = self.reports[system_id]
            if "latestBlip" not in system_reports.keys():
                return None
            return self.isRecent(system_reports.get["latestBlip"], max_age)

        return None

    def traffic(self, system_id):
        #TODO run traffic request
        return None

    def recentRecon(self, system_id, max_age):
        if self.hasSitRep(system_id):
            system_reports = self.reports[system_id]
            if "latestRecon" not in system_reports.keys():
                return None

            return self.isRecent(system_reports.get["latestRecon"], max_age)

        return None
    
    def isRecent(self, timestamp, max_age):
        n = datetime.datetime.now()
        js_epoch_n = calendar.timegm(n.timetuple()) * 1000

        return (js_epoch_n - timestamp) <= max_age / 1000
