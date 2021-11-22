from os import system
from edri18n import _, _c
import re
import copy
from edtime import EDTime

class EDRFSSInsights(object):
    def __init__(self):
        self.timestamp = EDTime()
        # TODO show unreg comms as its own category
        self.signals = {
            "$MULTIPLAYER_SCENARIO42_TITLE;": {"count": 0, "short_name": _("Nav Beacon") },
            "$MULTIPLAYER_SCENARIO64_TITLE;": {"count": 0, "short_name": _("USS") },
            "$MULTIPLAYER_SCENARIO80_TITLE;": {"count": 0, "short_name": _("Compromised Nav Beacon") },
            "$MULTIPLAYER_SCENARIO81_TITLE;": {"count": 0, "short_name": _("Salvageable Wreckage")},
            "$FIXED_EVENT_NUMBERSTATION;": {"count": 0, "short_name": _("Anomalous Signal - Numbers Station") },
            "$Warzone_TG;": {"count": 0, "short_name": _("CZ [AX]") },
            "$FIXED_EVENT_CAPSHIP;": {"count": 0, "short_name": _("CAPITAL SHIP") },
            "$NumberStation:#index=1;": {"count": 0, "short_name": _("Unreg. Comms - Numbers Station (Ⅰ)") },
            "$NumberStation:#index=1;": {"count": 0, "short_name": _("Unreg. Comms") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T7;": {"count": 0, "short_name": _("Pirates [Th. 7]") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T6;": {"count": 0, "short_name": _("Pirates [Th. 6]") },
            "$FIXED_EVENT_HIGHTHREATSCENARIO_T5;": {"count": 0, "short_name": _("Pirates [Th. 5]") },
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
        self.uss = {"available": False, "variants": {"$USS_Type_Salvage;":  {"count": 0, "expiring": [], "short_name": _c("Degraded Emissions|Degraded")}, "$USS_Type_ValuableSalvage;":  {"count": 0, "expiring": [], "short_name": _c("Encoded Emissions|Encoded")}, "$USS_Type_VeryValuableSalvage;": {"count": 0, "expiring": [], "short_name": _c("High Grade Emissions|High Grade")}, "misc": {"count": 0, "expiring": [], "short_name": _c("Misc.")}}, "short_name": _("USS") }
        self.pirates = {"available": False, "variants": {"$FIXED_EVENT_HIGHTHREATSCENARIO_T7;":  {"count": 0, "short_name": _c("Pirates Threat 7|Th7")}, "$FIXED_EVENT_HIGHTHREATSCENARIO_T6;":  {"count": 0, "short_name": _c("Pirates Threat 6|Th6")}, "$FIXED_EVENT_HIGHTHREATSCENARIO_T5;":  {"count": 0, "short_name": _c("Pirates Threat 5|Th5")}}, "short_name": _("Pirates") }

        # $USS_Type_DistressSignal;
        # $USS_Type_Convoy;
        # $USS_Type_Aftermath;
        # $USS_Type_Ceremonial;
        # $USS_Type_NonHuman; USSThreat = 4
        # $USS_Type_TradingBeacon;
        # $USS_Type_WeaponsFire; USSThreat

        self.star_system = {"name": None, "address": None}
        self.noteworthy = False
        self.processed = 0
        self.reported = False

    def reset(self, override_timestamp=None):
        for signal_name in self.signals:
            self.signals[signal_name]["count"] = 0
            if "expiring" in self.signals[signal_name]:
                self.signals[signal_name]["expiring"] = []

        self.stations = set()
        self.fleet_carriers = {}
        self.other_locations = set()
        if override_timestamp:
            self.timestamp.from_journal_timestamp(override_timestamp)
        self.resource_extraction_sites = {"available": False, "variants": {"$MULTIPLAYER_SCENARIO14_TITLE;": {"count": 0, "short_name": _c("Standard Res|Std")}, "$MULTIPLAYER_SCENARIO77_TITLE;": {"count": 0, "short_name": _c("Res Low|Low")}, "$MULTIPLAYER_SCENARIO78_TITLE;": {"count": 0, "short_name": _c("Res High|High")}, "$MULTIPLAYER_SCENARIO79_TITLE;": {"count": 0, "short_name": _c("Res Hazardous|Haz")}}, "short_name": _("RES") }
        self.combat_zones = {"available": False, "variants": {"$Warzone_PointRace_Low;":  {"count": 0, "short_name": _c("CZ Low intensity|Low")}, "$Warzone_PointRace_Medium;":  {"count": 0, "short_name": _c("CZ Medium intensity|Med")}, "$Warzone_PointRace_High;":  {"count": 0, "short_name": _c("CZ High intensity|High")}}, "short_name": _("CZ") }
        self.uss = {"available": False, "variants": {"$USS_Type_Salvage;":  {"count": 0, "expiring": [], "short_name": _c("Degraded Emissions|Degraded")}, "$USS_Type_ValuableSalvage;":  {"count": 0, "expiring": [], "short_name": _c("Encoded Emissions|Encoded")}, "$USS_Type_VeryValuableSalvage;": {"count": 0, "expiring": [], "short_name": _c("High Grade Emissions|High Grade")}, "misc": {"count": 0, "expiring": [], "short_name": _c("Misc.")}}, "short_name": _("USS") }
        self.pirates = {"available": False, "variants": {"$FIXED_EVENT_HIGHTHREATSCENARIO_T7;":  {"count": 0, "short_name": _c("Pirates Threat 7|Th7")}, "$FIXED_EVENT_HIGHTHREATSCENARIO_T6;":  {"count": 0, "short_name": _c("Pirates Threat 6|Th6")}, "$FIXED_EVENT_HIGHTHREATSCENARIO_T5;":  {"count": 0, "short_name": _c("Pirates Threat 5|Th5")}}, "short_name": _("Pirates") }
        self.star_system = {"name": None, "address": None}
        self.noteworthy = False
        self.processed = 0
        self.reported = False

    def related_to(self, current_star_system):
        return (self.star_system["name"] is None) or current_star_system == self.star_system["name"]

    def update(self, current_star_system):
        if current_star_system != self.star_system["name"]:
            self.reset()
            self.star_system["address"] = None
            self.star_system["name"] = None

    def update_system(self, system_address, system_name):
        if system_address is not None and self.star_system["address"] is not None and system_address != self.star_system["address"]:
            self.reset()
            self.star_system["address"] = system_address
        if system_name is not None:
            self.star_system["name"] = system_name

    def process(self, fss_event):
        system_address = fss_event.get("SystemAddress", None)
        if system_address is None:
            self.reset()
            return False
        
        if system_address != self.star_system["address"]:
            self.reset(fss_event["timestamp"])
            self.star_system["address"] = system_address
            self.star_system["name"] = None

        result = self.__process(fss_event)
        if result:
            self.processed += 1
            self.timestamp.from_journal_timestamp(fss_event["timestamp"])
        self.__prune_expired_signals()
        return result
       

    def __process(self, fss_event):
        if fss_event.get("event", None) != "FSSSignalDiscovered":
            return False

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
        elif signal_name in ["$USS;"]:
            uss_type = "misc"
            if  fss_event.get("USSType", None) in self.uss["variants"]:
                uss_type = fss_event["USSType"]
            self.uss["variants"][uss_type]["count"] += 1
            self.uss["available"] = True
            if "TimeRemaining" in fss_event:
                event_time = EDTime()
                event_time.from_journal_timestamp(fss_event["timestamp"])
                expires = event_time.as_py_epoch() + fss_event["TimeRemaining"]
                self.uss["variants"][uss_type]["expiring"].append(expires)
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
        elif signal_name in self.pirates["variants"]:
            self.pirates["available"] = True
            self.pirates["variants"][signal_name]["count"] += 1
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
        if self.uss["available"]:
            counts = []
            for variant in self.uss["variants"]:
                signal = self.uss["variants"][variant]
                if signal["count"] <= 0:
                    continue
                rank = self.__expiring_rank(signal["expiring"])
                counts.append("{} {}({})".format(signal["count"], signal["short_name"], rank))
            if counts:
                summary.append("{}: {}".format(self.uss["short_name"], "; ".join(counts)))
        
        if self.resource_extraction_sites["available"]:
            counts = []
            for variant in self.resource_extraction_sites["variants"]:
                signal = self.resource_extraction_sites["variants"][variant]
                if signal["count"] > 0:
                    counts.append("{} {}".format(signal["count"], signal["short_name"]))
            if counts:
                summary.append("{}: {}".format(self.resource_extraction_sites["short_name"], "; ".join(counts)))

        if self.combat_zones["available"]:
            counts = []
            for variant in self.combat_zones["variants"]:
                signal = self.combat_zones["variants"][variant]
                if signal["count"] > 0:
                    counts.append("{} {}".format(signal["count"], signal["short_name"]))
            if counts:
                summary.append("{}: {}".format(self.combat_zones["short_name"], "; ".join(counts)))

        if self.pirates["available"]:
            counts = []
            for variant in self.pirates["variants"]:
                signal = self.pirates["variants"][variant]
                if signal["count"] > 0:
                    counts.append("{} {}".format(signal["count"], signal["short_name"]))
            if counts:
                summary.append("{}: {}".format(self.pirates["short_name"], "; ".join(counts)))
        
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
        now_epoch = EDTime.py_epoch_now()
        for uss_type in self.uss["variants"]:
            signal = self.uss["variants"][uss_type]
            for expiring in signal["expiring"]:
                if now_epoch >= expiring:
                    signal["expiring"].remove(expiring)
                    signal["count"] -= 1


    def __expiring_rank(self, expiring):
        now_epoch = EDTime.py_epoch_now()
        best_one = max(expiring)
        duration = best_one - now_epoch
        if duration <= 60*5:
            return "-"
        
        return round(min(duration / (40*60), 1) * 5)*"+"

    def fleet_carriers_report(self, force_reporting=False):
        if not force_reporting and (self.star_system["name"] is None or self.processed == 0):
            return None

        report = {
            "starSystem": self.star_system["name"],
            "timestamp": self.timestamp.as_js_epoch(),
            "fcCount": len(self.fleet_carriers),
        }

        if len(self.fleet_carriers):
            report["fc"] = copy.deepcopy(self.fleet_carriers)

        return report


    # TODO: dangerous fleet carriers