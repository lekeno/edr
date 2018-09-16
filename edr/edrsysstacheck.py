class EDRSystemStationCheck(object):

    def __init__(self):
        self.max_distance = 50
        self.max_sc_distance = 1500
        self.name = None
        self.hint = None

    def check_system(self, system):
        if not system:
            return False
        
        if not system.get('distance', None):
            return False
        
        return system['distance'] <= self.max_distance

    def check_station(self, station):
        if not station:
            return False

        if not station.get('distanceToArrival', None):
            return False
        
        return station['distanceToArrival'] < self.max_sc_distance