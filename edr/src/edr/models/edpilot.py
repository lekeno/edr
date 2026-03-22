from edr.utils.edtime import EDTime
from edr.core.edrconfig import EDR_CONFIG
from .edvehicles import EDVehicleFactory
from .edspacesuits import EDSuitFactory
from .edsitu import EDLocation, EDAttitude, EDSpaceDimension
from .edrpowerplay import EDRPowerplayUnknown
from edr.utils.edrutils import pretty_print_number
from edr.core.edri18n import _, _c
from edr.core.edrlog import EDR_LOG

class EDFineOrBounty:
    """
    Represents a fine or bounty.
    """
    def __init__(self, value, faction=None):
        """
        Initialize fine or bounty.

        Args:
            value (int): Amount in credits.
            faction (str, optional): Faction name.
        """
        self.value = value
        self.faction = faction
        config = EDR_CONFIG
        self.threshold = config.intel_bounty_threshold()

    def is_significant(self):
        """
        Returns:
            bool: True if value exceeds noteworthy threshold.
        """
        return self.value >= self.threshold

    def __repr__(self):
        return str(self.__dict__)

    def __iadd__(self, other):
        self.value += other
        return self

    def pretty_print(self):
        """
        Returns:
            str: Formatted numeric string (e.g. 10k).
        """
        return pretty_print_number(self.value)


