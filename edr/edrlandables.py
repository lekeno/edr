
import os
import json


class EDRLandables:
    """
    Provides mapping information for landable bodies in systems.
    """
    
    _MAPS = None

    @classmethod
    def load_maps(cls):
        """
        Lazily load the landable-maps.json file.
        """
        if cls._MAPS is None:
            try:
                filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'landable-maps.json')
                with open(filename, 'r') as handle:
                    cls._MAPS = json.load(handle)
            except Exception:
                # If loading fails (e.g. file missing during test), initialize as empty dict to prevent crash
                cls._MAPS = {}
        return cls._MAPS

    @staticmethod
    def map_for(star_system, location_name, location_type):
        """
        Get the landable map for a specific location.

        :param star_system: The star system name.
        :param location_name: The name of the body/station.
        :param location_type: The type of the location (e.g. planet, station).
        :return: A dictionary representing the map, or empty if not found.
        """
        maps = EDRLandables.load_maps()
        
        if not star_system or star_system.lower() not in maps:
            star_system = "*"
        c_star_system = star_system.lower()
        c_location_name = location_name.lower()
        c_location_type = location_type.lower()

        locations = maps.get(c_star_system, {})
        if c_location_name not in locations:
            c_location_name = "*"

        landables = locations.get(c_location_name, {})
        the_map = landables.get(c_location_type, {})
        if not the_map:
            locations = maps.get("*", {})
            landables = locations.get("*", {})
            the_map = landables.get(c_location_type, landables.get("soon tm", {}))
        return the_map