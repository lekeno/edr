import os
import pickle
from edr.utils.edrpickle import edr_load_pickle

from .edsitu import EDLocation, EDAttitude, EDSpaceDimension, EDDestination  # EDR_INTERNAL
from edr.utils.edtime import EDTime  # EDR_INTERNAL
from .edvehicles import EDVehicleFactory  # EDR_INTERNAL
from .edspacesuits import EDSuitFactory, EDOdysseyCloset  # EDR_INTERNAL
from .edcodex import EDCodex  # EDR_INTERNAL
from .edinstance import EDInstance  # EDR_INTERNAL
from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL
from edr.core.edrconfig import EDR_CONFIG  # EDR_INTERNAL
from edr.ui.edreconbox import EDReconBox  # EDR_INTERNAL
from .edrinventory import EDRInventory, EDRRemlokHelmet  # EDR_INTERNAL
from edr.core.edri18n import _, _c  # EDR_INTERNAL
from .edrfleet import EDRFleet  # EDR_INTERNAL
from .edrfleetcarrier import EDRFleetCarrier  # EDR_INTERNAL
from edr.controllers.edrminingstats import EDRMiningStats  # EDR_INTERNAL
from edr.controllers.edrbountyhuntingstats import EDRBountyHuntingStats  # EDR_INTERNAL
from .edengineers import EDEngineers  # EDR_INTERNAL
from edr.utils.edrpath import edr_cache_path  # EDR_INTERNAL
from edr.utils.edrutils import pretty_print_number  # EDR_INTERNAL
from edr.controllers.edrroutes import EDRNavigator  # EDR_INTERNAL


class EDRCrew:
    """
    Manages crew members for a pilot.
    """
    def __init__(self, captain):
        """
        Initialize the crew.

        Args:
            captain (str): The captain's name.
        """
        self.captain = captain
        self.creation = EDTime.py_epoch_now()
        self.members = {captain: self.creation}

    def add(self, crew_member):
        """
        Add a crew member.

        Args:
            crew_member (str): Name of the crew member.

        Returns:
            bool: True if added, False if already present.
        """
        if crew_member in self.members:
            return False
        self.members[crew_member] = EDTime.py_epoch_now()
        return True

    def remove(self, crew_member):
        """
        Remove a crew member.

        Args:
            crew_member (str): Name of the crew member.

        Returns:
            bool: True if removed, False if not found.
        """
        try:
            del self.members[crew_member]
            return True
        except KeyError:
            return False

    def all_members(self):
        """
        Get all crew members.

        Returns:
            list: List of crew member names.
        """
        return list(self.members.keys())

    def disband(self):
        """
        Disband the crew.
        """
        self.members = {}
        self.captain = None
        self.creation = None

    def is_captain(self, member):
        """
        Check if a member is the captain.

        Args:
            member (str): Member name.

        Returns:
            bool: True if captain.
        """
        return member == self.captain

    def duration(self, member):
        """
        Get duration of membership for a crew member.

        Args:
            member (str): Member name.

        Returns:
            int: Duration in seconds? (check EDTime units).
        """
        if member not in self.members:
            return 0
        now = EDTime.py_epoch_now()
        then = self.members[member]
        return now - then


class EDRSquadronMember:
    """
    Represents a squadron member info.
    """
    SOMEWHAT_TRUSTED_LEVEL = {"rank": "wingman", "level": 100}
    FULLY_TRUSTED_LEVEL = {"rank": "co-pilot", "level": 300}

    def __init__(self, squadron_dict):
        """
        Initialize based on squadron dictionary.

        Args:
            squadron_dict (dict): Squadron info.
        """
        self.name = squadron_dict.get("squadronName", None)
        self.inara_id = squadron_dict.get("squadronId", None)
        self.rank = squadron_dict.get("squadronRank", None)
        self.heartbeat = squadron_dict.get("heartbeat", None)
        self.level = squadron_dict.get("squadronLevel", None)

    def is_somewhat_trusted(self):
        """
        Returns:
            bool: True if somewhat trusted ranking.
        """
        return self.level >= EDRSquadronMember.SOMEWHAT_TRUSTED_LEVEL["level"]

    def is_fully_trusted(self):
        """
        Returns:
            bool: True if fully trusted ranking.
        """
        return self.level >= EDRSquadronMember.FULLY_TRUSTED_LEVEL["level"]

    def info(self):
        """
        Returns:
            dict: Squadron info dictionary.
        """
        return {
            "squadronName": self.name,
            "squadronId": self.inara_id,
            "squadronRank": self.rank,
            "squadronLevel": self.level
        }


