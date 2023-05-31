import threading
import csv
import pickle
import requests
from urllib.parse import urlparse
import json
from os import path
from math import sqrt
import re

from edri18n import _
import utils2to3
from edtime import EDTime
from collections import deque

class BidiWaypointIterator(object):
    def __init__(self, collection):
        self.collection = collection
        self.current = collection[0]
        self.index = 0

    def __next__(self):
        if self.collection is None:
            print("no collection")
            return None
        try:
            self.index += 1
            if self.index >= len(self.collection):
                print("index over bound")
                raise StopIteration
            self.current = self.collection[self.index]
            print(self.current)
        except StopIteration:
            print("stopiteration")
            self.index = len(self.collection)
            self.current = None
        finally:
            return self.current
        
    def previous(self):
        if self.collection is None:
            return None
        try:
            self.index -= 1
            if self.index < 0:
                raise StopIteration
            self.current = self.collection[self.index]
        except StopIteration:
            self.index = -1
            self.current = None
        finally:
            return self.current
        
    def empty(self):
        if self.collection is None:
            return True
        
        if next(self):
            self.collection.previous()
            return False
        return True

    def current_wp_sysname(self):
        return self.__get_system_name(self.current)

    @staticmethod
    def __get_system_name(waypoint):
        if not waypoint:
            return
        
        if "system" in waypoint:
            return waypoint["system"]
        
        if "name" in waypoint:
            return waypoint["name"]
        
        return _("???")
    
    def includes(self, system_name):
        if not self.collection:
            return False
        
        return any([self.__get_system_name(waypoint) == system_name for waypoint in self.collection[self.index:]]) or any([self.__get_system_name(waypoint) == system_name for waypoint in self.collection[:self.index]])
    
    def get(self, system_name):
        if not self.collection or not self.system_name:
            return
        
        result = None
        for wp in self.collection:
            name = self.__get_system_name(wp)
            cname = name.lower() if name else None
            csystem_name = system_name.lower()
            if cname == csystem_name:
                result = wp
                break

        return result
        

class SpanshServer(threading.Thread):
    SPANSH_URL = "https://spansh.co.uk"
    SESSION = requests.Session()

    def __init__(self, url, callback):
        self.api_path = f"{self.SPANSH_URL}/api/results/"
        self.callback = callback
        self.url = url
        super().__init__()

    def run(self):
        result = self.__get_route()
        if self.callback:
            self.callback(result)

    @staticmethod
    def recognized_url(url):
        spansh_regexp = r"^https:\/\/(?:www\.)?spansh\.co\.uk\/(plotter|riches|ammonia|earth|exact-plotter|exobiology|fleet-carrier|tourist)\/results\/.*$"
        return bool(re.match(spansh_regexp, url))

    def __get_route(self):
        if not self.url or not self.recognized_url(self.url):
            return None
        
        parsed_url = urlparse(self.url)
        job_id, drop = path.splitext(path.basename(parsed_url.path))
        print(job_id)
        data = self.__get_job(job_id)
        if not data:
            return None
        if "plotter" in parsed_url.path:
            return SpanshPlotterJourneyJSON(data)
        elif any([x in parsed_url.path for x in ["riches", "ammnonia", "earth"]]):
            return SpanshBodiesJourneyJSON(data)
        elif "exact-plotter" in parsed_url.path:
            return SpanshExactPlotterJourneyJSON(data)
        elif "exobiology" in parsed_url.path:
            return SpanshExobiologyJourneyJSON(data)
        elif "fleet-carrier" in parsed_url.path:
            return SpanshFleetCarrierJourneyJSON(data)
        elif "tourist" in parsed_url.path:
            return SpanshTouristJourneyJSON(data)
        #elif "trade" in parsed_url.path:
        #    return SpanshTradeJourneyJSON(data)
        return None

    def __get_job(self, job_id):
        # TODO async
        url = self.api_path + job_id
        response = SpanshServer.SESSION.get(url)
        if response.status_code != 200:
            print("not 200: {}".format(response.status_code))
            return None
        
        data = json.loads(response.content)
        if not data:
            print("no data")
            return None
        print(data)
        return data.get("result", None)
    
    def close(self):
        return None

