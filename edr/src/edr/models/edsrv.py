from .edvehicles import EDVehicle

class EDSurfaceVehicle(EDVehicle):
    def __init__(self):
        super().__init__()

    def supports_slf(self):
        return False

    def supports_srv(self):
        return False
