from .edvehicles import EDVehicle, EDVehicleSize

class EDUnknownVehicle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDCrewUnknownVehicle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown (crew)'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8

class EDCaptainUnknownVehicle(EDVehicle):
    def __init__(self):
        super().__init__()
        self.type = 'Unknown (captain)'
        self.size = EDVehicleSize.UNKNOWN
        self.shield_base_strength = 25
        self.hull_mass = 10
        self.hull_base_strength = 25 / 1.8