class GenericRoute(object):
    def __init__(self):
        self.journey_type = "generic"
        self.waypoints = None
        self.destination = None
        self.start = None
        self.total_jumps = None
        self.total_waypoints = None
        self.position = None
        self.distance = None

    def current(self):
        if self.waypoints:
            return self.waypoints.current
        return None
    
    def current_wp_sysname(self):
        if not self.waypoints:
            return None

        return self.waypoints.current_wp_sysname()

    def reached_wp(self):
        if self.waypoints:
            self.position = self.waypoints.current
    
    def next(self):
        if self.waypoints:
            return next(self.waypoints)
        return None
    
    def previous(self):
        if self.waypoints:
            return self.waypoints.previous()
        return None
    
    def empty(self):
        return self.waypoints is None
    
    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))
        
        if self.distance:
            details.append(_("Distance: {} LY").format(int(self.distance)))
        
        if self.total_waypoints:
            details.append(_("{} waypoints").format(self.total_waypoints))

        if self.total_jumps:
            details.append(_("{} jumps").format(self.total_jumps))

        return details
    
    def is_waypoint(self, system_name):
        if not self.waypoints:
            return False

        return self.waypoints.includes(system_name) 

    def describe_wp(self, source_coords=None):
        current_wp = self.current()
        if not current_wp:
            return None
        
        details = []
        details.append(BidiWaypointIterator.__get_system_name(current_wp))
        dest_coords = self.__get_coords(current_wp)
        if source_coords and all([coord in dest_coords for coord in ["x", "y", "z"]]) and all([coord in source_coords for coord in ["x", "y", "z"]]):
            distance = sqrt((dest_coords["x"] - source_coords["x"])**2 + (dest_coords["y"] - source_coords["y"])**2 + (dest_coords["z"] - source_coords["z"])**2)
            details = []
            details.append(_("WP#{}/{}: {} @ {} LY").format(self.waypoints.index+1, self.total_waypoints or "?", BidiWaypointIterator.__get_system_name(current_wp), int(distance)))
        return details

    def describe_wp_bodies(self):
        return None

    def noteworthy_about_body(self, star_system, body_name):
        return None
    
    def leave_body(self, star_system, body_name):
        return None
    
    @staticmethod
    def __get_coords(waypoint):
        if not waypoint:
            return
        
        if all([coord in waypoint for coord in ["x", "y", "z"]]):
            return {k: waypoint[k] for k in waypoint.keys() & {'x', 'y', 'z'}}
        
        return None

class EDRNavRoute(object):
    def __init__(self, navroute):
        self.jumps = BidiWaypointIterator(navroute.get("Route", None))
        self.total_jumps = len(navroute.get("Route", ["dummy"]))-1
        self.position = None
        if self.jumps:
            self.start = self.jumps.collection[0]
            self.destination = self.jumps.collection[-1]
            if (self.start and "StarPos" in self.start) and (self.destination and "StarPos" in self.destination):
                s_pos = self.start["StarPos"]
                e_pos = self.destination["StarPos"]
                self.distance = sqrt((s_pos[0] - e_pos[0])**2 + (s_pos[1] - e_pos[1])**2 + (s_pos[1] - e_pos[1])**2)
    
    def empty(self):
        return self.jumps is None or self.total_jumps == 0
    
    def trivial(self):
        return self.empty() or self.total_jumps < 5
    
    def next(self):
        if self.jumps:
            return next(self.jumps)
        return None
    
    def previous(self):
        if self.jumps:
            return self.jumps.previous()
        return None

    def update(self, current_system):
        if not self.jumps:
            return False
        
        if current_system == self.jumps.current_wp_sysname():
            self.position = self.jumps.current
            next_wp = next(self.jumps)
            return next_wp is not None
        return False

    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))
        if self.distance and self.total_jumps:
            details.append(_("Distance: {} LY; {} jumps").format(int(self.distance), self.total_jumps))

        return details

class SpanshPlotterJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "plotter"
        self.destination = data.get("destination_system", None)
        self.via = data.get("via", None)
        self.start = data.get("source_system", None)
        self.efficiency = data.get("efficiency", None)
        self.range = data.get("range", None)
        self.distance = data.get("distance", None)
        self.waypoints = BidiWaypointIterator(data.get("system_jumps", None))
        self.total_jumps = data.get("total_jumps", None)
        self.total_waypoints = len(self.waypoints.collection) if self.waypoints.collection else 0

    def describe(self):
        details = []
        details.append(_("From {} to {}").format(self.start, self.destination))
        if self.via:
            details.append(_("From {} to {} (via {})").format(self.start, self.destination, ", ".join(self.via)))
        details.append(_("Distance: {} LY; {} waypoints, {} jumps").format(int(self.distance), self.total_waypoints, self.total_jumps))
        details.append(_("Range: {} LY @ {}% efficiency").format(self.range, self.efficiency))
        return details

# TODO hack, should move this function out of edentities and into something more lightweight
def pretty_print_number(number):
    readable = u""
    if number is None:
        return _(u"N/A")
    if number >= 10000000000:
        # Translators: this is a short representation for a bounty >= 10 000 000 000 credits (b stands for billion)  
        readable = _(u"{} b").format(number // 1000000000)
    elif number >= 1000000000:
        # Translators: this is a short representation for a bounty >= 1 000 000 000 credits (b stands for billion)
        readable = _(u"{:.1f} b").format(number / 1000000000.0)
    elif number >= 10000000:
        # Translators: this is a short representation for a bounty >= 10 000 000 credits (m stands for million)
        readable = _(u"{} m").format(number // 1000000)
    elif number >= 1000000:
        # Translators: this is a short representation for a bounty >= 1 000 000 credits (m stands for million)
        readable = _(u"{:.1f} m").format(number / 1000000.0)
    elif number >= 10000:
        # Translators: this is a short representation for a bounty >= 10 000 credits (k stands for kilo, i.e. thousand)
        readable = _(u"{} k").format(number // 1000)
    elif number >= 1000:
        # Translators: this is a short representation for a bounty >= 1000 credits (k stands for kilo, i.e. thousand)
        readable = _(u"{:.1f} k").format(number / 1000.0)
    else:
        # Translators: this is a short representation for a bounty < 1000 credits (i.e. shows the whole bounty, unabbreviated)
        readable = _(u"{}").format(number)
    return readable

class SpanshBodiesJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "bodies"
        self.waypoints = BidiWaypointIterator(data)
        self.start = self.waypoints.collection[0]["name"] if self.waypoints.collection and "name" in self.waypoints.collection[0] else None
        self.destination = self.waypoints.collection[-1]["name"] if self.waypoints.collection and "name" in self.waypoints.collection[-1] else None
        self.total_waypoints = len(self.waypoints.collection)
        self.total_bodies = sum([len(waypoint.get("bodies", [])) for waypoint in self.waypoints.collection])
        

    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))

        if self.total_waypoints:
            if self.total_bodies:
                details.append(_("{} waypoints; {} bodies").format(self.total_waypoints, self.total_bodies))
            else:
                details.append(_("{} waypoints").format(self.total_waypoints))

        return details
    
    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        if not current_wp or not "bodies" in current_wp:
            return False
        
        activities = set()
        value = 0
        for b in current_wp["bodies"]:
            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]
            
            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]
            
            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]

        if activities:
            details.append(_("{} bodies to visit; {} for ~{} cr").format(len(current_wp["bodies"]), " + ".join(activities), pretty_print_number(value)))
        else:
            details.append(_("{} bodies to visit").format(len(current_wp["bodies"])))

        if "jumps" in current_wp and self.waypoints.index > 0:
            details.append(_("{} jump(s) from previous waypoint").format(current_wp["jumps"]))

        return details
    
    def noteworthy_about_body(self, star_system,  body_name):
        wp = self.current()
        if star_system:
            wp = self.waypoints.get(star_system)
        
        if not wp:
            return
        
        return self.__describe_wp_body(wp, body_name)
    
    def leave_body(self, star_system,  body_name):
        wp = self.current()
        if star_system:
            wp = self.waypoints.get(star_system)
        
        if not wp or not body_name:
            return
        
        return self.__mark_body_as_visited(wp, body_name)
    
    def __mark_body_as_visited(self, wp, body_name):
        if not wp or not "bodies" in wp:
            return False

        updated = False        
        for b in wp["bodies"]:
            if b.get("name", None) != body_name:
                continue

            b["visited"] = True
            updated = True
            break

        return updated
    
    def describe_wp_bodies(self):
        current_wp = self.current()
        if not current_wp or not "bodies" in current_wp:
            return
        
        details = []
        for b in current_wp["bodies"]:
            if b.get("visited", False):
                continue

            value = 0
            activities = set()         
            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]
            
            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]
            
            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]
            
            if value and b.get("name", None):
                details.append(_("{}: {} cr ({})".format(b["name"], pretty_print_number(value), " + ".join(activities))))

        return details

    def __describe_wp_body(self, wp, body_name):
        if not wp or not "bodies" in wp:
            return
        
        details = []
        value = 0
        activities = set()    
        for b in wp["bodies"]:
            if b.get("name", None) != body_name:
                continue
            
            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]
            
            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]
            
            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]

            break
            
        distance = pretty_print_number(b["distance_to_arrival"]) if "distance_to_arrival" in b else None
        oneliner = "{}: ".format(b["name"])
        if value:
            oneliner += _("{} cr ({}) ").format(pretty_print_number(value), " + ".join(activities))
        
        if distance:
            oneliner += _("@ {} LY").format(distance)
        
        details.append(oneliner)
        
        return details

class SpanshExactPlotterJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "exact-plotter"
        self.destination = data.get("destination", None)
        self.start = data.get("source", None)
        self.algorithm = data.get("algorithm", None)
        self.tank_size = data.get("tank_size", 0)
        self.use_injections = data.get("use_injections", False)
        self.use_supercharge = data.get("use_supercharge", False)
        self.base_mass = data.get("base_mass", 0)
        self.cargo = data.get("cargo", 0)
        self.fuel_multiplier = data.get("fuel_multiplier", 0)
        self.fuel_power = data.get("fuel_power", 0)
        self.internal_tank_size = data.get("internal_tank_size", 0)
        self.is_supercharged = data.get("is_supercharged", 0)
        self.max_fuel_per_jump = data.get("max_fuel_per_jump", 0)
        self.max_time = data.get("max_time", 0)
        self.optimal_mass = data.get("optimal_mass", 0)
        self.range_boost = data.get("range_boost", 0)
        self.ship_build = data.get("ship_build", 0)
        self.waypoints = BidiWaypointIterator(data.get("jumps", None))
        self.total_waypoints = len(self.waypoints.collection)
        
class SpanshExobiologyJourneyJSON(SpanshBodiesJourneyJSON):
    def __init__(self, data):
        super().__init__(data)
        self.journey_type = "exobiology"
    
    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        if "bodies" in current_wp:
            value = 0
            for b in current_wp["bodies"]:
                if b.get("landmark_value", None):
                    value += b["landmark_value"]

            if value:
                details.append(_("{} biomes to survey for ~{} cr").format(len(current_wp["bodies"]), pretty_print_number(value)))
            else:
                details.append(_("{} bodies to visit").format(len(current_wp["bodies"])))

            if "jumps" in current_wp:
                details.append(_("{} jumps from previous waypoint").format(current_wp["jumps"]))

        return details

class SpanshFleetCarrierJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "fleet-carrier"
        self.calc_starting_fuel = data.get("calculate_starting_fuel", False)
        self.capacity_used = data.get("capacity_used", 0)
        self.destinations = data.get("destinations", [])
        self.destination = self.destinations[-1] if self.destinations else None
        self.fuel_loaded = data.get("fuel_loaded", 0)
        self.refuel_destinations = data.get("refuel_destinations", [])
        self.start = data.get("source", None)
        self.tritium_stored = data.get("tritium_stored", 0)
        self.waypoints = BidiWaypointIterator(data.get("jumps", None))
        self.total_waypoints = len(self.waypoints.collection)
        self.total_tritium_necessary = sum([waypoint.get("fuel_used", 0) for waypoint in self.waypoints.collection])

    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, ", ".join(self.destinations)))
        
        if len(self.destinations) > 1:
            details.append(_("via: {}").format(self.start, ", ".join(self.destinations[:-1])))

        if self.total_waypoints:
            details.append(_("{} waypoints; {} tritium ({} restocks)").format(self.total_waypoints, self.total_tritium_necessary, len(self.refuel_destinations)))
        
        return details

    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        
        prefix = ""
        if current_wp.get("is_desired_destination", False):
            prefix = _("[Stopover]") + " "
        
        if current_wp.get("distance", None) and current_wp.get("distance_to_destination", None): 
            total_distance = current_wp["distance"] + current_wp["distance_to_destination"]
            trip_percentage = current_wp["distance"] / total_distance
            details.append(_("{}Trip: {}/{} LY ({}%)").format(prefix, current_wp["distance"], trip_percentage, trip_percentage))

        if current_wp.get("must_restock", False):
            details.append(_("Restock {} tritium").format(current_wp.get("restock_amount", 0)))

        if current_wp.get("has_icy_ring", False):
            pristine = current_wp.get("is_system_pristine", False)
            if pristine:
                details.append(_("[Pristine icy ring]"))
            else:
                details.append(_("[Icy ring]"))

        return details

class SpanshTouristJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "tourist"
        self.destinations = data.get("destination_systems", [])
        self.range = data.get("range", None)
        self.start = data.get("source_system", None)
        self.waypoints = BidiWaypointIterator(data.get("system_jumps", None))
        self.destination = self.waypoints.collection[-1].get("system", None) if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        self.total_jumps = sum([waypoint.get("jumps", 0) for waypoint in self.waypoints.collection])

    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))
        
        if len(self.destinations) > 1:
            details.append(_("via: {}").format(", ".join(self.destinations[:-1])))

        if self.total_jumps:
            details.append(_("{} waypoints; {} jumps").format(self.total_waypoints, self.total_jumps))
        
        return details

    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        
        if current_wp.get("name", "") in self.destinations:
            details.append(_("[Stopover]"))
        
        if current_wp.get("jumps", 0):
            details.append(_("{} jumps from previous waypoint").format(current_wp["jumps"]))
        if self.waypoints.index < self.total_waypoints-1:
            next_wp = self.waypoints.collection[self.waypoints.index + 1]
            if next_wp and next_wp.get("jumps", 0):
                details.append(_("{} jumps to next waypoint").format(next_wp["jumps"]))

        return details
    
class CSVJourney(GenericRoute):
    def __init__(self, csvfile):
        self.journey_type = "custom"
        try:
            csvdata = open(csvfile, newline='')
        except:
            csvdata = ""
        # TODO what happens with error cases?
        self.waypoints = BidiWaypointIterator(csv.DictReader(csvdata, delimiter=",", quotechar='"'))
        next(self.waypoints)

        self.start = self.waypoints.collection[0].get("system", None) if self.waypoints.collection else None
        self.destination = self.waypoints.collection[-1].get("system", None) if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        self.total_jumps = sum([waypoint.get("jumps", 0) for waypoint in self.waypoints.collection]) or None
    
    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))
        
        if self.total_jumps:
            details.append(_("{} waypoints; {} jumps").format(self.total_waypoints, self.total_jumps))
        else:
            details.append(_("{} waypoints").format(self.total_waypoints))
        
        return details


    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        
        if current_wp.get("jumps", 0):
            details.append(_("{} jumps from previous waypoint").format(current_wp["jumps"]))
        
        if self.waypoints.index < self.total_waypoints-1:
            next_wp = self.waypoints.collection[self.waypoints.index + 1]
            if next_wp and next_wp.get("jumps", 0):
                details.append(_("{} jumps to next waypoint").format(next_wp["jumps"]))

        return details

