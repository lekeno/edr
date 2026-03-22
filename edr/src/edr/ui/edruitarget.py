import math
import re
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.models.edrlandables import EDRLandables
from edr.models.edentities import EDFineOrBounty
from edr.utils.edrutils import pretty_print_number
from edr.utils.edtime import EDTime

class EDRUITarget:
    def __init__(self, igm):
        self.igm = igm

    def target_guidance(self, target, subsys_details=None):
        if not self.igm.cfg["target-guidance"].get("enabled", None):
            return

        self.igm.clear_target_guidance()
        if not target or not target.vehicle:
            return
        tgt_vehicle = target.targeted_vehicle or target.vehicle
        if "panel" in self.igm.cfg["target-guidance"]:
            self.igm.ui_shape("target-guidance", self.igm.cfg["target-guidance"]["panel"])
        if "panel" in self.igm.cfg["target-guidance-graphs"] and self.igm.cfg["target-guidance-graphs"].get("enabled", False):
            self.igm.ui_shape("target-guidance-graphs", self.igm.cfg["target-guidance-graphs"]["panel"])
        
        header = _("{prefix}{cmdr} ({ship})").format(prefix=_("CMDR ") if target.is_human() else "", cmdr=target.name, ship=tgt_vehicle.type)
        details = []
        
        shield_stats = tgt_vehicle.shield_health_stats()
        shield_label = "{:.4g}".format(tgt_vehicle.shield_health) if tgt_vehicle.shield_health else "-"
        delta_shield = ""
        signal = "●" if tgt_vehicle.shield_up and shield_stats.last_value() else "◌"
        trend = shield_stats.trend()
        if int(trend) > 0:
            signal = "▴" if tgt_vehicle.shield_up and shield_stats.last_value() > 0 else "▵"
            if trend < 60*60:
                delta_shield = _("[{} to 100%/UP]").format(EDTime.pretty_print_timespan(int(trend), short=True, verbose=False))
        elif int(trend) < 0:
            signal = "▾"
            if trend > -60*60:
                delta_shield = _("[{} to   0%]").format(EDTime.pretty_print_timespan(int(-trend), short=True, verbose=False))
        details.append(_("SHLD{}: {}% {}").format(signal, shield_label, delta_shield))

        hull_stats = tgt_vehicle.hull_health_stats()
        hull_label = "{:.4g}".format(tgt_vehicle.hull_health) if tgt_vehicle.hull_health else "-"
        delta_hull = ""
        signal = "●"
        trend = hull_stats.trend()
        if int(trend) > 0:
            signal = "▴"
            if trend < 60*60:
                delta_hull = _("[{} to 100%]").format(EDTime.pretty_print_timespan(int(trend), short=True, verbose=False))
        elif int(trend) < 0:
            signal = "▾"
            if trend > -60*60:
                delta_hull = _("[{} to   0%]").format(EDTime.pretty_print_timespan(int(-trend), short=True, verbose=False))
        details.append(_("HULL{}: {}% {}").format(signal, hull_label, delta_hull))

        if subsys_details:
            signal = "●"
            delta_subsys = ""
            if subsys_details["stats"].meaningful():
                trend = subsys_details["stats"].trend()
                if int(trend) > 0:
                    signal = "▴"
                    if trend < 60*60:
                        delta_subsys = _("[{} to 100%]").format(EDTime.pretty_print_timespan(int(trend), short=True, verbose=False))
                elif int(trend) < 0:
                    signal = "▾"
                    if trend > -60*60:
                        delta_subsys = _("[{} to   0%]").format(EDTime.pretty_print_timespan(int(-trend), short=True, verbose=False))
            details.append(_("{subsys}{signal}: {hp:.4g}% {delta}").format(subsys=subsys_details["shortname"], signal=signal, hp=subsys_details["stats"].last_value(), delta=delta_subsys))
        self.igm.ui_msg_header("target-guidance", header)
        self.igm.ui_msg_body("target-guidance", details)

        if not self.igm.cfg["target-guidance-graphs"].get("enabled", None):
            return
        subsys_stats = subsys_details["stats"] if subsys_details else None
        self.__target_guidance_vizualization(tgt_vehicle.shield_up, shield_stats, hull_stats, subsys_stats)
    
    def __target_guidance_vizualization(self, shield_up, shield_stats, hull_stats, subsys_stats):
        shield_history = shield_stats.history
        hull_history = hull_stats.history
        subsys_history = subsys_stats.history if subsys_stats else None
        if len(shield_history) == 0 or len(hull_history) == 0:
            return

        cfg = self.igm.cfg["target-guidance-graphs"]
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
        EDR_LOG.debug("shield {}".format(shield_history))
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
            "id": "shield-sparkline",
            "color": cfg["shield"]["rgb"][1] if shield_down else cfg["shield"]["rgb"][0],
            "ttl": cfg["shield"]["ttl"],
            "vector": scaled
        }
        self.igm.ui_vect("target-guidance", vect)

        x = 1.0 - shield_stats.trend_span_ms / xspan
        vect = {
            "id": "shield-trend-span",
            "color": cfg["shield"]["rgb"][2],
            "ttl": cfg["shield"]["ttl"],
            "vector": [{"x":int(cx+x*w), "y":int(cy-.5*h-1)}, {"x":int(cx+x*w), "y":int(cy-.5*h+1)}]
        }
        self.igm.ui_vect("target-guidance", vect)
            

        x = cfg["hull"]["x"]
        y = cfg["hull"]["y"]
        w = cfg["hull"]["w"]
        h = cfg["hull"]["h"]
        cx = x
        cy = y+h
        scaled = []
        EDR_LOG.debug("hull {}".format(hull_history))
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
            "id": "hull-sparkline",
            "color": cfg["hull"]["rgb"][0],
            "ttl": cfg["hull"]["ttl"],
            "vector": scaled
        }
        self.igm.ui_vect("target-guidance", vect)
        
        x = 1.0 - hull_stats.trend_span_ms / xspan
        vect = {
            "id": "hull-trend-span",
            "color": cfg["hull"]["rgb"][1],
            "ttl": cfg["hull"]["ttl"],
            "vector": [{"x":int(cx+x*w), "y":int(cy-.5*h-1)}, {"x":int(cx+x*w), "y":int(cy-.5*h+1)}]
        }
        self.igm.ui_vect("target-guidance", vect)

        if not subsys_history or len(subsys_history) == 0:
            return
        x = cfg["subsys"]["x"]
        y = cfg["subsys"]["y"]
        w = cfg["subsys"]["w"]
        h = cfg["subsys"]["h"]
        cx = x
        cy = y+h
        scaled = []
        EDR_LOG.debug("subsys {}".format(subsys_history))
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
            "id": "subsys-sparkline",
            "color": cfg["subsys"]["rgb"][0],
            "ttl": cfg["subsys"]["ttl"],
            "vector": scaled
        }
        self.igm.ui_vect("target-guidance", vect)

        x = 1.0 - subsys_stats.trend_span_ms / xspan
        vect = {
            "id": "subsys-trend-span",
            "color": cfg["subsys"]["rgb"][1],
            "ttl": cfg["subsys"]["ttl"],
            "vector": [{"x":int(cx+x*w), "y":int(cy-.5*h-1)}, {"x":int(cx+x*w), "y":int(cy-.5*h+1)}]
        }
        self.igm.ui_vect("target-guidance", vect)

