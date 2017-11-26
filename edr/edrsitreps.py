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
        self.timespan = config.sitreps_timespan()
        self.last_updated = None
        self.reports = {}
        self.notams = {}
        self.server = server

    def updateIfStale(self):
        if not self.__isStale():
            return False

        missing_seconds = self.timespan
        now = datetime.datetime.now()
        if not self.last_updated is None: 
            missing_seconds = self.timespan - (now - self.last_updated).total_seconds()
            
        response = self.server.sitreps(missing_seconds)
        if not response is None:
            self.reports.update(response)

        response = self.server.NOTAMs(missing_seconds)
        if not response is None:
            self.notams.update(response)
        
        self.last_updated = now
        return True

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
            if minutes >0:
                readable += ":{}m".format(minutes)
        elif minutes > 0:
            readable = u"{}m".format(minutes)
            if seconds >0:
                readable += ":{}s".format(seconds)
        else:
            readable = u"{}s".format(seconds)    

        return readable

    def crimes_t_minus(self):
        #TODO needs last_crime_timestamp
        now = datetime.datetime.now()
        return "T-01h30m"

    def traffic_t_minus(self):
        #TODO needs last_blip_timestamp
        now = datetime.datetime.now()
        return "T-01h30m"

    def hasSitRep(self, system_id):
        self.updateIfStale()

        return system_id in self.reports.keys()

    def hasNOTAMs(self, system_id):
        self.updateIfStale()

        return system_id in self.notams.keys()

    def NOTAMs(self, system_id):
        if self.hasNOTAMs(system_id):
            activeNOTAMs = []
            allNOTAMs = self.notams[system_id].get("NOTAMs", None)
            n = datetime.datetime.now()
            js_epoch_n = calendar.timegm(n.timetuple()) * 1000
            for NOTAM in allNOTAMs:
                active = True
                if "from" in NOTAM:
                    active = NOTAM["from"] <= js_epoch_n
                if "until" in NOTAM:
                    active = js_epoch_n <= NOTAM["until"]
                if active:
                    activeNOTAMs.append(NOTAM["text"])
            return activeNOTAMs

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
        if timestamp is None:
            return False
        n = datetime.datetime.now()
        js_epoch_n = calendar.timegm(n.timetuple()) * 1000

        return (js_epoch_n - timestamp) / 1000 <= max_age

    def __isStale(self):
        if self.last_updated is None:
            return True
        n = datetime.datetime.now()
        epoch_n = calendar.timegm(n.timetuple())
        epoch_updated = calendar.timegm(self.last_updated.timetuple())

        return (epoch_n - epoch_updated) > self.reports_max_age
