import threading
from random import shuffle
from edr.core.edri18n import _
from edr.core.edrlog import EDR_LOG


class EDRPlanetFinder(threading.Thread):
    """
    Finds specific planets (e.g. for materials or interest) near a reference system.
    """

    def __init__(self, star_system, checker, edr_systems, callback):
        """
        Initialize the planet finder.

        Args:
            star_system (str): The name of the reference star system.
            checker (object): The checker object to validate candidates.
            edr_systems (EDRSystems): The EDR systems logic object.
            callback (function): The callback to trigger when search is complete.
        """
        super().__init__()
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

    def within_radius(self, radius):
        """
        Set the search radius in Light Years.

        Args:
            radius (int): The search radius.
        """
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        """
        Set the maximum supercruise distance for bodies.

        Args:
            sc_distance (int): Max supercruise distance in light seconds.
        """
        self.sc_distance = sc_distance

    def permits_in_possession(self, permits):
        """
        Set the permits the commander possesses.

        Args:
            permits (list): List of permit names.
        """
        self.permits = permits

    def shuffling(self, shuffle_systems, shuffle_planets):
        """
        Enable or disable shuffling of search order.

        Args:
            shuffle_systems (bool): Whether to shuffle systems.
            shuffle_planets (bool): Whether to shuffle planets within systems.
        """
        self.shuffle_systems = shuffle_systems
        self.shuffle_planets = shuffle_planets

    def ignore_center(self, exclude_center):
        """
        Whether to ignore the current system in the search.

        Args:
            exclude_center (bool): True to exclude the reference system.
        """
        self.exclude_center = exclude_center

    def set_dlc(self, name):
        """
        Set DLC context for the checker.

        Args:
            name (str): The DLC name (e.g., "Odyssey").
        """
        self.checker.set_dlc(name)

    def run(self):
        """
        Execute the search thread.
        """
        self.trials = 0
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.sc_distance, self.checker, results)

    def nearby(self):
        """
        Search for suitable planets nearby.

        Returns:
            dict: The best candidate found, or None.
        """
        service_prime = None
        service_alt = None
        self.checked_systems = []

        candidates = {'prime': service_prime, 'alt': service_alt}

        system = self.edr_systems.system(self.star_system)
        if system and not self.exclude_center:
            the_system = system[0] if isinstance(system, list) else system
            the_system["distance"] = 0
            candidates = self._check_system(the_system, candidates)
            self.checked_systems.append(the_system.get('name', ""))
            if candidates["prime"]:
                return candidates["prime"]

        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if systems is None:
            return candidates

        if systems is False:
            self.checker.preliminary_msg = _(f"Couldn't get systems within radius of {self.star_system}: EDSM API is probably having issues.")
            return candidates

        if self.shuffle_systems:
            EDR_LOG.debug("Nearby: shuffling systems")
            shuffle(systems)

        candidates = self._search(systems, candidates)
        if not (candidates and candidates.get('prime', None)):
            EDR_LOG.debug("Couldn't find any prime candidate so far. Trying again after a shuffle")
            shuffle(systems)
            candidates = self._search(systems, candidates)

        # Fallback to key Colonia systems if strictly in Colonia and nothing found
        if not (candidates and candidates.get('prime', None)) and self.edr_systems.in_colonia(self.star_system):
            EDR_LOG.debug("Couldn't find any candidate so far. Trying with key Colonia star systems")
            key_colonia_star_systems = [
                "Alberta", "Amatsuboshi", "Asura", "Aurora Astrum", "Benzaiten", "Centralis", "Coeus",
                "Colonia", "Deriso", "Desy", "Diggidiggi", "Dubbuennel", "Edge Fraternity Landing",
                "Einheriar", "Eol Procul Centauri", "Helgoland", "Kajuku", "Kinesi", "Kojeara",
                "Kopernik", "Los", "Luchtaine", "Magellan", "Mriya", "Pennsylvania", "Poe",
                "Randgnid", "Ratraii", "Saraswati", "Solitude", "Tir", "White Sun"
            ]
            for star_system in key_colonia_star_systems:
                system = self.edr_systems.system(star_system)
                if not system:
                    continue
                distance = self.edr_systems.distance(self.star_system, star_system)
                the_system = system[0] if isinstance(system, list) else system
                the_system["distance"] = distance
                candidates = self._check_system(the_system, candidates)
                if candidates and candidates.get('prime', None):
                    break

        if candidates:
            service_alt = candidates.get('alt', None)
            service_prime = candidates.get('prime', None)

        return service_prime if service_prime else service_alt

    def _check_system(self, system, candidates):
        """
        Check a system for suitable planets.

        Args:
            system (dict): The system info.
            candidates (dict): Current prime and alt candidates.

        Returns:
            dict: Updated candidates dictionary.
        """
        if not system:
            return candidates

        EDR_LOG.debug(f"System {system}")
        possibility = self.checker.check_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
        EDR_LOG.debug(f"System {system.get('name')}: possibility {possibility}, accessible {accessible}")

        if not possibility or not accessible:
            return candidates

        if self.edr_systems.are_bodies_stale(system['name']):
            self.trials += 1

        candidate = self._planet_in_system(system)
        if candidate:
            check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
            EDR_LOG.debug(f"System {system.get('name')} has a candidate {candidate.get('name')}: sc_distance {check_sc_distance}")

            if check_sc_distance:
                trialed = system.copy()
                trialed['planet'] = candidate
                closest = self.edr_systems.closest_planet(trialed, candidates['prime'])
                EDR_LOG.debug(f"Prime Trial {system.get('name')}, closest {closest.get('name')}")
                candidates['prime'] = closest
            else:
                trialed = system.copy()
                trialed['planet'] = candidate
                closest = self.edr_systems.closest_planet(trialed, candidates['alt'])
                EDR_LOG.debug(f"Trial {system.get('name')}, closest {closest.get('name')}")
                candidates['alt'] = closest
        return candidates

    def _search(self, systems, candidates):
        """
        Search through a list of systems for suitable candidates.

        Args:
            systems (list): List of systems to check.
            candidates (dict): Current prime and alt candidates.

        Returns:
            dict: Updated candidates dictionary.
        """
        self.trials = 0
        if not systems:
            return candidates

        for system in systems:
            if self.trials > self.max_trials:
                EDR_LOG.debug("Tried too many. Aborting here.")
                break

            if self.exclude_center and self.star_system == system.get("name", None):
                continue

            if system.get('name', None) in self.checked_systems:
                continue

            candidates = self._check_system(system, candidates)
            self.checked_systems.append(system.get('name', ""))

            if candidates and candidates.get('prime', None):
                EDR_LOG.debug("Prime found, breaking here.")
                break

        return candidates

    def closest_planet_fit(self, bodies, system_name):
        """
        Find the best matching planet from a list of bodies.

        Args:
            bodies (list): List of bodies in the system.
            system_name (str): The name of the system.

        Returns:
            dict: The best matching planet, or None.
        """
        overall = None
        for planet in bodies:
            if planet and not self.checker.check_planet(planet, system_name):
                continue

            if overall is None:
                EDR_LOG.debug(f"Closest planet fit: found first candidate: {planet}")
                overall = planet
            elif planet['distanceToArrival'] < overall['distanceToArrival']:
                EDR_LOG.debug(f"Closest planet fit: found better candidate: {planet}")
                overall = planet
            else:
                EDR_LOG.debug(f"Closest planet fit: worse candidate: {planet}")

        return overall

    def _planet_in_system(self, system):
        """
        Find a suitable planet in the given system.

        Args:
            system (dict): The system info.

        Returns:
            dict: The best matching planet found in the system, or None.
        """
        if not system:
            return None

        if system.get('requirePermit', False) and system['name'] not in self.permits:
            return None

        all_bodies = self.edr_systems.bodies(system['name'])
        if not all_bodies:
            return None

        if self.shuffle_planets:
            EDR_LOG.debug("Nearby: shuffling bodies")
            shuffle(all_bodies)

        return self.closest_planet_fit(all_bodies, system['name'])

    def close(self):
        """
        Close the finder (no-op).

        Returns:
            None: Always returns None.
        """
        return None
