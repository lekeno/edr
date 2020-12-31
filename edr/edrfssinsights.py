from edri18n import _, _c
import re
from edtime import EDTime

# TODO verify USS logic and names, perhaps split into its own thing, prioritize in the summary?
# TODO grade USS with long timer, etc.

class EDRFSSInsights(object):
    def __init__(self):
        self.signals = {
            # "$MULTIPLAYER_SCENARIO42_TITLE;": {"count": 0, "short_name": _("Nav Beacon") }, # Not super interesting 
            "$MULTIPLAYER_SCENARIO64_TITLE;": {"count": 0, "short_name": _("USS") },
            "$MULTIPLAYER_SCENARIO80_TITLE;": {"count": 0, "short_name": _("Compromised Nav Beacon") },
            "$MULTIPLAYER_SCENARIO81_TITLE;": {"count": 0, "short_name": _("Salvageable Wreckage")},
            "$FIXED_EVENT_NUMBERSTATION;": {"count": 0, "short_name": _("Anomalous Signal - Numbers Station") },
            "$Warzone_TG;": {"count": 0, "short_name": _("CZ [AX]") },
            "$FIXED_EVENT_CAPSHIP;": {"count": 0, "short_name": _("CAPITAL SHIP") },
            "$NumberStation:#index=1;": {"count": 0, "short_name": _("Unreg. Comms - Numbers Station (Ⅰ)") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T7;": {"count": 0, "short_name": _("Pirates [Th. 7]") },
            "$NumberStation:#index=1;": {"count": 0, "short_name": _("Unreg. Comms") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T7;": {"count": 0, "short_name": _("Pirates [Th. 7]") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T6;": {"count": 0, "short_name": _("Pirates [Th. 6]") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T5;": {"count": 0, "short_name": _("Pirates [Th. 5]") },
            "$USS_Type_Salvage;": {"count": 0, "short_name": _("Degraded E."), "expiring": [] },
            "$USS_Type_ValuableSalvage;": {"count": 0, "short_name": _("Encoded E."), "expiring": [] },
            "$USS_Type_VeryValuableSalvage;": {"count": 0, "short_name": _("High Grade E."), "expiring": [] },
            "$FIXED_EVENT_PROBE;": {"count": 0, "short_name": _("Ancient probe") },
            "$Gro_controlScenarioTitle;": {"count": 0, "short_name": _("Armed Revolt")},
            "$FIXED_EVENT_CHECKPOINT;": {"count": 0, "short_name": _("Checkpoint") },
            "$Ari_controlScenarioTitle;": {"count": 0, "short_name": _("Crime Sweep") },
            "$FIXED_EVENT_DEBRIS;": {"count": 0, "short_name": _("Debris field")},
            "$Aftermath_Large:#index=1;": {"count": 0, "short_name": _("Distress Call (Ⅰ)") },
            "$Aftermath_Large:#index=2;": {"count": 0, "short_name": _("Distress Call (Ⅱ)") },
            "$FIXED_EVENT_DISTRIBUTIONCENTRE;": {"count": 0, "short_name": _("Distribution centre") },
            "$Fixed_Event_Life_Cloud;": {"count": 0, "short_name": _("Stellar phenomena") },
            "$ListeningPost;": {"count": 0, "short_name": _("Listening Post") },
            "$Rep_controlScenarioTitle;": {"count": 0, "short_name": _("Military Strike")},
        }
        self.stations = set()
        self.fleet_carriers = {}
        self.other_locations = set()
        self.resource_extraction_sites = {"available": False, "variants": {"$MULTIPLAYER_SCENARIO14_TITLE;": {"count": 0, "short_name": _c("Standard Res|Std")}, "$MULTIPLAYER_SCENARIO77_TITLE;": {"count": 0, "short_name": _c("Res Low|Low")}, "$MULTIPLAYER_SCENARIO78_TITLE;": {"count": 0, "short_name": _c("Res High|High")}, "$MULTIPLAYER_SCENARIO79_TITLE;": {"count": 0, "short_name": _c("Res Hazardous|Haz")}}, "short_name": _("RES") }
        self.combat_zones = {"available": False, "variants": {"$Warzone_PointRace_Low;":  {"count": 0, "short_name": _c("CZ Low intensity|Low")}, "$Warzone_PointRace_Medium;":  {"count": 0, "short_name": _c("CZ Medium intensity|Med")}, "$Warzone_PointRace_High;":  {"count": 0, "short_name": _c("CZ High intensity|High")}}, "short_name": _("CZ") }

        self.system_address = None
        self.noteworthy = False

    def reset(self):
        for signal_name in self.signals:
            self.signals[signal_name]["count"] = 0
            if "expiring" in self.signals[signal_name]:
                self.signals[signal_name]["expiring"] = []

        self.stations = set()
        self.fleet_carriers = {}
        self.other_locations = set()
        self.resource_extraction_sites = {"available": False, "variants": {"$MULTIPLAYER_SCENARIO14_TITLE;": {"count": 0, "short_name": _("Standard Res|Std")}, "$MULTIPLAYER_SCENARIO77_TITLE;": {"count": 0, "short_name": _("Res Low|Low")}, "$MULTIPLAYER_SCENARIO78_TITLE;": {"count": 0, "short_name": _("Res High|High")}, "$MULTIPLAYER_SCENARIO79_TITLE;": {"count": 0, "short_name": _("Res Hazardous|Haz")}}, "short_name": _("RES") }
        self.combat_zones = {"available": False, "variants": {"$Warzone_PointRace_Low;":  {"count": 0, "short_name": _("CZ Low intensity|Low")}, "$Warzone_PointRace_Medium;":  {"count": 0, "short_name": "CZ Medium intensity|Med"}, "$Warzone_PointRace_High;":  {"count": 0, "short_name": _("CZ High intensity|High")}}, "short_name": _("CZ") }
        self.system_address = None
        self.noteworthy = False

    def process(self, fss_event):
        result = self.__process(fss_event)
        if result:
            self.__prune_expired_signals()
        return result
       

    def __process(self, fss_event):
        if fss_event.get("event", None) != "FSSSignalDiscovered":
            return False

        system_address = fss_event.get("SystemAddress", None)
        if system_address is None:
            return False
        
        if system_address != self.system_address:
            self.reset()
            self.system_address = system_address

        signal_name = fss_event.get("SignalName", None)
        if signal_name is None:
            return False

        if fss_event.get("SignalName_Localised", None) is None:
            self.__process_locations_fss(fss_event)
            self.noteworthy = True
            return True

        if signal_name in self.signals:
            self.signals[signal_name]["count"] += 1
            self.noteworthy = True
            return True
        elif signal_name in ["$USS_HighGradeEmissions;", "$USS_DegradedEmissions;"] and fss_event.get("USSType", None) in self.signals:
            uss_type = fss_event["USSType"]
            self.signals[uss_type]["count"] += 1
            if "TimeRemaining" in fss_event:
                event_time = edtime.EDTime()
                event_time.from_journal_timestamp(jump_request_event["timestamp"])
                expires = event_time.as_py_epoch() + fss_event["TimeRemaining"]
                self.expiring.append(expires)
            self.noteworthy = True
            return True
        elif signal_name in self.combat_zones["variants"]:
            self.combat_zones["available"] = True
            self.combat_zones["variants"][signal_name]["count"] += 1
            return True
        elif signal_name in self.resource_extraction_sites["variants"]:
            self.resource_extraction_sites["available"] = True
            self.resource_extraction_sites["variants"][signal_name]["count"] += 1
            return True
        return False

    def __process_locations_fss(self, fss_event):
        is_station = fss_event.get("IsStation", None)
        location_name = fss_event.get("SignalName", "")
        if not is_station:
            self.other_locations.add(location_name)
            return
        
        fc_regexp = r"^([ -`{}~]+) ([A-Z0-9]{3}-[A-Z0-9]{3})$"
        m = re.match(fc_regexp, location_name)
        if m:
            carrier_name = m.group(1)
            callsign = m.group(2)
            self.fleet_carriers[callsign] = carrier_name
        else:
            self.stations.add(location_name)

    def summarize(self):
        summary = []
        if not self.noteworthy:
            return summary

        self.__prune_expired_signals()

        if self.resource_extraction_sites["available"]:
            counts = []
            for variant in self.resource_extraction_sites["variants"]:
                signal = self.resource_extraction_sites["variants"][variant]
                if signal["count"]:
                    counts.append("{} {}".format(signal["count"], signal["short_name"]))
            if counts:
                summary.append("{}: {}".format(self.resource_extraction_sites["short_name"], "; ".join(counts)))

        if self.combat_zones["available"]:
            counts = []
            for variant in self.combat_zones["variants"]:
                signal = self.combat_zones["variants"][variant]
                if signal["count"]:
                    counts.append("{} {}".format(signal["count"], signal["short_name"]))
            if counts:
                summary.append("{}: {}".format(self.combat_zones["short_name"], "; ".join(counts)))
        
        signals_counts = []
        for signal in self.signals:
            if self.signals[signal]["count"]:
                signals_counts.append("{}: {}".format(self.signals[signal]["short_name"], self.signals[signal]["count"]))
        if signals_counts:
            summary.append("; ".join(signals_counts))

        landables = []
        if self.stations:
            landables.append("Stations: {}".format(len(self.stations)))

        if self.fleet_carriers:
            landables.append("FC: {}".format(len(self.fleet_carriers)))

        if landables:
            summary.append("; ".join(landables))

        if self.other_locations:
            summary.append("Misc.: {}".format(len(self.other_locations)))

        return summary
    
    def __prune_expired_signals(self):
        signals_that_can_expire = [ "$USS_Type_Salvage;", "$USS_Type_ValuableSalvage;", "$USS_Type_VeryValuableSalvage;" ]
        now_epoch = EDTime.py_epoch_now()
        for signal_name in signals_that_can_expire:
            signal = self.signals[signal_name]
            for expiring in signal["expiring"]:
                if now_epoch >= expiring:
                    signal["expiring"].remove(expiring)
                    signal["count"] -= 1

    # TODO: dangerous fleet carriers
    # TODO: report FC sightings
    # TODO: summarize fss insights (e.g. 3 HAZ Res, 3 Stations, 15 FC (3 Notorious))