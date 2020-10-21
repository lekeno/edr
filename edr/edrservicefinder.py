import threading
from random import shuffle
from edri18n import _
from edrlog import EDRLog

EDRLOG = EDRLog()

class EDRServiceFinder(threading.Thread):

    def __init__(self, star_system, checker, edr_systems, callback):
        self.star_system = star_system
        self.checker = checker
        self.radius = 50
        self.sc_distance = 1500
        self.trials = 0
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.callback = callback
        self.large_pad_required = True
        self.permits = []
        super(EDRServiceFinder, self).__init__()

    def with_large_pad(self, required):
        self.large_pad_required = required

    def within_radius(self, radius):
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        self.sc_distance = sc_distance

    def permits_in_possesion(self, permits):
        self.permits = permits

    def run(self):
        self.trials = 0
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.sc_distance, self.checker, results)

    def nearby(self):
        servicePrime = None
        serviceAlt = None

        candidates = {'prime': servicePrime, 'alt': serviceAlt}
        
        system = self.edr_systems.system(self.star_system)
        candidates = self.__check_system(system, candidates)
        if candidates["prime"]:
            return candidates["prime"]

        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if not systems:
            return None

        candidates = {'prime': servicePrime, 'alt': serviceAlt}
        candidates = self.__search(systems, candidates)
        if not (candidates and candidates.get('prime', None)):
            EDRLOG.log(u"Couldn't find any prime candidate so far. Trying again after a shuffle", "DEBUG")
            shuffle(systems)
            candidates = self.__search(systems, candidates)

        if not (candidates and candidates.get('prime', None) and self.edr_systems.in_colonia(self.star_system):
            EDRLOG.log(u"Couldn't find any candidate so far. Trying with key Colonia star systems", "DEBUG")
            key_colonia_star_systems = [ "Alberta", "Amatsuboshi", "Asura", "Aurora Astrum", "Benzaiten", "Centralis", "Coeus", "Colonia", "Deriso", "Desy", "Diggidiggi", "Dubbuennel", "Edge Fraternity Landing", "Einheriar", "Eol Procul Centauri", "Helgoland", "Kajuku", "Kinesi", "Kojeara", "Kopernik", "Los", "Luchtaine", "Magellan", "Mriya", "Pennsylvania", "Poe", "Randgnid", "Ratraii", "Saraswati", "Solitude", "Tir", "White Sun" ]
            for star_system in key_colonia_star_systems:
                system = self.edr_systems.system(self.star_system)
                candidates = self.__check_system(system, candidates)
                if candidates and candidates.get('prime', None):
                    break

        if candidates:
            serviceAlt = candidates.get('alt', None)
            servicePrime = candidates.get('prime', None)

        return servicePrime if servicePrime else serviceAlt

    def __check_system(self, star_system, candidates):
        if not system:
            return candidates

        possibility = self.checker.check_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
        EDRLOG.log(u"System {}: possibility {}, accessible {}".format(system['name'], possibility, accessible), "DEBUG")
        if not possibility or not accessible:
            return candidates

        if self.edr_systems.are_stations_stale(system['name']):
            self.trials += 1
        
        candidate = self.__service_in_system(system)
        if candidate:
            check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
            check_landing_pads = self.__has_large_lading_pads(candidate['type']) if self.large_pad_required else True
            ambiguous = self.checker.is_service_availability_ambiguous(candidate)
            EDRLOG.log(u"System {} is a candidate: ambiguous {}, sc_distance {}, landing_pads {}".format(system['name'], ambiguous, check_sc_distance, check_landing_pads), "DEBUG")
            if check_sc_distance and check_landing_pads and not ambiguous:
                trialed = system
                trialed['station'] = candidate
                closest = self.edr_systems.closest_destination(trialed, candidates['prime'])
                EDRLOG.log(u"Prime Trial {}, closest {}".format(system['name'], closest['name']), "DEBUG")
                candidates['prime'] = closest
            else:
                if ambiguous:
                    candidate['comment'] = _(u"[Confidence: LOW]")
                trialed = system
                trialed['station'] = candidate
                closest = self.edr_systems.closest_destination(trialed, candidates['alt'])
                EDRLOG.log(u"Trial {}, closest {}".format(system['name'], closest['name']), "DEBUG")
                candidates['alt'] = closest 


    def __search(self, systems, candidates):
        trials = 0
        if not systems:
            return None
        for system in systems:
            candidates = self.__check_system(system, candidates)                  

            if candidates['prime']:
                EDRLOG.log(u"Prime found, breaking here.", "DEBUG")
                break
                
            if self.trials > self.max_trials:
                EDRLOG.log(u"Tried too many. Aborting here.", "DEBUG")
                break

        return candidates        

    def closest_station_with_service(self, stations):
        overall = None
        with_large_landing_pads = None
        for station in stations:
            if not self.checker.check_station(station):
                continue

            (state, _) = self.edr_systems.system_state(self.star_system)
            state = state.lower() if state else state
            if state == u'lockdown':
                continue

            if overall == None:
                overall = station
            elif station['distanceToArrival'] < overall['distanceToArrival']:
                overall = station
            
            if self.__has_large_lading_pads(station['type']):
                with_large_landing_pads = station
        
        return with_large_landing_pads if self.large_pad_required and with_large_landing_pads else overall


    def __has_large_lading_pads(self, stationType):
        return stationType.lower() in ['coriolis starport', 'ocellus starport', 'orbis starport', 'planetary port', 'asteroid base', 'mega ship']

    def __service_in_system(self, system):
        if not system:
            return None
            
        if system.get('requirePermit', False) and not system['name'] in self.permits :
            return None

        all_stations = self.edr_systems.stations_in_system(system['name'])
        if not all_stations or not len(all_stations):
            return None

        return self.closest_station_with_service(all_stations)

    def close(self):
        return None
