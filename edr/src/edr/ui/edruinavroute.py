import math
import re
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.models.edrlandables import EDRLandables
from edr.models.edentities import EDFineOrBounty
from edr.utils.edrutils import pretty_print_number
from edr.utils.edtime import EDTime

class EDRUINavRoute:
    def __init__(self, igm):
        self.igm = igm

    def navroute(self, route_navigator):
        if not self.igm.cfg["navroute"].get("enabled", None):
            return
        
        self.igm.clear_nav_route()
        
        navroute = route_navigator.route
        if not navroute or navroute.empty() or navroute.trivial() or navroute.too_complex():
            return
        
        self.__draw_navroute(route_navigator)

            
    def __draw_navroute(self, route_navigator):
        navroute = route_navigator.route
        stats = route_navigator.route_stats
        
        cfg = self.igm.cfg["navroute"]
        if "panel" in cfg:
            self.igm.ui_shape("navroute", cfg["panel"])
            
        x = cfg["schema"]["x"]
        y = cfg["schema"]["y"]
        w = cfg["schema"]["w"]
        h = cfg["schema"]["h"]
        star_classes = "o,b,a,f,g,k,m,ms,c*,d*,h*,n,l,aebe,t,tts,s,w*,x,y,rogueplanet,nebula,stellarremnantnebula,*".split(",")
        default_rgbs = "D8793E,00B3F7,00B3F7,2423E9,2F2DE3,4C37D2,5C5C93,908E46,CC432A,E9332A,CC0000,55552B,616CE2,808080,3FEFFF,FF2600,F56A79,4A0000,4A0000,3B3B3B,6E6E89,FF00DC,B16C00,FF00DC,FF00DC,4CFF00,FF00CC".split(",")
        rgbs = cfg["schema"]["rgb"]
        if not rgbs or len(rgbs) < len(star_classes)+3:
            EDR_LOG.debug("Draw nav route: reverting to default rgbs (length mismatch)")
            rgbs = default_rgbs
        route_rgb = rgbs[0]
        travelled_rgb = rgbs[1]
        current_rgb = rgbs[2]
        star_rgbs = rgbs[3:]
        
        default_star_markers = "circle,circle,circle,circle,circle,circle,circle,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross,cross".split(",")
        star_markers = cfg["schema"]["marker"]
        if not star_markers or len(star_markers) < len(star_classes):
            EDR_LOG.debug("Draw nav route: reverting to default markers (length mismatch)")
            star_markers = default_star_markers

        default_suffix = ",,,,,,,,, dwarf, blackhole, neutron,,,,,,, exotic,, rogue, nebula, sr nebula, ???".split(",")
        star_suffix = cfg["schema"]["suffix"]
        if not star_suffix or len(star_suffix) < len(star_classes):
            EDR_LOG.debug("Draw nav route: reverting to default suffix (length mismatch)")
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
                EDR_LOG.debug("skipping: {} steps: {} vs {}".format(stop.get("StarSystem", None), steps, inc_steps))
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
            self.igm.ui_vect("navroute-map-travelled", vects["travelled"])
        
        if vects["remaining"]["vector"]:
            self.igm.ui_vect("navroute-map-remaining", vects["remaining"])

