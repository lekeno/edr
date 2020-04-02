from __future__ import absolute_import

import os
import json

import utils2to3

class EDRLandables(object):
    MAPS = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'landable-maps.json')).read())

    @staticmethod
    def map_for(star_system, location_name, location_type):
        if not star_system or star_system.lower() not in EDRLandables.MAPS:
            star_system = "*"
        c_star_system = star_system.lower()
        c_location_name = location_name.lower()
        c_location_type = location_type.lower()

        locations = EDRLandables.MAPS.get(c_star_system, {})
        if c_location_name not in locations:
            c_location_name = "*"

        landables = locations.get(c_location_name, {})
        the_map = landables.get(c_location_type, {})
        if not the_map:
            locations = EDRLandables.MAPS.get("*", {})
            landables = locations.get("*", {})
            the_map = landables.get(c_location_type, landables.get("soon tm", {}))
        return the_map