class EDRPowerplay:
    """
    Manages powerplay affiliation and checks.
    """
    POWERS_AFFILIATION = {
        "a_lavigny-duval": "Empire",
        "arissa lavigny duval": "Empire",
        "aisling_duval": "Empire",
        "aisling duval": "Empire",
        "archon_delaine": None,
        "archon delaine": None,
        "denton_patreus": "Empire",
        "denton patreus": "Empire",
        "edmund_mahon": "Alliance",
        "edmund mahon": "Alliance",
        "felicia_winters": "Federation",
        "felicia winters": "Federation",
        "li_yong-rui": None,
        "li yong-rui": None,
        "pranav_antal": None,
        "pranav antal": None,
        "yuri_grom": None,
        "yuri grom": None,
        "zachary_hudson": "Federation",
        "zachary hudson": "Federation",
        "zemina_torval": "Empire",
        "zemina torval": "Empire",
        "nakato_kaine": "Alliance",
        "nakato kaine": "Alliance",
        "jerome_archer": "Federation",
        "jerome archer": "Federation",
    }

    POWERS_PRETTY_PRINT = {
        "a_lavigny-duval": "Lavigny",
        "aisling_duval": "Aisling",
        "archon_delaine": "Archon",
        "denton_patreus": "Patreus",
        "edmund_mahon": "Mahon",
        "felicia_winters": "Winters",
        "li_yong-rui": "Li Yong-rui",
        "pranav_antal": "Antal",
        "yuri_grom": "Yuri",
        "zachary_hudson": "Zachary",
        "zemina_torval": "Zemina",
        "nakato_kaine": "Nakato",
        "jerome_archer": "Jerome",
        "independent": "Independent",
        "unknown": "Unknown"
    }

    def __init__(self, pledged_to, time_pledged):
        """
        Initialize powerplay info.

        Args:
            pledged_to (str): Name of the power.
            time_pledged (int): Timestamp when pledged? or duration? (Assuming timestamp based on calc)
        """
        self.pledged_to = pledged_to
        self.since = EDTime.py_epoch_now() - time_pledged

    def is_enemy(self, power):
        """
        Check if another power is an enemy.

        Args:
            power (str): The other power's name.

        Returns:
            bool: True if enemy, False otherwise.
        """
        power = power.lower()
        if not (self.pledged_to in self.POWERS_AFFILIATION and power in self.POWERS_AFFILIATION):
            return False
        my_affiliation = self.POWERS_AFFILIATION[self.pledged_to]
        their_affiliation = self.POWERS_AFFILIATION[power]
        return my_affiliation != their_affiliation if my_affiliation else True

    def pretty_print(self):
        """
        Returns:
            str: Pretty printed power name.
        """
        if self.pledged_to in self.POWERS_PRETTY_PRINT:
            return self.POWERS_PRETTY_PRINT[self.pledged_to]
        return self.pledged_to

    def canonicalize(self):
        """
        Returns:
            str: Canonicalized power name (lowercase, snake_case).
        """
        if self.pledged_to:
            return self.pledged_to.lower().replace(" ", "_")
        else:
            return ""

    def time_pledged(self):
        """
        Returns:
            int: Duration pledged in seconds.
        """
        return EDTime.py_epoch_now() - self.since

    def is_somewhat_trusted(self):
        """
        Returns:
            bool: True if trusted (placeholder).
        """
        return False
        # TODO return true if enough time has passed (parameterize)

    def is_fully_trusted(self):
        """
        Returns:
            bool: True if fully trusted (placeholder).
        """
        return False
        # TODO return true if enough time has passed (parameterize)


