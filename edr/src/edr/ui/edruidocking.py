import math
import re
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.models.edrlandables import EDRLandables
from edr.models.edentities import EDFineOrBounty
from edr.utils.edrutils import pretty_print_number
from edr.utils.edtime import EDTime

class EDRUIDocking:
    def __init__(self, igm):
        self.igm = igm

    def docking(self, system, station, pad, faction, description):
        if not self.igm.cfg["docking"].get("enabled", None):
            return

        self.igm.clear_docking()
        if not station:
            return
        if "panel" in self.igm.cfg["docking"]:
            self.igm.ui_shape("docking", self.igm.cfg["docking"]["panel"])
        if "panel" in self.igm.cfg["docking-station"] and self.igm.cfg["docking-station"].get("enabled", False):
            self.igm.ui_shape("docking-station", self.igm.cfg["docking-station"]["panel"])
        
        economy = "{}/{}".format(station["economy"], station["secondEconomy"]) if station["secondEconomy"] else station["economy"]
        station_type = (station.get("type","N/A") or "N/A").lower()

        header = "{} ({})".format(station["name"], economy)
        self.igm.ui_msg_header("docking", header)
        self.igm.ui_msg_body("docking", description)

        if not self.igm.cfg["docking-station"]["enabled"]:
            return {"header": header, "body": description}
        
        # TODO "StationType":"Dodec", "LandingPads":{ "Small":6, "Medium":9, "Large":5 }
        if station_type in ["asteroid base", 'bernal starport', "coriolis starport", "ocellus starport", "orbis starport", "bernal", "bernal statioport"]:
            self.__station_schematic(pad, self.igm.cfg["docking-station"]["schema"]["rotate"])
        else:
            self.__landable_schematic(system, station, pad)
        return {"header": header, "body": description}

    def __landable_schematic(self, system, station, pad):
        station_type = (station.get("type","N/A") or "N/A").lower()
        station_name = (station.get("name","N/A") or "N/A").lower()
        map_data = EDRLandables.map_for(system, station_name, station_type)
        if not map_data:
            return
        
        suffix = ""
        if station_type == "squadron carrier":
            # Squadron carriers have twice the number of landing pads,
            # split in two groups with a corrected fleet carrier mapping
            # (pads 13,14,15,16 have a more natural order)
            suffix = "_L" if pad > 16 else "_R"
            pad = pad % 16

        cfg = self.igm.cfg["docking-station"]
        x = cfg["schema"]["x"]
        y = cfg["schema"]["y"]
        w = cfg["schema"]["w"]
        h = cfg["schema"]["h"]
        hw = w/2.0
        hh = h/2.0
        cx = int(round(x + hw))
        cy = int(round(y + hh))
        the_pad = str(pad)
        
        contour = map_data.get(f"contour{suffix}", {})
        for element in contour:
            points = contour[element]["points"]
            scaled = [{"x":int(cx+(coords["x"]*hw)), "y":int(cy-(coords["y"]*hh))} for coords in points]
            vect = {
                "id": "landable-{}".format(element),
                "color": contour[element]["active"] if element == the_pad else contour[element]["color"],
                "ttl": cfg["schema"]["ttl"],
                "vector": scaled
            }
            self.igm.ui_vect("docking", vect)
        
        pads_guidance = map_data.get("pads-guidance", {})
        if the_pad in pads_guidance:
            guidance = pads_guidance.get(the_pad, {})
            points = guidance["points"]
            scaled = [{"x":int(cx+(coords["x"]*hw)), "y":int(cy-(coords["y"]*hh))} for coords in points]
            vect = {
                "id": "guidance-{}".format(pad),
                "color": guidance["color"],
                "ttl": cfg["schema"]["ttl"],
                "vector": scaled
            }
            self.igm.ui_vect("docking", vect)
    
    def __station_schematic(self, landing_pad, rotated=False):
        cfg = self.igm.cfg["docking-station"]
        x = cfg["schema"]["x"]
        y = cfg["schema"]["y"]
        w = cfg["schema"]["w"]
        h = cfg["schema"]["h"]

        cx = int(round(x + w/2.0))
        cy = int(round(y + h/2.0))
        
        red_light_x = x
        green_light_x = x+w-(0.03125 * w)
        if rotated:
            red_light_x, green_light_x = green_light_x, red_light_x

        red_light = {
            "x": int(red_light_x),
            "y": int(cy - (0.12962962962962962962962962962963 * h)),
            "x2": max(1, int(0.03125 * w)),
            "y2": max(1,int(2.0*0.12962962962962962962962962962963 * h)),
            "rgb": cfg["schema"]["rgb"][0],
            "fill": cfg["schema"]["fill"][0],
            "ttl": cfg["schema"]["ttl"],
        }
        self.igm.ui_shape("docking", red_light)

        green_light = {
            "x": int(green_light_x),
            "y": int(cy - (0.12962962962962962962962962962963 * h)),
            "x2": max(1,int(0.03125 * w)),
            "y2": max(1, int(2.0*0.12962962962962962962962962962963 * h)),
            "rgb": cfg["schema"]["rgb"][1],
            "fill": cfg["schema"]["fill"][1],
            "ttl": cfg["schema"]["ttl"],
        }
        self.igm.ui_shape("docking", green_light)

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

        if rotated:
            dodecagon.reverse()

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
                "id": "station-wireframe-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.igm.ui_vect("docking", wireframe)
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
                "id": "station-wireframe-1-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.igm.ui_vect("docking", wireframe)
            
            points = []
            for (dx, dy) in dodecagon[4:8]:
                x = int(round(cx + dx*rx))
                y = int(round(cy + dy*ry))
                points.append({"x": x, "y": y})
            wireframe = {
                "id": "station-wireframe-2-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.igm.ui_vect("docking", wireframe)

            points = []
            for (dx, dy) in dodecagon[8:12]:
                x = int(round(cx + dx*rx))
                y = int(round(cy + dy*ry))
                points.append({"x": x, "y": y})
            wireframe = {
                "id": "station-wireframe-3-{}".format(s),
                "color": cfg["schema"]["rgb"][2+i],
                "ttl": cfg["schema"]["ttl"],
                "vector": points
            }
            self.igm.ui_vect("docking", wireframe)
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
            "id": "station-wireframe-1-{}".format(s),
            "color": cfg["schema"]["rgb"][3],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.igm.ui_vect("docking", wireframe)
        
        points = []
        for (dx, dy) in dodecagon[6:8]:
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
        wireframe = {
            "id": "station-wireframe-2-{}".format(s),
            "color": cfg["schema"]["rgb"][3],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.igm.ui_vect("docking", wireframe)

        points = []
        for (dx, dy) in dodecagon[10:12]:
            x = int(round(cx + dx*rx))
            y = int(round(cy + dy*ry))
            points.append({"x": x, "y": y})
        wireframe = {
            "id": "station-wireframe-3-{}".format(s),
            "color": cfg["schema"]["rgb"][3],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.igm.ui_vect("docking", wireframe)
        
        for o,i in zip(radials["outer"], radials["inner"]):
            wireframe = {
                "id": "station-radial-{}-{}-{}-{}".format(o["x"], o["y"], i["x"], i["y"]),
                "color": cfg["schema"]["rgb"][5],
                "ttl": cfg["schema"]["ttl"],
                "vector": [o,i]
            }
            self.igm.ui_vect("docking", wireframe)
        
        pad_lut = {
            35: [0,1,0,1,1], 38: [0,1,4,5,1], 37: [0,1,2,4,1], 36: [0,1,1,2,0],
            31: [1,2,0,1,0], 34: [1,2,4,5,0], 33: [1,2,2,4,1], 32: [1,2,1,2,2],
            26: [2,3,0,1,1], 30: [2,3,4,5,1], 29: [2,3,3,4,0], 28: [2,3,2,3,0], 27: [2,3,1,2,0],
            24: [3,4,0,2,2], 25: [3,4,2,5,2],
            20: [4,5,0,1,1], 23: [4,5,4,5,1], 22: [4,5,2,4,1], 21: [4,5,1,2,0],
            16: [5,6,0,1,0], 19: [5,6,4,5,0], 18: [5,6,2,4,1], 17: [5,6,1,2,2],
            11: [6,7,0,1,1], 15: [6,7,4,5,1], 14: [6,7,3,4,0], 13: [6,7,2,3,0], 12: [6,7,1,2,0],
            9: [7,8,0,2,2], 10: [7,8,2,5,2],
            5: [8,9,0,1,1], 8: [8,9,4,5,1], 7: [8,9,2,4,1], 6: [8,9,1,2,0],
            1: [9,10,0,1,0], 4: [9,10,4,5,0], 3: [9,10,2,4,1], 2: [9,10,1,2,2],
            41: [10,11,0,1,1], 45: [10,11,4,5,1], 44: [10,11,3,4,0], 43: [10,11,2,3,0], 42: [10,11,1,2,0],
            39: [11,12,0,2,2], 40: [11,12,2,5,2],
        } if rotated else {
            35: [0,1,0,1,1], 36: [0,1,1,2,0], 37: [0,1,2,4,1], 38: [0,1,4,5,1],
            31: [1,2,0,1,0], 32: [1,2,1,2,2], 33: [1,2,2,4,1], 34: [1,2,4,5,0],
            26: [2,3,0,1,1], 27: [2,3,1,2,0], 28: [2,3,2,3,0], 29: [2,3,3,4,0], 30: [2,3,4,5,1],
            24: [3,4,0,2,2], 25: [3,4,2,5,2],
            20: [4,5,0,1,1], 21: [4,5,1,2,0], 22: [4,5,2,4,1], 23: [4,5,4,5,1],
            16: [5,6,0,1,0], 17: [5,6,1,2,2], 18: [5,6,2,4,1], 19: [5,6,4,5,0],
            11: [6,7,0,1,1], 12: [6,7,1,2,0], 13: [6,7,2,3,0], 14: [6,7,3,4,0], 15: [6,7,4,5,1],
            9: [7,8,0,2,2], 10: [7,8,2,5,2],
            5: [8,9,0,1,1], 6: [8,9,1,2,0], 7: [8,9,2,4,1], 8: [8,9,4,5,1],
            1: [9,10,0,1,0], 2: [9,10,1,2,2], 3: [9,10,2,4,1], 4: [9,10,4,5,0],
            41: [10,11,0,1,1], 42: [10,11,1,2,0], 43: [10,11,2,3,0], 44: [10,11,3,4,0], 45: [10,11,4,5,1],
            39: [11,12,0,2,2], 40: [11,12,2,5,2],
        }

        pad_loc = pad_lut[landing_pad] if landing_pad in pad_lut else None
        if pad_loc is None:
            return

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
            "id": "station-pad-{}".format(landing_pad),
            "color": cfg["schema"]["rgb"][6+pad_loc[4]],
            "ttl": cfg["schema"]["ttl"],
            "vector": points
        }
        self.igm.ui_vect("docking", pad_highlight)