class EDPilot:
    """
    Base class for a pilot (human or NPC).
    """
    def __init__(self, name, rank):
        """
        Initialize the pilot.

        Args:
            name (str): Pilot name.
            rank (int): Rank index (combat rank?).
        """
        now = EDTime.py_epoch_now()
        self._name = name
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.spacesuit = EDSuitFactory.unknown_suit()
        self.piloted_vehicle = self.mothership
        self.on_foot = False
        self.srv = None
        self.slf = None
        self.shuttle = None
        self.location = EDLocation()
        self.last_station = None
        self.powerplay = EDRPowerplayUnknown()
        self.squadron = None
        self.sqid = None
        self.destroyed = False
        self.wanted = False
        self.enemy = False
        self._bounty = None
        self._fine = None
        self.bounties = {}
        self.fines = {}
        self.targeted_vehicle = None
        self.timestamp = now
        self.rank = rank
        self.is_docked = False
        self.attitude = EDAttitude()

    def __repr__(self):
        return str(self.__dict__)

    def json(self):
        """
        Returns:
            dict: JSON representation of the pilot status.
        """
        blob = {
            "name": self.name,
            "timestamp": self.timestamp * 1000,
            "wanted": self.wanted,
            "bounty": self.bounty,
            "power": self.powerplay.canonicalize() if self.powerplay else '',
            "enemy": self.enemy,
        }

        if self.piloted_vehicle:
            blob["ship"] = self.piloted_vehicle.json()
        else:
            blob["suit"] = self.spacesuit.json()

        if self.sqid:
            blob["sqid"] = self.sqid
        return blob

    def is_human(self):
        """
        Returns:
            bool: True if human player (always False for base class).
        """
        return False

    def killed(self):
        """
        Handle pilot death event.
        """
        self._touch()
        self.destroyed = True
        self.wanted = False
        self._bounty = None
        self._fine = None
        self.bounties = {}
        self.fines = {}
        self.targeted_vehicle = None
        self.shuttle = None
        if self.mothership:
            self.mothership.destroy()
        if self.srv:
            self.srv.destroy()
        if self.slf:
            self.slf.destroy()
        if self.spacesuit:
            self.spacesuit.destroy()
        self.to_normal_space()
        self.is_docked = False
        self.on_foot = False

    def needs_large_landing_pad(self):
        """
        Returns:
            bool: True if mothership needs a large pad.
        """
        return self.mothership is None or self.mothership.needs_large_landing_pad()

    def needs_medium_landing_pad(self):
        """
        Returns:
            bool: True if mothership needs at least a medium pad.
        """
        return self.mothership is None or self.mothership.needs_medium_landing_pad()

    @property
    def vehicle(self):
        """
        Returns:
            EDVehicle: The active vehicle (ship or mothership), or None if on foot.
        """
        if self.on_foot:
            return None
        return self.piloted_vehicle or self.mothership

    def vehicle_type(self):
        """
        Returns:
            str: The type of the active vehicle.
        """
        if self.on_foot:
            return None
        vec_type = None
        if self.piloted_vehicle:
            vec_type = self.piloted_vehicle.type
        elif self.mothership:
            vec_type = self.mothership.type
        return vec_type

    def spacesuit_type(self):
        """
        Returns:
            str: The type of the spacesuit.
        """
        if not self.spacesuit:
            return None
        return self.spacesuit.type

    @property
    def name(self):
        return self._name

    @property
    def star_system(self):
        return self.location.star_system

    @star_system.setter
    def star_system(self, star_system):
        self._touch()
        self.location.star_system = star_system

    @property
    def star_system_address(self):
        return self.location.star_system_address

    @star_system_address.setter
    def star_system_address(self, star_system_address):
        self._touch()
        self.location.star_system_address = star_system_address

    @property
    def place(self):
        if self.location.place is None:
            return _c("For an unknown or missing place|Unknown")
        return self.location.place

    @place.setter
    def place(self, place):
        self._touch()
        self.location.place = place

    @property
    def body(self):
        if self.location.body is None:
            return _c("For an unknown or missing body|Unknown")
        return self.location.body

    @body.setter
    def body(self, body):
        self._touch()
        self.location.body = body

    def update_attitude(self, attitude):
        """
        Update pilot's attitude/coordinates.
        """
        self.attitude.update(attitude)

    def location_security(self, ed_security_state):
        """
        Update security state of current location.
        """
        self._touch()
        self.location.security = ed_security_state

    def in_bad_neighborhood(self):
        """
        Returns:
            bool: True if in Anarchy or Lawless system.
        """
        return self.location.is_anarchy_or_lawless()

    def in_supercruise(self):
        """
        Returns:
            bool: True if in supercruise.
        """
        return self.location.space_dimension == EDSpaceDimension.SUPER_SPACE

    def in_hyper_space(self):
        """
        Returns:
            bool: True if in hyperspace (jumping).
        """
        return self.location.space_dimension == EDSpaceDimension.HYPER_SPACE

    def in_normal_space(self):
        """
        Returns:
            bool: True if in normal space.
        """
        return self.location.space_dimension == EDSpaceDimension.NORMAL_SPACE

    def in_a_fight(self):
        """
        Returns:
            bool: True if currently in a fight.
        """
        if not self.in_normal_space():
            return False

        if self.mothership and self.mothership.in_a_fight() and self.mothership.in_danger():
            return True

        if self.slf and self.slf.in_a_fight() and self.slf.in_danger():
            return True

        if self.srv and self.srv.in_a_fight() and self.srv.in_danger():
            return True

        if self.on_foot and self.spacesuit:
            return self.spacesuit.in_a_fight() and self.spacesuit.in_danger() # fixed typo srv -> spacesuit

        return False

    def booked_shuttle(self, entry):
        """
        Record a shuttle booking.
        """
        if entry.get("event", None) == "BookTaxi":
            self.shuttle = EDVehicleFactory.apex_taxi(entry)
        elif entry.get("event", None) == "BookDropship":
            self.shuttle = EDVehicleFactory.frontlines_dropship(entry)

    def cancelled_shuttle(self, entry):
        """
        Cancel a shuttle booking.
        """
        self.shuttle = None

    def disembark(self, entry):
        """
        Handle disembark event.
        """
        if entry.get("event", None) != "Disembark":
            return

        self.in_spacesuit()
        if entry.get("ShipID", self.mothership.id) != self.mothership.id:
            EDR_LOG.debug("Player disembarked from their ship but the ID was different new:{} vs old:{}".format(entry["ShipID"], self.mothership.id))
            self.mothership = EDVehicleFactory.unknown_vehicle()
            self.mothership.id = entry["ShipID"]
        self.location.from_entry(entry)

    def embark(self, entry):
        """
        Handle embark event.
        """
        if entry.get("event", None) != "Embark":
            return

        if entry.get("SRV", False):
            self.in_srv()
        elif entry.get("Taxi", False):
            self.in_taxi()
        elif entry.get("Multicrew", False):
            self.mothership = EDVehicleFactory.unknown_crew_vehicle()
            self.in_mothership()
        else:
            if entry.get("ShipID", self.mothership.id) != self.mothership.id:
                EDR_LOG.debug("Player embarked on their ship but the ID was different new:{} vs old:{}".format(entry["ShipID"], self.mothership.id))
                self.mothership = EDVehicleFactory.unknown_vehicle()
                self.mothership.id = entry["ShipID"]
            self.in_mothership()
        self.location.from_entry(entry)

    def dropship_deployed(self, entry):
        """
        Handle dropship deployment.
        """
        if entry.get("event", None) != "DropshipDeploy":
            return

        self.in_spacesuit()
        self.location.from_entry(entry)

    def in_mothership(self):
        """
        Set status to in mothership.
        """
        self._touch()
        self.on_foot = False
        if not self.mothership:
            self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership

    def in_srv(self):
        """
        Set status to in SRV.
        """
        self._touch()
        self.is_docked = False
        self.on_foot = False
        if not self.mothership or not self.mothership.supports_srv():
            self.mothership = EDVehicleFactory.unknown_vehicle()
        if not self.srv:
            self.srv = EDVehicleFactory.default_srv()
        self.piloted_vehicle = self.srv

    def in_slf(self):
        """
        Set status to in SLF (fighter).
        """
        self._touch()
        self.on_foot = False
        if not self.mothership or not self.mothership.supports_slf():
            self.mothership = EDVehicleFactory.unknown_vehicle()
        if not self.slf:
            self.slf = EDVehicleFactory.unknown_slf()
        self.piloted_vehicle = self.slf

    def in_spacesuit(self):
        """
        Set status to on foot (spacesuit).
        """
        self._touch()
        self.on_foot = True
        self.piloted_vehicle = None

    def in_taxi(self):
        """
        Set status to in taxi.
        """
        self._touch()
        self.on_foot = False
        if not self.shuttle:
            EDR_LOG.debug("Player in a taxi but we had none")
            self.shuttle = EDVehicleFactory.unknown_taxi()
        self.piloted_vehicle = self.shuttle

    def docked(self, is_docked=True):
        """
        Set docked status.
        """
        self._touch()
        self.is_docked = is_docked
        if is_docked:
            self.on_foot = False
            self.mothership.safe()
            if self.slf:
                self.slf.safe()
            if self.srv:
                self.srv.safe()

    def docked_at(self, entry):
        """
        Handle docking at a station/carrier.
        """
        self.docked()
        from .edrfleetcarrier import EDRFleetCarrier  # Avoid circular import
        if entry.get("StationType", None) == "FleetCarrier":
            self.last_station = EDRFleetCarrier()
            self.last_station.update_from_location_or_docking(entry)
        else:
            self.last_station = None

    def hardpoints(self, deployed):
        """
        Update hardpoints status.
        """
        self._touch()
        if self.mothership:
            self.mothership.hardpoints(deployed)
        if self.slf:
            self.slf.hardpoints(deployed)
        if self.srv:
            self.srv.hardpoints(deployed)
        if self.spacesuit:
             self.spacesuit.hardpoints(deployed)

    def _touch(self):
        """
        Update timestamp of last activity.
        """
        self.timestamp = EDTime.py_epoch_now()

    def to_normal_space(self):
        """
        Set location to normal space.
        """
        self._touch()
        self.location.to_normal_space()

    def to_super_space(self):
        """
        Set location to supercruise.
        """
        self._touch()
        self.location.to_super_space()

    def to_hyper_space(self):
        """
        Set location to hyperspace.
        """
        self._touch()
        self.location.to_hyper_space()
