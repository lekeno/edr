import threading
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
        self.checked_systems = []
        super(EDRParkingSystemFinder, self).__init__()

    def within_radius(self, radius):
        self.radius = radius

    def nb_to_pick(self, rank):
        self.rank = rank

    def run(self):
        self.trials = 0
        result = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.rank, result)

    def nearby(self):
        self.checked_systems = []

        system = self.edr_systems.system(self.star_system)
        if system and self.rank == 0:
            the_system = system[0] if isinstance(system, list) else system
            the_system["distance"] = 0
            self.checked_systems.append(the_system.get('name', ""))
            self.trials += 1
            if self.__check_system(the_system):
                candidate = the_system
                return candidate
        
        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if not systems:
            return None

        sorted_systems = sorted(systems, key=lambda s: s['distance'])
        return self.__search(sorted_systems)

    def __check_system(self, system):
        if not system:
            return False

        slots = self.__theoretical_parking_slots(system)
        info = self.__parking_info(system)
        accessible = not system.get('requirePermit', False) # didn't work for Shinrarta...
        if accessible and slots > 0:
            system["parking"] = {"slots": slots, "info": info}
            return True
        return False

    def __theoretical_parking_slots(self, system):
        if not system:
            return 0
        if "bodyCount" not in system:
            bodies = self.edr_systems.bodies(system.get("name", None))
            system["bodyCount"] = len(bodies) if bodies else 1
        return min(128, system["bodyCount"] * 16)
    
    def __parking_info(self, system):
        if not system:
            return None
        
        bodies = self.edr_systems.bodies(system.get("name", None))
        if not bodies:
            return None
        stats = {"max": 0, "median": 0, "min": 0, "avg": 0, "count": 0}
        stars_stats = {"max": 0, "median": 0, "min": 0, "avg": 0, "count": 0}
        sum_dist = {"all": 0, "stars": 0}
        sum_bodies = {"all": 0, "stars": 0}
        distances = []
        stars_distances = []
        for body in sorted(bodies, key=lambda b: b['distanceToArrival']):
            distance = body.get("distanceToArrival", None)
            if distance is None:
                continue
            distances.append(distance)
            sum_dist["all"] += distance
            sum_bodies["all"] += 1
            stats["max"] = max(stats["max"], distance)
            stats["min"] = min(stats["min"], distance)

            if body.get("type", "").lower() == "star":
                stars_distances.append(distance)
                sum_dist["stars"] += distance
                sum_bodies["stars"] += 1
                stars_stats["max"] = max(stats["max"], distance)
                stars_stats["min"] = min(stats["min"], distance)
                
        stats["count"] = sum_bodies["all"]
        stars_stats["count"] = sum_bodies["stars"]
        stats["avg"] = sum_dist["all"] / sum_bodies["all"]
        stars_stats["avg"] = sum_dist["stars"] / sum_bodies["stars"]
        stats["median"] = distances[len(distances)//2]
        stars_stats["median"] = stars_distances[len(stars_distances)//2]
        return {"all": {"distances": distances, "stats": stats}, "stars": {"distances": stars_distances, "stats": stars_stats}}


    def __search(self, systems):
        if not systems:
            return None
        rank = max(0,min(len(systems), self.rank))
        candidates = []
        for system in systems:
            if self.__check_system(system):
                candidates.append(system)
            self.checked_systems.append(system.get('name', ""))
            self.trials += 1
            if len(candidates) > rank:
                break
        return candidates[rank] if len(candidates) >= rank else None

    def close(self):
        return None
