import os
import csv
import pickle
import requests
from urllib.parse import urlparse
import json
from os import path
from math import sqrt
import re

from edri18n import _
from edtime import EDTime
from collections import deque
from edrutils import pretty_print_number, simplified_body_name
from edrconfig import EDR_CONFIG

from edrlog import EDR_LOG


class BidiWaypointIterator(object):
    def __init__(self, collection):
        self.collection = collection
        self.current = collection[0] if collection else None
        self.index = 0

    def __next__(self):
        if self.collection is None:
            return None
        try:
            self.index += 1
            if self.index >= len(self.collection):
                raise StopIteration
            self.current = self.collection[self.index]
        except StopIteration:
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
        return self.get_system_name(self.current)

    @staticmethod
    def get_system_name(waypoint):
        if not waypoint:
            return
        
        if "StarSystem" in waypoint:
            return waypoint["StarSystem"]
        
        if "system" in waypoint:
            return waypoint["system"]
        
        if "name" in waypoint:
            return waypoint["name"]
        
        return _("???")
    
    def includes(self, system_name):
        if not self.collection:
            return False
        
        return any([self.get_system_name(waypoint) == system_name for waypoint in self.collection[self.index:]]) or any([self.get_system_name(waypoint) == system_name for waypoint in self.collection[:self.index]])
    
    def get(self, system_name):
        if not self.collection or not system_name:
            return
        
        result = None
        for wp in self.collection:
            name = self.get_system_name(wp)
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
    def get_url(source, destination, range, genre):
        genre = genre or "plotter"
        url = f"{SpanshServer.SPANSH_URL}/{genre}/results/auto?"
        if source:
            url += f"from={source.capitalize()}"
        
        if destination:
            url += f"&to={destination.capitalize()}"
        
        if range:
            url += f"&range={range}"

        return url

    @staticmethod
    def recognized_url(url):
        spansh_regexp = r"^https:\/\/(?:www\.)?spansh\.co\.uk\/(plotter|riches|ammonia|earth|exact-plotter|exobiology|fleet-carrier|tourist)\/results\/.*$"
        return bool(re.match(spansh_regexp, url))

    def __get_route(self):
        if not self.url or not self.recognized_url(self.url):
            return None
        
        parsed_url = urlparse(self.url)
        job_id, drop = path.splitext(path.basename(parsed_url.path))
        data = self.__get_job(job_id)
        if not data:
            return None
        if "plotter" in parsed_url.path:
            return SpanshPlotterJourneyJSON(data)
        elif any([x in parsed_url.path for x in ["riches", "ammonia", "earth"]]):
            return SpanshBodiesJourneyJSON(data)
        elif "exact-plotter" in parsed_url.path:
            return SpanshExactPlotterJourneyJSON(data)
        elif "exobiology" in parsed_url.path:
            return SpanshExobiologyJourneyJSON(data)
        elif "fleet-carrier" in parsed_url.path:
            # TODO fleet carrier failed
            return SpanshFleetCarrierJourneyJSON(data)
        elif "tourist" in parsed_url.path:
            return SpanshTouristJourneyJSON(data)
        #elif "trade" in parsed_url.path:
        #    return SpanshTradeJourneyJSON(data)
        return None

    def __get_job(self, job_id):
        url = self.api_path + job_id
        response = SpanshServer.SESSION.get(url)
        if response.status_code != 200:
            EDR_LOG.log("SpanshServer status not 200 OK: {}".format(response.status_code), "DEBUG")
            return None
        
        data = json.loads(response.content)
        if not data:
            EDR_LOG.log("SpanshServer returned no data", "DEBUG")
            return None
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
            wp_progress = self.waypoints.index+1 if self.waypoints else 0
            details.append(_("{}/{} waypoints").format(wp_progress, self.total_waypoints))

        if self.total_jumps and self.total_jumps != self.total_waypoints:
            # TODO progress on jumps
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
        details.append(BidiWaypointIterator.get_system_name(current_wp))
        dest_coords = self.__get_coords(current_wp)
        if source_coords and all([coord in dest_coords for coord in ["x", "y", "z"]]) and all([coord in source_coords for coord in ["x", "y", "z"]]):
            distance = sqrt((dest_coords["x"] - source_coords["x"])**2 + (dest_coords["y"] - source_coords["y"])**2 + (dest_coords["z"] - source_coords["z"])**2)
            details = []
            if distance:
                details.append(_("WP#{}/{}: {} @ {} LY").format(self.waypoints.index+1, self.total_waypoints or "?", BidiWaypointIterator.get_system_name(current_wp), int(distance)))
            else:
                details.append(_("WP#{}/{}: [here]").format(self.waypoints.index+1, self.total_waypoints or "?"))
        else:
            details.append(_("WP#{}/{}: {}").format(self.waypoints.index+1, self.total_waypoints or "?", BidiWaypointIterator.get_system_name(current_wp)))
        return details

    def describe_wp_bodies(self):
        return None
    
    def wp_bodies_to_survey(self, star_system):
        return None

    def noteworthy_about_body(self, star_system, body_name):
        return None
    
    def leave_body(self, star_system, body_name):
        return True
    
    def check_body(self, star_system, body_name):
        return True
    
    def surveyed_body(self, star_system, body_name):
        return True
    
    def mapped_body(self, star_system, body_name):
        return True

    def current_wp_surveyed(self):
        return True

    def remaining_waypoints(self):
        if not self.waypoints or not self.total_waypoints:
            return None
        
        return self.total_waypoints - self.waypoints.index+1
    
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
        self.total_waypoints = self.total_jumps
        self.position = None
        if self.jumps:
            self.start = self.jumps.collection[0] if self.jumps.collection else None
            self.destination = self.jumps.collection[-1] if self.jumps.collection else None
            if (self.start and "StarPos" in self.start) and (self.destination and "StarPos" in self.destination):
                s_pos = self.start["StarPos"]
                e_pos = self.destination["StarPos"]
                self.distance = sqrt((s_pos[0] - e_pos[0])**2 + (s_pos[1] - e_pos[1])**2 + (s_pos[1] - e_pos[1])**2)

        self.jumps_threshold_min = EDR_CONFIG.navroute_jumps_threshold_to_show()
        self.jumps_threshold_max = EDR_CONFIG.navroute_jumps_threshold_to_give_up()        
    
    def empty(self):
        return self.jumps is None or self.total_jumps == 0
    
    def trivial(self):
        return self.empty() or self.total_jumps < self.jumps_threshold_min
    
    def too_complex(self):
        return not self.empty() and self.total_jumps > self.jumps_threshold_max
    
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
    
    def remaining_waypoints(self):
        if not self.jumps or not self.total_waypoints:
            return None
        
        return self.total_waypoints - self.jumps.index+1

class SpanshPlotterJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "plotter"
        self.waypoints = BidiWaypointIterator(data.get("system_jumps", None))
        self.destination_name = data.get("destination_system", None)
        self.destination = self.waypoints.collection[-1]
        self.via = data.get("via", None)
        self.start = data.get("source_system", None)
        self.efficiency = data.get("efficiency", None)
        self.range = data.get("range", None)
        self.distance = data.get("distance", None)
        self.total_jumps = data.get("total_jumps", None)
        self.total_waypoints = len(self.waypoints.collection) if self.waypoints.collection else 0

    def describe(self):
        details = []
        details.append(_("From {} to {}").format(self.start, self.destination_name))
        if self.via:
            details.append(_("From {} to {} (via {})").format(self.start, self.destination_name, ", ".join(self.via)))
        
        wp_progress = self.waypoints.index+1 if self.waypoints else 0
        if self.total_jumps and self.total_jumps != self.total_waypoints:
            details.append(_("Distance: {} LY; {}/{} waypoints, {} jumps").format(int(self.distance), wp_progress, self.total_waypoints, self.total_jumps))
        else:
            details.append(_("Distance: {} LY; {}/{} waypoints").format(int(self.distance), wp_progress, self.total_waypoints, self.total_jumps))
        details.append(_("Range: {} LY @ {}pct efficiency").format(self.range, self.efficiency))
        return details

class SpanshBodiesJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "bodies"
        self.waypoints = BidiWaypointIterator(data)
        self.start = self.waypoints.collection[0]["name"] if self.waypoints.collection and "name" in self.waypoints.collection[0] else None
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.destination_name = self.waypoints.collection[-1]["name"] if self.waypoints.collection and "name" in self.waypoints.collection[-1] else None
        self.total_waypoints = len(self.waypoints.collection)
        # TODO total jumps by iterating on waypoints for "jumps"
        self.total_bodies = sum([len(waypoint.get("bodies", [])) for waypoint in self.waypoints.collection])
        

    def describe(self):
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))

        if self.total_waypoints:
            wp_progress = self.waypoints.index+1 if self.waypoints else 0
            # TODO also do body progress?
            if self.total_bodies:
                details.append(_("{}/{} waypoints; {} bodies").format(wp_progress, self.total_waypoints, self.total_bodies))
            else:
                details.append(_("{}/{} waypoints").format(wp_progress, self.total_waypoints))

        return details
    
    def describe_wp_baseline(self, source_coords=None):
        return super().describe_wp(source_coords)
    
    def describe_wp(self, source_coords=None):
        details = self.describe_wp_baseline(source_coords)
        current_wp = self.current()
        if not current_wp or not "bodies" in current_wp:
            return False
        
        activities = set()
        value = 0
        remaining_bodies = []
        for b in current_wp["bodies"]:
            if b.get("checked", False):
                continue

            remaining_bodies.append(b)
            
            if b.get("estimated_scan_value", None):
                activities.add(_("scan"))
                value += b["estimated_scan_value"]
            
            if b.get("estimated_mapping_value", None):
                activities.add(_("map"))
                value += b["estimated_mapping_value"]
            
            if b.get("landmark_value", None):
                activities.add(_("survey"))
                value += b["landmark_value"]

        if not remaining_bodies:
            return details

        if activities:
            if len(remaining_bodies) > 1:
                details.append(_("{} bodies to check; {} for ~{} cr").format(len(remaining_bodies), " + ".join(activities), pretty_print_number(value)))
            else:
                details.append(_("1 body to check; {} for ~{} cr").format(" + ".join(activities), pretty_print_number(value)))
        else:
            if len(remaining_bodies) > 1:
                details.append(_("{} bodies to check").format(len(current_wp["bodies"])))
            else:
                details.append(_("1 body to check").format(len(current_wp["bodies"])))
            details.append(_(u"Send '!journey bodies' to see the list of bodies to check"))

        return details
    
    def update(self, current_system):
        if not self.jumps:
            return False
        
        if current_system == self.jumps.current_wp_sysname():
            self.position = self.jumps.current
            if self.current_wp_surveyed():
                next_wp = next(self.jumps)
                return next_wp is not None
            else:
                return False
        return False
    
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
        
        return self.__mark_body_as_checked(wp, body_name)
    
    def check_body(self, star_system, body_name):
        wp = self.current()
        if star_system:
            wp = self.waypoints.get(star_system)
        
        if not wp or not body_name:
            return
        
        return self.__mark_body_as_checked(wp, star_system, body_name)

    def surveyed_body(self, star_system, body_name):
        return self.check_body(star_system, body_name)
    
    def mapped_body(self, star_system, body_name):
        return self.check_body(star_system, body_name)
    
    def __mark_body_as_checked(self, wp, star_system, body_name):
        if not wp or not "bodies" in wp:
            return False

        updated = False   
        for b in wp["bodies"]:
            full_body_name = b.get("name", "?")
            simple_body_name = simplified_body_name(star_system, full_body_name)
            if not body_name.lower() in [simple_body_name.lower(), full_body_name.lower()]:
                continue

            b["checked"] = True
            updated = True
            break

        return updated
    
    def current_wp_surveyed(self):
        wp = self.current()
        
        if not wp:
            return False
        
        surveyed = True
        for b in wp["bodies"]:
            if b.get("checked", False) == False:
                surveyed = False
                break

        return surveyed
        
    
    def describe_wp_bodies(self):
        current_wp = self.current()
        if not current_wp or not "bodies" in current_wp:
            return
        
        details = []
        for b in current_wp["bodies"]:
            if b.get("checked", False):
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
                simple_body_name = simplified_body_name(self.current_wp_sysname(), b["name"])
                details.append(_("{}: {} cr ({})").format(simple_body_name, pretty_print_number(value), " + ".join(activities)))

        return details
    
    def wp_bodies_to_survey(self, star_system):
        current_wp = self.current()
        if not current_wp or not "bodies" in current_wp:
            return None
        
        current_wp_sys_name = self.current_wp_sysname()
        if star_system and current_wp_sys_name and not (star_system.lower() == current_wp_sys_name.lower()):
            return None
        
        remaining_bodies = []
        for b in current_wp["bodies"]:
            if b.get("checked", False):
                continue

            if b.get("name", None):
                simple_body_name = simplified_body_name(self.current_wp_sysname(), b["name"])
                remaining_bodies.append(simple_body_name)

        return remaining_bodies

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
        sys_name = BidiWaypointIterator.get_system_name(wp)
        simple_body_name = simplified_body_name(sys_name, b["name"])
        oneliner = "{}: ".format(simple_body_name)
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
        self.destination_name = data.get("destination", None)
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
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        
class SpanshExobiologyJourneyJSON(SpanshBodiesJourneyJSON):
    def __init__(self, data):
        super().__init__(data)
        self.journey_type = "exobiology"
    
    def describe_wp(self, source_coords=None):
        details = super().describe_wp_baseline(source_coords)
        current_wp = self.current()
        if "bodies" in current_wp:
            body_names = []
            value = 0
            for b in current_wp["bodies"]:
                if b.get("landmark_value", False) and not b.get("checked", False):
                    value += b["landmark_value"]
                    simple_body_name = simplified_body_name(self.current_wp_sysname(), b.get("name", None))
                    if simple_body_name:
                        body_names.append(simple_body_name)

            if body_names:
                if value:
                    details.append(_("biomes to survey (~{} cr): {}").format(pretty_print_number(value), "; ".join(body_names)))
                else:
                    details.append(_("biomes to survey: {}").format(body_names))

        return details

    def mapped_body(self, star_system, body_name):
        # overriding SpanshBodiesJourneyJSON's behavior since the point is to scan some biology.
        return True

