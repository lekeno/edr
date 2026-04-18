import math
import re
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.models.edrlandables import EDRLandables
from edr.models.edentities import EDFineOrBounty
from edr.utils.edrutils import pretty_print_number
from edr.utils.edtime import EDTime

class EDRUIBounty:
    def __init__(self, igm):
        self.igm = igm

    def bounty_hunting_guidance(self, bounty_hunting_stats):
        if not self.igm.cfg["bounty-hunting"].get("enabled", None):
            return

        self.igm.clear_bounty_hunting_guidance()
        self.igm.clear_docking()
        if "panel" in self.igm.cfg["bounty-hunting"]:
            self.igm.ui_shape("bounty-hunting", self.igm.cfg["bounty-hunting"]["panel"])
        if "panel" in self.igm.cfg["bounty-hunting-graphs"] and self.igm.cfg["bounty-hunting-graphs"].get("enabled", False):
            self.igm.ui_shape("bounty-hunting-graphs", self.igm.cfg["bounty-hunting-graphs"]["panel"])
        
        header = _("Bounty Hunting Stats")
        details = []
        last_bounty = EDFineOrBounty(bounty_hunting_stats.last["bounty"])
        max_bounty = EDFineOrBounty(bounty_hunting_stats.max)
        avg_bounty = EDFineOrBounty(bounty_hunting_stats.bounty_average())
        cr_h = EDFineOrBounty(bounty_hunting_stats.credits_per_hour())
        tgt = EDFineOrBounty(bounty_hunting_stats.max_efficiency)
        total_awarded = EDFineOrBounty(bounty_hunting_stats.sum_awarded)
        details.append(_("BOUNTY: {} cr [{}]").format(last_bounty.pretty_print(), bounty_hunting_stats.last["name"]))
        details.append(_("MAX B.: {} cr").format(max_bounty.pretty_print()))
        details.append(_("AVG B.: {} cr").format(avg_bounty.pretty_print()))
        details.append(_("CR / H: {} [TGT: {}]").format(cr_h.pretty_print(), tgt.pretty_print()))
        details.append(_("TOTALS: {} cr [{} rewards]").format(total_awarded.pretty_print(), bounty_hunting_stats.awarded_nb))
        self.igm.ui_msg_header("bounty-hunting", header)
        self.igm.ui_msg_body("bounty-hunting", details)
        
        if not self.igm.cfg["bounty-hunting-graphs"].get("enabled", None):
            return
        self.__bounty_hunting_vizualization(bounty_hunting_stats)
    
    def __bounty_hunting_vizualization(self, bounty_hunting_stats):
        cfg = self.igm.cfg["bounty-hunting-graphs"]
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
                self.igm.ui_shape("bounty-hunting-graphs-bounty-bar", bar)
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
        self.igm.ui_shape("bounty-hunting-graphs-bounty-avg-bar", bar)


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
            self.igm.ui_shape("bounty-hunting-graphs-distribution-bar", bar)
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
        self.igm.ui_shape("bounty-hunting-graphs-distribution-last-mark", bar)


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
            self.igm.ui_shape("bounty-hunting-graphs-efficiency-bar", bar)
            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}

