import csv
import requests
from urllib.parse import urlparse
import json
from os import path

class BidiIterator(object):
    def __init__(self, collection):
        self.collection = collection
        self.current = None
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
        
    def __previous__(self):
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

class SpanshServer(object):
    SPANSH_URL = "https://spansh.co.uk"

    def __init__(self):
        self.api_path = f"{self.SPANSH_URL}/api/results/"
        # TODO SESSIONIFY

    def get_route_from_url(self, url):
        parsed_url = urlparse(url)
        print(parsed_url.path)
        job_id, drop = path.splitext(path.basename(parsed_url.path))
        print(job_id)
        data = self.__get_job(job_id)
        if not data:
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
        url = self.api_path + job_id
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
        data = json.loads(response.content)
        if not data:
            return None
        return data.get("result", None)

class GenericRoute(object):
    def __init__(self):
        self.route_type = "generic"
        self.jumps = None

    def current(self):
        if self.jumps:
            return self.jumps.current
        return None
    
    def next(self):
        if self.jumps:
            return next(self.jumps)
        return None
    
    def previous(self):
        if self.jumps:
            return previous(self.jumps)
        return None
    

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
        self.index = 0
        self.total_jumps = data.get("total_jumps", None)

    

class SpanshBodiesRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "bodies"
        self.jumps = data
        self.index = 0

    def current(self):
        if self.jumps:
            return self.jumps[self.index]
    
    def next(self):
        if self.jumps and self.index < len(self.jumps):
            self.index += 1
            return self.jumps[self.index]

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
        self.index = 0
        
class SpanshExobiologyRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "exobiology"
        self.jumps = data
        self.index = 0


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
        self.index = 0

class SpanshTouristRouteJSON(GenericRoute):
    def __init__(self, data):
        self.route_type = "tourist"
        self.destinations = data.get("destination_systems", None)
        self.range = data.get("range", None)
        self.start = data.get("source_system", None)
        self.jumps = BidiIterator(data.get("system_jumps", None))
        self.index = 0
    
class CSVRoute(object):
    def __init__(self, csvfile):
        csvdata = open(csvfile, newline='')
        # TODO what happens with error cases?
        self.csvreader = IteratorBuf1(csv.DictReader(csvdata, delimiter=",", quotechar='"'))
        next(self.csvreader)

    def current(self):
        if self.csvreader:
            return self.csvreader.current
    
    def next(self):
        if self.csvreader:
            return next(self.csvreader)
        
    def next(self):
        if self.csvreader:
            return previous(self.csvreader)
    
class RouteNavigator(object):
    def __init__(self, csvfile, edrsystems):
        self.route = CSVRoute(csvfile)
        self.systems = edrsystems

    def next_waypoint(self, current_sysname):
        # TODO check distance, advance check distance, rewind if distance got 
        pass