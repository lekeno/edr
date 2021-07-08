from __future__ import absolute_import

import os
import json

import utils2to3
from edsitu import EDPlanetaryLocation

class EDRBodiesOfInterest(object):
    BOI = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'boi.json')).read())

    @staticmethod
    def bodies_of_interest(star_system):
        if not star_system:
            return None
        c_star_system = star_system.lower()
        return EDRBodiesOfInterest.BOI.get(c_star_system, {}).keys()
    
    @staticmethod
    def points_of_interest(star_system, body_name):
        if not star_system or not body_name:
            return None
        c_star_system = star_system.lower()
        c_body_name = EDRBodiesOfInterest.__simplified_body_name(star_system, body_name)
        return EDRBodiesOfInterest.BOI.get(c_star_system, {}).get(c_body_name, None)

    @staticmethod
    def closest_point_of_interest(star_system, body_name, attitude, planet_radius):
        pois = EDRBodiesOfInterest.points_of_interest(star_system, body_name)
        if not pois:
            return None
        if not planet_radius:
            return pois[0]
        closest = {"distance": None, "poi": None} 
        for poi in pois:
            destination = EDPlanetaryLocation(poi)
            candidate = destination.distance(attitude, planet_radius)
            if closest["distance"] is None or candidate < closest["distance"]:
                closest["distance"] = candidate
                closest["poi"] = poi
        return closest["poi"]


    @staticmethod
    def __simplified_body_name(star_system, body_name):
        if body_name.lower().startswith(star_system.lower()):
            # Example: Pleione A 1 A => a 1 a
            # Remove prefix + space
            return body_name[len(star_system)+1:].lower()
        return body_name.lower()