class EDRPowerplayUnknown(EDRPowerplay):
    """
    Represents an unknown powerplay affiliation.
    """
    def __init__(self):
        """
        Initialize unknown powerplay.
        """
        super().__init__("Unknown", EDTime.py_epoch_now())

    def is_enemy(self, power):
        """
        Check if enemy (always False for distinct unknown).
        """
        return False

    def pretty_print(self):
        """
        Returns:
            str: 'Unknown'.
        """
        return "Unknown"

    def canonicalize(self):
        """
        Returns:
            str: 'unknown'.
        """
        return "unknown"

    def time_pledged(self):
        """
        Returns:
            int: 0.
        """
        return 0

    def is_somewhat_trusted(self):
        return False

    def is_fully_trusted(self):
        return False


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
        self.is_docked = False  # probably OK (assuming a proper event after resurrection)
        self.on_foot = False  # probably OK (assuming a proper event after resurrection)

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
            str: The type of the active vehicle (ship ID/Model).
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
            # Translators: this is used when a location, comprised of a system and a place (e.g. Alpha Centauri & Hutton Orbital), has no place specified
            return _c("For an unknown or missing place|Unknown")
        return self.location.place

    @place.setter
    def place(self, place):
        self._touch()
        self.location.place = place

    @property
    def body(self):
        if self.location.body is None:
            # Translators: this is used when a location, comprised of a system and a body (e.g. Alpha Centauri & 3 A), has no body specified
            return _c("For an unknown or missing body|Unknown")
        return self.location.body

    @body.setter
    def body(self, body):
        self._touch()
        self.location.body = body

    def update_attitude(self, attitude):
        """
        Update pilot's attitude/coordinates.

        Args:
            attitude (object): Attitude object (lat/long/heading).
        """
        self.attitude.update(attitude)

    def location_security(self, ed_security_state):
        """
        Update security state of current location.

        Args:
            ed_security_state (str): Security level.
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
            bool: True if currently in a fight (under attack).
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
            return self.spacesuit.in_a_fight() and self.srv.in_danger()

        return False

    def booked_shuttle(self, entry):
        """
        Record a shuttle booking.

        Args:
            entry (dict): Journal entry.
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

        Args:
            entry (dict): Journal entry.
        """
        if entry.get("event", None) != "Disembark":
            return

        self.in_spacesuit()
        if entry.get("ShipID", self.mothership.id) != self.mothership.id:
            EDR_LOG.debug("Player disembarked from their ship but the ID was different new:{} vs old:{}".format(entry["ShipID"], self.mothership.id))
            self.mothership = EDVehicleFactory.unknown_vehicle()
            self.mothership.id = entry["ShipID"]
        self.location.from_entry(entry)

        # TODO handle other info?
        '''
        SRV: true if getting out of SRV, false if getting out of a ship
        Taxi: true when getting out of a taxi transposrt ship
        Multicrew: true when getting out of another player’s vessel
        '''

    def embark(self, entry):
        """
        Handle embark event.

        Args:
            entry (dict): Journal entry.
        """
        if entry.get("event", None) != "Embark":
            return

        if entry.get("SRV", False):
            self.in_srv()
        elif entry.get("Taxi", False):
            self.in_taxi()
        elif entry.get("Multicrew", False):
            # TODO multicrew
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

        Args:
            entry (dict): Journal entry.
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

        Args:
            is_docked (bool): Docked state.
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

        Args:
            entry (dict): Journal entry.
        """
        self.docked()
        if entry.get("StationType", None) == "FleetCarrier":
            self.last_station = EDRFleetCarrier()
            self.last_station.update_from_location_or_docking(entry)
        else:
            self.last_station = None  # TODO

    def hardpoints(self, deployed):
        """
        Update hardpoints status.

        Args:
            deployed (bool): True if deployed.
        """
        self._touch()
        if self.piloted_vehicle:
            self.piloted_vehicle.hardpoints(deployed)


    def in_danger(self, danger=True):
        """
        Update danger status.

        Args:
            danger (bool): True if in danger.
        """
        self._touch()
        if not danger:
            if self.piloted_vehicle:
                self.piloted_vehicle.safe()
            else:
                self.spacesuit.safe()
        else:
            if self.piloted_vehicle:
                self.piloted_vehicle.unsafe()
            else:
                self.spacesuit.unsafe()

    def to_normal_space(self):
        """
        Transition to normal space.
        """
        self._touch()
        self.blue_tunnel = False
        self.location.space_dimension = EDSpaceDimension.NORMAL_SPACE
        self.mothership.safe()
        self.spacesuit.safe()
        self.targeted_vehicle = None
        self.on_foot = False
        if self.slf:
            self.slf.safe()
        if self.srv:
            self.srv.safe()

    def to_super_space(self):
        """
        Transition to supercruise.
        """
        self._touch()
        self.blue_tunnel = False
        self.location.space_dimension = EDSpaceDimension.SUPER_SPACE
        self.mothership.safe()
        self.spacesuit.safe()
        self.targeted_vehicle = None
        self.is_docked = False
        self.on_foot = False
        if self.slf:
            self.slf.safe()
        if self.srv:
            self.srv.safe()

    def to_hyper_space(self):
        """
        Transition to hyperspace (jump).
        """
        self._touch()
        self.blue_tunnel = True
        self.location.space_dimension = EDSpaceDimension.HYPER_SPACE
        self.planetary_destination = None  # leaving the system, so no point in keep a planetary destination
        self.mothership.safe()
        self.spacesuit.safe()
        self.targeted_vehicle = None
        self.is_docked = False
        self.on_foot = False
        if self.slf:
            self.slf.safe()
        if self.srv:
            self.srv.safe()

    def targeted(self, mothership=True, slf=False, srv=False):
        """
        Handle being targeted.

        Args:
            mothership (bool): Targeted in mothership.
            slf (bool): Targeted in SLF.
            srv (bool): Targeted in SRV.
        """
        if mothership:
            self.targeted_vehicle = self.mothership
        elif slf:
            self.targeted_vehicle = self.slf
        elif srv:
            self.targeted_vehicle = self.srv
        else:
            self.targeted_vehicle = None
        self._touch()

    def untargeted(self):
        """
        Clear targeted status.
        """
        self.targeted_vehicle = None
        self._touch()

    def is_targeted(self):
        """
        Returns:
            bool: True if targeted.
        """
        return self.targeted_vehicle is not None

    @property
    def bounty(self):
        if self._bounty:
            return self._bounty.value
        return 0

    @bounty.setter
    def bounty(self, credits):
        self._touch()
        if credits:
            self._bounty = EDFineOrBounty(credits)
        else:
            self._bounty = None

    # TODO should be moved to the ship....
    def add_bounty(self, credits, faction):
        """
        Add a bounty from a faction.

        Args:
            credits (int): Amount.
            faction (str): Faction name.
        """
        self._touch()
        self.bounties[faction] = self.bounties.get(faction, 0) + credits

    def add_fine(self, credits, faction):
        """
        Add a fine from a faction.

        Args:
            credits (int): Amount.
            faction (str): Faction name.
        """
        self._touch()
        self.fines[faction] = self.fines.get(faction, 0) + credits

    def paid_all_bounties(self):
        """
        Clear all bounties.
        """
        self._touch()
        self.bounties = {}
        self.bounty = 0

    def paid_fine(self, entry):
        """
        Record payment of a fine.

        Args:
            entry (dict): Journal entry.
        """
        true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0) / 100.0)
        self.fine = max(0, self.fine - true_amount)

    def paid_bounty(self, entry):
        """
        Record payment of a bounty.

        Args:
            entry (dict): Journal entry.
        """
        true_amount = entry["Amount"] * (1.0 - entry.get("BrokerPercentage", 0) / 100.0)
        self.bounty = max(0, self.bounty - true_amount)
        if "Faction" in entry:
            self.bounties[entry["Faction"]] = max(0, self.bounties.get(entry["Faction"], true_amount) - true_amount)

    def is_wanted_by_faction(self, faction):
        """
        Check if wanted by a specific faction.

        Args:
            faction (str): Faction name.

        Returns:
            bool: True if wanted.
        """
        return self.bounties.get(faction, 0) > 0

    def paid_all_fines(self):
        """
        Clear all fines.
        """
        self._touch()
        self.fines = {}
        self.fine = 0

    @property
    def fine(self):
        if self._fine:
            return self._fine.value
        return 0

    @fine.setter
    def fine(self, credits):
        self._touch()
        if credits:
            self._fine = EDFineOrBounty(credits)
        else:
            self._fine = None

    @property
    def power(self):
        if self.is_independent():
            return None
        return self.powerplay.pledged_to

    @property
    def time_pledged(self):
        if self.is_independent():
            return None
        return self.powerplay.time_pledged()

    def pledged_to(self, power, time_pledged=0):
        """
        Update pledge status.

        Args:
            power (str): Power name.
            time_pledged (int): Timestamp or duration.
        """
        self._touch()
        if power is None:
            self.powerplay = None
        else:
            self.powerplay = EDRPowerplay(power, time_pledged)

    def pledged_since(self):
        """
        Returns:
            int: Timestamp of pledge start?
        """
        if self.is_independent():
            return None
        return self.powerplay.since

    def squadron_member(self, squadron_dict):
        """
        Update squadron membership.

        Args:
            squadron_dict (dict): Squadron info.
        """
        self.squadron = EDRSquadronMember(squadron_dict)

    def lone_wolf(self):
        """
        Leave squadron (become lone wolf).
        """
        self.squadron = None

    def squadron_info(self):
        """
        Returns:
            dict: Squadron info or None.
        """
        if self.is_lone_wolf():
            return None
        return self.squadron.info()

    def is_independent(self):
        """
        Returns:
            bool: True if not pledged to a power.
        """
        return self.powerplay is None

    def is_lone_wolf(self):
        """
        Returns:
            bool: True if not in a squadron.
        """
        return self.squadron is None

    def has_partial_status(self):
        """
        Returns:
            bool: True if status is incomplete (missing location/ship info).
        """
        EDR_LOG.debug(f"status: {self.mothership} {self.location.star_system} {self.location.place}")
        return self.mothership is None or self.location.star_system is None or self.location.place is None

    def update_suit_if_obsolete(self, entry):
        """
        Update suit info if outdated.

        Args:
            entry (dict): Journal entry.

        Returns:
            bool: True if updated.
        """
        if "event" not in entry or entry["event"] not in ["SuitLoadout", "SwitchSuitLoadout"]:
            return False

        if entry["event"] in ["SwitchSuitLoadout", "SuitLoadout"]:
            # note: game says that the backpack content is cleared, nothing about organic data
            return self.__update_suit_if_obsolete(entry)
        return False

    def __update_suit_if_obsolete(self, entry):
        self.in_spacesuit()
        self.spacesuit = self.closet.switch_suit_loadout(entry)
        self._touch()
        return True

    def update_vehicle_or_suit_if_obsolete(self, entry):
        """
        Update vehicle or suit if outdated.

        Args:
            entry (dict): Journal entry.

        Returns:
            bool: True if updated.
        """
        if entry.get("event", None) in ["LoadGame", "Loadout"]:
            so_called_ship = entry.get("Ship", None)
            if not so_called_ship:
                return False

            if EDSuitFactory.is_spacesuit(so_called_ship):
                return self.__update_suit_if_obsolete(entry)
            else:
                return self.update_vehicle_if_obsolete(EDVehicleFactory.from_loadgame_or_loadout_event(entry))
        return False

    def update_vehicle_if_obsolete(self, vehicle, piloted=True):
        """
        Update vehicle if outdated.

        Args:
            vehicle (EDVehicle): New vehicle info.
            piloted (bool): If the vehicle is currently piloted.

        Returns:
            bool: True if updated.
        """
        if vehicle is None:
            return False
        updated = False
        if EDVehicleFactory.is_ship_launched_fighter(vehicle):
            updated = self.__update_slf_if_obsolete(vehicle)
            if not self.mothership.supports_slf():
                self.mothership = EDVehicleFactory.unknown_vehicle()
            if piloted:
                self.piloted_vehicle = self.slf
        elif EDVehicleFactory.is_surface_vehicle(vehicle):
            updated = self.__update_srv_if_obsolete(vehicle)
            if not self.mothership.supports_srv():
                self.mothership = EDVehicleFactory.unknown_vehicle()
            if piloted:
                self.piloted_vehicle = self.srv
        else:
            updated = self.__update_mothership_if_obsolete(vehicle)
            if piloted:
                self.piloted_vehicle = self.mothership
        if updated:
            self._touch()
        return updated

    def __update_mothership_if_obsolete(self, vehicle):
        if self.mothership is None or self.mothership.type != vehicle.type:
            self.mothership = vehicle
            return True
        return False

    def __update_slf_if_obsolete(self, vehicle):
        if self.slf is None or self.slf.type != vehicle.type:
            self.slf = vehicle
            return True
        return False

    def __update_srv_if_obsolete(self, vehicle):
        if self.srv is None or self.srv.type != vehicle.type:
            self.srv = vehicle
            return True
        return False

    def update_star_system_if_obsolete(self, star_system, system_address=None):
        """
        Update star system if outdated.

        Args:
            star_system (str): System name.
            system_address (int): System address.

        Returns:
            bool: True if updated.
        """
        self._touch()
        if system_address:
            self.location.star_system_address = system_address
        if star_system and (self.location.star_system is None or self.location.star_system != star_system):
            EDR_LOG.info("Updating system info (was missing or obsolete). {old} vs. {system}".format(old=self.location.star_system, system=star_system))
            self.location.star_system = star_system
            return True
        return False

    def update_place_if_obsolete(self, place):
        """
        Update place (station/body) if outdated.

        Args:
            place (str): Place name.

        Returns:
            bool: True if updated.
        """
        self._touch()
        if self.location.place is None or self.location.place != place:
            EDR_LOG.info("Updating place info (was missing or obsolete). {old} vs. {place}".format(old=self.location.place, place=place))
            self.location.place = place
            return True
        return False

    def update_body_if_obsolete(self, body):
        """
        Update body if outdated.

        Args:
            body (str): Body name.

        Returns:
            bool: True if updated.
        """
        self._touch()
        if self.location.body is None or self.location.body != body:
            EDR_LOG.info("Updating body info (was missing or obsolete). {old} vs. {body}".format(old=self.location.body, body=body))
            self.location.body = body
            return True
        return False

    def _touch(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now


class EDPlayer(EDPilot):
    """
    Represents a player (Commander).
    """
    def __init__(self, name, rank=None):
        """
        Initialize the player.

        Args:
            name (str): Commander name.
            rank (int, optional): Rank.
        """
        super().__init__(name, rank)
        self.blue_tunnel = False

    def json(self):
        """
        Returns:
            dict: JSON representation of player.
        """
        blob = {
            "cmdr": self.name,
            "timestamp": self.timestamp * 1000,
            "wanted": self.wanted,
            "bounty": self.bounty,
            "power": self.powerplay.canonicalize() if self.powerplay else '',
            "enemy": self.enemy
        }

        if (self.piloted_vehicle):
            blob["ship"] = self.piloted_vehicle.json()
        else:
            blob["spacesuit"] = self.spacesuit.json()

        if self.sqid:
            blob["sqid"] = self.sqid
        return blob

    def is_human(self):
        """
        Returns:
            bool: True (always human).
        """
        return True

    def to_normal_space(self):
        """
        Transition to normal space.
        """
        self.blue_tunnel = False
        super(EDPlayer, self).to_normal_space()

    def to_super_space(self):
        """
        Transition to supercruise.
        """
        self.blue_tunnel = False
        super(EDPlayer, self).to_super_space()

    def to_hyper_space(self):
        """
        Transition to hyperspace.
        """
        self.blue_tunnel = True
        super(EDPlayer, self).to_hyper_space()

    def in_blue_tunnel(self, tunnel=True):
        """
        Update blue tunnel status (hyperspace tunnel).

        Args:
            tunnel (bool): True if in tunnel.
        """
        if tunnel != self.blue_tunnel:
            EDR_LOG.debug("Blue Tunnel update: {old} vs. {new}".format(old=self.blue_tunnel, new=tunnel))
        self.blue_tunnel = tunnel

    def is_trusted_by_squadron(self):
        """
        Returns:
            bool: True if trusted by squadron.
        """
        if self.is_lone_wolf():
            return False
        return self.squadron.is_somewhat_trusted()

    def squadron_trusted_rank(self):
        """
        Returns:
            str: Rank required for trust.
        """
        return EDRSquadronMember.SOMEWHAT_TRUSTED_LEVEL["rank"]

    def squadron_empowered_rank(self):
        """
        Returns:
            str: Rank required for empowerment.
        """
        return EDRSquadronMember.FULLY_TRUSTED_LEVEL["rank"]

    def is_empowered_by_squadron(self):
        """
        Returns:
            bool: True if empowered by squadron.
        """
        if self.is_lone_wolf():
            return False
        return self.squadron.is_fully_trusted()

    def is_trusted_by_power(self):
        """
        Returns:
            bool: True if trusted by power.
        """
        if self.is_independent():
            return False
        return self.powerplay.is_somewhat_trusted()

    def is_empowered_by_power(self):
        """
        Returns:
            bool: True if empowered by power (or independent).
        """
        if self.is_independent():
            return True
        return self.powerplay.is_fully_trusted()


class EDWing:
    """
    Manages wingmates (team).
    """
    def __init__(self, wingmates=set()):
        """
        Initialize wing.

        Args:
            wingmates (set): Set of wingmate names.
        """
        self.wingmates = wingmates.copy()
        self.timestamp = None
        self.last_check_timestamp = None
        self._touched = False

    def leave(self):
        """
        Leave the wing.
        """
        self.wingmates = set()
        self._touch()

    def join(self, others):
        """
        Join a wing.

        Args:
            others (list): List of wingmate names.
        """
        self.wingmates = set(others)
        self._touch()

    def add(self, other):
        """
        Add a wingmate.

        Args:
            other (str): Name of wingmate.
        """
        self.wingmates.add(other)
        self._touch()

    def formed(self):
        """
        Returns:
            bool: True if wing is formed.
        """
        return len(self.wingmates) > 0

    def _touch(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._touched = True

    def noteworthy_changes_json(self, instance):
        """
        Get JSON of noteworthy changes in wing status.

        Args:
            instance (EDInstance): Current instance info.

        Returns:
            list: List of changes.
        """
        changes = []
        if not self._touched:
            for wingmate in self.wingmates:
                if instance.player(wingmate) is None:
                    continue
                timestamp, _ = instance.blip(wingmate).values()
                if self.last_check_timestamp is None or timestamp >= self.last_check_timestamp:
                    changes.append({"cmdr": wingmate, "instanced": True})
        elif self.last_check_timestamp is None or self.timestamp is None or self.timestamp >= self.last_check_timestamp:
            changes = [{"cmdr": wingmate, "instanced": instance.player(wingmate) is not None} for wingmate in self.wingmates]
        self._touched = False
        now = EDTime.py_epoch_now()
        self.last_check_timestamp = now
        return changes

class EDPlayerOne(EDPlayer):
    """
    Represents the main player (the user).
    """
    EDR_FLEET_CARRIER_CACHE = edr_cache_path(os.path.join('fleet_carrier.v3.p'))

    def __init__(self, name=None):
        """
        Initialize the main player.

        Args:
            name (str, optional): Player name.
        """
        super(EDPlayerOne, self).__init__(name)
        self.powerplay = None
        self.game_mode = None
        self.dlc_name = None
        self.private_group = None
        self.in_game = False
        self.previous_mode = None
        self.previous_private_group = None
        self.previous_wing = set()
        self.from_genesis = False
        self.wing = EDWing()
        self.friends = set()
        self.crew = None
        self._target = None
        self.instance = EDInstance()
        self.planetary_destination = None
        self.recon_box = EDReconBox()
        self.inventory = EDRInventory()
        self.closet = EDOdysseyCloset()
        self.codex = EDCodex()
        self.fleet = EDRFleet()
        try:
            with open(self.EDR_FLEET_CARRIER_CACHE, 'rb') as handle:
                self.fleet_carrier = edr_load_pickle(handle)
        except (IOError, EOFError, pickle.PickleError):
            self.fleet_carrier = EDRFleetCarrier()
        self.mining_stats = EDRMiningStats()
        self.bounty_hunting_stats = EDRBountyHuntingStats()
        self.engineers = EDEngineers()
        self.destination = EDDestination()
        self.remlok_helmet = EDRRemlokHelmet()
        self.routenav = EDRNavigator()

    def __repr__(self):
        return str(self.__dict__)

    def persist(self):
        """
        Save player state to cache/disk.
        """
        self.inventory.persist()
        with open(self.EDR_FLEET_CARRIER_CACHE, 'wb') as handle:
            pickle.dump(self.fleet_carrier, handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.routenav.persist()

    def target_pilot(self):
        """
        Returns:
            EDPilot: The currently targeted pilot.
        """
        return self._target

    def target_vehicle(self):
        """
        Returns:
            EDVehicle: The vehicle of the targeted pilot.
        """
        if not self._target:
            return None
        return self._target.targeted_vehicle

    def targeting(self, pilot, ship_internal_name=None):
        """
        Set the target to a pilot.

        Args:
            pilot (EDPilot): The pilot to target.
            ship_internal_name (str, optional): Internal ship name of target.
        """
        if pilot.is_human():
            self.instance.player_in(pilot)
        else:
            self.instance.npc_in(pilot)

        if self._target:
            self._target.untargeted()
            self._target._touch()
        self._target = pilot

        mothership = True
        slf = False
        srv = False
        if ship_internal_name:
            vehicle = EDVehicleFactory.from_internal_name(ship_internal_name)
            slf = EDVehicleFactory.is_ship_launched_fighter(vehicle)
            srv = EDVehicleFactory.is_surface_vehicle(vehicle)
            mothership = not (slf or srv)

        pilot.targeted(mothership, slf, srv)
        pilot._touch()
        self._touch()

    def untarget(self):
        """
        Clear the current target.
        """
        if self._target:
            self._target.untargeted()
            self._target._touch()
        self._target = None
        self._touch()

    def set_destination(self, destination):
        """
        Set navigation destination.

        Args:
            destination (str/dict): Destination info.

        Returns:
            bool: True if updated.
        """
        return self.destination.update(destination)

    def has_destination(self):
        """
        Returns:
            bool: True if a destination is set.
        """
        return self.destination.is_valid()

    def lowish_fuel(self):
        """
        Returns:
            bool: True if fuel is low (<= 30%).
        """
        if self.mothership.fuel_level is None or self.mothership.fuel_capacity is None:
            return True  # Better safe than sorry
        return (self.mothership.fuel_level / self.mothership.fuel_capacity) <= 0.3

    def heavily_damaged(self):
        """
        Returns:
            bool: True if hull health is low (<= 50%).
        """
        if self.mothership.hull_health is None:
            return True  # Better safe than sorry
        return self.mothership.hull_health <= 50

    def json(self, fuel_info=False, with_target=False):
        """
        Get JSON representation of player state.

        Args:
            fuel_info (bool): Include fuel info.
            with_target (bool): Include target info.

        Returns:
            dict: JSON blob.
        """
        result = {
            "cmdr": self.name,
            "timestamp": self.timestamp * 1000,
            "wanted": self.wanted,
            "bounty": self.bounty,
            "starSystem": self.star_system,
            "place": self.place,
            "wingof": len(self.wing.wingmates),
            "wing": self.wing.noteworthy_changes_json(self.instance),
            "byPledge": self.powerplay.canonicalize() if self.powerplay else '',
            "mode": self.game_mode,
            "dlc": self.dlc_name,
            "group": self.private_group
        }

        if (self.piloted_vehicle):
            result["ship"] = self.piloted_vehicle.json(fuel_info=fuel_info)
        else:
            result["spacesuit"] = self.spacesuit.json()

        if with_target:
            result["target"] = self.target_pilot().json() if self._target else {}

        result["crew"] = []
        if self.crew:
            result["crew"] = [{"cmdr": crew_member} for crew_member in self.crew.all_members()]

        return result
   
    def force_new_name(self, new_name):
        """
        Force a name change (e.g. if detected differently).

        Args:
            new_name (str): New name.
        """
        self._name = new_name

    def in_solo_or_private(self):
        """
        Returns:
            bool: True if in Solo or Private Group.
        """
        return self.game_mode in ["Solo", "Group"]

    def in_solo(self):
        """
        Returns:
            bool: True if in Solo.
        """
        return self.game_mode == "Solo"

    def in_open(self):
        """
        Returns:
            bool: True if in Open.
        """
        return self.game_mode == "Open"

    def inception(self, genesis=False):
        """
        Initialize/Reset player state at game start.

        Args:
            genesis (bool): True if fresh start (app launch).
        """
        if genesis:
            self.from_genesis = True
        self.in_game = True
        self.previous_mode = None
        self.previous_wing = set()
        self.wing = EDWing()
        self.crew = None
        self.destroyed = False
        self.untarget()
        self.wanted = False
        self.shuttle = None
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.targeted_vehicle = None
        self.srv = None
        self.slf = None
        self.location = EDLocation()
        self._bounty = None
        self.bounties = {}
        self.fines = {}
        self.instance.reset()
        self.to_normal_space()
        self._touch()
        self.reset_stats()

    def killed(self):
        """
        Handle player death.
        """
        super(EDPlayerOne, self).killed()
        self.in_game = False
        self.previous_mode = self.game_mode
        self.previous_private_group = self.private_group
        self.previous_wing = self.wing.wingmates.copy()
        self.game_mode = None
        self.private_group = None
        self.wing = EDWing()
        self.crew = None
        self.shuttle = None
        self.untarget()
        self.instance.reset()
        self.recon_box.reset()
        self._touch()

    def resurrect(self, rebought=True):
        """
        Handle player resurrection.

        Args:
            rebought (bool): True if user rebought their ship.
        """
        self.in_game = True
        self.game_mode = self.previous_mode
        self.private_group = self.previous_private_group
        self.wing = EDWing(self.previous_wing)
        self.previous_mode = None
        self.previous_wing = set()
        self.destroyed = False
        self.untarget()
        self.to_normal_space()
        self.instance.reset()
        self._touch()
        if rebought:
            self.mothership.reset()
            self.spacesuit.reset()
            if self.slf:
                self.slf.reset()
            if self.srv:
                self.srv.reset()
        else:
            self.mothership = EDVehicleFactory.unknown_vehicle()
            self.piloted_vehicle = self.mothership
            self.spacesuit = EDSuitFactory.unknown_suit()
            self.slf = None
            self.srv = None

    def is_crew_member(self):
        """
        Returns:
            bool: True if being a crew member (not captain).
        """
        if not self.crew:
            return False
        return self.crew.captain != self.name

    def in_a_crew(self):
        """
        Returns:
            bool: True if in a multicrew session.
        """
        return self.crew is not None

    def leave_wing(self):
        """
        Leave the current wing.
        """
        self.wing.leave()
        self._touch()

    def join_wing(self, others):
        """
        Join a wing with others.

        Args:
            others (list): List of wingmate names.
        """
        self.wing.join(others)
        self.crew = None
        self._touch()

    def add_to_wing(self, other):
        """
        Add a pilot to the wing.

        Args:
            other (str): Name of pilot.
        """
        self.wing.add(other)
        self._touch()

    def in_a_wing(self):
        """
        Returns:
            bool: True if in a wing.
        """
        return self.wing.formed()

    def leave_crew(self):
        """
        Leave the multicrew session.
        """
        self._touch()
        if not self.crew:
            return
        self.crew = None
        self.instance.reset()

    def disband_crew(self):
        """
        Disband the multicrew session.
        """
        self._touch()
        if not self.crew:
            return
        for member in self.crew.members:
            self.instance.player_out(member)
        self.crew.disband()

    def join_crew(self, captain):
        """
        Join a multicrew session.

        Args:
            captain (str): Captain's name.
        """
        self.wing = EDWing()
        self.instance.reset()
        self.crew = EDRCrew(captain)
        self.crew.add(self.name)
        self.instanced_player(captain)
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.slf = None
        self.srv = None
        self.location = EDLocation()
        self._touch()

    def add_to_crew(self, member):
        """
        Add a member to the crew.

        Args:
            member (str): Member name.

        Returns:
            bool: Success status.
        """
        self._touch()
        if not self.crew:
            self.crew = EDRCrew(self.name)
            self.wing = EDWing()
            self.instance.reset()
        self.instanced_player(member)
        return self.crew.add(member)

    def remove_from_crew(self, member):
        """
        Remove a member from the crew.

        Args:
            member (str): Member name.

        Returns:
            bool: Success status.
        """
        self._touch()
        if not self.crew:
            self.crew = EDRCrew(self.name)
            self.wing = EDWing()
            self.instance.reset()
        self.instance.player_out(member)
        return self.crew.remove(member)

    def crew_time_elapsed(self, member):
        """
        Get time elapsed since member joined crew.

        Args:
            member (str): Member name.

        Returns:
            int: Duration in seconds.
        """
        if not self.crew:
            return 0
        return self.crew.duration(member)

    def is_captain(self, member=None):
        """
        Check if self (or member) is captain.

        Args:
            member (str, optional): Member to check. Defaults to self.

        Returns:
            bool: True if captain.
        """
        if not self.crew:
            return False
        if not member:
            member = self.name
        return self.crew.is_captain(member)

    def is_friend(self, cmdr_name):
        """
        Check if a commander is a friend.
        """
        return cmdr_name in self.friends

    def is_wingmate(self, cmdr_name):
        """
        Check if a commander is a wingmate.
        """
        return cmdr_name in self.wing.wingmates

    def is_crewmate(self, cmdr_name):
        """
        Check if a commander is a crewmate.
        """
        if not self.crew:
            return False
        return cmdr_name in self.crew.all_members()

    def is_enemy_with(self, power):
        """
        Check if enemy with a power.
        """
        if self.is_independent() or not power:
            return False
        return self.powerplay.is_enemy(power)

    def to_normal_space(self):
        """
        Transition to normal space (with instance reset).
        """
        if self.in_normal_space():
            return
        super(EDPlayerOne, self).to_normal_space()
        self.instance.reset()

    def to_super_space(self):
        """
        Transition to supercruise (with instance reset).
        """
        if self.in_supercruise():
            return
        super(EDPlayerOne, self).to_super_space()
        self.instance.reset()
        self.recon_box.reset()

    def to_hyper_space(self):
        """
        Transition to hyperspace (with instance reset).
        """
        if self.in_hyper_space():
            return
        super(EDPlayerOne, self).to_hyper_space()
        self.instance.reset()
        self.recon_box.reset()

    def wing_and_crew(self):
        """
        Get all wing and crew members.

        Returns:
            set: Set of names.
        """
        wing_and_crew = self.wing.wingmates.copy()
        if self.crew:
            wing_and_crew.update(self.crew.all_members())
        return wing_and_crew

    def maybe_in_a_pvp_fight(self):
        """
        Check if likely in a PvP fight.

        Returns:
            bool: True if conditions suggest PvP.
        """
        if not self.in_a_fight():
            return False

        if self.instance.is_void_of_player():
            # Can't PvP if there is no other player.
            return False

        if not self.instance.any_player_beside(self.wing_and_crew()):
            return False

        return True

    def leave_vehicle(self):
        """
        Leave current vehicle (e.g. to SRV or on foot?).
        Wait, this sets mothership to unknown.
        """
        self.mothership = EDVehicleFactory.unknown_vehicle()
        self.piloted_vehicle = self.mothership
        self.slf = None
        self.srv = None
        self.instance.reset()
        self.recon_box.reset()
        self._touch()

    def destroy(self, cmdr):
        """
        Record that this player destroyed another commander.

        Args:
            cmdr (EDPilot): The destroyed commander.
        """
        self._touch()
        cmdr.killed()
        self.instance.player_out(cmdr.name)
        if self.target_pilot() and self.target_pilot().name == cmdr.name:
            self.untarget()

    def interdiction(self, interdicted, success):
        """
        Handle interdiction initiated by player.

        Args:
            interdicted (EDPilot): The target.
            success (bool): Result.
        """
        self._touch()
        self.to_normal_space()
        if success and interdicted:
            interdicted.location.from_other(self.location)
            if interdicted.is_human():
                self.instance.player_in(interdicted)
            else:
                self.instance.npc_in(interdicted)
        else:
            self.recon_box.reset()

    def interdicted(self, interdictor, success):
        """
        Handle being interdicted.

        Args:
            interdictor (EDPilot): The interdictor.
            success (bool): Result.
        """
        self._touch()
        if success:
            self.to_normal_space()
            if interdictor:
                interdictor.location.from_other(self.location)
                if interdictor.is_human():
                    self.instance.player_in(interdictor)
                else:
                    self.instance.npc_in(interdictor)
        else:
            if interdictor:
                if interdictor.is_human():
                    self.instance.player_out(interdictor.name)
                else:
                    self.instance.npc_out(interdictor.name)
            self.recon_box.reset()

    def is_instanced_with_player(self, cmdr_name):
        """
        Check if instanced with a specific commander.
        """
        return self.instance.player(cmdr_name) is not None

    def instanced_player(self, cmdr_name, rank=None, ship_internal_name=None, piloted=True):
        """
        Register a player in the current instance.

        Args:
            cmdr_name (str): Commander name.
            rank (int, optional): Rank.
            ship_internal_name (str, optional): Ship type.
            piloted (bool): If piloted.

        Returns:
            EDPlayer: The player object.
        """
        self._touch()
        cmdr = self.instance.player(cmdr_name)
        if not cmdr:
            cmdr = EDPlayer(cmdr_name, rank)
        cmdr.location.from_other(self.location)
        if ship_internal_name:
            if EDSuitFactory.is_spacesuit(ship_internal_name):
                suit = EDSuitFactory.from_internal_name(ship_internal_name)
                cmdr.spacesuit = suit
                cmdr.in_spacesuit()
            else:
                vehicle = EDVehicleFactory.from_internal_name(ship_internal_name)
                cmdr.update_vehicle_if_obsolete(vehicle, piloted)
        self.instance.player_in(cmdr)
        return cmdr

    def deinstanced_player(self, cmdr_name):
        """
        Remove player from instance.
        """
        self._touch()
        self.instance.player_out(cmdr_name)

    def instanced_npc(self, name, rank=None, ship_internal_name=None, piloted=True):
        """
        Register an NPC in the current instance.

        Returns:
            EDPilot: The NPC object.
        """
        self._touch()
        npc = self.instance.npc(name, rank, ship_internal_name)
        if not npc:
            npc = EDPilot(name, rank)
        npc.location.from_other(self.location)
        if ship_internal_name:
            vehicle = EDVehicleFactory.from_internal_name(ship_internal_name)
            npc.update_vehicle_if_obsolete(vehicle, piloted)
        self.instance.npc_in(npc)
        return npc

    def attacked(self, target):
        """
        Handle being attacked.

        Args:
            target (str): What was attacked ('Mothership', 'Fighter', 'You', 'SRV').
        """
        self._touch()
        if target == "Mothership":
            self.mothership.attacked()
        elif target == "Fighter":
            if self.slf:
                self.slf.attacked()
            else:
                EDR_LOG.warning("SLF attacked but player had none")
        elif target == "You":
            if self.on_foot:
                self.spacesuit.attacked()
            else:
                self.piloted_vehicle.attacked()
        elif target == "SRV":
            if self.srv:
                self.srv.attacked()
            else:
                EDR_LOG.warning("SRV attacked but player had none")
        else:
            EDR_LOG.warning(f"Unrecognized target: {target}")


    def pips(self, values):
        """
        Update power distributor pips.

        Args:
            values (list): Pips configuration.

        Returns:
            bool: Success status.
        """
        if self.vehicle:
            return self.vehicle.pips(values)
        return False

    def update_fleet(self, stored_ships_entry):
        """
        Update fleet information from journal.

        Args:
            stored_ships_entry (dict): StoredShips event.
        """
        self.fleet.update(stored_ships_entry)

    def prospected(self, entry):
        """
        Record prospecting event.

        Args:
            entry (dict): Journal entry.
        """
        self.mining_stats.prospected(entry)

    def refined(self, entry):
        """
        Record refining event.

        Args:
            entry (dict): Journal entry.
        """
        self.mining_stats.refined(entry)

    def bounty_scanned(self, entry):
        """
        Record bounty scan.

        Args:
            entry (dict): Journal entry.
        """
        self.bounty_hunting_stats.scanned(entry)

    def bounty_awarded(self, entry):
        """
        Record bounty awarded.

        Args:
            entry (dict): Journal entry.
        """
        self.bounty_hunting_stats.awarded(entry)

    def reset_stats(self):
        """
        Reset session stats (mining, bounty hunting).
        """
        self.mining_stats.reset()
        self.bounty_hunting_stats.reset()

    def describe_item(self, internal_name):
        """
        Get description of an item.

        Args:
            internal_name (str): Internal name of item.

        Returns:
            str: Description.
        """
        return self.remlok_helmet.describe_item(internal_name, self.inventory)

    def describe_odyssey_material_short(self, internal_name, ignore_eng_unlocks=False):
        """
        Get short description of Odyssey material.

        Args:
            internal_name (str): Internal name.
            ignore_eng_unlocks (bool): Whether to ignore engineer unlocks.

        Returns:
            str: Short description.
        """
        return self.remlok_helmet.describe_odyssey_material_short(internal_name, self.inventory, ignore_eng_unlocks)

    def process_organic_scan(self, scan_event):
        """
        Process organic scan event.

        Args:
            scan_event (dict): Journal entry.
        """
        self.closet.genetic_sampler.process(scan_event, self.attitude)
        self.codex.process(scan_event)

    def tracking_organic(self):
        """
        Returns:
            bool: True if tracking an organic scan.
        """
        return self.closet.genetic_sampler.is_tracking()