class SpanshFleetCarrierJourneyJSON(GenericRoute):
    def __init__(self, data):
        super().__init__()
        self.journey_type = "fleet-carrier"
        self.calc_starting_fuel = data.get("calculate_starting_fuel", False)
        self.capacity_used = data.get("capacity_used", 0)
        self.destinations = data.get("destinations", [])
        self.destination_name = self.destinations[-1] if self.destinations else None
        self.waypoints = BidiWaypointIterator(data.get("jumps", None))
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.fuel_loaded = data.get("fuel_loaded", 0)
        self.refuel_destinations = data.get("refuel_destinations", [])
        self.start = data.get("source", None)
        self.tritium_stored = data.get("tritium_stored", 0)
        self.total_waypoints = len(self.waypoints.collection)
        self.total_tritium_necessary = sum([waypoint.get("fuel_used", 0) for waypoint in self.waypoints.collection])

    def describe(self):
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))
        
        if len(self.destinations) > 1:
            details.append(_("via: {}").format(self.start, ", ".join(self.destinations[:-1])))

        if self.total_waypoints:
            wp_progress = self.waypoints.index+1 if self.waypoints else 0
            details.append(_("{}/{} waypoints; {} tritium ({} restocks)").format(wp_progress, self.total_waypoints, self.total_tritium_necessary, len(self.refuel_destinations)))
        
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
        self.destination_name = self.waypoints.collection[-1].get("system", None) if self.waypoints.collection else None
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        self.total_jumps = sum([waypoint.get("jumps", 0) for waypoint in self.waypoints.collection])

    def describe(self):
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))
        
        if len(self.destinations) > 1:
            details.append(_("via: {}").format(", ".join(self.destinations[:-1])))

        wp_progress = self.waypoints.index+1 if self.waypoints else 0
        if self.total_jumps and self.total_jumps != self.total_waypoints:
            details.append(_("{}/{} waypoints; {} jumps").format(wp_progress, self.total_waypoints, self.total_jumps))
        else:
            details.append(_("{}/{} waypoints").format(wp_progress, self.total_waypoints))
        
        return details

    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        
        if current_wp.get("name", "") in self.destinations:
            details.append(_("[Stopover]"))
        
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
        self.destination_name = self.waypoints.collection[-1].get("system", None) if self.waypoints.collection else None
        self.destination = self.waypoints.collection[-1] if self.waypoints.collection else None
        self.total_waypoints = len(self.waypoints.collection)
        self.total_jumps = sum([waypoint.get("jumps", 0) for waypoint in self.waypoints.collection]) or None
    
    def describe(self):
        details = []
        if self.start and self.destination_name:
            details.append(_("From {} to {}").format(self.start, self.destination_name))
        
        
        wp_progress = self.waypoints.index+1 if self.waypoints else 0
        if self.total_jumps and self.total_jumps != self.total_waypoints:
            details.append(_("{}/{} waypoints; {} jumps").format(wp_progress, self.total_waypoints, self.total_jumps))
        else:
            details.append(_("{}/{} waypoints").format(wp_progress, self.total_waypoints))
        
        return details


    def describe_wp(self, source_coords=None):
        details = super().describe_wp(source_coords)
        current_wp = self.current()
        
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
        self.remaining_waypoints = route.total_waypoints
        self.jumps_nb = 0
        self.distances = deque([], 25)
        self.intervals = deque([], 25)
        now = EDTime.py_epoch_now()
        self.start = now
        self.previous_timestamp = now
        self.current = now
        self.travelled_ly = 0
        self.ship_jump_range = ship_jump_range
    
    def meaningful(self):
        return len(self.intervals) > 0

    def update(self, system, coords, waypoints_to_go):
        now = EDTime.py_epoch_now()
        self.current = now
        self.remaining_waypoints = waypoints_to_go
        self.jumps_nb += 1
        if self.coords and coords:
            distance = sqrt((self.coords["x"] - coords["x"])**2 + (self.coords["y"] - coords["y"])**2 + (self.coords["z"] - coords["z"])**2)
            self.distances.append(distance)
            self.travelled_ly += distance
        elif "StarPos" in self.departure and coords:
            s_pos = self.departure["StarPos"]
            distance = sqrt((s_pos[0] - coords["x"])**2 + (s_pos[1] - coords["y"])**2 + (s_pos[2] - coords["z"])**2)
            self.distances.append(distance)
            self.travelled_ly += distance
            
        jump_duration = now - self.previous_timestamp
        self.intervals.append(jump_duration)
        self.previous_timestamp = now
        self.position = system
        self.coords = coords

    def elapsed_time(self):
        return EDTime.py_epoch_now() - self.start 

    def remaining_time(self, waypoints_based=False):
        if waypoints_based:
            jumps = self.remaining_waypoints
            duration = self.s_jmp()
            if duration:
                return int(jumps * duration)
            else:
                return None
        else:
            remaining_distance = self.remaining_ly()
            ly_hr_stat = self.ly_hr()
            if not remaining_distance or not ly_hr_stat:
                return None
            return int(remaining_distance / ly_hr_stat * 60 * 60)
        

    def remaining_ly(self):
        if self.coords and all([coord in self.coords for coord in ["x", "y", "z"]]):
            if "StarPos" in self.destination:
                d_pos = self.destination["StarPos"]
                return round(sqrt((d_pos[0] - self.coords["x"])**2 + (d_pos[1] - self.coords["y"])**2 + (d_pos[2] - self.coords["z"])**2))
            else:
                return round(sqrt((self.destination["x"] - self.coords["x"])**2 + (self.destination["y"] - self.coords["y"])**2 + (self.destination["z"] - self.coords["z"])**2))
        else:
            return round(self.distance) if not self.distance is None else None

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
    
    def remaining_jumps(self):
        remaining_distance = self.remaining_ly()
        ly_jmp_stat = self.ly_jmp()
        if remaining_distance is None or not ly_jmp_stat:
            return None
        
        if remaining_distance == 0:
            return 0
        
        return int(remaining_distance / ly_jmp_stat)
        
        
    def inferred_range(self):
        total_distance = sum(self.distances)
        if len(self.distances):
            return total_distance / len(self.distances)
        return None
    
