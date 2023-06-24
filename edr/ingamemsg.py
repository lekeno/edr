# coding= utf-8
from __future__ import division
import os
import sys
import math
import json
from random import choices
from string import ascii_uppercase, digits
import re

import igmconfig
import edrlog
import textwrap
from edri18n import _, _c
import utils2to3
from edrlandables import EDRLandables
from edentities import EDFineOrBounty, pretty_print_number
from edtime import EDTime

EDRLOG = edrlog.EDRLog()

if sys.platform == "win32":
    _overlay_dir = utils2to3.pathmaker(__file__, u'EDMCOverlay')
    if _overlay_dir not in sys.path:
        sys.path.append(_overlay_dir)

try:
    import edmcoverlay
except ImportError:
    raise Exception(str(sys.path))

import lrucache

class InGameMsg(object):   
    MESSAGE_KINDS = ["intel", "warning", "sitrep", "notice", "help", "navigation", "docking", "mining", "bounty-hunting", "target-guidance", "biology"]
    LEGAL_KINDS = ["intel", "warning"] 

    def __init__(self, standalone=False):
        self.standalone_overlay = standalone
        self.compatibility_issue = False
        if (standalone):
            try:
                self._overlay = edmcoverlay.Overlay(args=["--standalone"])
            except:
                self._overlay = edmcoverlay.Overlay()
                self.compatibility_issue = True
        else:
            self._overlay = edmcoverlay.Overlay()
        self.cfg = {}
        self.layout_type = None
        self.must_clear = False
        self.msg_ids = lrucache.LRUCache(1000, 60*15)
        self.in_ship_layout()

    def in_ship_layout(self):
        if self.layout_type != "ship":
            self.clear()
            conf = igmconfig.IGMConfigInShip()
            self.configure_layout(conf)
            self.layout_type = "ship"
    
    def on_foot_layout(self):
        if self.layout_type != "spacelegs":
            self.clear()
            conf = igmconfig.IGMConfigOnFoot()
            self.configure_layout(conf)
            self.layout_type = "spacelegs"

    def configure_layout(self, conf):
        self.cfg = {}
        self.general_config(conf)
        for kind in self.MESSAGE_KINDS:
            self.message_config(kind, conf)
        for kind in self.LEGAL_KINDS:
            self.legal_config(kind, conf)
        self.docking_config(conf)
        self.mining_config(conf)
        self.bounty_hunting_config(conf)
        self.target_guidance_config(conf)
        self.navroute_config(conf)

    def reconfigure(self):
        if self.layout_type == "spacelegs":
            self.layout_type = None
            self.on_foot_layout()
        else:
            self.layout_type = None
            self.in_ship_layout()
          
        
    def general_config(self, conf):
        self.cfg["general"] = {
            "large" : {
                "h": conf.large_height(),
                "w": conf.large_width()
            },
            "normal" : {
                "h": conf.normal_height(),
                "w": conf.normal_width()
            }
        }

    def message_config(self, kind, conf):
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "h": {
                "x": conf.x(kind, "header"),
                "y": conf.y(kind, "header"),
                "ttl": conf.ttl(kind, "header"),
                "rgb": conf.rgb(kind, "header"),
                "size": conf.size(kind, "header"),
                "len": conf.len(kind, "header"),
                "align": conf.align(kind, "header")
            },
            "b": {
                "x": conf.x(kind, "body"),
                "y": conf.y(kind, "body"),
                "ttl": conf.ttl(kind, "body"),
                "rgb": conf.rgb(kind, "body"),
                "size": conf.size(kind, "body"),
                "len": conf.len(kind, "body"),
                "align": conf.align(kind, "body"),
                "rows": conf.body_rows(kind),
                "cache": lrucache.LRUCache(conf.body_rows(kind), conf.ttl(kind, "body")),
                "last_row": 0
            }
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def legal_config(self, kind, conf):
        kind = u"{}-legal".format(kind)
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "clean": {
                "x": conf.x(kind, "clean"),
                "y": conf.y(kind, "clean"),
                "h": conf.h(kind, "clean_bar"),
                "w": conf.w(kind, "clean_bar"),
                "s": conf.s(kind, "clean_bar"),
                "ttl": conf.ttl(kind, "clean"),
                "rgb": conf.rgb_list(kind, "clean"),
                "fill": conf.fill_list(kind, "clean"),
            },
            "wanted": {
                "x": conf.x(kind, "wanted"),
                "y": conf.y(kind, "wanted"),
                "h": conf.h(kind, "wanted_bar"),
                "w": conf.w(kind, "wanted_bar"),
                "s": conf.s(kind, "wanted_bar"),
                "ttl": conf.ttl(kind, "wanted"),
                "rgb": conf.rgb_list(kind, "wanted"),
                "fill": conf.fill_list(kind, "wanted"),
            },
            "bounties": {
                "x": conf.x(kind, "bounties"),
                "y": conf.y(kind, "bounties"),
                "h": conf.h(kind, "bounties_bar"),
                "w": conf.w(kind, "bounties_bar"),
                "s": conf.s(kind, "bounties_bar"),
                "ttl": conf.ttl(kind, "bounties"),
                "rgb": conf.rgb_list(kind, "bounties"),
                "fill": conf.fill_list(kind, "bounties"),
            },
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def docking_config(self, conf):
        kind = "docking-station"
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "schema": {
                "x": conf.x(kind, "schema"),
                "y": conf.y(kind, "schema"),
                "h": conf.h(kind, "schema"),
                "w": conf.w(kind, "schema"),
                "ttl": conf.ttl(kind, "schema"),
                "rgb": conf.rgb_list(kind, "schema"),
                "fill": conf.fill_list(kind, "schema"),
            }
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def navroute_config(self, conf):
        default_markers = ["circle"]*7
        default_markers.extend(["cross"]*16)
        kind = "navroute"
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "schema": {
                "x": conf.x(kind, "schema"),
                "y": conf.y(kind, "schema"),
                "h": conf.h(kind, "schema"),
                "w": conf.w(kind, "schema"),
                "ttl": conf.ttl(kind, "schema"),
                "rgb": conf.rgb_list(kind, "schema"),
                "marker": conf.string_list(kind, "schema", "marker", default_markers),
                "suffix": conf.string_list(kind, "schema", "suffix", None),
                "intervalx": conf.getint(kind, "schema", "intervalx", 60),
                "intervaly": conf.getint(kind, "schema", "intervaly", 0),
                "symbolintervalx": conf.getint(kind, "schema", "symbolintervalx", 16),
                "symbolintervaly": conf.getint(kind, "schema", "symbolintervaly", 0),
                "stoplen": conf.getint(kind, "schema", "stoplen", 25)
            }
        }
    
        if not conf.panel(kind):
            return
        
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def mining_config(self, conf):
        kind = "mining-graphs" 
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "yield": {
                "x": conf.x(kind, "yield"),
                "y": conf.y(kind, "yield"),
                "h": conf.h(kind, "yield_bar"),
                "w": conf.w(kind, "yield_bar"),
                "s": conf.s(kind, "yield_bar"),
                "ttl": conf.ttl(kind, "yield"),
                "rgb": conf.rgb_list(kind, "yield"),
                "fill": conf.fill_list(kind, "yield"),
            },
            "efficiency": {
                "x": conf.x(kind, "efficiency"),
                "y": conf.y(kind, "efficiency"),
                "h": conf.h(kind, "efficiency_bar"),
                "w": conf.w(kind, "efficiency_bar"),
                "s": conf.s(kind, "efficiency_bar"),
                "ttl": conf.ttl(kind, "efficiency"),
                "rgb": conf.rgb_list(kind, "efficiency"),
                "fill": conf.fill_list(kind, "efficiency"),
            },
            "distribution": {
                "x": conf.x(kind, "distribution"),
                "y": conf.y(kind, "distribution"),
                "h": conf.h(kind, "distribution_bar"),
                "w": conf.w(kind, "distribution_bar"),
                "s": conf.s(kind, "distribution_bar"),
                "ttl": conf.ttl(kind, "distribution"),
                "rgb": conf.rgb_list(kind, "distribution"),
                "fill": conf.fill_list(kind, "distribution"),
            },
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def bounty_hunting_config(self, conf):
        kind = "bounty-hunting-graphs" 
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "bounty": {
                "x": conf.x(kind, "bounty"),
                "y": conf.y(kind, "bounty"),
                "h": conf.h(kind, "bounty_bar"),
                "w": conf.w(kind, "bounty_bar"),
                "s": conf.s(kind, "bounty_bar"),
                "ttl": conf.ttl(kind, "bounty"),
                "rgb": conf.rgb_list(kind, "bounty"),
                "fill": conf.fill_list(kind, "bounty"),
            },
            "efficiency": {
                "x": conf.x(kind, "efficiency"),
                "y": conf.y(kind, "efficiency"),
                "h": conf.h(kind, "efficiency_bar"),
                "w": conf.w(kind, "efficiency_bar"),
                "s": conf.s(kind, "efficiency_bar"),
                "ttl": conf.ttl(kind, "efficiency"),
                "rgb": conf.rgb_list(kind, "efficiency"),
                "fill": conf.fill_list(kind, "efficiency"),
            },
            "distribution": {
                "x": conf.x(kind, "distribution"),
                "y": conf.y(kind, "distribution"),
                "h": conf.h(kind, "distribution_bar"),
                "w": conf.w(kind, "distribution_bar"),
                "s": conf.s(kind, "distribution_bar"),
                "ttl": conf.ttl(kind, "distribution"),
                "rgb": conf.rgb_list(kind, "distribution"),
                "fill": conf.fill_list(kind, "distribution"),
            },
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def target_guidance_config(self, conf):
        kind = "target-guidance-graphs" 
        self.cfg[kind] = {
            "enabled": conf._getboolean(kind, "enabled"),
            "shield": {
                "x": conf.x(kind, "shield"),
                "y": conf.y(kind, "shield"),
                "h": conf.h(kind, "shield"),
                "w": conf.w(kind, "shield"),
                "ttl": conf.ttl(kind, "shield"),
                "rgb": conf.rgb_list(kind, "shield")
            },
            "hull": {
                "x": conf.x(kind, "hull"),
                "y": conf.y(kind, "hull"),
                "h": conf.h(kind, "hull"),
                "w": conf.w(kind, "hull"),
                "ttl": conf.ttl(kind, "hull"),
                "rgb": conf.rgb_list(kind, "hull")
            },
            "subsys": {
                "x": conf.x(kind, "subsys"),
                "y": conf.y(kind, "subsys"),
                "h": conf.h(kind, "subsys"),
                "w": conf.w(kind, "subsys"),
                "ttl": conf.ttl(kind, "subsys"),
                "rgb": conf.rgb_list(kind, "subsys")
            },
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }

    def intel(self, header, details, legal=None):
        if not self.cfg["intel"].get("enabled", None):
            return

        self.__clear_if_needed()
        if "panel" in self.cfg["intel"]:
            self.__shape("intel", self.cfg["intel"]["panel"])
        kind_legal = u"intel-legal"
        if "panel" in self.cfg[kind_legal] and self.cfg[kind_legal].get("enabled", False):
            self.__shape(kind_legal, self.cfg[kind_legal]["panel"])
        self.__msg_header("intel", header)
        self.__msg_body("intel", details)
        
        if not self.cfg["intel-legal"].get("enabled", None):
            return
        if not legal:
            legal = { "clean": [0]*12, "wanted": [0]*12, "bounties": [0]*12 }
        self.__legal_vizualization(legal, "intel")
        

    def warning(self, header, details, legal=None):
        if not self.cfg["warning"].get("enabled", None):
            return

        self.__clear_if_needed()
        if "panel" in self.cfg["warning"]:
            self.__shape("warning", self.cfg["warning"]["panel"])
        kind_legal = u"warning-legal"
        if "panel" in self.cfg[kind_legal] and self.cfg[kind_legal].get("enabled", False):
            self.__shape(kind_legal, self.cfg[kind_legal]["panel"])
        self.__msg_header("warning", header)
        self.__msg_body("warning", details)
        if not self.cfg["warning-legal"].get("enabled", None):
            return
        if not legal:
            legal = { "clean": [0]*12, "wanted": [0]*12, "bounties": [0]*12 }
        self.__legal_vizualization(legal, "warning")

    def notify(self, header, details):
        if not self.cfg["notice"].get("enabled", None):
            return

        self.__clear_if_needed()
        if "panel" in self.cfg["notice"]:
            self.__shape("notice", self.cfg["notice"]["panel"])
        self.__msg_header("notice", header)
        self.__msg_body("notice", details)
    
    def help(self, header, details):
        if not self.cfg["help"].get("enabled", None):
            return
        self.__clear_if_needed()
        if "panel" in self.cfg["help"]:
            self.__shape("help", self.cfg["help"]["panel"])
        self.__msg_header("help", header)
        self.__msg_body("help", details)
        self.must_clear = True

    def sitrep(self, header, details):
        if not self.cfg["sitrep"].get("enabled", None):
            return
        self.__clear_if_needed()
        self.__clear_kind("sitrep")
        if "panel" in self.cfg["sitrep"]:
            self.__shape("sitrep", self.cfg["sitrep"]["panel"])
        self.__msg_header("sitrep", header)
        self.__msg_body("sitrep", details)

    def navigation(self, bearing, destination, distance=None, pitch=None):
        if not self.cfg["navigation"].get("enabled", None):
            return
        self.clear_navigation()
        if "panel" in self.cfg["navigation"]:
            self.__shape("navigation", self.cfg["navigation"]["panel"])
        header = u"› {:03} ‹     ↓ {:02} ↓".format(bearing, pitch) if pitch else u"> {:03} <".format(bearing)
        details = [destination.title] if destination.title else []
        if distance >= 1.0:
            details.append(_(u"Dis: {}km").format(int(distance)))
        else:
            details.append(_(u"Dis: {}m").format(int(distance*1000)))
        details.append(_(u"Lat: {:.4f}").format(destination.latitude))
        details.append(_(u"Lon: {:.4f}").format(destination.longitude))
        if destination.heading is not None:
            details.append(_(u"Head: > {:03} <").format(destination.heading))
        if destination.altitude:
            if destination.altitude >= 1.0:
                details.append(_(u"Alt: {}km").format(int(destination.altitude)))
            else:
                details.append(_(u"Alt: {}m").format(destination.altitude))
        self.__msg_header("navigation", header)
        self.__msg_body("navigation", details)

    def biology_guidance(self, species, ccr, value, distances_meters, bearings):
        # TODO Osseus Discus on rough, hilly areas instead. Concha Renibus will keep to rocky places, bacteria flat ground hard to find not worth much
        # TODO planets with thin water atmospheres are best; best main stars to filter for are B and A, then Neutron stars, Non-Sequence filter), F and G, in this order. In mass codes, not surprisingly this would mean D and E.
        # TODO the DSS filters only show genus, and if a planet has different species (and/or colours) of the same kind, they won't show up there separately! For example, a planet might have three species of brain trees, or bacteria, or whatever else, all under the same biological signal. See the Organics tab on the system map to see how many distinct species you can sample on a planet.
        if not self.cfg["biology"].get("enabled", None):
            return
        self.clear_biology()
        if "panel" in self.cfg["biology"]:
            self.__shape("biology", self.cfg["biology"]["panel"])
        header = species
        details = []
        details.append(_("Value: {} credits".format(pretty_print_number(value))))
        details.append(_("Gene diversity: +{}m").format(ccr))
        i = 1
        for distance in distances_meters:
            check = u"◌" if distance < ccr else u"●"
            if distance > ccr and distance >= 10000:
                details.append(_(u"{} Sample #{}: ≥10km  ›{:03}‹").format(check, i, bearings[i-1]))
            else:
                details.append(_(u"{} Sample #{}: {}m  ›{:03}‹").format(check, i, math.floor(distance), bearings[i-1]))
            i += 1
        self.__msg_header("biology", header)
        self.__msg_body("biology", details)

    def describe_station(self, station):
        station_type = (station.get("type","N/A") or "N/A").lower()
        station_other_services = (station.get("otherServices", []) or []) 
        station_economy = (station.get('economy', "") or "").lower()
        station_second_economy = (station.get('secondEconomy', "") or "").lower()
        details = []
        a = u"◌" if station_type in ["outpost"] else u"●"
        b = u"●" if station.get("haveOutfitting", False) else u"◌"
        c = u"●" if station.get("haveShipyard", False) else u"◌"
        details.append(_(u"LG. Pad:{}   Outfit:{}   Shipyard:{}").format(a,b,c))
        a = u"●" if "Refuel" in station_other_services else u"◌"
        b = u"●" if "Repair" in station_other_services else u"◌"
        c = u"●" if "Restock" in station_other_services else u"◌"
        details.append(_(u"Refuel:{}   Repair:{}   Restock:{}").format(a,b,c))
        a = u"●" if station.get("haveMarket", False) else u"◌"
        b = u"●" if "Black Market" in station_other_services else u"◌"
        c = u"◌"
        m = _c(u"material trader|M.") 
        if "Material Trader" in station_other_services:
            c = u"●"
            if station_economy in ['extraction', 'refinery']:
                if not station["secondEconomy"]:
                    m = _(u"RAW")
                elif station_second_economy == "industrial":
                    m = _(u"R/M")
                elif station_second_economy in ["high tech", "military"]:
                    m = _(u"R/E")
            elif station_economy == 'industrial':
                if not station["secondEconomy"]:
                    m = _(u"MAN")
                elif station_second_economy in ["extraction", "refinery"]:
                    m = _(u"M/R")
                elif station_second_economy in ["high tech", "military"]:
                    m = _(u"M/E")
            elif station_economy in ['high tech', 'military']:
                if not station["secondEconomy"]:
                    m = _(u"ENC")
                elif station_second_economy in ["extraction", "refinery"]:
                    m = _(u"E/R")
                elif station_second_economy == "industrial":
                    m = _(u"E/M")
        details.append(_(u"Market:{}   B.Market:{}   {} Trad:{}").format(a,b,m,c))
        a = u"●" if "Interstellar Factors Contact" in station_other_services else u"◌"
        t = _c(u"tech broker|T.")
        b =  u"◌" 
        if "Technology Broker" in station_other_services:
            b = u"●"
            if station_economy == 'high tech':
                if not station["secondEconomy"]:
                    t = _c(u"guardian tech|GT.")
                elif station_second_economy == "industrial":
                    t = _c(u"ambiguous tech|T.")
            elif station_economy == 'industrial':
                if not station["secondEconomy"]:
                    t = _c(u"human tech|HT.") 
                elif station_second_economy == "high tech":
                    t = _c(u"ambiguous tech|T.")

        details.append(_(u"I.Factor:{}   {} Broker:{}").format(a,t,b))
        details.append(_(u"as of {date}").format(date=station['updateTime']['information']))
        return details

    def describe_fleet_carrier(self, fc):
        fc_other_services = (fc.get("otherServices", []) or []) 
        details = []
        a = u"●" if fc.get("haveOutfitting", False) else u"◌"
        b = u"●" if fc.get("haveShipyard", False) else u"◌"
        details.append(_(u"Outfit:{}   Shipyard:{}").format(a,b))
        a = u"●" if "Refuel" in fc_other_services else u"◌"
        b = u"●" if "Repair" in fc_other_services else u"◌"
        c = u"●" if "Restock" in fc_other_services else u"◌"
        details.append(_(u"Refuel:{}   Repair:{}   Restock:{}").format(a,b,c))
        a = u"●" if fc.get("haveMarket", False) else u"◌"
        b = u"●" if "Black Market" in fc_other_services else u"◌"
        details.append(_(u"Market:{}   B.Market:{}").format(a,b))
        a = u"●" if "Interstellar Factors Contact" in fc_other_services else u"◌"
        details.append(_(u"I.Factor:{}").format(a))
        details.append(_(u"as of {date}").format(date=fc['updateTime']['information']))
        return details

    def docking(self, system, station, pad):
        if not self.cfg["docking"].get("enabled", None):
            return

        self.clear_docking()
        if not station:
            return
        if "panel" in self.cfg["docking"]:
            self.__shape("docking", self.cfg["docking"]["panel"])
        if "panel" in self.cfg["docking-station"] and self.cfg["docking-station"].get("enabled", False):
            self.__shape("docking-station", self.cfg["docking-station"]["panel"])
        
        economy = u"{}/{}".format(station["economy"], station["secondEconomy"]) if station["secondEconomy"] else station["economy"]
        station_type = (station.get("type","N/A") or "N/A").lower()

        header = u"{} ({})".format(station["name"], economy)
        details = self.describe_station(station)
        self.__msg_header("docking", header)
        self.__msg_body("docking", details)

        if not self.cfg["docking-station"]["enabled"]:
            return {"header": header, "body": details}
        
        if station_type in ["asteroid base", 'bernal starport', "coriolis starport", "ocellus starport", "orbis starport", "bernal", "bernal statioport"]:
            self.__station_schematic(pad)
        else:
            self.__landable_schematic(system, station, pad)
        return {"header": header, "body": details}

    def __landable_schematic(self, system, station, pad):
        station_type = (station.get("type","N/A") or "N/A").lower()
        station_name = (station.get("name","N/A") or "N/A").lower()
        map_data = EDRLandables.map_for(system, station_name, station_type)
        if not map_data:
            return

        cfg = self.cfg[u"docking-station"]
        x = cfg["schema"]["x"]
        y = cfg["schema"]["y"]
        w = cfg["schema"]["w"]
        h = cfg["schema"]["h"]
        hw = w/2.0
        hh = h/2.0
        cx = int(round(x + hw))
        cy = int(round(y + hh))
        the_pad = str(pad)
        contour = map_data.get("contour", {})
        for element in contour:
            points = contour[element]["points"]
            scaled = [{"x":int(cx+(coords["x"]*hw)), "y":int(cy-(coords["y"]*hh))} for coords in points]
            vect = {
                "id": u"landable-{}".format(element),
                "color": contour[element]["active"] if element == the_pad else contour[element]["color"],
                "ttl": cfg["schema"]["ttl"],
                "vector": scaled
            }
            self.__vect(u"docking", vect)
        
        pads_guidance = map_data.get("pads-guidance", {})
        if the_pad in pads_guidance:
            guidance = pads_guidance.get(the_pad, {})
            points = guidance["points"]
            scaled = [{"x":int(cx+(coords["x"]*hw)), "y":int(cy-(coords["y"]*hh))} for coords in points]
            vect = {
                "id": u"guidance-{}".format(pad),
                "color": guidance["color"],
                "ttl": cfg["schema"]["ttl"],
                "vector": scaled
            }
            self.__vect(u"docking", vect)
    
    def __station_schematic(self, landing_pad):
        cfg = self.cfg[u"docking-station"]
        x = cfg["schema"]["x"]
        y = cfg["schema"]["y"]
        w = cfg["schema"]["w"]
        h = cfg["schema"]["h"]

        cx = int(round(x + w/2.0))
        cy = int(round(y + h/2.0))
        
        red_light = {
            "x": int(x),
            "y": int(cy - (0.12962962962962962962962962962963 * h)),
            "x2": max(1, int(0.03125 * w)),
            "y2": max(1,int(2.0*0.12962962962962962962962962962963 * h)),
            "rgb": cfg["schema"]["rgb"][0],
            "fill": cfg["schema"]["fill"][0],
            "ttl": cfg["schema"]["ttl"],
        }
        self.__shape(u"docking", red_light)

        green_light = {
            "x": int(x+w-(0.03125 * w)),
            "y": int(cy - (0.12962962962962962962962962962963 * h)),
            "x2": max(1,int(0.03125 * w)),
            "y2": max(1, int(2.0*0.12962962962962962962962962962963 * h)),
            "rgb": cfg["schema"]["rgb"][1],
            "fill": cfg["schema"]["fill"][1],
            "ttl": cfg["schema"]["ttl"],
        }
        self.__shape(u"docking", green_light)

        # dodecaedron
        w = w-4
        h = h-2
        alpha = math.radians(15)
        sin15 = math.sin(alpha)
        cos15 = math.cos(alpha)
        sin45 = math.sqrt(2) / 2
        dodecagon = [
            (cos15, sin15),
            (cos15, -sin15),
            (sin45, -sin45),
            (sin15, -cos15),
            (-sin15, -cos15),
            (-sin45, -sin45),
            (-cos15, -sin15),
            (-cos15, sin15),
            (-sin45, sin45),
            (-sin15, cos15),
            (sin15, cos15),
            (sin45, sin45),
            (cos15, sin15),
        ]

        radials = {
            "outer": [],
            "inner": []
        }
        scales = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25 ]
        major_scales = [scales[0], scales[2], scales[5]]
        i = 0
        for s in major_scales:
            rx = 1.0*s*w/2.0
            ry = 1.0*s*h/2.0
            points = []
            for (dx, dy) in dodecagon:
                x = int(round(cx + dx*rx))
                y = int(round(cy + dy*ry))
                points.append({"x": x, "y": y})
            if s == major_scales[0]:
                radials["outer"] = points
            elif s == major_scales[-1]:
                radials["inner"] = points
            wireframe = {
                "id": u"station-wireframe-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.__vect(u"docking", wireframe)
            i = i+1

        i = 0
        for s in [scales[1], scales[4]]:
            points = []
            rx = 1.0*s*w/2.0
            ry = 1.0*s*h/2.0
            for (dx, dy) in dodecagon[0:4]:
                x = int(round(cx + dx*rx))
                y = int(round(cy + dy*ry))
                points.append({"x": x, "y": y})
            wireframe = {
                "id": u"station-wireframe-1-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.__vect(u"docking", wireframe)
            
            points = []
            for (dx, dy) in dodecagon[4:8]:
                x = int(round(cx + dx*rx))
                y = int(round(cy + dy*ry))
                points.append({"x": x, "y": y})
            wireframe = {
                "id": u"station-wireframe-2-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.__vect(u"docking", wireframe)

            points = []
            for (dx, dy) in dodecagon[8:12]:
                x = int(round(cx + dx*rx))
                y = int(round(cy + dy*ry))
                points.append({"x": x, "y": y})
            wireframe = {
                "id": u"station-wireframe-3-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.__vect(u"docking", wireframe)
            i = i+1

        s = scales[3]
        rx = 1.0*s*w/2.0
        ry = 1.0*s*h/2.0
        points = []
        for (dx, dy) in dodecagon[2:4]:
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
        wireframe = {
            "id": u"station-wireframe-1-{}".format(s),
            "color": cfg["schema"]["rgb"][3],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.__vect(u"docking", wireframe)
        
        points = []
        for (dx, dy) in dodecagon[6:8]:
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
        wireframe = {
            "id": u"station-wireframe-2-{}".format(s),
            "color": cfg["schema"]["rgb"][3],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.__vect(u"docking", wireframe)

        points = []
        for (dx, dy) in dodecagon[10:12]:
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
        wireframe = {
            "id": u"station-wireframe-3-{}".format(s),
            "color": cfg["schema"]["rgb"][3],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.__vect(u"docking", wireframe)
        
        for o,i in zip(radials["outer"], radials["inner"]):
            wireframe = {
                "id": u"station-radial-{}-{}-{}-{}".format(o["x"], o["y"], i["x"], i["y"]),
                "color": cfg["schema"]["rgb"][5],
                "ttl": cfg["schema"]["ttl"],
                "vector": [o,i]
            }
            self.__vect(u"docking", wireframe)
        
        pad_lut = {
            35: [0,1,0,1,1],
            36: [0,1,1,2,0],
            37: [0,1,2,4,1],
            38: [0,1,4,5,1],
            31: [1,2,0,1,0],
            32: [1,2,1,2,2],
            33: [1,2,2,4,1],
            34: [1,2,4,5,0],
            26: [2,3,0,1,1],
            27: [2,3,1,2,0],
            28: [2,3,2,3,0],
            29: [2,3,3,4,0],
            30: [2,3,4,5,1],
            24: [3,4,0,2,2],
            25: [3,4,2,5,2],
            20: [4,5,0,1,1],
            21: [4,5,1,2,0],
            22: [4,5,2,4,1],
            23: [4,5,4,5,1],
            16: [5,6,0,1,0],
            17: [5,6,1,2,2],
            18: [5,6,2,4,1],
            19: [5,6,4,5,0],
            11: [6,7,0,1,1],
            12: [6,7,1,2,0],
            13: [6,7,2,3,0],
            14: [6,7,3,4,0],
            15: [6,7,4,5,1],
             9: [7,8,0,2,2],
            10: [7,8,2,5,2],
             5: [8,9,0,1,1],
             6: [8,9,1,2,0],
             7: [8,9,2,4,1],
             8: [8,9,4,5,1],
             1: [9,10,0,1,0],
             2: [9,10,1,2,2],
             3: [9,10,2,4,1],
             4: [9,10,4,5,0],
            41: [10,11,0,1,1],
            42: [10,11,1,2,0],
            43: [10,11,2,3,0],
            44: [10,11,3,4,0],
            45: [10,11,4,5,1],
            39: [11,12,0,2,2],
            40: [11,12,2,5,2],
        }

        pad_loc = pad_lut[landing_pad]
        points = []
        pad_scales = [scales[pad_loc[2]], scales[pad_loc[3]]]
        pad_scales[0] = pad_scales[0]-(pad_scales[0]-pad_scales[1])*.1
        pad_scales[1] = pad_scales[1]+(pad_scales[0]-pad_scales[1])*.1
        for s in pad_scales:
            rx = 1.0*s*w/2.0
            ry = 1.0*s*h/2.0
            (dx, dy) = dodecagon[pad_loc[0]]
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
            (dx, dy) = dodecagon[pad_loc[1]]
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
        points.append(points[0])
        points.append(points[2])
        points.append(points[3])
        points.append(points[1])
        points.append(points[0])
        pad_highlight = {
            "id": u"station-pad-{}".format(landing_pad),
            "color": cfg["schema"]["rgb"][6+pad_loc[4]],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.__vect(u"docking", pad_highlight)


    def __legal_vizualization(self, legal, kind):
        cleans = legal["clean"]
        wanteds = legal["wanted"]
        bounties = legal["bounties"]
        cfg = self.cfg[u"{}-legal".format(kind)]
        maxBounty = max(bounties)
        maxCW = max(cleans + wanteds)
        ystep = {"clean": maxCW / float(cfg["clean"]["h"]), "wanted": maxCW / float(cfg["wanted"]["h"]), "bounties": maxBounty / float(cfg["bounties"]["h"])} 
        x = {"clean": 0, "wanted": 0, "bounties": 0}
        y = 0
        h = 0
        m = 0

        bar = {
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 0,
            "rgb": "#000000",
            "fill": "#000000",
            "ttl": 0,
        }

        for clean, wanted, bounty in zip(cleans, wanteds, bounties):
            dx = cfg["clean"]["x"]
            dy = cfg["clean"]["y"]
            h = max(clean/ystep["clean"],1) if clean else 1
            y = cfg["clean"]["h"] - h
            bar["x"] = int(x["clean"]+dx)
            bar["y"] =int(dy-h)
            bar["x2"] = int(cfg["clean"]["w"])
            bar["y2"] = dy - bar["y"]
            bar["rgb"] = cfg["clean"]["rgb"][m] or self.__cleancolor(clean, kind) 
            bar["fill"] = self.__cleancolor(clean, kind)
            bar["ttl"] = cfg["clean"]["ttl"]
            self.__shape(u"{}-clean-bar".format(kind), bar)

            dx = cfg["wanted"]["x"]
            dy = cfg["wanted"]["y"]
            h = max(wanted/ystep["wanted"], 1) if wanted else 1
            y = 0
            bar["x"] = int(x["wanted"]+dx)
            bar["y"] = int(y+dy)
            bar["x2"] = int(cfg["wanted"]["w"])
            bar["y2"] = int(h)
            bar["rgb"] = cfg["wanted"]["rgb"][m] or self.__wantedcolor(wanted, kind) 
            bar["fill"] = self.__wantedcolor(wanted, kind)
            bar["ttl"] = cfg["wanted"]["ttl"]
            self.__shape(u"{}-wanted-bar".format(kind), bar)

            dx = cfg["bounties"]["x"]
            dy = cfg["bounties"]["y"]
            h = max(bounty/ystep["bounties"],1) if bounty else 1
            y = cfg["bounties"]["h"] - h
            bar["x"] = int(x["bounties"]+dx)
            bar["y"] = int(dy-h)
            bar["x2"] = int(cfg["bounties"]["w"])
            bar["y2"] = dy - bar["y"]
            bar["rgb"] = cfg["bounties"]["rgb"][m] or self.__bountycolor(bounty, kind) 
            bar["fill"] = self.__bountycolor(bounty, kind)
            bar["ttl"] = cfg["bounties"]["ttl"]
            self.__shape("{}-bounty-bar".format(kind), bar)

            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}
            m += 1

    def mining_guidance(self, mining_stats):
        if not self.cfg["mining"].get("enabled", None):
            return
        self.clear_mining_guidance()
        if "panel" in self.cfg["mining"]:
            self.__shape("mining", self.cfg["mining"]["panel"])
        if "panel" in self.cfg["mining-graphs"] and self.cfg["mining-graphs"].get("enabled", False):
            self.__shape("mining-graphs", self.cfg["mining-graphs"]["panel"])
        
        header = _(u"Mining Stats")
        details = []
        has_stuff = len(mining_stats.last["minerals_stats"]) > 0
        if has_stuff:
            detailed_stats = mining_stats.last["minerals_stats"]
            header = _(u"Mining Stats - MNR: {}").format(",".join(m.symbol for m in detailed_stats))
            details.append(_(u"MNR %: {:>6.2f}  [{}/{}; {}]").format(detailed_stats[0].last["proportion"], detailed_stats[0].symbol, mining_stats.last["materials"], mining_stats.last["raw"]))
            details.append(_(u"MAX %: {:>6.2f}").format(detailed_stats[0].max))
            details.append(_(u"AVG %: {:>6.2f}").format(detailed_stats[0].yield_average(mining_stats.prospected_nb)))
        elif mining_stats.depleted:
            details.append(u"")
            details.append(_(u">> DEPLETED <<"))
            details.append(u"")
        else:
            details.append(u"")
            details.append(_(u">> WORTHLESS <<"))
            details.append(u"")
        
        
        details.append(_(u"ITM/H: {:>6.0f} [TGT: {:.0f}]").format(mining_stats.item_per_hour(), mining_stats.max_efficiency))
        details.append(_(u"ITM #: {:>6}").format(mining_stats.refined_nb))
        self.__msg_header("mining", header)
        self.__msg_body("mining", details)

        if not self.cfg["mining-graphs"].get("enabled", None):
            return
            
        self.__mining_vizualization(mining_stats)
    
    def __mining_vizualization(self, mining_stats):
        if mining_stats.last["minerals_stats"]:
            self.__mineral_stats_vizualization(mining_stats.last["minerals_stats"][0], mining_stats.prospected_nb)
        
        cfg = self.cfg[u"mining-graphs"]
        max_efficiency = mining_stats.max_efficiency
        ystep = {"efficiency": max_efficiency / float(cfg["efficiency"]["h"])} 
        x = {"efficiency": 0}
        y = 0
        h = 0

        bar = {
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 0,
            "rgb": "#000000",
            "fill": "#000000",
            "ttl": 0,
        }
        
        for e in mining_stats.efficiency:
            dx = cfg["efficiency"]["x"]
            dy = cfg["efficiency"]["y"]
            efficiency = e[1]
            h = max(efficiency/ystep["efficiency"],1) if efficiency else 0
            bar["x"] = int(x["efficiency"]+dx)
            bar["y"] = int(dy-h)
            bar["x2"] = int(cfg["efficiency"]["w"])
            bar["y2"] = 1
            index = int(efficiency/mining_stats.max_efficiency * (len(cfg["efficiency"]["rgb"])-1.0))
            bar["rgb"] = cfg["efficiency"]["rgb"][index]
            bar["fill"] = cfg["efficiency"]["fill"][index]
            bar["ttl"] = cfg["efficiency"]["ttl"]
            self.__shape(u"mining-graphs-efficiency-bar", bar)
            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}

    def __mineral_stats_vizualization(self, mineral_stats, prospected_nb):
        cfg = self.cfg[u"mining-graphs"]
        max_yield = max(50, mineral_stats.max)
        max_distribution = max(mineral_stats.distribution["bins"][1:])
        ystep = {"yield": max_yield / float(cfg["yield"]["h"])} 
        x = {"yield": 0}
        y = 0
        h = 0

        bar = {
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 0,
            "rgb": "#000000",
            "fill": "#000000",
            "ttl": 0,
        }

        for p in mineral_stats.prospectements:
            dx = cfg["yield"]["x"]
            dy = cfg["yield"]["y"]
            proportion = p[1]
            if proportion > 0:
                h = max(proportion/ystep["yield"],1)
                bar["x"] = int(x["yield"]+dx)
                bar["y"] =int(dy-h)
                bar["x2"] = int(cfg["yield"]["w"])
                bar["y2"] = dy - bar["y"]
                index = int(proportion/100.0 * (len(cfg["yield"]["rgb"])-1.0))
                bar["rgb"] = cfg["yield"]["rgb"][index]
                index = int(proportion/100.0 * (len(cfg["yield"]["fill"])-1.0))
                bar["fill"] = cfg["yield"]["fill"][index]
                bar["ttl"] = cfg["yield"]["ttl"]
                self.__shape(u"mining-graphs-yield-bar", bar)
            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}
        
        avg = mineral_stats.yield_average(prospected_nb)
        h = max(avg/ystep["yield"],1)
        bar["x"] = dx
        bar["y"] =int(dy-h)
        bar["x2"] = x["yield"]
        bar["y2"] = 1
        index = int(avg/100.0 * (len(cfg["yield"]["rgb"])-1.0))
        bar["rgb"] = cfg["yield"]["rgb"][index]
        index = int(avg/100.0 * (len(cfg["yield"]["fill"])-1.0))
        bar["fill"] = cfg["yield"]["fill"][index]
        bar["ttl"] = cfg["yield"]["ttl"]
        self.__shape(u"mining-graphs-yield-avg-bar", bar)


        y = {"distribution": cfg["distribution"]["w"]+cfg["distribution"]["s"]}
        i = 1
        for c in mineral_stats.distribution["bins"][1:]:
            dx = cfg["distribution"]["x"]
            dy = cfg["distribution"]["y"]
            p = c / max_distribution if max_distribution > 0 else 1 
            h = max(p * cfg["distribution"]["h"],1) if c else 0
            x = h
            bar["x"] = int(dx)
            bar["y"] = int(dy-y["distribution"])
            bar["x2"] = int(x)
            bar["y2"] = int(cfg["distribution"]["w"])
            index = int(i/len(mineral_stats.distribution["bins"]) * (len(cfg["distribution"]["rgb"])-1.0))
            bar["rgb"] = cfg["distribution"]["rgb"][index]
            bar["fill"] = cfg["distribution"]["fill"][index]
            bar["ttl"] = cfg["distribution"]["ttl"]
            self.__shape(u"mining-graphs-distribution-bar", bar)
            i = i+1
            y = {category: y[category] + cfg[category]["w"] + cfg[category]["s"] for category in y}

        dx = cfg["distribution"]["x"]
        dy = cfg["distribution"]["y"]
        h = (mineral_stats.distribution["last_index"] * (cfg["distribution"]["w"] + cfg["distribution"]["s"]))
        bar["x"] = int(dx-3)
        bar["y"] = int(dy-h)
        bar["x2"] = 1
        bar["y2"] = int(cfg["distribution"]["w"])
        index = int(mineral_stats.distribution["last_index"]/len(mineral_stats.distribution["bins"]) * (len(cfg["distribution"]["rgb"])-1.0))
        bar["rgb"] = cfg["distribution"]["rgb"][index]
        bar["fill"] = cfg["distribution"]["fill"][index]
        bar["ttl"] = cfg["distribution"]["ttl"]
        self.__shape(u"mining-graphs-distribution-last-mark", bar)

    def bounty_hunting_guidance(self, bounty_hunting_stats):
        if not self.cfg["bounty-hunting"].get("enabled", None):
            return

        self.clear_bounty_hunting_guidance()
        self.clear_docking()
        if "panel" in self.cfg["bounty-hunting"]:
            self.__shape("bounty-hunting", self.cfg["bounty-hunting"]["panel"])
        if "panel" in self.cfg["bounty-hunting-graphs"] and self.cfg["bounty-hunting-graphs"].get("enabled", False):
            self.__shape("bounty-hunting-graphs", self.cfg["bounty-hunting-graphs"]["panel"])
        
        header = _(u"Bounty Hunting Stats")
        details = []
        last_bounty = EDFineOrBounty(bounty_hunting_stats.last["bounty"])
        max_bounty = EDFineOrBounty(bounty_hunting_stats.max)
        avg_bounty = EDFineOrBounty(bounty_hunting_stats.bounty_average())
        cr_h = EDFineOrBounty(bounty_hunting_stats.credits_per_hour())
        tgt = EDFineOrBounty(bounty_hunting_stats.max_efficiency)
        total_awarded = EDFineOrBounty(bounty_hunting_stats.sum_awarded)
        details.append(_(u"BOUNTY: {} cr [{}]").format(last_bounty.pretty_print(), bounty_hunting_stats.last["name"]))
        details.append(_(u"MAX B.: {} cr").format(max_bounty.pretty_print()))
        details.append(_(u"AVG B.: {} cr").format(avg_bounty.pretty_print()))
        details.append(_(u"CR / H: {} [TGT: {}]").format(cr_h.pretty_print(), tgt.pretty_print()))
        details.append(_(u"TOTALS: {} cr [{} rewards]").format(total_awarded.pretty_print(), bounty_hunting_stats.awarded_nb))
        self.__msg_header("bounty-hunting", header)
        self.__msg_body("bounty-hunting", details)
        
        if not self.cfg["bounty-hunting-graphs"].get("enabled", None):
            return
        self.__bounty_hunting_vizualization(bounty_hunting_stats)
    
    def __bounty_hunting_vizualization(self, bounty_hunting_stats):
        cfg = self.cfg[u"bounty-hunting-graphs"]
        max_bounty = max(bounty_hunting_stats.max_normal_bounty, bounty_hunting_stats.max)
        max_distribution = max(bounty_hunting_stats.distribution["bins"][1:])
        max_efficiency = bounty_hunting_stats.max_efficiency
        ystep = {"bounty": max_bounty / float(cfg["bounty"]["h"]), "efficiency": max_efficiency / float(cfg["efficiency"]["h"])} 
        x = {"bounty": 0}
        y = 0
        h = 0

        bar = {
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 0,
            "rgb": "#000000",
            "fill": "#000000",
            "ttl": 0,
        }

        dx = cfg["bounty"]["x"]
        dy = cfg["bounty"]["y"]
        for p in bounty_hunting_stats.scans:
            scan = p[1]
            if scan > 0:
                h = max(scan/ystep["bounty"],1)
                bar["x"] = int(x["bounty"]+dx)
                bar["y"] =int(dy-h)
                bar["x2"] = int(cfg["bounty"]["w"])
                bar["y2"] = dy - bar["y"]
                index = int(scan/max_bounty * (len(cfg["bounty"]["rgb"])-1.0))
                bar["rgb"] = cfg["bounty"]["rgb"][index]
                index = int(scan/max_bounty * (len(cfg["bounty"]["fill"])-1.0))
                bar["fill"] = cfg["bounty"]["fill"][index]
                bar["ttl"] = cfg["bounty"]["ttl"]
                self.__shape(u"bounty-hunting-graphs-bounty-bar", bar)
            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}
        
        avg = bounty_hunting_stats.bounty_average()
        h = max(avg/ystep["bounty"],1)
        bar["x"] = dx
        bar["y"] =int(dy-h)
        bar["x2"] = x["bounty"]
        bar["y2"] = 1
        index = int(avg/max_bounty * (len(cfg["bounty"]["rgb"])-1.0))
        bar["rgb"] = cfg["bounty"]["rgb"][index]
        index = int(avg/max_bounty * (len(cfg["bounty"]["fill"])-1.0))
        bar["fill"] = cfg["bounty"]["fill"][index]
        bar["ttl"] = cfg["bounty"]["ttl"]
        self.__shape(u"bounty-hunting-graphs-bounty-avg-bar", bar)


        y = {"distribution": cfg["distribution"]["w"]+cfg["distribution"]["s"]}
        i = 1
        dx = cfg["distribution"]["x"]
        dy = cfg["distribution"]["y"]
        for c in bounty_hunting_stats.distribution["bins"][1:]:
            p = c / max_distribution if max_distribution > 0 else 1
            h = max(p * cfg["distribution"]["h"],1) if c else 0
            x = h
            bar["x"] = int(dx)
            bar["y"] = int(dy-y["distribution"])
            bar["x2"] = int(x)
            bar["y2"] = int(cfg["distribution"]["w"])
            index = int(i/len(bounty_hunting_stats.distribution["bins"]) * (len(cfg["distribution"]["rgb"])-1.0))
            bar["rgb"] = cfg["distribution"]["rgb"][index]
            bar["fill"] = cfg["distribution"]["fill"][index]
            bar["ttl"] = cfg["distribution"]["ttl"]
            self.__shape(u"bounty-hunting-graphs-distribution-bar", bar)
            i = i+1
            y = {category: y[category] + cfg[category]["w"] + cfg[category]["s"] for category in y}

        h = (bounty_hunting_stats.last["distribution_index"] * (cfg["distribution"]["w"] + cfg["distribution"]["s"]))
        bar["x"] = int(dx-3)
        bar["y"] = int(dy-h)
        bar["x2"] = 1
        bar["y2"] = int(cfg["distribution"]["w"])
        index = int(bounty_hunting_stats.last["distribution_index"]/len(bounty_hunting_stats.distribution["bins"]) * (len(cfg["distribution"]["rgb"])-1.0))
        bar["rgb"] = cfg["distribution"]["rgb"][index]
        bar["fill"] = cfg["distribution"]["fill"][index]
        bar["ttl"] = cfg["distribution"]["ttl"]
        self.__shape(u"bounty-hunting-graphs-distribution-last-mark", bar)


        x = {"efficiency": 0}
        dx = cfg["efficiency"]["x"]
        dy = cfg["efficiency"]["y"]
        for e in bounty_hunting_stats.efficiency:
            efficiency = e[1]
            h = max(efficiency/ystep["efficiency"],1) if efficiency else 0
            bar["x"] = int(x["efficiency"]+dx)
            bar["y"] = int(dy-h)
            bar["x2"] = int(cfg["efficiency"]["w"])
            bar["y2"] = 1
            index = int(efficiency/bounty_hunting_stats.max_efficiency * (len(cfg["efficiency"]["rgb"])-1.0))
            bar["rgb"] = cfg["efficiency"]["rgb"][index]
            bar["fill"] = cfg["efficiency"]["fill"][index]
            bar["ttl"] = cfg["efficiency"]["ttl"]
            self.__shape(u"bounty-hunting-graphs-efficiency-bar", bar)
            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}

    def target_guidance(self, target, subsys_details=None):
        if not self.cfg["target-guidance"].get("enabled", None):
            return

        self.clear_target_guidance()
        if not target or not target.vehicle:
            return
        tgt_vehicle = target.targeted_vehicle or target.vehicle
        if "panel" in self.cfg["target-guidance"]:
            self.__shape("target-guidance", self.cfg["target-guidance"]["panel"])
        if "panel" in self.cfg["target-guidance-graphs"] and self.cfg["target-guidance-graphs"].get("enabled", False):
            self.__shape("target-guidance-graphs", self.cfg["target-guidance-graphs"]["panel"])
        
        header = _(u"{prefix}{cmdr} ({ship})").format(prefix=_(u"CMDR ") if target.is_human() else "", cmdr=target.name, ship=tgt_vehicle.type)
        details = []
        
        shield_stats = tgt_vehicle.shield_health_stats()
        shield_label = u"{:.4g}".format(tgt_vehicle.shield_health) if tgt_vehicle.shield_health else u"-"
        delta_shield = ""
        signal = "●" if tgt_vehicle.shield_up and shield_stats.last_value() else "◌"
        trend = shield_stats.trend()
        if int(trend) > 0:
            signal = "▴" if tgt_vehicle.shield_up and shield_stats.last_value() > 0 else "▵"
            if trend < 60*60:
                delta_shield = _(u"[{} to 100%/UP]").format(EDTime.pretty_print_timespan(int(trend), short=True, verbose=False))
        elif int(trend) < 0:
            signal = "▾"
            if trend > -60*60:
                delta_shield = _(u"[{} to   0%]").format(EDTime.pretty_print_timespan(int(-trend), short=True, verbose=False))
        details.append(_(u"SHLD{}: {}% {}").format(signal, shield_label, delta_shield))

        hull_stats = tgt_vehicle.hull_health_stats()
        hull_label = u"{:.4g}".format(tgt_vehicle.hull_health) if tgt_vehicle.hull_health else u"-"
        delta_hull = ""
        signal = "●"
        trend = hull_stats.trend()
        if int(trend) > 0:
            signal = "▴"
            if trend < 60*60:
                delta_hull = _(u"[{} to 100%]").format(EDTime.pretty_print_timespan(int(trend), short=True, verbose=False))
        elif int(trend) < 0:
            signal = "▾"
            if trend > -60*60:
                delta_hull = _(u"[{} to   0%]").format(EDTime.pretty_print_timespan(int(-trend), short=True, verbose=False))
        details.append(_(u"HULL{}: {}% {}").format(signal, hull_label, delta_hull))

        if subsys_details:
            signal = "●"
            delta_subsys = ""
            if subsys_details["stats"].meaningful():
                trend = subsys_details["stats"].trend()
                if int(trend) > 0:
                    signal = "▴"
                    if trend < 60*60:
                        delta_subsys = _(u"[{} to 100%]").format(EDTime.pretty_print_timespan(int(trend), short=True, verbose=False))
                elif int(trend) < 0:
                    signal = "▾"
                    if trend > -60*60:
                        delta_subsys = _(u"[{} to   0%]").format(EDTime.pretty_print_timespan(int(-trend), short=True, verbose=False))
            details.append(_(u"{subsys}{signal}: {hp:.4g}% {delta}").format(subsys=subsys_details["shortname"], signal=signal, hp=subsys_details["stats"].last_value(), delta=delta_subsys))
        self.__msg_header("target-guidance", header)
        self.__msg_body("target-guidance", details)

        if not self.cfg["target-guidance-graphs"].get("enabled", None):
            return
        subsys_stats = subsys_details["stats"] if subsys_details else None
        self.__target_guidance_vizualization(tgt_vehicle.shield_up, shield_stats, hull_stats, subsys_stats)
    
    def __target_guidance_vizualization(self, shield_up, shield_stats, hull_stats, subsys_stats):
        shield_history = shield_stats.history
        hull_history = hull_stats.history
        subsys_history = subsys_stats.history if subsys_stats else None
        if len(shield_history) == 0 or len(hull_history) == 0:
            return

        cfg = self.cfg[u"target-guidance-graphs"]
        xspan = max(shield_stats.history_max_span_ms, hull_stats.history_max_span_ms)
        if subsys_history:
            xspan = max(xspan, subsys_stats.history_max_span_ms)
        x = cfg["shield"]["x"]
        y = cfg["shield"]["y"]
        w = cfg["shield"]["w"]
        h = cfg["shield"]["h"]
        hw = w/2.0
        hh = h/2.0
        cx = x
        cy = y+h
        scaled = []
        last = max(shield_history[-1]["timestamp"], hull_history[-1]["timestamp"])
        if subsys_history:
            last = max(last, subsys_history[-1]["timestamp"])
        shield_down = not shield_up or (shield_history[-1]["value"] <= 0 if shield_history[-1] else False)
        EDRLOG.log("shield {}".format(shield_history), "DEBUG")
        for t_v in shield_history:
            t = t_v["timestamp"]
            if (last - t) > xspan and len(scaled) >= 2:
                continue
            x = max(0.0, 1.0 - (last-t) / xspan)
            y = t_v["value"]/100.0
            s = {"x":int(cx+x*w), "y":int(cy-(y*h))}
            if scaled and scaled[-1]["x"] == s["x"]:
                adjusted = scaled[-1]
                adjusted["y"] = min(scaled[-1]["y"], s["y"])
                scaled[-1] = adjusted
            else:
                scaled.append(s)
        vect = {
            "id": u"shield-sparkline",
            "color": cfg["shield"]["rgb"][1] if shield_down else cfg["shield"]["rgb"][0],
            "ttl": cfg["shield"]["ttl"],
            "vector": scaled
        }
        self.__vect(u"target-guidance", vect)

        x = 1.0 - shield_stats.trend_span_ms / xspan
        vect = {
            "id": u"shield-trend-span",
            "color": cfg["shield"]["rgb"][2],
            "ttl": cfg["shield"]["ttl"],
            "vector": [{"x":int(cx+x*w), "y":int(cy-.5*h-1)}, {"x":int(cx+x*w), "y":int(cy-.5*h+1)}]
        }
        self.__vect(u"target-guidance", vect)
            

        x = cfg["hull"]["x"]
        y = cfg["hull"]["y"]
        w = cfg["hull"]["w"]
        h = cfg["hull"]["h"]
        cx = x
        cy = y+h
        scaled = []
        EDRLOG.log("hull {}".format(hull_history), "DEBUG")
        for t_v in hull_history:
            t = t_v["timestamp"]
            if (last - t) > xspan and len(scaled) >= 2:
                continue
            x = max(0.0, 1.0 - (last-t) / xspan)
            y = t_v["value"]/100.0
            s = {"x":int(cx+x*w), "y":int(cy-(y*h))}
            if scaled and scaled[-1]["x"] == s["x"]:
                adjusted = scaled[-1]
                adjusted["y"] = min(scaled[-1]["y"] , s["y"])
                scaled[-1] = adjusted
            else:
                scaled.append(s)
        vect = {
            "id": u"hull-sparkline",
            "color": cfg["hull"]["rgb"][0],
            "ttl": cfg["hull"]["ttl"],
            "vector": scaled
        }
        self.__vect(u"target-guidance", vect)
        
        x = 1.0 - hull_stats.trend_span_ms / xspan
        vect = {
            "id": u"hull-trend-span",
            "color": cfg["hull"]["rgb"][1],
            "ttl": cfg["hull"]["ttl"],
            "vector": [{"x":int(cx+x*w), "y":int(cy-.5*h-1)}, {"x":int(cx+x*w), "y":int(cy-.5*h+1)}]
        }
        self.__vect(u"target-guidance", vect)

        if not subsys_history or len(subsys_history) == 0:
            return
        x = cfg["subsys"]["x"]
        y = cfg["subsys"]["y"]
        w = cfg["subsys"]["w"]
        h = cfg["subsys"]["h"]
        cx = x
        cy = y+h
        scaled = []
        EDRLOG.log("subsys {}".format(subsys_history), "DEBUG")
        for t_v in subsys_history:
            t = t_v["timestamp"]
            if (last - t) > xspan and len(scaled) >= 2:
                continue
            x = max(0.0, 1.0 - (last-t) / xspan)
            y = t_v["value"]/100.0
            s = {"x":int(cx+x*w), "y":int(cy-(y*h))}
            if scaled and scaled[-1]["x"] == s["x"]:
                adjusted = {"x": s["x"], "y": min(scaled[-1]["y"], s["y"])}
                scaled[-1] = adjusted
            else:
                scaled.append(s)
        vect = {
            "id": u"subsys-sparkline",
            "color": cfg["subsys"]["rgb"][0],
            "ttl": cfg["subsys"]["ttl"],
            "vector": scaled
        }
        self.__vect(u"target-guidance", vect)

        x = 1.0 - subsys_stats.trend_span_ms / xspan
        vect = {
            "id": u"subsys-trend-span",
            "color": cfg["subsys"]["rgb"][1],
            "ttl": cfg["subsys"]["ttl"],
            "vector": [{"x":int(cx+x*w), "y":int(cy-.5*h-1)}, {"x":int(cx+x*w), "y":int(cy-.5*h+1)}]
        }
        self.__vect(u"target-guidance", vect)

    def navroute(self, route_navigator):
        if not self.cfg["navroute"].get("enabled", None):
            return
        
        self.clear_nav_route()
        
        navroute = route_navigator.route
        if not navroute or navroute.empty() or navroute.trivial():
            return
        
        self.__draw_navroute(route_navigator)

            
    def __draw_navroute(self, route_navigator):
        navroute = route_navigator.route
        stats = route_navigator.route_stats
        
        cfg = self.cfg["navroute"]
        if "panel" in cfg:
            self.__shape("navroute", cfg["panel"])
            
        x = cfg["schema"]["x"]
        y = cfg["schema"]["y"]
        w = cfg["schema"]["w"]
        h = cfg["schema"]["h"]
        star_classes = "o,b,a,f,g,k,m,ms,c*,d*,h*,n,l,aebe,t,tts,s,w*,x,y,rogueplanet,nebula,stellarremnantnebula,*".split(",")
        default_rgbs = "D8793E,00B3F7,00B3F7,2423E9,2F2DE3,4C37D2,5C5C93,908E46,CC432A,E9332A,CC0000,55552B,616CE2,808080,3FEFFF,FF2600,F56A79,4A0000,4A0000,3B3B3B,6E6E89,FF00DC,B16C00,FF00DC,FF00DC,4CFF00,FF00CC".split(",")
        rgbs = cfg["schema"]["rgb"]
        if not rgbs or len(rgbs) < len(star_classes)+3:
            EDRLOG.log("Draw nav route: reverting to default rgbs (length mismatch)", "DEBUG")
            rgbs = default_rgbs
        route_rgb = rgbs[0]
        travelled_rgb = rgbs[1]
        current_rgb = rgbs[2]
        star_rgbs = rgbs[3:]
        
        default_star_markers = "circle,circle,circle,circle,circle,circle,circle,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross".split(",")
        star_markers = cfg["schema"]["marker"]
        if not star_markers or len(star_markers) < len(star_classes):
            EDRLOG.log("Draw nav route: reverting to default markers (length mismatch)", "DEBUG")
            star_markers = default_star_markers

        default_suffix = ",,,,,,,,, dwarf, blackhole, neutron,,,,,,, exotic,, rogue, nebula, sr nebula, ???".split(",")
        star_suffix = cfg["schema"]["suffix"]
        if not star_suffix or len(star_suffix) < len(star_classes):
            EDRLOG.log("Draw nav route: reverting to default suffix (length mismatch)", "DEBUG")
            star_suffix = default_suffix

        
        # TODO see if the position of the last label can be fixed; seems way off.
        # TODO overlap on the last-1 step....
        vects = {
            "travelled": {
                "id": "navroute-schema-travelled",
                "color": travelled_rgb,
                "shape": "vect",
                "ttl": cfg["schema"]["ttl"],
                "vector": []
            },
            "remaining": {
                "id": "navroute-schema-remaining",
                "color": route_rgb,
                "shape": "vect",
                "ttl": cfg["schema"]["ttl"],
                "vector": []
            }
        }

        inc_x = w / (len(navroute.jumps.collection)-1)
        inc_y = h / (len(navroute.jumps.collection)-1)
        sys_name_len = cfg["schema"]["stoplen"]
        interval_x = cfg["schema"]["intervalx"]
        interval_y = cfg["schema"]["intervaly"]
        symbol_interval_x = cfg["schema"]["symbolintervalx"]
        symbol_interval_y = cfg["schema"]["symbolintervaly"]
        inc_steps = 1
        if inc_x and inc_x < symbol_interval_x:
            inc_steps = symbol_interval_x / inc_x
            inc_x = symbol_interval_x
        elif inc_y and inc_y < symbol_interval_y:
            inc_steps = symbol_interval_x / inc_x
            inc_y = symbol_interval_y
        
        prev_x = None
        prev_y = None
        last_x = x + w
        last_y = y + h
        
        white_dwarves = "d da dab dao daz dav db dbz dbv do dov dq dc dcv dx".split()
        carbon_stars = "c c-j cj c-n cn c-hd chd".split()
        blackholes = "h blackhole supermassiveblackhole".split()
        wolf_rayet = "w wc wn wnc wo".split()
            

        steps = 0
        for i, stop in enumerate(navroute.jumps.collection):
            steps += 1
            if steps < inc_steps:
                EDRLOG.log("skipping: {} steps: {} vs {}".format(stop.get("StarSystem", None), steps, inc_steps), "DEBUG")
                continue
            steps = 0
            star_class = stop.get("StarClass", "N/A").lower()
            if star_class in white_dwarves:
                star_class = "d*"
            elif star_class in carbon_stars:
                star_class = "c*"
            elif star_class in blackholes:
                star_class = "h*"
            elif star_class in wolf_rayet:
                star_class = "w*"

            if star_class not in star_classes:
                star_class = "*"

        
            sc_index = star_classes.index(star_class) if star_class in star_classes else len(star_classes)-1
            vector = {
                "x":int(x), 
                "y":int(y),
                "marker": star_markers[sc_index],
                "color": star_rgbs[sc_index],
            }

            system_name = stop.get("StarSystem", None)
            generic = bool(re.search(r'\d',  system_name))
            too_close_to_last = (i < len(navroute.jumps.collection)-1) and ((last_x - x) < interval_x or (last_y - y < interval_y))
            risk_of_overlap = (prev_x and prev_y) and ((((x - prev_x) < interval_x) or ((y - prev_y) < interval_y)) or too_close_to_last)
            
            if not risk_of_overlap and system_name and (not generic or i in [0, navroute.jumps.index-1, navroute.jumps.index, len(navroute.jumps.collection)-1]):
                trunc_label = system_name[:sys_name_len]+"..." if len(system_name) > sys_name_len+2 else system_name
                # TODO further trunc generic name by removing the common part if there is a close one "Eol Prou Px-T D3-1078" => "E... 1078" ?
                label = trunc_label
                
                if i == 0 and stats.jumps_nb:
                    label += "\n{} J; {} LY; {}".format(stats.jumps_nb, round(stats.travelled_ly,1), EDTime.pretty_print_timespan(stats.elapsed_time()))
                elif i == navroute.jumps.index-1:
                    vector["color"] = current_rgb
                    label = "► {}".format(system_name)
                    if stats.jmp_hr() and stats.ly_hr() and stats.s_jmp():
                        label += "\n{} sec/J; {} LY/HR".format(stats.s_jmp(), stats.ly_hr())
                elif i == len(navroute.jumps.collection)-1 and stats.remaining_ly():
                    # TODO should be jump based not distance based
                    remaining_time = stats.remaining_time(True)
                    if remaining_time:
                        label += "\n{} J; {} LY; {}".format(stats.remaining_waypoints, stats.remaining_ly(), EDTime.pretty_print_timespan(remaining_time))
                    else:
                        label += "\n{} J; {} LY".format(stats.remaining_waypoints, stats.remaining_ly())
                elif sc_index < len(star_suffix) and star_suffix[sc_index]:
                    label += star_suffix[sc_index]
                    
                vector["text"] = label
                prev_x = x
                prev_y = y
            
            if i <= navroute.jumps.index-1:
                vects["travelled"]["vector"].append(vector)
            else:
                if not vects["remaining"]["vector"] and vects["travelled"]["vector"]:
                    previous_stop = vects["travelled"]["vector"][-1]
                    vects["remaining"]["vector"].append(previous_stop)
                vects["remaining"]["vector"].append(vector)

            x += inc_x
            y += inc_y

        if vects["travelled"]["vector"]:
            self.__vect(u"navroute-map-travelled", vects["travelled"])
        
        if vects["remaining"]["vector"]:
            self.__vect(u"navroute-map-remaining", vects["remaining"])

    def clear(self):
        msg_ids = list(self.msg_ids.keys())
        for msg_id in msg_ids:
            self.__clear(msg_id)
        self.msg_ids.reset()
        self.must_clear = False

    def clear_intel(self):
        self.__clear_kind("intel")
    
    def clear_sitrep(self):
        self.__clear_kind("sitrep")

    def clear_notice(self):
        self.__clear_kind("notice")
    
    def clear_warning(self):
        self.__clear_kind("warning")

    def clear_navigation(self):
        self.__clear_kind("navigation")
    
    def clear_biology(self):
        self.__clear_kind("biology")

    def clear_docking(self):
        self.__clear_kind("docking")
    
    def clear_mining_guidance(self):
        self.__clear_kind("mining")

    def clear_bounty_hunting_guidance(self):
        self.__clear_kind("bounty-hunting")

    def clear_target_guidance(self):
        self.__clear_kind("target-guidance")  

    def clear_nav_route(self):
        self.__clear_kind("navroute")    

    def __clear_kind(self, kind):
        tag = "EDR-{}".format(kind)
        msg_ids = list(self.msg_ids.keys())
        for msg_id in msg_ids:
            if msg_id.startswith(tag):
                self.__clear(msg_id)
                self.msg_ids.evict(msg_id)

    def __clear_if_needed(self):
        if self.must_clear:
            self.clear()
    
    def __wrap_body(self, kind, lines):
        if not lines:
            return []
        chunked_lines = []
        rows = self.cfg[kind]["b"]["rows"]
        rows_per_line = int(max(1, rows / len(lines)))
        bonus_rows = rows % len(lines)
        for line in lines:
            max_rows = rows_per_line
            if bonus_rows:
                max_rows += 1
            wrapped_text = self.__wrap_text(kind, "b", line, max_rows)
            if bonus_rows and wrapped_text == max_rows:
               bonus_rows -= 1
            chunked_lines.append(wrapped_text)
            if len(chunked_lines) >= rows:
                break
        return chunked_lines

    def __wrap_text(self, kind, part, text, max_rows):
        EDRLOG.log(u"text: {}".format(text), "DEBUG")
        if text is None:
            return None
        width = self.cfg[kind][part]["len"]
        wrapper = textwrap.TextWrapper(width=width, subsequent_indent="  ", break_on_hyphens=False)
        return wrapper.wrap(text)[:max_rows]

    def __adjust_x(self, kind, part, text):
        conf = self.cfg[kind][part]
        x = conf["x"]
        if conf["align"] == "center":
            w = self.cfg["general"][conf["size"]]["w"]
            text_w = len(text)*w
            return max(0,int(x-text_w/2.0))
        return x

    def __msg_header(self, kind, header, timeout=None):
        conf = self.cfg[kind]["h"]
        ttl = timeout if timeout else conf["ttl"]
        text = header[:conf["len"]]
        x = self.__adjust_x(kind, "h", text)
        EDRLOG.log(u"header={}, row={}, col={}, color={}, ttl={}, size={}".format(header, conf["y"], x, conf["rgb"], ttl, conf["size"]), "DEBUG")
        self.__display(kind, text, row=conf["y"], col=x, color=conf["rgb"], ttl=ttl, size=conf["size"])

    def __msg_body(self, kind, body, timeout=None):
        conf = self.cfg[kind]["b"]
        ttl = timeout if timeout else conf["ttl"]
        x = conf["x"]
        chunked_lines = self.__wrap_body(kind, body)
        
        for chunked_line in chunked_lines:
            if chunked_line is None:
                continue
            for chunk in chunked_line:
                row_nb = self.__best_body_row(kind, chunk)
                y = conf["y"] + row_nb * self.cfg["general"][conf["size"]]["h"]
                conf["cache"].set(row_nb, chunk)
                x = self.__adjust_x(kind, "b", chunk)
                EDRLOG.log(u"line={}, rownb={}, last_row={}, row={}, col={}, color={}, ttl={}, size={}".format(chunk, row_nb, conf["last_row"], y, x, conf["rgb"], ttl, conf["size"]), "DEBUG")
                self.__display(kind, chunk, row=y, col=x, color=conf["rgb"], size=conf["size"], ttl=ttl)
                self.__bump_body_row(kind)

    def __best_body_row(self, kind, text):
        rows = range(self.cfg[kind]["b"]["rows"])
        used_rows = []
        for row_nb in rows:
            cached = self.cfg[kind]["b"]["cache"].get(row_nb)
            used_rows.append(row_nb)
            if (cached is None or cached == text):
                return row_nb
        
        remaining_rows = (set(rows) - set(used_rows))
        if len(remaining_rows):
            return remaining_rows.pop()
        else:
            self.__bump_body_row(kind)
            return self.cfg[kind]["b"]["last_row"]

    def __bump_body_row(self, kind):
        self.cfg[kind]["b"]["last_row"] += 1
        if self.cfg[kind]["b"]["last_row"] > self.cfg[kind]["b"]["rows"]:
            self.cfg[kind]["b"]["last_row"] = 0


    def __display(self, kind, text, row, col, color="#dd5500", size="large", ttl=5):
        try:
            msg_id = "EDR-{}-{}".format(kind, row)
            self._overlay.send_message(msg_id, text, color, int(col), int(row), ttl=ttl, size=size)
            self.msg_ids.set(msg_id, ttl)
        except Exception as e:
            EDRLOG.log(u"In-Game Message failed with {}.".format(e), "ERROR")
            pass

    def __shape(self, kind, panel):
        try:
            shape_id = "EDR-{}-{}-{}-{}-{}-shape".format(kind, panel["x"], panel["y"], panel["x2"], panel["y2"])
            self._overlay.send_shape(shape_id, "rect", panel["rgb"], panel["fill"], panel["x"], panel["y"], panel["x2"], panel["y2"], ttl=panel["ttl"])
            self.msg_ids.set(shape_id, panel["ttl"])
        except Exception as e:
            EDRLOG.log(u"In-Game Shape failed with {}.".format(e), "ERROR")
            pass

    def __vect(self, kind, vector):
        try:
            vect_id = "EDR-{}-{}-{}-vect".format(kind, vector["id"], hash(json.dumps(vector)))
            raw = vector
            raw["id"] = vect_id
            raw["shape"] = "vect"
            self._overlay.send_raw(raw)
            self.msg_ids.set(vect_id, vector["ttl"])
        except Exception as e:
            EDRLOG.log(u"In-Game Vect failed with {}.".format(e), "ERROR")
            pass
    
    def __clear(self, msg_id):
        try:
            self._overlay.send_message(msg_id, "", "", 0, 0, 0, 0)
            self.msg_ids.evict(msg_id)
            self.__reset_caches()
        except Exception as e:
            EDRLOG.log(u"In-Game Message failed to clear {} with {}.".format(msg_id, e), "ERROR")
            pass
    
    def __reset_caches(self):
        for kind in self.MESSAGE_KINDS:
            self.cfg[kind]["b"]["cache"].reset()
    
    def __bountycolor(self, bounty, kind):
        kind = u"{}-legal".format(kind)
        cfg = self.cfg[kind]["bounties"]
        if bounty > 0:
            try:
                order_of_magnitude = int(math.log10(max(bounty,1)/100.0))
                index = max(1, min(order_of_magnitude+1, len(cfg["fill"])-1 ))
                return cfg["fill"][index]
            except:
                return cfg["fill"][1]
        return cfg["fill"][0]

    def __cleancolor(self, clean, kind):
        kind = u"{}-legal".format(kind)
        cfg = self.cfg[kind]["clean"]
        if clean > 0:
            try:
                order_of_magnitude = int(math.log10(max(clean,1)))
                index = max(1, min(order_of_magnitude+1, len(cfg["fill"])-1 ))
                return cfg["fill"][index]
            except:
                return cfg["fill"][1]
        return cfg["fill"][0]
    
    def __wantedcolor(self, wanted, kind):
        kind = u"{}-legal".format(kind)
        cfg = self.cfg[kind]["wanted"]
        if wanted > 0:
            try:
                order_of_magnitude = int(math.log10(max(wanted,1)))
                index = max(1, min(order_of_magnitude+1, len(cfg["fill"])-1 ))
                return cfg["fill"][index]
            except:
                return cfg["fill"][1]
        return cfg["fill"][0]

    def shutdown(self):
        try:
            self._overlay.send_raw({ "command": "exit" })
        except:
            pass
        return
