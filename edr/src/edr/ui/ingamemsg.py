import os
import sys
import math
import json
from random import choices
from string import ascii_uppercase, digits
import re

from edr.core import igmconfig
from edr.core.edrlog import EDR_LOG # EDR_INTERNAL
import textwrap
from edr.core.edri18n import _, _c # EDR_INTERNAL
from edr.models.edrlandables import EDRLandables
from edr.models.edentities import EDFineOrBounty # EDR_INTERNAL
from edr.utils.edrutils import pretty_print_number # EDR_INTERNAL
from edr.utils.edrpath import plugin_root # EDR_INTERNAL
from edr.utils.edtime import EDTime # EDR_INTERNAL

if sys.platform == "win32":
    _overlay_dir = os.path.join(plugin_root(), 'EDMCOverlay')
    if _overlay_dir not in sys.path:
        sys.path.append(_overlay_dir)

try:
    from EDMCOverlay import edmcoverlay
except ImportError:
    try:
        from .EDMCOverlay import edmcoverlay
    except ImportError:
        EDR_LOG.error("Could not import EDMCOverlay!")
        edmcoverlay = None

from edr.utils import lrucache
from .edruidocking import EDRUIDocking
from .edruimining import EDRUIMining
from .edruibounty import EDRUIBounty
from .edruitarget import EDRUITarget
from .edruinavroute import EDRUINavRoute

