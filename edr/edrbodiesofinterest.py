import os
import json

class EDRBodiesOfInterest(object):
    BOI = json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/boi.json')).read())

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
    def closest_point_of_interest(star_system, body_name, attitude):
        pois = EDRBodiesOfInterest.points_of_interest(star_system, body_name)
        poi = pois[0] # TODO find the closest one
        return poi


    @staticmethod
    def __simplified_body_name(star_system, body_name):
        if body_name.lower().startswith(star_system.lower()):
            # Example: Pleione A 1 A => a 1 a
            # Remove prefix + space
            return body_name[len(star_system)+1:].lower()
        return body_name.lower()
