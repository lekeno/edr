class EDRSystemStationCheck(object):

    def __init__(self):
        self.max_distance = 50
        self.max_sc_distance = 1500
        self.name = None
        self.hint = None
        self.systems_counter = 0
        self.stations_counter = 0

    def check_system(self, system):
        self.systems_counter = self.systems_counter + 1
        if not system:
            return False
        
        if system.get('distance', None) is None:
            return False
        
        return system['distance'] <= self.max_distance

    def check_station(self, station):
        self.stations_counter = self.stations_counter + 1
        if not station:
            return False

        if not station.get('distanceToArrival', None):
            return False
        
        return station['distanceToArrival'] < self.max_sc_distance