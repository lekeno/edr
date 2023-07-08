import threading
from random import shuffle, seed
from edri18n import _
from edrlog import EDRLog

EDRLOG = EDRLog()

class EDRPlanetFinder(threading.Thread):

    def __init__(self, star_system, checker, edr_systems, callback):
        self.star_system = star_system
        self.checker = checker
        self.radius = 50
        self.sc_distance = 1500
        self.trials = 0
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.callback = callback
        self.permits = []
        self.shuffle_systems = False
        self.shuffle_planets = False
        self.exclude_center = False
        self.checked_systems = []
        super(EDRPlanetFinder, self).__init__()

    def within_radius(self, radius):
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        self.sc_distance = sc_distance

    def permits_in_possesion(self, permits):
        self.permits = permits

    def shuffling(self, shuffle_systems, shuffle_planets):
        self.shuffle_systems = shuffle_systems
        self.shuffle_planets = shuffle_planets

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
        if system and not self.exclude_center:
            the_system = system[0] if isinstance(system, list) else system
            the_system["distance"] = 0
            candidates = self.__check_system(the_system, candidates)
            self.checked_systems.append(the_system.get('name', ""))
            if candidates["prime"]:
                return candidates["prime"]
               
        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if not systems:
            return candidates

        if self.shuffle_systems:
            seed() # TODO should no longer be necessary
            EDRLOG.log("Nearby: shuffling systems", "DEBUG")
            shuffle(systems)

        candidates = self.__search(systems, candidates)
        if not (candidates and candidates.get('prime', None)):
            EDRLOG.log(u"Couldn't find any prime candidate so far. Trying again after a shuffle", "DEBUG")
            shuffle(systems)
            candidates = self.__search(systems, candidates)

        if not (candidates and candidates.get('prime', None)) and self.edr_systems.in_colonia(self.star_system):
            EDRLOG.log(u"Couldn't find any candidate so far. Trying with key Colonia star systems", "DEBUG")
            key_colonia_star_systems = [ "Alberta", "Amatsuboshi", "Asura", "Aurora Astrum", "Benzaiten", "Centralis", "Coeus", "Colonia", "Deriso", "Desy", "Diggidiggi", "Dubbuennel", "Edge Fraternity Landing", "Einheriar", "Eol Procul Centauri", "Helgoland", "Kajuku", "Kinesi", "Kojeara", "Kopernik", "Los", "Luchtaine", "Magellan", "Mriya", "Pennsylvania", "Poe", "Randgnid", "Ratraii", "Saraswati", "Solitude", "Tir", "White Sun" ]
            for star_system in key_colonia_star_systems:
                system = self.edr_systems.system(star_system)
                distance = self.edr_systems.distance(self.star_system, star_system)
                the_system = system[0] if isinstance(system, list) else system
                the_system["distance"] = distance
                candidates = self.__check_system(the_system, candidates)
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

        if self.edr_systems.are_bodies_stale(system['name']):
            self.trials += 1
        
        candidate = self.__planet_in_system(system)
        if candidate:
            check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
            EDRLOG.log(u"System {} has a candidate {}: sc_distance {}".format(system['name'], candidate['name'], check_sc_distance), "DEBUG")
            if check_sc_distance:
                trialed = system
                trialed['planet'] = candidate
                closest = self.edr_systems.closest_planet(trialed, candidates['prime'])
                EDRLOG.log(u"Prime Trial {}, closest {}".format(system['name'], closest['name']), "DEBUG")
                candidates['prime'] = closest
            else:
                trialed = system
                trialed['planet'] = candidate
                closest = self.edr_systems.closest_planet(trialed, candidates['alt'])
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

    def closest_planet_fit(self, bodies, system_name):
        overall = None
        for planet in bodies:
            if planet and not self.checker.check_planet(planet, system_name):
                continue
            
            if overall == None:
                EDRLOG.log("Closest planet fit: found first candidate: {}".format(planet), "DEBUG")
                overall = planet
            elif planet['distanceToArrival'] < overall['distanceToArrival']:
                EDRLOG.log("Closest planet fit: found better candidate: {}".format(planet), "DEBUG")
                overall = planet
            else:
                EDRLOG.log("Closest planet fit: worse candidate: {}".format(planet), "DEBUG")
            
        return overall

    def __planet_in_system(self, system):
        if not system:
            return None
            
        if system.get('requirePermit', False) and not system['name'] in self.permits :
            return None

        all_bodies = self.edr_systems.bodies(system['name'])
        if not all_bodies or not len(all_bodies):
            return None

        if self.shuffle_planets:
            seed() # TODO should no longer be necessary
            EDRLOG.log("Nearby: shuffling bodies", "DEBUG")
            shuffle(all_bodies)

        return self.closest_planet_fit(all_bodies, system['name'])

    def close(self):
        return None
