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
        self.medium_pad_required = True
        self.permits = []
        self.shuffle_systems = False
        self.shuffle_stations = False
        self.exclude_center = False
        self.checked_systems = []
        super(EDRServiceFinder, self).__init__()

    def with_large_pad(self, required):
        self.large_pad_required = required

    def with_medium_pad(self, required):
        self.medium_pad_required = required

    def within_radius(self, radius):
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        self.sc_distance = sc_distance

    def permits_in_possesion(self, permits):
        self.permits = permits

    def shuffling(self, shuffle_systems, shuffle_stations):
        self.shuffle_systems = shuffle_systems
        self.shuffle_stations = shuffle_stations

    def ignore_center(self, exclude_center):
        self.exclude_center = exclude_center

    def set_dlc(self, name):
        self.checker.set_dlc(name)

    def run(self):
        self.trials = 0
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.sc_distance, self.checker, results)

    def nearby(self):
        servicePrime = None
        serviceAlt = None
        self.checked_systems = []

        candidates = {'prime': servicePrime, 'alt': serviceAlt}
        
        system = self.edr_systems.system(self.star_system)
        if not self.exclude_center:
            if isinstance(system, list):
                if system[0] and "distance" not in system[0]:
                    system[0]["distance"] = 0
            else:
                if "distance" not in system[0]:
                    system["distance"] = 0
            the_system = system[0] if isinstance(system, list) else system
            candidates = self.__check_system(the_system, candidates)
            self.checked_systems.append(the_system.get('name', ""))
            if candidates["prime"]:
                return candidates["prime"]
               
        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if not systems:
            return candidates

        if self.shuffle_systems:
            shuffle(systems)

        candidates = self.__search(systems, candidates)
        if not (candidates and candidates.get('prime', None)):
            EDRLOG.log(u"Couldn't find any prime candidate so far. Trying again after a shuffle", "DEBUG")
            # TODO remove from systems the checked systems
            # TODO check colonia commands
            shuffle(systems)
            candidates = self.__search(systems, candidates)

        if not (candidates and candidates.get('prime', None)) and self.edr_systems.in_colonia(self.star_system):
            EDRLOG.log(u"Couldn't find any candidate so far. Trying with key Colonia star systems", "DEBUG")
            key_colonia_star_systems = [ "Alberta", "Amatsuboshi", "Asura", "Aurora Astrum", "Benzaiten", "Centralis", "Coeus", "Colonia", "Deriso", "Desy", "Diggidiggi", "Dubbuennel", "Edge Fraternity Landing", "Einheriar", "Eol Procul Centauri", "Helgoland", "Kajuku", "Kinesi", "Kojeara", "Kopernik", "Los", "Luchtaine", "Magellan", "Mriya", "Pennsylvania", "Poe", "Randgnid", "Ratraii", "Saraswati", "Solitude", "Tir", "White Sun" ]
            for star_system in key_colonia_star_systems:
                system = self.edr_systems.system(star_system)
                candidates = self.__check_system(system[0] if isinstance(system, list) else system, candidates)
                if candidates and candidates.get('prime', None):
                    break

        if candidates:
            serviceAlt = candidates.get('alt', None)
            servicePrime = candidates.get('prime', None)

        return servicePrime if servicePrime else serviceAlt

    def __check_system(self, system, candidates):
        if not system:
            return candidates

        EDRLOG.log(u"System {}".format(system), "DEBUG")
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
            check_landing_pads = self.__check_landing_pads(candidate.get('type', ''))
            ambiguous = self.checker.is_service_availability_ambiguous(candidate)
            EDRLOG.log(u"System {} has a candidate {}: ambiguous {}, sc_distance {}, landing_pads {}".format(system['name'], candidate['name'], ambiguous, check_sc_distance, check_landing_pads), "DEBUG")
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
        return candidates


    def __search(self, systems, candidates):
        self.trials = 0
        if not systems:
            return candidates
        for system in systems:
            if self.trials > self.max_trials:
                EDRLOG.log(u"Tried too many. Aborting here.", "DEBUG")
                break

            if self.exclude_center and self.star_system == system.get("name", None):
                continue

            if system.get('name', None) in self.checked_systems:
                continue
            candidates = self.__check_system(system, candidates)                  
            self.checked_systems.append(system.get('name', ""))

            if candidates and candidates.get('prime', None):
                EDRLOG.log(u"Prime found, breaking here.", "DEBUG")
                break

        return candidates        

    def closest_station_with_service(self, stations, system_name):
        overall = None
        with_large_landing_pads = None
        with_medium_landing_pads = None
        (state, _) = self.edr_systems.system_state(system_name)
        state = state.lower() if state else state
        if state == u'lockdown':
            return None

        for station in stations:
            if not self.checker.check_station(station):
                continue
            
            if overall == None:
                overall = station
            elif station['distanceToArrival'] < overall['distanceToArrival'] and not self.checker.is_service_availability_ambiguous(station):
                overall = station
            
            if self.__has_large_landing_pads(station['type']):
                with_large_landing_pads = station
            elif self.__has_medium_landing_pads(station['type']):
                with_medium_landing_pads = station
        if self.large_pad_required and with_large_landing_pads:
            return with_large_landing_pads
        elif self.medium_pad_required and with_medium_landing_pads:
            return with_medium_landing_pads
        return overall

    def __check_landing_pads(self, type):
        if self.large_pad_required:
            return self.__has_large_landing_pads(type)
        elif self.medium_pad_required:
            return self.__has_medium_landing_pads(type)
        return self.__has_small_landing_pads(type)

    def __has_large_landing_pads(self, stationType):
        return stationType.lower() in ['coriolis starport', 'ocellus starport', 'orbis starport', 'planetary port', 'planetary outpost', 'asteroid base', 'mega ship', 'fleet carrier']

    def __has_medium_landing_pads(self, stationType):
        if self.__has_large_landing_pads(stationType):
            return True
        return False # TODO odyssey settlements can be anything at this point :(

    def __has_small_landing_pads(self, stationType):
        if self.__has_large_landing_pads(stationType):
            return True
        if self.__has_medium_landing_pads(stationType):
            return True
        return stationType.lower() in ['odyssey settlement']

    def __service_in_system(self, system):
        if not system:
            return None
            
        if system.get('requirePermit', False) and not system['name'] in self.permits :
            return None

        all_stations = self.edr_systems.stations_in_system(system['name'])
        if not all_stations or not len(all_stations):
            return None

        if self.shuffle_stations:
            shuffle(all_stations)

        return self.closest_station_with_service(all_stations, system['name'])

    def close(self):
        return None