class EDRRouteStatistics(object):

    DEFAULT_SEC_PER_JUMP = 90

    def __init__(self, route, ship_jump_range=None):
        self.departure = route.start
        self.destination = route.destination
        self.distance = route.distance
        self.position = None
        self.coords = None
        self.total_jumps = route.total_jumps
        self.jumps_nb = 0
        self.remaining_jumps = route.total_jumps
        self.distances = deque([], 25)
        self.intervals = deque([], 25)
        now = EDTime.py_epoch_now()
        self.start = now
        self.previous_timestamp = now
        self.current = now
        self.travelled_ly = 0
        self.ship_jump_range = ship_jump_range
    
    def update(self, system, coords):
        now = EDTime.py_epoch_now()
        self.current = now
        self.jumps_nb += 1
        if self.coords:
            distance = sqrt((self.coords["x"] - coords["x"])**2 + (self.coords["y"] - coords["y"])**2 + (self.coords["z"] - coords["z"])**2)
            self.distances.append(distance)
            print(self.distances)
            self.travelled_ly += distance
        else:
            s_pos = self.departure["StarPos"]
            distance = sqrt((s_pos[0] - coords["x"])**2 + (s_pos[1] - coords["y"])**2 + (s_pos[2] - coords["z"])**2)
            self.distances.append(distance)
            print(self.distances)
            self.travelled_ly += distance
        
        self.remaining_jumps -= 1
        jump_duration = now - self.previous_timestamp
        self.intervals.append(jump_duration)
        self.previous_timestamp = now
        self.position = system
        self.coords = coords

    def elapsed_time(self):
        return EDTime.py_epoch_now() - self.start 

    def remaining_time(self):
        if self.s_jmp():
            return self.s_jmp() * self.remaining_jumps
        return None

    def remaining_ly(self):
        if self.coords and all([coord in self.coords for coord in ["x", "y", "z"]]):
            if "StarPos" in self.destination:
                d_pos = self.destination["StarPos"]
                return round(sqrt((d_pos[0] - self.coords["x"])**2 + (d_pos[1] - self.coords["y"])**2 + (d_pos[2] - self.coords["z"])**2))
            else:
                return round(sqrt((self.destination["x"] - self.coords["x"])**2 + (self.destination["y"] - self.coords["y"])**2 + (self.destination["z"] - self.coords["z"])**2))
        else:
            return round(self.distance)

    def ly_hr(self):
        jmp_range = self.ly_jmp()
        if jmp_range:
            return round(jmp_range * self.jmp_hr())
        return 0

    def jmp_hr(self):
        if self.s_jmp():
            return round(3600 / self.s_jmp())
        return 0
        
    def s_jmp(self):
        if len(self.intervals):
            total_duration = sum(self.intervals)
            return min(999, int(total_duration / len(self.intervals)))
        return self.DEFAULT_SEC_PER_JUMP

    def ly_jmp(self):
        range = self.inferred_range() or self.ship_jump_range
        if range:
            return round(range,1)
        return None
        
    def inferred_range(self):
        total_distance = sum(self.distances)
        if len(self.distances):
            return total_distance / len(self.distances)
        return None
    
    def route_range(self):
        if self.remaining_jumps:
            return self.remaining_ly() / self.remaining_jumps
        return None
    
