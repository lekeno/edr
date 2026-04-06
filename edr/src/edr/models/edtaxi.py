from .edvehicles import EDVehicle, EDVehicleSize

class EDTaxi(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown (taxi)'
        self.size = EDVehicleSize.UNKNOWN
        self.destination = {"system": None, "location": None}
    
    def bound_for(self, system, location):
        self.destination["system"]= system
        self.destination["location"]= location
