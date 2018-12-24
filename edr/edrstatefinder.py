import threading
from random import shuffle

class EDRStateFinder(threading.Thread):

    def __init__(self, star_system, checker, edr_systems, callback):
        self.star_system = star_system
        self.checker = checker
        self.radius = 50
        self.max_trials = 25
        self.edr_systems = edr_systems
        self.callback = callback
        self.permits = []
        super(EDRStateFinder, self).__init__()

    def within_radius(self, radius):
        self.radius = radius

    def permits_in_possesion(self, permits):
        self.permits = permits

    def run(self):
        (results, grade) = self.nearby()
        if self.callback:
            self.callback(self.checker.name, self.star_system, self.radius, self.checker, results, grade)

    def nearby(self):
        best_system_so_far = None
        best_grade_so_far = 0
        
        system = self.edr_systems.system(self.star_system)
        if not system:
            return (None, None)

        system = system[0]
        system['distance'] = 0
        grade = self.checker.grade_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
        if grade > 0 and accessible:
            (state, updated) = self.edr_systems.system_state(system['name'])
            allegiance = self.edr_systems.system_allegiance(system['name'])
            allegiance_grade = self.checker.grade_allegiance(allegiance)
            state_grade = self.checker.grade_state(state) 
            if allegiance_grade and state_grade:
                grade += allegiance_grade + state_grade
                best_system_so_far = system
                best_system_so_far['lastUpdated'] = updated
                best_grade_so_far = grade
                if grade >= 5:
                    return (best_system_so_far, best_grade_so_far)

        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        
        (best_system_so_far, best_grade_so_far) = self.__search(systems, best_system_so_far, best_grade_so_far)
        if not best_system_so_far:
            shuffle(systems)
            (best_system_so_far, best_grade_so_far) = self.__search(systems, best_system_so_far, best_grade_so_far)

        return (best_system_so_far, best_grade_so_far)

    def close(self):
        return None

    def __search(self, systems, best_system_so_far, best_grade_so_far):
        trials = 0
        for system in systems:
            grade = self.checker.grade_system(system)
            accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
            if grade <= 0 or not accessible:
                continue

            if self.edr_systems.are_factions_stale(system['name']):  
                trials = trials + 1
                if trials > self.max_trials:
                    break

            (state, updated) = self.edr_systems.system_state(system['name'])
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
 
        return (best_system_so_far, best_grade_so_far)