import threading
from random import shuffle
from edr.core.edri18n import _


class EDRStateFinder(threading.Thread):
    """
    Finds systems with specific states near a reference system.
    """

    def __init__(self, star_system, checker, edr_systems, callback):
        """
        Initialize the state finder.

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
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.callback = callback
        self.permits = []

    def within_radius(self, radius):
        """
        Set the search radius.

        Args:
            radius (int): The search radius.
        """
        self.radius = radius

    def permits_in_possession(self, permits):
        """
        Set the list of permits the commander possesses.

        Args:
            permits (list): List of permit names.
        """
        self.permits = permits

    def run(self):
        """
        Execute the search thread.
        """
        results, grade = self.nearby()
        if self.callback:
            self.callback(self.checker.name, self.star_system, self.radius, self.checker, results, grade)

    def nearby(self):
        """
        Search for a suitable system nearby.

        Returns:
            tuple: A tuple of (best_system, best_grade).
        """
        best_system_so_far = None
        best_grade_so_far = 0

        system = self.edr_systems.system(self.star_system)
        if not system:
            return None, None

        system = system[0]
        system['distance'] = 0
        grade = self.checker.grade_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)

        if grade > 0 and accessible:
            state, updated = self.edr_systems.system_state(system['name'])
            allegiance = self.edr_systems.system_allegiance(system['name'])
            allegiance_grade = self.checker.grade_allegiance(allegiance)
            state_grade = self.checker.grade_state(state)

            if allegiance_grade and state_grade:
                grade += allegiance_grade + state_grade
                best_system_so_far = system
                best_system_so_far['lastUpdated'] = updated
                best_grade_so_far = grade
                if grade >= 5:
                    return best_system_so_far, best_grade_so_far

        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        if systems is None:
            return None, None

        if systems is False:
            self.checker.preliminary_msg = _("Couldn't get systems within radius of {}: EDSM API is probably having issues.").format(self.star_system)
            return None, None

        best_system_so_far, best_grade_so_far = self._search(systems, best_system_so_far, best_grade_so_far)
        if not best_system_so_far:
            shuffle(systems)
            best_system_so_far, best_grade_so_far = self._search(systems, best_system_so_far, best_grade_so_far)

        return best_system_so_far, best_grade_so_far

    def close(self):
        """
        Close the finder (no-op).

        Returns:
            None: Always returns None.
        """
        return None

    def _search(self, systems, best_system_so_far, best_grade_so_far):
        """
        Internal search logic for suitable systems.

        Args:
            systems (list): List of systems to search.
            best_system_so_far (dict): Current best system candidate.
            best_grade_so_far (int): Current best grade.

        Returns:
            tuple: A tuple of (updated_best_system, updated_best_grade).
        """
        trials = 0
        if not systems:
            return None, None

        for system in systems:
            grade = self.checker.grade_system(system)
            accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)

            if grade <= 0 or not accessible:
                continue

            if self.edr_systems.are_factions_stale(system['name']):
                trials += 1
                if trials > self.max_trials:
                    break

            state, updated = self.edr_systems.system_state(system['name'])
            allegiance = self.edr_systems.system_allegiance(system['name'])
            allegiance_grade = self.checker.grade_allegiance(allegiance)
            state_grade = self.checker.grade_state(state)

            if allegiance_grade and state_grade:
                grade += allegiance_grade + state_grade
                if grade > best_grade_so_far:
                    best_system_so_far = system
                    best_system_so_far['updateTime'] = updated
                    best_grade_so_far = grade
                if grade >= 5:
                    break

        return best_system_so_far, best_grade_so_far
