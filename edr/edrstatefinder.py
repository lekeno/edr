import threading
from random import shuffle

class EDRStateFinder(threading.Thread):

    def __init__(self, star_system, checker, edr_systems, callback):
        self.star_system = star_system
        self.checker = checker
        self.radius = 50
        self.max_trials = 50
        self.edr_systems = edr_systems
        self.callback = callback
        self.permits = []
        super(EDRStateFinder, self).__init__()

    def within_radius(self, radius):
        self.radius = radius

    def permits_in_possesion(self, permits):
        self.permits = permits

    def run(self):
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, results)

    def nearby(self):
        statePrime = None
        
        system = self.edr_systems.system(self.star_system)
        if not system:
            return None

        system = system[0]
        system['distance'] = 0
        possibility = self.checker.check_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
        if possibility and accessible:
            state = self.__state_of_system(system)
            allegiance = self.__
            fit = state and self.checker.check_state(state) 
            if :
                statePrime = system
                return statePrime

        systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)
        shuffle(systems)
        trials = 0

        for system in systems:
            possibility = self.checker.check_system(system)
            accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
            if not possibility or not accessible:
                continue

            state = self.edr_systems.system_state(system['name'])
            allegiance = self.edr_systems.system_allegiance(system['allegiance'])

            if self.checker.check_state(state) and self.checker.check_allegiance(allegiance):
                statePrime = system
                break

            trials = trials + 1
            if trials > self.max_trials:
                break

        return statePrime

    def close(self):
        # TODO
        return None
