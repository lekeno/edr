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

class BidiIterator(object):
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

class SpanshServer(object):
    SPANSH_URL = "https://spansh.co.uk"
    SESSION = requests.Session()

    def __init__(self):
        self.api_path = f"{self.SPANSH_URL}/api/results/"

    def recognized_url(self, url):
        spansh_regexp = r"^https:\/\/(?:www\.)?spansh\.co\.uk\/(plotter|riches|ammonia|earth|exact-plotter|exobiology|fleet-carrier|tourist)\/results\/.*$"
        return bool(re.match(spansh_regexp, url))

    def get_route_from_url(self, url):
        if not self.recognized_url(url):
            return None
        
        print(url)
        parsed_url = urlparse(url)
        job_id, drop = path.splitext(path.basename(parsed_url.path))
        print(job_id)
        data = self.__get_job(job_id)
        if not data:
            print("no data")
            return None
        if "plotter" in parsed_url.path:
            return SpanshPlotterRouteJSON(data)
        elif any([x in parsed_url.path for x in ["riches", "ammnonia", "earth"]]):
            return SpanshBodiesRouteJSON(data)
        elif "exact-plotter" in parsed_url.path:
            return SpanshExactPlotterRouteJSON(data)
        elif "exobiology" in parsed_url.path:
            return SpanshExobiologyRouteJSON(data)
        elif "fleet-carrier" in parsed_url.path:
            return SpanshFleetCarrierRouteJSON(data)
        elif "tourist" in parsed_url.path:
            return SpanshTouristRouteJSON(data)
        #elif "trade" in parsed_url.path:
        #    return SpanshTradeRouteJSON(data)
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

class GenericRoute(object):
    def __init__(self):
        self.route_type = "generic"
        self.jumps = None
        self.destination = None
        self.start = None
        self.total_jumps = None
        self.position = None

    def current(self):
        if self.jumps:
            return self.jumps.current
        return None

    def reached_wp(self):
        if self.jumps:
            self.position = self.jumps.current
    
    def next(self):
        if self.jumps:
            return next(self.jumps)
        return None
    
    def previous(self):
        if self.jumps:
            return self.jumps.previous()
        return None
    
    def empty(self):
        return self.jumps is None
    
    def describe(self):
        details = []
        if self.start and self.destination:
            details.append(_("From {} to {}").format(self.start, self.destination))
        if self.distance and self.total_jumps:
            details.append(_("Distance: {} LY; {} jumps").format(int(self.distance), self.total_jumps))

        return details

class EDRInGameNavRoute(GenericRoute):
    def __init__(self, navroute):
        self.route_type = "in-game"
        self.jumps = BidiIterator(navroute.get("Route", None))
        self.total_jumps = len(navroute.get("Route", ["dummy"]))-1
        if self.jumps:
            self.start = self.jumps.collection[0]
            self.destination = self.jumps.collection[-1]
            if (self.start and "StarPos" in self.start) and (self.destination and "StarPos" in self.destination):
                s_pos = self.start["StarPos"]
                e_pos = self.destination["StarPos"]
                self.distance = sqrt((s_pos[0] - e_pos[0])**2 + (s_pos[1] - e_pos[1])**2 + (s_pos[1] - e_pos[1])**2)
    
    def trivial(self):
        return self.empty() or self.total_jumps < 5
    
    def next_scoopable(self):
        scoopables = [*"KGBFOAM"]
        jumps = 1
        for system in self.jumps.collection[self.jumps.index:]:
            if system.get("StarClass", "N/A") in scoopables:
                result = system
                result["jumps"] = jumps
                return result
            jumps += 1

    def previous_scoopable(self):
        scoopables = [*"KGBFOAM"]
        jumps = 1
        for system in reversed(self.jumps.collection[self.jumps.index:]):
            if system.get("StarClass", "N/A") in scoopables:
                result = system
                result["jumps"] = jumps
                return result
            jumps += 1

class SpanshPlotterRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "plotter"
        self.destination = data.get("destination_system", None)
        self.via = data.get("via", None)
        self.start = data.get("source_system", None)
        self.efficiency = data.get("efficiency", None)
        self.range = data.get("range", None)
        self.distance = data.get("distance", None)
        self.jumps = BidiIterator(data.get("system_jumps", None))
        self.total_jumps = data.get("total_jumps", None)

    def describe(self):
        details = []
        details.append(_("From {} to {}").format(self.start, self.destination))
        if self.via:
            details.append(_("From {} to {} (via {})").format(self.start, self.destination, ", ".join(self.via)))
        details.append(_("Distance: {} LY; {} jumps").format(int(self.distance), self.total_jumps))
        details.append(_("Range: {} LY @ {}% efficiency").format(self.range, self.efficiency))
        return details

    

class SpanshBodiesRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "bodies"
        self.jumps = BidiIterator(data)

class SpanshExactPlotterRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "exact-plotter"
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
        self.jumps = BidiIterator(data.get("jumps", None))
        
class SpanshExobiologyRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "exobiology"
        print(data)
        self.jumps = BidiIterator(data)

class SpanshFleetCarrierRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "fleet-carrier"
        self.calc_starting_fuel = data.get("calculate_starting_fuel", False)
        self.capacity_used = data.get("capacity_used", 0)
        self.destination = data.get("destinations", None)
        self.fuel_loaded = data.get("fuel_loaded", 0)
        self.refuel_destination = data.get("refuel_destinations", None)
        self.start = data.get("Sol", None)
        self.tritium_stored = data.get("tritium_stored", 0)
        self.jumps = BidiIterator(data.get("jumps", None))

class SpanshTouristRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "tourist"
        self.destinations = data.get("destination_systems", None)
        self.destination = self.destinations[-1] if self.destinations else None
        self.range = data.get("range", None)
        self.start = data.get("source_system", None)
        self.jumps = BidiIterator(data.get("system_jumps", None))
    
class CSVRoute(object):
    def __init__(self, csvfile):
        try:
            csvdata = open(csvfile, newline='')
        except:
            csvdata = ""
        # TODO what happens with error cases?
        self.csvreader = BidiIterator(csv.DictReader(csvdata, delimiter=",", quotechar='"'))
        next(self.csvreader)
    
    def current(self):
        return self.csvreader.current()
    
    def next(self):
        return next(self.csvreader)
    
    def previous(self):
        return self.csvreader.previous()

    def empty(self):
        return self.csvreader.empty()
    
    def describe(self):
        # TODO
        return ["CSV"]

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
        # TODO
        self.ship_jump_range = ship_jump_range
    
    def update(self, system, coords):
        # TODO missing first jump because coords are not set?
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
        print(self.intervals)
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
    
class EDRRouteNavigator(object):
    EDR_ROUTE_CACHE = utils2to3.abspathmaker(__file__, 'cache', 'route.v1.p')

    def __init__(self):
        self.stats = None
        self.ingame_route = None
        self.route = None
        self.position = None
        try:
            with open(self.EDR_ROUTE_CACHE, 'rb') as handle:
                self.route = pickle.load(handle)
        except:
            self.route = None

    def persist(self):
        with open(self.EDR_ROUTE_CACHE, 'wb') as handle:
            pickle.dump(self.route, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def update(self, current_sys, coords):
        self.position = {"system": current_sys, "coords": coords}
        job1_success = self.__update_route(current_sys)
        job2_success = self.__update_ingame_route(current_sys)
        
        if self.stats and (job1_success or job2_success):
            self.stats.update(current_sys, coords)

        return job1_success or job2_success 
        
    def __update_route(self, current_sys):
        if self.no_route():
            return False
        
        current_wp = self.route.current()
        if not current_wp:
            return False
        
        # TODO what iif the player isn't at the start or following point by point...
        if current_sys == current_wp.get("system", None):
            next_wp = self.route.next()
            return next_wp is not None
        return False
    
    def __update_ingame_route(self, current_sys):
        if self.no_ingame_route():
            print("no ingame route")
            return False
        
        current_wp = self.ingame_route.current()
        if not current_wp:
            print("no current wp")
            return False
        
        # TODO what iif the player isn't at the start or following point by point...
        print("current_sys {} == current_wp.get(StarSystem, None) {}".format(current_sys, current_wp.get("StarSystem", None)))
        if current_sys == current_wp.get("StarSystem", None):
            self.ingame_route.reached_wp()
            next_wp = self.ingame_route.next()
            return next_wp is not None
        return False
    
    def fsd_range(self, range):
        if self.stats:
           self.stats.ship_jump_range = range
    
    def set(self, route):
        self.route = route
        # TODO 2 stats obj?
        self.stats = EDRRouteStatistics(route)

    def set_ingame_route(self, navroute):
        self.ingame_route = EDRInGameNavRoute(navroute)
        self.stats = EDRRouteStatistics(self.ingame_route)
        # TODO hack to get past the starting poinnt which should be the current system
        self.ingame_route.next()

    def clear(self):
        self.route = None

    def clear_ingame_route(self):
        self.ingame_route = None

    def no_route(self):
        return self.route is None or self.route.empty()
    
    def no_ingame_route(self):
        return self.ingame_route is None or self.ingame_route.empty()

    def forward(self):
        if self.route:
            return self.route.next()
        return False
    
    def rewind(self):
        if self.route:
            return self.route.previous()
        return False

    def current(self):
        if self.route:
            return self.route.current()
        return False
    
    def describe(self):
        if not self.route:
            return None
        
        return self.route.describe()

    def stats_summary(self):
        if not self.stats:
            return None
        
        summary = []
        remaining_time = self.stats.remaining_time()
        remaining_ly = self.stats.remaining_ly()
        remaining_jumps = self.stats.remaining_jumps()

        ly_hr = self.stats.ly_hr()
        jmp_hr = self.stats.jmp_hr()
        ly_jmp = self.stats.ly_jmp()
        s_jmp = self.stats.s_jmp()

        elements = []
        if remaining_time:
            elements.append(_("Time: {}").format(EDTime.route_time(remaining_time)))
        
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