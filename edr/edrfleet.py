from edvehicles import EDVehicleFactory

class EDRFleet(object):
    def __init__(self):
        self.ships = [] #TODO dictionary?
    
    @staticmethod
    def from_stored_ships_event(event):
        fleet = EDRFleet()
        local_system = event.get("StarSystem", None)
        local_station = event.get("StationName", None)
        local_market_id = event.get("MarketID", None)
        if not local_station or not local_system or not local_market_id:
            return fleet

        here = event.get("ShipsHere", [])
        for stored_ship in here:
            a_ship = EDVehicleFactory.from_stored_ship(stored_ship)
            if a_ship:
                fleet.ships.append(a_ship) #TODO key on what? #TODO add location
        
        remote = event.get("ShipsRemote", [])
        for stored_ship in remote:
            a_ship = EDVehicleFactory.from_stored_ship(stored_ship)
            if a_ship:
                fleet.ships.append(a_ship) #TODO key on what? #TODO add location