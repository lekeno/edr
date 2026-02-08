import threading
from edri18n import _
from edrlog import EDR_LOG


class EDRParkingSystemFinder(threading.Thread):
    """
    Finds systems with available fleet carrier parking slots nearby.
    """

    def __init__(self, star_system, edr_systems, callback):
        """
        Initialize the parking system finder.

        Args:
            star_system (str): The name of the star system to search around.
            edr_systems (EDRSystems): The EDR systems logic object.
            callback (function): The callback to trigger when search is complete.
        """
        super().__init__()
        self.star_system = star_system
        self.radius = 25
        self.rank = 0
        self.trials = 0
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.callback = callback
        self.checked_systems = []

    def within_radius(self, radius):
        """
        Set the search radius.

        Args:
            radius (int): The search radius in light years.
        """
        self.radius = radius

    def nb_to_pick(self, rank):
        """
        Set the rank (index) of the result to pick.

        Args:
            rank (int): The index of the result to pick.
        """
        self.rank = rank

    def run(self):
        """
        Execute the search thread.
        """
        self.trials = 0
        result = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.rank, result)

    def nearby(self):
        """
        Search for a nearby system suitable for parking.

        Returns:
            dict: The system info for a suitable parking system, or None if not found.
        """
        self.checked_systems = []

        system = self.edr_systems.system(self.star_system)
        if system and self.rank == 0:
            the_system = system[0] if isinstance(system, list) else system
            the_system["distance"] = 0
            self.checked_systems.append(the_system.get('name', ""))
            self.trials += 1
            if self._check_system(the_system):
                return the_system

        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if systems is None:
            return None

        if systems is False:
            EDR_LOG.error(f"Couldn't get systems within radius of {self.star_system}: EDSM API issue?")
            return None

        sorted_systems = sorted(systems, key=lambda s: s['distance'])
        return self._search(sorted_systems)

    def _check_system(self, system):
        """
        Check if a system is suitable for parking.

        Args:
            system (dict): The system info.

        Returns:
            bool: True if suitable, False otherwise.
        """
        if not system:
            return False

        if system.get("distance", 0) == 0 and system.get("name", "N/A") != self.star_system:
            # Takes care of some odd distant system showing up nearby shinrarta with distance set to 0
            return False

        slots = self._theoretical_parking_slots(system)
        info = self._parking_info(system)
        accessible = not system.get('requirePermit', False)  # didn't work for Shinrarta...

        if accessible and slots > 0:
            system["parking"] = {"slots": slots, "info": info}
            return True
        return False

    def _theoretical_parking_slots(self, system):
        """
        Calculate theoretical parking slots based on body count.

        Args:
            system (dict): The system info.

        Returns:
            int: The theoretical number of parking slots.
        """
        if not system:
            return 0
        if "bodyCount" not in system or system["bodyCount"] is None:
            bodies = self.edr_systems.bodies(system.get("name", None))
            system["bodyCount"] = len(bodies) if bodies else 1
        return min(128, system["bodyCount"] * 16)

    def _parking_info(self, system):
        """
        Retrieve parking information for a system.

        Args:
            system (dict): The system info.

        Returns:
            dict: Parking statistics and distance information.
        """
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
            stats["min"] = min(stats["min"], distance) if stats["min"] != 0 else distance

            if body.get("type", "").lower() == "star":
                stars_distances.append(distance)
                sum_dist["stars"] += distance
                sum_bodies["stars"] += 1
                stars_stats["max"] = max(stars_stats["max"], distance)
                stars_stats["min"] = min(stars_stats["min"], distance) if stars_stats["min"] != 0 else distance

        stats["count"] = sum_bodies["all"]
        stars_stats["count"] = sum_bodies["stars"]
        stats["avg"] = sum_dist["all"] / (sum_bodies["all"] or 1)
        stars_stats["avg"] = sum_dist["stars"] / (sum_bodies["stars"] or 1)

        if distances:
            mid = len(distances) // 2
            stats["median"] = distances[mid] if len(distances) > 1 else distances[0]

        if stars_distances:
            mid = len(stars_distances) // 2
            stars_stats["median"] = stars_distances[mid] if len(stars_distances) > 1 else stars_distances[0]

        return {"all": {"distances": distances, "stats": stats}, "stars": {"distances": stars_distances, "stats": stars_stats}}

    def _search(self, systems):
        """
        Search through a list of systems for a parking candidate.

        Args:
            systems (list): List of systems to check.

        Returns:
            dict: The system info for the first suitable candidate at the specified rank.
        """
        if not systems:
            return None

        rank = max(0, min(len(systems), self.rank))
        candidates = []

        for system in systems:
            if self._check_system(system):
                candidates.append(system)
            self.checked_systems.append(system.get('name', ""))
            self.trials += 1
            if len(candidates) > rank:
                break

        return candidates[rank] if len(candidates) >= rank else None

    def close(self):
        """
        Close the finder (no-op).

        Returns:
            None: Always returns None.
        """
        return None
