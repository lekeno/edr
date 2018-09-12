import threading

class EDRServiceFinder(threading.Thread):

    def __init__(self, star_system, checker, edr_systems, callback):
        self.star_system = star_system
        self.checker = checker
        self.radius = 50
        self.sc_distance = 1500
        self.edr_systems = edr_systems
        self.callback = callback
        self.large_pad_required = True
        self.permits = []
        super(EDRServiceFinder, self).__init__()

    def with_large_pad(self, required):
        self.large_pad_required = required

    def within_radius(self, radius):
        self.radius = radius

    def within_supercruise_distance(self, sc_distance):
        self.sc_distance = sc_distance

    def permits_in_possesion(self, permits):
        self.permits = permits

    def run(self):
        results = self.nearby()
        if self.callback:
            self.callback(self.star_system, self.radius, self.sc_distance, results)

    def nearby(self):
        servicePrime = None
        serviceAlt = None
        
        system = self.edr_systems.system(self.star_system)
        if not system:
            return None

        system = system[0]
        system['distance'] = 0
        possibility = self.checker.check_system(system)
        accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
        if possibility and accessible:
            candidate = self.__service_in_system(system)
            if candidate:
                check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
                check_landing_pads = self.__has_large_lading_pads(candidate['type']) if self.large_pad_required else True
                if check_sc_distance and check_landing_pads:
                    servicePrime = system
                    servicePrime['station'] = candidate
                    return servicePrime
                else:
                    serviceAlt = system
                    serviceAlt['station'] = candidate

        sorted_systems = self.edr_systems.systems_within_radius(self.star_system, self.radius)

        for system in sorted_systems:
            possibility = self.checker.check_system(system)
            accessible = not system.get('requirePermit', False) or (system.get('requirePermit', False) and system['name'] in self.permits)
            if not possibility or not accessible:
                continue

            candidate = self.__service_in_system(system)
            if candidate:
                check_sc_distance = candidate['distanceToArrival'] <= self.sc_distance
                check_landing_pads = self.__has_large_lading_pads(candidate['type']) if self.large_pad_required else True
                if check_sc_distance and check_landing_pads:
                    trialed = system
                    trialed['station'] = candidate
                    closest = self.edr_systems.closest_destination(trialed, servicePrime)
                    servicePrime = closest
                else:
                    trialed = system
                    trialed['station'] = candidate
                    closest = self.edr_systems.closest_destination(trialed, serviceAlt)
                    serviceAlt = closest

            if servicePrime:
                break

        return servicePrime if servicePrime else serviceAlt


    def closest_station_with_service(self, stations):
        overall = None
        with_large_landing_pads = None
        for station in stations:
            if not self.checker.check_station(station):
                continue

            state = self.edr_systems.system_state(self.star_system)
            state = state.lower() if state else state
            if state == u'lockdown':
                print "skipping: lockdown"
                continue

            if overall == None:
                overall = station
            elif station['distanceToArrival'] < overall['distanceToArrival']:
                overall = station
            
            if self.__has_large_lading_pads(station['type']):
                with_large_landing_pads = station
        
        return with_large_landing_pads if self.large_pad_required and with_large_landing_pads else overall


    def __has_large_lading_pads(self, stationType):
        return stationType.lower() in ['coriolis starport', 'ocellus starport', 'orbis starport', 'planetary port', 'asteroid base', 'mega ship']

    def __service_in_system(self, system):
        if not system:
            return None
            
        if system.get('requirePermit', False) and not system['name'] in self.permits :
            return None

        all_stations = self.edr_systems.stations_in_system(system['name'])
        if not all_stations or not len(all_stations):
            return None

        return self.closest_station_with_service(all_stations)

    def close(self):
        # TODO
        return None
