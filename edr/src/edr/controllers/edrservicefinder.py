import threading
from random import shuffle
from edr.core.edri18n import _  # EDR_INTERNAL
from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL


class EDRServiceFinder(threading.Thread):
    """
    Finds specific services (e.g. Interstellar Factors, Brokers) near a reference system.
    """

    def __init__(self, star_system, checker, edr_systems, callback):
        """
        Initialize the service finder.

        Args:
            star_system (str): The name of the reference star system.
            checker (object): The checker object to validate candidates.
            edr_systems (EDRSystems): The EDR systems logic object.
            callback (function): The callback to trigger when search is complete.
        """
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
        super().__init__()

    def with_large_pad(self, required):
        """
        Set requirement for large landing pads.

        Args:
            required (bool): True if large pad is required.
        """
        self.large_pad_required = required

    def with_medium_pad(self, required):
        """
        Set requirement for medium landing pads.

        Args:
            required (bool): True if medium pad is required.
        """
        self.medium_pad_required = required

    def within_radius(self, radius):
        """
        Set the search radius in Light Years.

        Args:
            radius (int): The search radius.
        """
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        """
        Set the maximum supercruise distance.

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

    def shuffling(self, shuffle_systems, shuffle_stations):
        """
        Enable or disable shuffling of search order.

        Args:
            shuffle_systems (bool): Whether to shuffle systems.
            shuffle_stations (bool): Whether to shuffle stations within systems.
        """
        self.shuffle_systems = shuffle_systems
        self.shuffle_stations = shuffle_stations

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
        Search for suitable services nearby.

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
            return candidates["prime"] or candidates["alt"]

        if systems is False:
            self.checker.preliminary_msg = _(
                "Couldn't get systems within radius of {}: EDSM API is probably having issues.").format(self.star_system)
            return None

        if self.shuffle_systems:
            shuffle(systems)

        candidates = self._search(systems, candidates)
        if not (candidates and candidates.get('prime', None)):
            EDR_LOG.debug("Couldn't find any prime candidate so far. Trying again after a shuffle")
            shuffle(systems)
            candidates = self._search(systems, candidates)

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
        Check a system for suitable services.

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
        accessible = not system.get('requirePermit', False) or (
                    system.get('requirePermit', False) and system['name'] in self.permits)
        EDR_LOG.debug(f"System {system['name']}: possibility {possibility}, accessible {accessible}")
        if not possibility or not accessible:
            return candidates

        if self.edr_systems.are_stations_stale(system['name']):
            self.trials += 1

        candidate = self._service_in_system(system)
        if candidate:
            check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
            check_landing_pads = self._check_landing_pads(candidate.get('type', ''))
            ambiguous = self.checker.is_service_availability_ambiguous(candidate)
            EDR_LOG.debug(
                f"System {system['name']} has a candidate {candidate.get('name')}: "
                f"ambiguous {ambiguous}, sc_distance {check_sc_distance}, landing_pads {check_landing_pads}"
            )
            if check_sc_distance and check_landing_pads and not ambiguous:
                trialed = system.copy()
                trialed['station'] = candidate
                closest = self.edr_systems.closest_station(trialed, candidates['prime'])
                EDR_LOG.debug(f"Prime Trial {system['name']}, closest {closest.get('name')}")
                candidates['prime'] = closest
            else:
                if ambiguous:
                    candidate['comment'] = _("[Confidence: LOW]")
                trialed = system.copy()
                trialed['station'] = candidate
                closest = self.edr_systems.closest_station(trialed, candidates['alt'])
                EDR_LOG.debug(f"Trial {system['name']}, closest {closest.get('name')}")
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

    def closest_station_with_service(self, stations, system_name):
        """
        Find the best matching station from a list of stations.

        Args:
            stations (list): List of stations in the system.
            system_name (str): The name of the system.

        Returns:
            dict: The best matching station, or None.
        """
        overall = None
        with_large_landing_pads = None
        with_medium_landing_pads = None
        (state, _) = self.edr_systems.system_state(system_name)
        state = state.lower() if state else state
        if state == 'lockdown':
            return None

        for station in stations:
            if not self.checker.check_station(station):
                continue

            if overall is None:
                overall = station
            elif station['distanceToArrival'] < overall['distanceToArrival'] and not self.checker.is_service_availability_ambiguous(station):
                overall = station

            if self._has_large_landing_pads(station['type']):
                with_large_landing_pads = station
            elif self._has_medium_landing_pads(station['type']):
                with_medium_landing_pads = station

        if self.large_pad_required and with_large_landing_pads:
            return with_large_landing_pads
        elif self.medium_pad_required and with_medium_landing_pads:
            return with_medium_landing_pads
        return overall

    def _check_landing_pads(self, type):
        """
        Check if the station type has the required landing pads.
        """
        if self.large_pad_required:
            return self._has_large_landing_pads(type)
        elif self.medium_pad_required:
            return self._has_medium_landing_pads(type)
        return self._has_small_landing_pads(type)

    def _has_large_landing_pads(self, station_type):
        """
        Check if the station type has large landing pads.
        """
        return station_type.lower() in [
            'coriolis starport', 'ocellus starport',
            'orbis starport', 'planetary port',
            'planetary outpost', 'asteroid base',
            'mega ship', 'fleet carrier'
        ]

    def _has_medium_landing_pads(self, station_type):
        """
        Check if the station type has medium landing pads.
        """
        if self._has_large_landing_pads(station_type):
            return True
        return False  # TODO odyssey settlements can be anything at this point :(

    def _has_small_landing_pads(self, station_type):
        """
        Check if the station type has small landing pads.
        """
        if self._has_large_landing_pads(station_type):
            return True
        if self._has_medium_landing_pads(station_type):
            return True
        return station_type.lower() in ['odyssey settlement']

    def _service_in_system(self, system):
        """
        Find a suitable service in the given system.

        Args:
            system (dict): The system info.

        Returns:
            dict: The best matching service found in the system, or None.
        """
        if not system:
            return None

        if system.get('requirePermit', False) and system['name'] not in self.permits:
            return None

        all_stations = self.edr_systems.stations_in_system(system['name'])
        if not all_stations or not len(all_stations):
            return None

        if self.shuffle_stations:
            shuffle(all_stations)

        return self.closest_station_with_service(all_stations, system['name'])

    def close(self):
        """
        Close the finder (no-op).

        Returns:
            None.
        """
        return None
