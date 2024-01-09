import threading
from random import shuffle
from edri18n import _
from edrlog import EDRLog

EDRLOG = EDRLog()

class EDRSettlementFinder(threading.Thread):

    def __init__(self, star_system, checker, edr_systems, callback):
        self.star_system = star_system
        self.checker = checker
        self.radius = 50
        self.sc_distance = 1500
        self.trials = 0
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.odyssey_settlement = False
        self.callback = callback
        self.permits = []
        self.shuffle_systems = False
        self.shuffle_settlements = False
        self.exclude_center = False
        self.exclude_states = []
        self.include_states = []
        self.checked_systems = []
        super(EDRSettlementFinder, self).__init__()

    def for_odyssey(self, required):
        self.odyssey_settlement = required
    
    def within_radius(self, radius):
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        self.sc_distance = sc_distance

    def permits_in_possesion(self, permits):
        self.permits = permits

    def shuffling(self, shuffle_systems, shuffle_settlements):
        self.shuffle_systems = shuffle_systems
        self.shuffle_settlements = shuffle_settlements

    def ignore_center(self, exclude_center):
        self.exclude_center = exclude_center

    def ignore_states(self, states_to_ignore):
        self.exclude_states = states_to_ignore

    def require_states(self, states_to_require):
        self.include_states = states_to_require

    def set_dlc(self, name):
        self.checker.set_dlc(name)

    def run(self):
        self.trials = 0
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.sc_distance, self.checker, results)

    def nearby(self):
        settlementPrime = None
        settlementAlt = None
        self.checked_systems = []

        candidates = {'prime': settlementPrime, 'alt': settlementAlt}
        
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
            settlementAlt = candidates.get('alt', None)
            settlementPrime = candidates.get('prime', None)

        return settlementPrime if settlementPrime else settlementAlt

    def __check_system(self, system, candidates):
        if not system:
            return candidates

        EDRLOG.log(u"System {}".format(system), "DEBUG")
        possibility = self.checker.check_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
        EDRLOG.log(u"System {}: possibility {}, accessible {}".format(system['name'], possibility, accessible), "DEBUG")
        if not possibility or not accessible:
            return candidates

        if self.edr_systems.are_settlements_stale(system['name']):
            self.trials += 1
        
        candidate = self.__settlement_in_system(system)
        if candidate:
            check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
            ambiguous = self.checker.is_ambiguous(candidate, system['name'])
            EDRLOG.log(u"System {} has a candidate {}: ambiguous {}, sc_distance {}".format(system['name'], candidate['name'], ambiguous, check_sc_distance), "DEBUG")
            if check_sc_distance and not ambiguous:
                trialed = system
                trialed['settlement'] = candidate
                closest = self.edr_systems.closest_settlement(trialed, candidates['prime'])
                EDRLOG.log(u"Prime Trial {}, closest {}".format(system['name'], closest['name']), "DEBUG")
                candidates['prime'] = closest
            else:
                if ambiguous:
                    candidate['comment'] = _(u"[Confidence: LOW]")
                trialed = system
                trialed['settlement'] = candidate
                closest = self.edr_systems.closest_settlement(trialed, candidates['alt'])
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

    def closest_matching_settlement(self, settlements, system_name):
        overall = None
        for settlement in settlements:
            EDRLOG.log(settlement, "DEBUG")
            if not self.checker.check_settlement(settlement, system_name):
                continue
            
            factionIDName = settlement.get("controllingFaction", { "id": -1, "name": ""})
            factionName = factionIDName.get("name", "")
            faction = self.edr_systems.faction_in_system(factionName, system_name)
            if faction and faction.state in self.exclude_states:
                EDRLOG.log("Skipping {} due to bad state for the controlling faction: {}".format(settlement, faction), "DEBUG")
                continue

            if self.include_states and faction and faction.state not in self.include_states:
                EDRLOG.log("Skipping {} due to state not matching any of the the required state for the controlling faction: {}".format(settlement, faction), "DEBUG")
                continue
            
            if overall == None:
                overall = settlement
            elif settlement['distanceToArrival'] < overall['distanceToArrival']:
                overall = settlement
            
        return overall

    def __settlement_in_system(self, system):
        if not system:
            return None
            
        if system.get('requirePermit', False) and not system['name'] in self.permits :
            return None

        EDRLOG.log("sys: " + system['name'], "DEBUG")
        all_settlements = self.edr_systems.stations_in_system(system['name']) # also returns settlements
        if not all_settlements or not len(all_settlements):
            EDRLOG.log("no settlements in " + system['name'], "DEBUG")
            return None
        
        EDRLOG.log("settlements: {}".format(all_settlements), "DEBUG")

        if self.shuffle_settlements:
            shuffle(all_settlements)

        return self.closest_matching_settlement(all_settlements, system['name'])

    def close(self):
        return None
