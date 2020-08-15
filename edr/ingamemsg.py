# coding= utf-8
from __future__ import division
import os
import sys
import math
import json

import igmconfig
import edrlog
import textwrap
from edri18n import _, _c
import utils2to3
from edrlandables import EDRLandables

EDRLOG = edrlog.EDRLog()

_overlay_dir = utils2to3.pathmaker(__file__, u'EDMCOverlay')

if _overlay_dir not in sys.path:
    sys.path.append(_overlay_dir)

try:
    import edmcoverlay
except ImportError:
    raise Exception(str(sys.path))

import lrucache

class InGameMsg(object):   
    MESSAGE_KINDS = [ "intel", "warning", "sitrep", "notice", "help", "navigation", "docking", "mining", "bounty-hunting"]
    LEGAL_KINDS = ["intel", "warning"] 

    def __init__(self):
        self._overlay = edmcoverlay.Overlay()
        self.cfg = {}
        self.general_config()
        self.must_clear = False
        for kind in self.MESSAGE_KINDS:
            self.message_config(kind)
        for kind in self.LEGAL_KINDS:
            self.legal_config(kind)
        self.docking_config()
        self.mining_config()
        self.bounty_hunting_config()
        self.msg_ids = lrucache.LRUCache(1000, 60*15)

    def general_config(self):
        conf = igmconfig.IGMConfig()
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

    def message_config(self, kind):
        conf = igmconfig.IGMConfig() 
        self.cfg[kind] = {
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

    def legal_config(self, kind):
        conf = igmconfig.IGMConfig() 
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

    def docking_config(self):
        conf = igmconfig.IGMConfig()
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

    def mining_config(self):
        conf = igmconfig.IGMConfig()
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

    def bounty_hunting_config(self):
        conf = igmconfig.IGMConfig()
        kind = "bounty-hunting-graphs" 
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

    def intel(self, header, details, legal=None):
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
        self.__clear_if_needed()
        if "panel" in self.cfg["notice"]:
            self.__shape("notify", self.cfg["notify"]["panel"])
        self.__msg_header("notice", header)
        self.__msg_body("notice", details)
    
    def help(self, header, details):
        self.__clear_if_needed()
        if "panel" in self.cfg["help"]:
            self.__shape("help", self.cfg["help"]["panel"])
        self.__msg_header("help", header)
        self.__msg_body("help", details)
        self.must_clear = True

    def sitrep(self, header, details):
        self.__clear_if_needed()
        self.__clear_kind("sitrep")
        if "panel" in self.cfg["sitrep"]:
            self.__shape("sitrep", self.cfg["sitrep"]["panel"])
        self.__msg_header("sitrep", header)
        self.__msg_body("sitrep", details)

    def navigation(self, bearing, destination, distance=None, pitch=None):
        self.clear_navigation()
        if "panel" in self.cfg["navigation"]:
            self.__shape("navigation", self.cfg["navigation"]["panel"])
        header = u"› {:03} ‹     ↓ {:02} ↓".format(bearing, pitch) if pitch else u"> {:03} <".format(bearing)
        details = [destination.title] if destination.title else []
        if distance:
            details.append(_(u"Dis: {}km".format(int(distance))))
        details.append(_(u"Lat: {:.4f}".format(destination.latitude)))
        details.append(_(u"Lon: {:.4f}".format(destination.longitude)))
        self.__msg_header("navigation", header)
        self.__msg_body("navigation", details)

    def docking(self, system, station, pad):
        self.clear_docking()
        if not station:
            return
        if "panel" in self.cfg["docking"]:
            self.__shape("docking", self.cfg["docking"]["panel"])
        if "panel" in self.cfg["docking-station"] and self.cfg["docking-station"].get("enabled", False):
            self.__shape("docking-station", self.cfg["docking-station"]["panel"])
        economy = u"{}/{}".format(station["economy"], station["secondEconomy"]) if station["secondEconomy"] else station["economy"]
        header = u"{} ({})".format(station["name"], economy)
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
        self.clear_mining_guidance()
        if "panel" in self.cfg["mining"]:
            self.__shape("mining", self.cfg["mining"]["panel"])
        if "panel" in self.cfg["mining-graphs"] and self.cfg["mining-graphs"].get("enabled", False):
            self.__shape("mining-graphs", self.cfg["mining-graphs"]["panel"])
        
        header = _(u"Mining Stats")
        details = []
        has_stuff = mining_stats.last["proportion"] > 0
        details.append(_(u"ITM %: {:>6.2f}  [{}/{}; {}]".format(mining_stats.last["proportion"], 1 if has_stuff else 0, mining_stats.last["materials"], mining_stats.last["raw"])))
        details.append(_(u"MAX %: {:>6.2f}".format(mining_stats.max)))
        details.append(_(u"AVG %: {:>6.2f}".format(mining_stats.mineral_yield_average())))
        details.append(_(u"ITM/H: {:>6.0f} [TGT: {:.0f}]".format(mining_stats.mineral_per_hour(), mining_stats.max_efficiency)))
        details.append(_(u"ITM #: {:>6}".format(mining_stats.refined_nb)))
        self.__msg_header("mining", header)
        self.__msg_body("mining", details)

        if not self.cfg["mining-graphs"].get("enabled", None):
            return
        self.__mining_vizualization(mining_stats)
    
    def __mining_vizualization(self, mining_stats):
        cfg = self.cfg[u"mining-graphs"]
        max_yield = max(50, mining_stats.max)
        max_distribution = max(mining_stats.distribution["bins"][1:])
        max_efficiency = mining_stats.max_efficiency
        ystep = {"yield": max_yield / float(cfg["yield"]["h"]), "efficiency": max_efficiency / float(cfg["efficiency"]["h"])} 
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

        for p in mining_stats.prospectements:
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
        
        avg = mining_stats.mineral_yield_average()
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
        for c in mining_stats.distribution["bins"][1:]:
            dx = cfg["distribution"]["x"]
            dy = cfg["distribution"]["y"]
            p = c / max_distribution
            h = max(p * cfg["distribution"]["h"],1) if c else 0
            x = h
            bar["x"] = int(dx)
            bar["y"] = int(dy-y["distribution"])
            bar["x2"] = int(x)
            bar["y2"] = int(cfg["distribution"]["w"])
            index = int(i/len(mining_stats.distribution["bins"]) * (len(cfg["distribution"]["rgb"])-1.0))
            bar["rgb"] = cfg["distribution"]["rgb"][index]
            bar["fill"] = cfg["distribution"]["fill"][index]
            bar["ttl"] = cfg["distribution"]["ttl"]
            self.__shape(u"mining-graphs-distribution-bar", bar)
            i = i+1
            y = {category: y[category] + cfg[category]["w"] + cfg[category]["s"] for category in y}

        dx = cfg["distribution"]["x"]
        dy = cfg["distribution"]["y"]
        h = (mining_stats.distribution["last_index"] * (cfg["distribution"]["w"] + cfg["distribution"]["s"]))
        bar["x"] = int(dx-3)
        bar["y"] = int(dy-h)
        bar["x2"] = 1
        bar["y2"] = int(cfg["distribution"]["w"])
        index = int(mining_stats.distribution["last_index"]/len(mining_stats.distribution["bins"]) * (len(cfg["distribution"]["rgb"])-1.0))
        bar["rgb"] = cfg["distribution"]["rgb"][index]
        bar["fill"] = cfg["distribution"]["fill"][index]
        bar["ttl"] = cfg["distribution"]["ttl"]
        self.__shape(u"mining-graphs-distribution-last-mark", bar)


        x = {"efficiency": 0}
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

    def bounty_hunting_guidance(self, bounty_hunting_stats):
        self.clear_bounty_hunting_guidance()
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
        details.append(_(u"BOUNTY: {} cr".format(last_bounty.pretty_print())))
        details.append(_(u"MAX B.: {} cr".format(max_bounty.pretty_print())))
        details.append(_(u"AVG B.: {} cr".format(avg_bounty.pretty_print())))
        details.append(_(u"CR / H: {} [TGT: {}]".format(cr_h.pretty_print(), tgt.pretty_print())))
        details.append(_(u"TOTALS: {} cr [{} awards]".format(total_awarded.pretty_print(), bounty_hunting_stats.awarded_nb)))
        self.__msg_header("bounty-hunting", header)
        self.__msg_body("bounty-hunting", details)

        if not self.cfg["bounty-hunting-graphs"].get("enabled", None):
            return
        self.__bounty_hunting_vizualization(bounty_hunting_stats)
    
    def __bounty_hunting_vizualization(self, bounty_hunting_stats):
        # TODO
        return

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

    def clear_docking(self):
        self.__clear_kind("docking")
    
    def clear_mining_guidance(self):
        self.__clear_kind("mining")

    def clear_mining_guidance(self):
        self.__clear_kind("bounty-hunting")

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
        # TODO self._overlay.shutdown() or something
        return