class EDRNavigator(object):
    EDR_JOURNEY_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'navigator.v1.p')
    
    def __init__(self):
        self.route = None
        self.route_stats = None
        self.journey = None
        self.journey_stats = None
        self.position = None
        try:
            with open(self.EDR_JOURNEY_CACHE, 'rb') as handle:
                self.journey = pickle.load(handle)
                if self.journey:
                    self.journey_stats = EDRRouteStatistics(self.journey)
        except:
            self.journey = None

    def persist(self):
        with open(self.EDR_JOURNEY_CACHE, 'wb') as handle:
            pickle.dump(self.journey, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def update(self, current_sys, coords):
        self.position = {"system": current_sys, "coords": coords}
        journey_updated = self.__update_journey(current_sys)
        route_updated = self.__update_route(current_sys)
        
        if self.route_stats and (journey_updated or route_updated):
            self.route_stats.update(current_sys, coords, self.route.remaining_waypoints())

        if self.journey_stats and (journey_updated or route_updated):
            self.journey_stats.update(current_sys, coords, self.journey.remaining_waypoints())

        return {
            "journey_updated": journey_updated,
            "route_updated": route_updated
        }
        
    def __update_journey(self, current_sys):
        if self.no_journey():
            return False
        
        current_wp_sysname = self.journey.current_wp_sysname()
        if not current_wp_sysname:
            return False
        
        if current_sys == current_wp_sysname:
            if self.journey.current_wp_surveyed():
                next_wp = self.journey.next()
                return next_wp is not None
            else:
                return True
        return False
    
    def __update_route(self, current_sys):
        if self.no_route():
            return False
        
        return self.route.update(current_sys)
    
    def fsd_range(self, range):
        if self.route_stats:
           self.route_stats.ship_jump_range = range
    
    def set_journey(self, route):
        self.journey = route
        self.journey_stats = EDRRouteStatistics(self.journey)

    def set_route(self, navroute):
        self.route = EDRNavRoute(navroute)
        self.route_stats = EDRRouteStatistics(self.route)
        # get past the starting poinnt which should be the current system
        self.route.next()

    def clear_journey(self):
        self.journey = None

    def clear_route(self):
        self.route = None
        self.route_stats = None

    def no_journey(self):
        return self.journey is None or self.journey.empty()
    
    def no_route(self):
        return self.route is None or self.route.empty()

    def journey_next(self):
        if self.journey:
            return self.journey.next()
        return False
    
    def journey_previous(self):
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
        
        details = self.journey.describe()
        stats_summary = self.journey_stats_summary()
        if details and stats_summary:
            details.extend(stats_summary)
        return details
    
    def is_waypoint(self, system_name):
        if not self.journey:
            return None
        
        return self.journey.is_waypoint(system_name)

    def describe_wp(self, current_coords=None):
        if not self.journey:
            return None
        
        return self.journey.describe_wp(current_coords)

    def route_stats_summary(self):
        if not self.route_stats:
            return None
        
        return self.__stats_summary(self.route_stats)
    
    def journey_stats_summary(self):
        if not self.journey_stats:
            return None
        
        return self.__stats_summary(self.journey_stats)

    def __stats_summary(self, stats):
        if not stats.meaningful():
            return None
        summary = []
        remaining_time = stats.remaining_time()
        remaining_ly = stats.remaining_ly()
        remaining_jumps = stats.remaining_jumps()

        ly_hr = stats.ly_hr()
        jmp_hr = stats.jmp_hr()
        ly_jmp = stats.ly_jmp()
        s_jmp = stats.s_jmp()

        elements = []
        if remaining_time:
            elements.append(_("ETA: {}").format(EDTime.pretty_print_timespan(remaining_time)))
        
        if remaining_ly:
            elements.append(_("Distance: {}").format(int(remaining_ly)))

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
        if self.no_journey():
            return False
        
        return self.journey.noteworthy_about_body(star_system, body_name)

    def leave_body(self, star_system, body_name):
        if self.no_journey():
            return False
        
        return self.journey.leave_body(star_system, body_name)

    def check_bodies(self, star_system, bodies_names):
        if self.no_journey():
            return False
        
        checked = False
        for body_name in bodies_names:
            checked |= self.journey.check_body(star_system, body_name)

        return checked
    
    def surveyed_body(self, star_system, body_name):
        if self.no_journey():
            return False
        
        return self.journey.surveyed_body(star_system, body_name)
    
    def mapped_body(self, star_system, body_name):
        if self.no_journey():
            return False
        
        return self.journey.mapped_body(star_system, body_name)
    
    def describe_wp_bodies(self):
        if self.no_journey():
            return False
        
        return self.journey.describe_wp_bodies()
    
    def wp_bodies_to_survey(self, star_system):
        if self.no_journey():
            return None
        
        return self.journey.wp_bodies_to_survey(star_system)