class EDRNavigator(object):
    EDR_JOURNEY_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'journey.v1.p')

    def __init__(self):
        self.stats = None
        self.route = None
        self.journey = None
        self.position = None
        try:
            with open(self.EDR_JOURNEY_CACHE, 'rb') as handle:
                self.journey = pickle.load(handle)
        except:
            self.journey = None

    def persist(self):
        with open(self.EDR_JOURNEY_CACHE, 'wb') as handle:
            pickle.dump(self.journey, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def update(self, current_sys, coords):
        self.position = {"system": current_sys, "coords": coords}
        print(self.position)
        job1_success = self.__update_journey(current_sys)
        job2_success = self.__update_route(current_sys)
        
        if self.stats and (job1_success or job2_success):
            self.stats.update(current_sys, coords)

        return {
            "journey_updated": job1_success,
            "route_updated": job2_success
        }
        
    def __update_journey(self, current_sys):
        if self.no_journey():
            print("no journey")
            return False
        
        current_wp_sysname = self.journey.current_wp_sysname()
        if not current_wp_sysname:
            print("no current wp")
            return False
        
        # TODO what iif the player isn't at the start or following point by point...
        if current_sys == current_wp_sysname:
            print("advance")
            next_wp = self.journey.next()
            print("next wp: {}".format(next_wp))
            return next_wp is not None
        return False
    
    def __update_route(self, current_sys):
        if self.no_route():
            print("no route")
            return False
        
        return self.route.update(current_sys)
    
    def fsd_range(self, range):
        if self.stats:
           self.stats.ship_jump_range = range
    
    def set_journey(self, route):
        self.journey = route

    def set_route(self, navroute):
        self.route = EDRNavRoute(navroute)
        self.stats = EDRRouteStatistics(self.route)
        # get past the starting poinnt which should be the current system
        self.route.next()

    def clear_journey(self):
        self.journey = None

    def clear_route(self):
        self.route = None
        self.stats = None

    def no_journey(self):
        return self.journey is None or self.journey.empty()
    
    def no_route(self):
        return self.route is None or self.route.empty()

    def forward(self):
        if self.journey:
            return self.journey.next()
        return False
    
    def rewind(self):
        if self.journey:
            return self.journey.previous()
        return False

    def current(self):
        if self.journey:
            return self.journey.current()
        return False
    
    def current_wp_sysname(self):
        if self.journey:
            return self.journey.current_wp_sysname()
        return False
    
    def describe(self):
        if not self.journey:
            return None
        
        return self.journey.describe()
    
    def is_waypoint(self, system_name):
        if not self.journey:
            return None
        
        return self.journey.is_waypoint(system_name)

    def describe_wp(self, current_coords=None):
        if not self.journey:
            return None
        
        return self.journey.describe_wp(current_coords)

    def stats_summary(self):
        if not self.stats:
            return None
        
        summary = []
        remaining_time = self.stats.remaining_time()
        remaining_ly = self.stats.remaining_ly()
        remaining_jumps = self.stats.remaining_jumps

        ly_hr = self.stats.ly_hr()
        jmp_hr = self.stats.jmp_hr()
        ly_jmp = self.stats.ly_jmp()
        s_jmp = self.stats.s_jmp()

        elements = []
        if remaining_time:
            elements.append(_("Time: {}").format(EDTime.pretty_print_timespan(remaining_time)))
        
        if remaining_ly:
            elements.append(_("LY: {}").format(int(remaining_ly)))

        if remaining_jumps:
            elements.append(_("Jumps: {}").format(int(remaining_jumps)))
        
        if elements:
            summary.append("; ".join(elements))
        

        elements = []
        if ly_hr:
            elements.append(_("LY/HR: {}").format(int(ly_hr)))
        
        if jmp_hr:
            elements.append(_("JMP/HR: {}").format(int(jmp_hr)))

        if ly_jmp:
            elements.append(_("LY/JMP: {}").format(int(ly_jmp)))

        if s_jmp:
            elements.append(_("T/JMP: {}").format(EDTime.pretty_print_timespan(s_jmp)))
        
        if elements:
            summary.append("; ".join(elements))
        
        return summary
    
    def noteworthy_about_body(self, star_system, body_name):
        if self.no_route():
            return False
        
        return self.route.noteworthy_about_body(star_system, body_name)

    def leave_body(self, star_system, body_name):
        if self.no_route():
            return False
        
        return self.route.leave_body(star_system, body_name)

    def visit_bodies(self, star_system, bodies_names):
        if self.no_route():
            return False
        
        visited = False
        for body_name in bodies_names:
            visited |= self.route.leave_body(star_system, body_name)

        return visited
    
    def describe_wp_bodies(self):
        if self.no_route():
            return False
        
        return self.route.describe_wp_bodies()