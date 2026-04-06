import math
import re
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.models.edrlandables import EDRLandables
from edr.models.edentities import EDFineOrBounty
from edr.utils.edrutils import pretty_print_number
from edr.utils.edtime import EDTime

class EDRUIMining:
    def __init__(self, igm):
        self.igm = igm

    def mining_guidance(self, mining_stats):
        if not self.igm.cfg["mining"].get("enabled", None):
            return
        self.igm.clear_mining_guidance()
        if "panel" in self.igm.cfg["mining"]:
            self.igm.ui_shape("mining", self.igm.cfg["mining"]["panel"])
        if "panel" in self.igm.cfg["mining-graphs"] and self.igm.cfg["mining-graphs"].get("enabled", False):
            self.igm.ui_shape("mining-graphs", self.igm.cfg["mining-graphs"]["panel"])
        
        header = _("Mining Stats")
        details = []
        has_stuff = len(mining_stats.last["minerals_stats"]) > 0
        if has_stuff:
            detailed_stats = mining_stats.last["minerals_stats"]
            header = _("Mining Stats - MNR: {}").format(",".join(m.symbol for m in detailed_stats))
            details.append(_("MNR %: {:>6.2f}  [{}/{}; {}]").format(detailed_stats[0].last["proportion"], detailed_stats[0].symbol, mining_stats.last["materials"], mining_stats.last["raw"]))
            details.append(_("MAX %: {:>6.2f}").format(detailed_stats[0].max))
            details.append(_("AVG %: {:>6.2f}").format(detailed_stats[0].yield_average(mining_stats.prospected_nb)))
        elif mining_stats.depleted:
            details.append("")
            details.append(_(">> DEPLETED <<"))
            details.append("")
        else:
            details.append("")
            details.append(_(">> WORTHLESS <<"))
            details.append("")
        
        
        details.append(_("ITM/H: {:>6.0f} [TGT: {:.0f}]").format(mining_stats.item_per_hour(), mining_stats.max_efficiency))
        details.append(_("ITM #: {:>6}").format(mining_stats.refined_nb))
        self.igm.ui_msg_header("mining", header)
        self.igm.ui_msg_body("mining", details)

        if not self.igm.cfg["mining-graphs"].get("enabled", None):
            return
            
        self.__mining_vizualization(mining_stats)
    
    def __mining_vizualization(self, mining_stats):
        if mining_stats.last["minerals_stats"]:
            self.__mineral_stats_vizualization(mining_stats.last["minerals_stats"][0], mining_stats.prospected_nb)
        
        cfg = self.igm.cfg["mining-graphs"]
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
            max_rgb_index = len(cfg["efficiency"]["rgb"]) - 1
            if max_rgb_index >= 0:
                rgb_index = int(efficiency/mining_stats.max_efficiency * max_rgb_index)
                bar["rgb"] = cfg["efficiency"]["rgb"][min(rgb_index, max_rgb_index)]

            max_fill_index = len(cfg["efficiency"]["fill"]) - 1
            if max_fill_index >= 0:
                fill_index = int(efficiency/mining_stats.max_efficiency * max_fill_index)
                bar["fill"] = cfg["efficiency"]["fill"][min(fill_index, max_fill_index)]
            bar["ttl"] = cfg["efficiency"]["ttl"]
            self.igm.ui_shape("mining-graphs-efficiency-bar", bar)
            x = {category: x[category] + cfg[category]["w"] + cfg[category]["s"] for category in x}

    def __mineral_stats_vizualization(self, mineral_stats, prospected_nb):
        cfg = self.igm.cfg["mining-graphs"]
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
                self.igm.ui_shape("mining-graphs-yield-bar", bar)
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
        self.igm.ui_shape("mining-graphs-yield-avg-bar", bar)


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
            self.igm.ui_shape("mining-graphs-distribution-bar", bar)
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
        self.igm.ui_shape("mining-graphs-distribution-last-mark", bar)

