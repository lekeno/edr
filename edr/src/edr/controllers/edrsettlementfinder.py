import threading
from random import shuffle
from edr.core.edri18n import _
from edr.core.edrlog import EDR_LOG


class EDRSettlementFinder(threading.Thread):
    """
    Finds specific settlements (e.g. for odyssey mats, services) near a reference system.
    """

    def __init__(self, star_system, checker, edr_systems, callback):
        """
        Initialize the settlement finder.

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
        self.odyssey_settlement = False
        self.callback = callback
        self.permits = []
        self.shuffle_systems = False
        self.shuffle_settlements = False
        self.exclude_center = False
        self.exclude_states = []
        self.include_states = []
        self.checked_systems = []

    def for_odyssey(self, required):
        """
        Set whether looking for Odyssey settlements.

        Args:
            required (bool): True if looking for Odyssey settlements.
        """
        self.odyssey_settlement = required

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

    def shuffling(self, shuffle_systems, shuffle_settlements):
        """
        Enable or disable shuffling of search order.

        Args:
            shuffle_systems (bool): Whether to shuffle systems.
            shuffle_settlements (bool): Whether to shuffle settlements within systems.
        """
        self.shuffle_systems = shuffle_systems
        self.shuffle_settlements = shuffle_settlements

    def ignore_center(self, exclude_center):
        """
        Whether to ignore the current system in the search.

        Args:
            exclude_center (bool): True to exclude the reference system.
        """
        self.exclude_center = exclude_center

    def ignore_states(self, states_to_ignore):
        """
        Set list of faction states to ignore.

        Args:
            states_to_ignore (list): List of state names to ignore.
        """
        self.exclude_states = states_to_ignore

    def require_states(self, states_to_require):
        """
        Set list of faction states to require.

        Args:
            states_to_require (list): List of state names to require.
        """
        self.include_states = states_to_require

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
        Search for suitable settlements nearby.

        Returns:
            dict: The best candidate found, or None.
        """
        settlement_prime = None
        settlement_alt = None
        self.checked_systems = []

        candidates = {'prime': settlement_prime, 'alt': settlement_alt}

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
            return None

        if self.shuffle_systems:
            shuffle(systems)

        candidates = self._search(systems, candidates)
        if not (candidates and candidates.get('prime', None)):
            EDR_LOG.debug("Couldn't find any prime candidate so far. Trying again after a shuffle")
            shuffle(systems)
            candidates = self._search(systems, candidates)

        # Fallback to key Colonia systems
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
            settlement_alt = candidates.get('alt', None)
            settlement_prime = candidates.get('prime', None)

        return settlement_prime if settlement_prime else settlement_alt

    def _check_system(self, system, candidates):
        """
        Check a system for suitable settlements.

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

        if self.edr_systems.are_settlements_stale(system['name']):
            self.trials += 1

        candidate = self._settlement_in_system(system)
        if candidate:
            check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
            ambiguous = self.checker.is_ambiguous(candidate, system['name'])
            EDR_LOG.debug(f"System {system.get('name')} has a candidate {candidate.get('name')}: ambiguous {ambiguous}, sc_distance {check_sc_distance}")

            if check_sc_distance and not ambiguous:
                trialed = system.copy()
                trialed['settlement'] = candidate
                closest = self.edr_systems.closest_settlement(trialed, candidates['prime'])
                EDR_LOG.debug(f"Prime Trial {system.get('name')}, closest {closest.get('name')}")
                candidates['prime'] = closest
            else:
                if ambiguous:
                    candidate['comment'] = _("[Confidence: LOW]")
                trialed = system.copy()
                trialed['settlement'] = candidate
                closest = self.edr_systems.closest_settlement(trialed, candidates['alt'])
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

    def closest_matching_settlement(self, settlements, system_name):
        """
        Find the best matching settlement from a list of settlements.

        Args:
            settlements (list): List of settlements in the system.
            system_name (str): The name of the system.

        Returns:
            dict: The best matching settlement, or None.
        """
        overall = None
        for settlement in settlements:
            EDR_LOG.debug(settlement)
            if not self.checker.check_settlement(settlement, system_name):
                continue

            faction_id_name = settlement.get("controllingFaction", {"id": -1, "name": ""})
            faction_name = faction_id_name.get("name", "")
            faction = self.edr_systems.faction_in_system(faction_name, system_name)

            if faction and faction.state in self.exclude_states:
                EDR_LOG.debug(f"Skipping {settlement} due to bad state for the controlling faction: {faction}")
                continue

            if self.include_states and faction and faction.state not in self.include_states:
                EDR_LOG.debug(f"Skipping {settlement} due to state not matching any of the required state for the controlling faction: {faction}")
                continue

            if overall is None:
                overall = settlement
            elif settlement['distanceToArrival'] < overall['distanceToArrival']:
                overall = settlement

        return overall

    def _settlement_in_system(self, system):
        """
        Find a suitable settlement in the given system.

        Args:
            system (dict): The system info.

        Returns:
            dict: The best matching settlement found in the system, or None.
        """
        if not system:
            return None

        if system.get('requirePermit', False) and system['name'] not in self.permits:
            return None

        EDR_LOG.debug(f"sys: {system['name']}")
        all_settlements = self.edr_systems.stations_in_system(system['name'])  # also returns settlements
        if not all_settlements:
            EDR_LOG.debug(f"no settlements in {system['name']}")
            return None

        EDR_LOG.debug(f"settlements: {all_settlements}")

        if self.shuffle_settlements:
            shuffle(all_settlements)

        return self.closest_matching_settlement(all_settlements, system['name'])

    def close(self):
        """
        Close the finder (no-op).

        Returns:
            None: Always returns None.
        """
        return None
