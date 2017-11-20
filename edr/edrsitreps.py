import datetime
import calendar

import edrserver
import edrconfig
import edrlog

EDRLOG = edrlog.EDRLog()

class EDRSitReps(object):
    def __init__(self):
        config = edrconfig.EDRConfig()
        self.reports_max_age = config.sitreps_max_age()
        self.last_updated = None
        self.reports = {}

    def updateIfStale(self):
        if self.last_updated is None or self.isRecent(self.last_updated, self.reports_max_age):
            #TODO run query
            self.last_updated = datetime.datetime.now()
            return True

        return False

    def hasSitRep(self, system_name):
        self.updateIfStale()

        return system_name in self.reports.keys()

    def NOTSMs(self, system_name):
        if self.hasSitRep(system_name):
            return self.reports[system_name].get("NOTSM", None)

        return None

    def recentCrimes(self, system_name, max_age):
        if self.hasSitRep(system_name):
            system_reports = self.reports[system_name]
            if "latestCrime" not in system_reports.keys():
                return None
            return self.isRecent(system_reports.get["latestCrime"], max_age)
    
        return None

    def crimes(self, system_name):
        #TODO run crimes request
        return None

    def recentTraffic(self, system_name, max_age):
        if self.hasSitRep(system_name):
            system_reports = self.reports[system_name]
            if "latestBlip" not in system_reports.keys():
                return None
            return self.isRecent(system_reports.get["latestBlip"], max_age)

        return None

    def traffic(self, system_name):
        #TODO run traffic request
        return None

    def recentRecon(self, system_name, max_age):
        if self.hasSitRep(system_name):
            system_reports = self.reports[system_name]
            if "latestRecon" not in system_reports.keys():
                return None

            return self.isRecent(system_reports.get["latestRecon"], max_age)

        return None
    
    def isRecent(self, timestamp, max_age):
        n = datetime.datetime.now()
        js_epoch_n = calendar.timegm(n.timetuple()) * 1000

        return (js_epoch_n - timestamp) <= max_age / 1000

