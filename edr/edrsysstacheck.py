class EDRSystemStationCheck(object):

    def __init__(self):
        self.max_distance = 50
        self.max_sc_distance = 1500
        self.name = None
        self.hint = None
        self.systems_counter = 0
        self.stations_counter = 0
        self.dlc_name = None


    def set_dlc(self, name):
        self.dlc_name = name

    def check_system(self, system):
        self.systems_counter = self.systems_counter + 1
        if not system:
            print("not system")
            return False
        
        if system.get('distance', None) is None:
            print("distance none")
            return False
        
        print("distance check: {} <= {}".format(system['distance'], self.max_distance))
        return system['distance'] <= self.max_distance

    def check_station(self, station):
        self.stations_counter = self.stations_counter + 1
        if not station:
            return False

        if station.get('distanceToArrival', None) is None:
            return False

        if "odyssey" in station.get("type", "").lower() and self.dlc_name != "Odyssey":
            return False
        return station['distanceToArrival'] < self.max_sc_distance

    def is_service_availability_ambiguous(self, station):
        return False

class EDRApexSystemStationCheck(EDRSystemStationCheck):

    def __init__(self, max_sc_distance=1500):
        super(EDRApexSystemStationCheck, self).__init__()
        self.max_distance = 100
        self.max_sc_distance = max_sc_distance

    def check_station(self, station):
        if not super(EDRApexSystemStationCheck, self).check_station(station):
            return False
        
        if not station.get('type', None):
            return False

        if not station.get('type', "n/a").lower() in ["asteroid base", 'bernal starport', "coriolis starport", "ocellus starport", "orbis starport", "bernal", "bernal statioport", "planetary port", "asteroid base", "outpost", "planetary outpost"]:
            return False
        return True