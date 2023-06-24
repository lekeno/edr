from __future__ import absolute_import

import os
import json
import copy

import utils2to3
from edsitu import EDPlanetaryLocation
from edrlog import EDRLog

EDRLOG = EDRLog()

class EDRBodiesOfInterest(object):
    def __init__(self, dlc=None):
        filename = "{}_boi.json".format(dlc) if dlc else "boi.json"
        self.boi = json.loads(open(utils2to3.abspathmaker(__file__, 'data', filename)).read())
        self.custom_pois = {}
        self.index_custom_pois = {}
        self.dlc = None

    def set_dlc(self, dlc):
        c_dlc = dlc.lower()
        if c_dlc == "horizons":
            self.dlc = None
        else:
            self.dlc = c_dlc
        filename = "{}_boi.json".format(self.dlc) if self.dlc else "boi.json"
        self.boi = json.loads(open(utils2to3.abspathmaker(__file__, 'data', filename)).read())

    def bodies_of_interest(self, star_system):
        if not star_system:
            return None
        c_star_system = star_system.lower()
        return list(self.boi.get(c_star_system, {}).keys())
    
    def points_of_interest(self, star_system, body_name):
        if not star_system or not body_name:
            return None
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        return self.boi.get(c_star_system, {}).get(c_body_name, None)

    def closest_point_of_interest(self, star_system, body_name, attitude, planet_radius):
        pois = self.points_of_interest(star_system, body_name)
        if not pois:
            return None
        if not planet_radius:
            return pois[0]
        closest = {"distance": None, "poi": None}
        i = 0
        for poi in pois:
            destination = EDPlanetaryLocation(poi)
            candidate = destination.distance(attitude, planet_radius)
            if closest["distance"] is None or candidate < closest["distance"]:
                closest["distance"] = candidate
                closest["poi"] = poi
                self.__set_index_custom_pois(star_system, body_name, i)
            i += 1

        poi = copy.deepcopy(closest["poi"])
        if self.dlc == "odyssey" and "odyssey" not in poi:
            poi["title"] = "{} (Horizons Lat/Lon)".format(closest["poi"]["title"])
        return poi

    def add_custom_poi(self, star_system, body_name, poi):
        if not star_system or not body_name:
            EDRLOG.log("Can't add poi: no system or no body", "WARNING")
            return False
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        
        if c_star_system not in self.custom_pois:
            self.custom_pois[c_star_system] = {}
            self.index_custom_pois[c_star_system] = {}
        
        if c_body_name not in self.custom_pois[c_star_system]:
            self.custom_pois[c_star_system][c_body_name] = []
            self.index_custom_pois[c_star_system][c_body_name] = None
        
        self.custom_pois[c_star_system][c_body_name].append({
            "title": poi["title"],
            "latitude": poi["latitude"],
            "longitude": poi["longitude"],
            "heading": poi["heading"]
        })
        return True

    def reset_custom_poi(self, star_system, body_name):
        self.index_custom_pois = {}
        if not star_system or not body_name:
            EDRLOG.log("Can't clear custom POIs, no system or no body: {}, {}".format(star_system, body_name), "WARNING")
            return None
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        if c_star_system not in self.custom_pois:
            EDRLOG.log("System has no custom POIs: {}, {}".format(c_star_system, self.custom_pois), "WARNING")
            return
        
        if c_body_name not in self.custom_pois[c_star_system]:
            EDRLOG.log("Body has no custom POIs: {}, {}".format(c_body_name, self.custom_pois), "WARNING")
            return
        
        self.custom_pois[c_star_system][c_body_name] = []

    def clear_current_custom_poi(self, star_system, body_name):
        if self.__get_index_custom_pois(star_system, body_name) is None:
            return

        if not star_system or not body_name:
            EDRLOG.log("Can't clear custom POIs, no system or no body: {}, {}".format(star_system, body_name), "WARNING")
            return None
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        if c_star_system not in self.custom_pois:
            EDRLOG.log("System has no custom POIs: {}, {}".format(c_star_system, self.custom_pois), "WARNING")
            return
        
        if c_body_name not in self.custom_pois[c_star_system]:
            EDRLOG.log("Body has no custom POIs: {}, {}".format(c_body_name, self.custom_pois), "WARNING")
            return
        
        index = self.__get_index_custom_pois(star_system, body_name)
        if index < len(self.custom_pois[c_star_system][c_body_name]):
            del self.custom_pois[c_star_system][c_body_name][index]
        self.__clear_index_custom_pois(star_system, body_name)

    def custom_points_of_interest(self, star_system, body_name):
        if not star_system or not body_name:
            EDRLOG.log("No star system or body name: {}, {}".format(star_system, body_name), "WARNING")
            return None
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        return self.custom_pois.get(c_star_system, {}).get(c_body_name, None)

    def closest_custom_point_of_interest(self, star_system, body_name, attitude, planet_radius):
        pois = self.custom_points_of_interest(star_system, body_name)
        if not pois:
            return None
        if not planet_radius:
            EDRLOG.log("No planet radius, sending back first poi", "WARNING")
            return pois[0]
        closest = {"distance": None, "poi": None}
        i = 0
        for poi in pois:
            destination = EDPlanetaryLocation(poi)
            candidate = destination.distance(attitude, planet_radius)
            if closest["distance"] is None or candidate < closest["distance"]:
                closest["distance"] = candidate
                closest["poi"] = poi
                self.__set_index_custom_pois(star_system, body_name, i)
            i += 1

        poi = copy.deepcopy(closest["poi"])
        return poi

    def next_custom_point_of_interest(self, star_system, body_name):
        if not star_system or not body_name:
            return None

        pois = self.custom_points_of_interest(star_system, body_name)
        if not pois:
            EDRLOG.log("No pois for {}, {}".format(star_system, body_name), "INFO")
            return None
        
        index = self.__forward_index_custom_pois(star_system, body_name)
        poi = copy.deepcopy(pois[index])
        return poi
    
    def previous_custom_point_of_interest(self, star_system, body_name):
        if not star_system or not body_name:
            return None
            
        pois = self.custom_points_of_interest(star_system, body_name)
        if not pois:
            EDRLOG.log("No pois for {}, {}".format(star_system, body_name), "INFO")
            return None
        
        index = self.__rewind_index_custom_pois(star_system, body_name)
        poi = copy.deepcopy(pois[index])
        return poi

    def __get_index_custom_pois(self, star_system, body_name):
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        index_system_pois = self.index_custom_pois.get(c_star_system, None)
        if index_system_pois is None:
            return None
        
        return index_system_pois.get(c_body_name, None)
        
    def __set_index_custom_pois(self, star_system, body_name, index):
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        if c_star_system not in self.index_custom_pois:
            self.index_custom_pois[c_star_system] = {}
        
        if c_body_name not in self.index_custom_pois[c_star_system]:
            self.index_custom_pois[c_star_system][c_body_name] = None
        

        self.index_custom_pois[c_star_system][c_body_name] = index

    def __clear_index_custom_pois(self, star_system, body_name):
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        if c_star_system not in self.index_custom_pois:
            self.index_custom_pois[c_star_system] = {}
        
        if c_body_name not in self.index_custom_pois[c_star_system]:
            self.index_custom_pois[c_star_system][c_body_name] = None
        
        self.index_custom_pois[c_star_system][c_body_name] = None

    def __forward_index_custom_pois(self, star_system, body_name):
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        if c_star_system not in self.index_custom_pois:
            self.index_custom_pois[c_star_system] = {}
        
        if c_body_name not in self.index_custom_pois[c_star_system]:
            self.index_custom_pois[c_star_system][c_body_name] = None
        
        if self.index_custom_pois[c_star_system][c_body_name] is None:
            self.index_custom_pois[c_star_system][c_body_name] = 0
        else:
            self.index_custom_pois[c_star_system][c_body_name] = (self.index_custom_pois[c_star_system][c_body_name] + 1) % len(self.custom_pois[c_star_system][c_body_name])
        
        return self.index_custom_pois[c_star_system][c_body_name]

    def __rewind_index_custom_pois(self, star_system, body_name):
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.simplified_body_name(star_system, body_name)
        if c_star_system not in self.index_custom_pois:
            self.index_custom_pois[c_star_system] = {}
        
        if c_body_name not in self.index_custom_pois[c_star_system]:
            self.index_custom_pois[c_star_system][c_body_name] = None
        
        if self.index_custom_pois[c_star_system][c_body_name] is None:
            self.index_custom_pois[c_star_system][c_body_name] = len(self.custom_pois[c_star_system][c_body_name]) - 1
        else:
            self.index_custom_pois[c_star_system][c_body_name] = (self.index_custom_pois[c_star_system][c_body_name] - 1) % len(self.custom_pois[c_star_system][c_body_name])

        return self.index_custom_pois[c_star_system][c_body_name]

    @staticmethod
    def simplified_body_name(star_system, body_name, empty_name_overrider=None):
        if star_system is None or body_name is None:
            return None
        if body_name.lower().startswith(star_system.lower()):
            # Example: Pleione A 1 A => a 1 a
            # Remove prefix + space
            return body_name[len(star_system)+1:].lower() or (empty_name_overrider if empty_name_overrider else body_name)
        return body_name.lower()
