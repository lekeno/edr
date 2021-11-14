import threading
from random import shuffle
from edri18n import _
from edrlog import EDRLog

EDRLOG = EDRLog()

class EDRParkingSystemFinder(threading.Thread):

    def __init__(self, star_system, edr_systems, callback):
        self.star_system = star_system
        self.radius = 25
        self.rank = 0
        self.trials = 0
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.callback = callback
        self.shuffle_systems = False
        self.exclude_center = True # TODO until we can check if a system is full or not
        self.checked_systems = []
        super(EDRParkingSystemFinder, self).__init__()

    def within_radius(self, radius):
        self.radius = radius

    def shuffling(self, shuffle_systems):
        self.shuffle_systems = shuffle_systems

    def ignore_center(self, exclude_center):
        self.exclude_center = exclude_center

    def nb_to_pick(self, rank):
        self.rank = rank

    def run(self):
        self.trials = 0
        results = self.nearby()
        if self.callback:
            print(results)
            print(self.rank)
            result = results[self.rank] if self.rank >= 0 and self.rank < len(results) else None
            self.callback(self.star_system, self.radius, self.rank, result)

    def nearby(self):
        candidates = []
        self.checked_systems = []

        system = self.edr_systems.system(self.star_system)
        if system and not self.exclude_center:
            the_system = system[0] if isinstance(system, list) else system
            the_system["distance"] = 0
            candidates = self.__check_system(the_system, candidates)
            self.checked_systems.append(the_system.get('name', ""))
               
        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if not systems:
            return candidates

        if self.shuffle_systems:
            shuffle(systems)

        # TODO why did it stop with just one, and not the reference system?
        candidates = self.__search(systems, candidates)
        if not candidates:
            EDRLOG.log(u"Couldn't find any prime candidate so far. Trying again after a shuffle", "DEBUG")
            # TODO check colonia commands
            shuffle(systems)
            candidates = self.__search(systems, candidates)

        return candidates

    def __check_system(self, system, candidates):
        if not system:
            return candidates

        EDRLOG.log(u"System {}".format(system), "DEBUG")
        # TODO see if we can get some insights about how many FC are already there...
        slots = self.__theoretical_parking_slots(system)
        info = self.__parking_info(system)
        accessible = not system.get('requirePermit', False) # TODO FC are only allowed in systems that don't require a permit
        EDRLOG.log(u"System {}: slots {}, info {}, accessible {}".format(system['name'], slots, info, accessible), "DEBUG")
        if accessible and slots > 0:
            system["parking"] = {"slots": slots, "info": info}
            candidates.append(system)
        return candidates

    def __theoretical_parking_slots(self, system):
        if not system:
            return 0
        
        return min(128, system.get("bodyCount", 0) * 16)
    
    def __parking_info(self, system):
        if not system:
            return None
        
        bodies = self.edr_systems.bodies(system.get("name", None))
        if not bodies:
            return None
        stats = {"max": 0, "median": 0, "min": 0, "avg": 0}
        sum_dist = 0
        sum_slots = 0
        sum_bodies = 0
        distances = []
        for body in sorted(bodies, key=lambda b: b['distanceToArrival']):
            distance = body.get("distanceToArrival", None)
            if distance is None:
                continue
            distances.append(distance)
            sum_dist += distance
            stats["max"] = max(stats["max"], distance)
            stats["min"] = min(stats["min"], distance)
            sum_slots += 16
            sum_bodies += 1
            if sum_slots >= 128:
                sum_slots = 128
                break
        stats["avg"] = sum_dist / sum_bodies
        stats["median"] = distances[len(distances)//2]
        return {"distances": distances, "stats": stats}


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

        return candidates

    def close(self):
        return None