class InGameMsg:   
    MESSAGE_KINDS = ["intel", "warning", "sitrep", "notice", "help", "navigation", "docking", "mining", "bounty-hunting", "target-guidance", "biology"]
    LEGAL_KINDS = ["intel", "warning"] 

    def __init__(self, standalone=False):
        self.standalone_overlay = standalone
        self.compatibility_issue = False
        if edmcoverlay:
            if (standalone):
                try:
                    self._overlay = edmcoverlay.Overlay(args=["--standalone"])
                except:
                    self._overlay = edmcoverlay.Overlay()
                    self.compatibility_issue = True
            else:
                self._overlay = edmcoverlay.Overlay()
        else:
            self._overlay = None
            self.compatibility_issue = True
        self.cfg = {}
        self.layout_type = None
        self.must_clear = False
        self.msg_ids = lrucache.LRUCache(1000, 60*15)
        self.ui_docking = EDRUIDocking(self)
        self.ui_mining = EDRUIMining(self)
        self.ui_bounty = EDRUIBounty(self)
        self.ui_target = EDRUITarget(self)
        self.ui_navroute = EDRUINavRoute(self)
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
        kind = "{}-legal".format(kind)
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
                "rotate": conf._getboolean(kind, "rotate_schematic")
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
            self.ui_shape("intel", self.cfg["intel"]["panel"])
        kind_legal = "intel-legal"
        if "panel" in self.cfg[kind_legal] and self.cfg[kind_legal].get("enabled", False):
            self.ui_shape(kind_legal, self.cfg[kind_legal]["panel"])
        self.ui_msg_header("intel", header)
        self.ui_msg_body("intel", details)
        
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
            self.ui_shape("warning", self.cfg["warning"]["panel"])
        kind_legal = "warning-legal"
        if "panel" in self.cfg[kind_legal] and self.cfg[kind_legal].get("enabled", False):
            self.ui_shape(kind_legal, self.cfg[kind_legal]["panel"])
        self.ui_msg_header("warning", header)
        self.ui_msg_body("warning", details)
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
            self.ui_shape("notice", self.cfg["notice"]["panel"])
        self.ui_msg_header("notice", header)
        self.ui_msg_body("notice", details)
    
    def help(self, header, details):
        if not self.cfg["help"].get("enabled", None):
            return
        self.__clear_if_needed()
        if "panel" in self.cfg["help"]:
            self.ui_shape("help", self.cfg["help"]["panel"])
        self.ui_msg_header("help", header)
        self.ui_msg_body("help", details)
        self.must_clear = True

    def sitrep(self, header, details):
        if not self.cfg["sitrep"].get("enabled", None):
            return
        self.__clear_if_needed()
        self.__clear_kind("sitrep")
        if "panel" in self.cfg["sitrep"]:
            self.ui_shape("sitrep", self.cfg["sitrep"]["panel"])
        self.ui_msg_header("sitrep", header)
        self.ui_msg_body("sitrep", details)

    def navigation(self, bearing, destination, distance=None, pitch=None):
        if not self.cfg["navigation"].get("enabled", None):
            return
        self.clear_navigation()
        if "panel" in self.cfg["navigation"]:
            self.ui_shape("navigation", self.cfg["navigation"]["panel"])
        header = "› {:03} ‹     ↓ {:02} ↓".format(bearing, pitch) if pitch else "> {:03} <".format(bearing)
        details = [destination.title] if destination.title else []
        if distance >= 1.0:
            details.append(_("Dis: {}km").format(int(distance)))
        else:
            details.append(_("Dis: {}m").format(int(distance*1000)))
        details.append(_("Lat: {:.4f}").format(destination.latitude))
        details.append(_("Lon: {:.4f}").format(destination.longitude))
        if destination.heading is not None:
            details.append(_("Head: > {:03} <").format(destination.heading))
        if destination.altitude:
            if destination.altitude >= 1.0:
                details.append(_("Alt: {}km").format(int(destination.altitude)))
            else:
                details.append(_("Alt: {}m").format(destination.altitude))
        self.ui_msg_header("navigation", header)
        self.ui_msg_body("navigation", details)

    def biology_guidance(self, species, ccr, value, distances_meters, bearings):
        # TODO Osseus Discus on rough, hilly areas instead. Concha Renibus will keep to rocky places, bacteria flat ground hard to find not worth much
        # TODO planets with thin water atmospheres are best; best main stars to filter for are B and A, then Neutron stars, Non-Sequence filter), F and G, in this order. In mass codes, not surprisingly this would mean D and E.
        # TODO the DSS filters only show genus, and if a planet has different species (and/or colours) of the same kind, they won't show up there separately! For example, a planet might have three species of brain trees, or bacteria, or whatever else, all under the same biological signal. See the Organics tab on the system map to see how many distinct species you can sample on a planet.
        if not self.cfg["biology"].get("enabled", None):
            return
        self.clear_biology()
        if "panel" in self.cfg["biology"]:
            self.ui_shape("biology", self.cfg["biology"]["panel"])
        header = species
        details = []
        details.append(_("Value: {} credits").format(pretty_print_number(value)))
        details.append(_("Gene diversity: +{}m").format(ccr))
        i = 1
        for distance in distances_meters:
            check = "◌" if distance < ccr else "●"
            if distance > ccr and distance >= 10000:
                details.append(_("{} Sample #{}: ≥10km  ›{:03}‹").format(check, i, bearings[i-1]))
            else:
                details.append(_("{} Sample #{}: {}m  ›{:03}‹").format(check, i, math.floor(distance), bearings[i-1]))
            i += 1
        self.ui_msg_header("biology", header)
        self.ui_msg_body("biology", details)

    def docking(self, system, station, pad, faction, description):
        return self.ui_docking.docking(system, station, pad, faction, description)
    def __landable_schematic(self, system, station, pad):
        self.ui_docking._EDRUIDocking__landable_schematic(system, station, pad)
    def __station_schematic(self, landing_pad, rotated=False):
        self.ui_docking._EDRUIDocking__station_schematic(landing_pad, rotated)
    def __legal_vizualization(self, legal, kind):
        cleans = legal["clean"]
        wanteds = legal["wanted"]
        bounties = legal["bounties"]
        cfg = self.cfg["{}-legal".format(kind)]
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
            self.ui_shape("{}-clean-bar".format(kind), bar)

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
            self.ui_shape("{}-wanted-bar".format(kind), bar)

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
            self.ui_shape("{}-bounty-bar".format(kind), bar)

            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}
            m += 1

    def mining_guidance(self, mining_stats):
        self.ui_mining.mining_guidance(mining_stats)
    def __mining_vizualization(self, mining_stats):
        self.ui_mining._EDRUIMining__mining_vizualization(mining_stats)
    def __mineral_stats_vizualization(self, mineral_stats, prospected_nb):
        self.ui_mining._EDRUIMining__mineral_stats_vizualization(mineral_stats, prospected_nb)
    def bounty_hunting_guidance(self, bounty_hunting_stats):
        self.ui_bounty.bounty_hunting_guidance(bounty_hunting_stats)
    def __bounty_hunting_vizualization(self, bounty_hunting_stats):
        self.ui_bounty._EDRUIBounty__bounty_hunting_vizualization(bounty_hunting_stats)
    def target_guidance(self, target, subsys_details=None):
        self.ui_target.target_guidance(target, subsys_details)
    def __target_guidance_vizualization(self, shield_up, shield_stats, hull_stats, subsys_stats):
        self.ui_target._EDRUITarget__target_guidance_vizualization(shield_up, shield_stats, hull_stats, subsys_stats)
    def navroute(self, route_navigator):
        self.ui_navroute.navroute(route_navigator)
    def __draw_navroute(self, route_navigator):
        self.ui_navroute._EDRUINavRoute__draw_navroute(route_navigator)
    def clear(self):
        msg_ids = list(self.msg_ids.keys())
        for msg_id in msg_ids:
            self.ui_clear(msg_id)
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
                self.ui_clear(msg_id)
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
        EDR_LOG.debug("text: {}".format(text))
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

    def ui_msg_header(self, kind, header, timeout=None):
        conf = self.cfg[kind]["h"]
        ttl = timeout if timeout else conf["ttl"]
        text = header[:conf["len"]]
        x = self.__adjust_x(kind, "h", text)
        EDR_LOG.debug("header={}, row={}, col={}, color={}, ttl={}, size={}".format(header, conf["y"], x, conf["rgb"], ttl, conf["size"]))
        self.__display(kind, text, row=conf["y"], col=x, color=conf["rgb"], ttl=ttl, size=conf["size"])

    def ui_msg_body(self, kind, body, timeout=None):
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
                EDR_LOG.debug("line={}, rownb={}, last_row={}, row={}, col={}, color={}, ttl={}, size={}".format(chunk, row_nb, conf["last_row"], y, x, conf["rgb"], ttl, conf["size"]))
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
            EDR_LOG.exception("In-Game Message failed with {}.".format(e))
            pass

    def ui_shape(self, kind, panel):
        try:
            shape_id = "EDR-{}-{}-{}-{}-{}-shape".format(kind, panel["x"], panel["y"], panel["x2"], panel["y2"])
            self._overlay.send_shape(shape_id, "rect", panel["rgb"], panel["fill"], panel["x"], panel["y"], panel["x2"], panel["y2"], ttl=panel["ttl"])
            self.msg_ids.set(shape_id, panel["ttl"])
        except Exception as e:
            EDR_LOG.exception(f"In-Game Shape failed with {e}.")
            pass

    def ui_vect(self, kind, vector):
        try:
            vect_id = "EDR-{}-{}-{}-vect".format(kind, vector["id"], hash(json.dumps(vector)))
            raw = vector
            raw["id"] = vect_id
            raw["shape"] = "vect"
            self._overlay.send_raw(raw)
            self.msg_ids.set(vect_id, vector["ttl"])
        except Exception as e:
            EDR_LOG.exception(f"In-Game Vect failed with {e}.")
            pass
    
    def ui_clear(self, msg_id):
        try:
            self._overlay.send_message(msg_id, "", "", 0, 0, 0, 0)
            self.msg_ids.evict(msg_id)
            self.__reset_caches()
        except Exception as e:
            EDR_LOG.exception(f"In-Game Message failed to clear {msg_id} with {e}.")
            pass
    
    def __reset_caches(self):
        for kind in self.MESSAGE_KINDS:
            self.cfg[kind]["b"]["cache"].reset()
    
    def __bountycolor(self, bounty, kind):
        kind = "{}-legal".format(kind)
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
        kind = "{}-legal".format(kind)
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
        kind = "{}-legal".format(kind)
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
