import os
import pickle
from .edplayer import EDPlayer
from .edwing import EDWing
from .edrcrew import EDRCrew
from .edinstance import EDInstance
from edr.ui.edreconbox import EDReconBox
from .edrinventory import EDRInventory, EDRRemlokHelmet
from .edspacesuits import EDOdysseyCloset
from .edcodex import EDCodex
from .edrfleet import EDRFleet
from .edrfleetcarrier import EDRFleetCarrier
from edr.controllers.edrminingstats import EDRMiningStats
from edr.controllers.edrbountyhuntingstats import EDRBountyHuntingStats
from .edengineers import EDEngineers
from .edsitu import EDDestination
from edr.controllers.edrroutes import EDRNavigator
from edr.utils.edrpath import edr_cache_path
from edr.utils.edrpickle import edr_load_pickle
from .edvehicles import EDVehicleFactory

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
        return self._target.vehicle

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

    def inception(self):
        """
        Record the start of a game session.
        """
        self.in_game = True
        self._touch()

    def killed(self):
        """
        Handle player death.
        """
        self.in_game = False
        self.previous_mode = self.game_mode
        self.game_mode = None
        super(EDPlayerOne, self).killed()

    def resurrect(self, rebought=True):
        """
        Handle player resurrection.

        Args:
            rebought (bool): True if the ship was rebought.
        """
        self.in_game = True
        self.game_mode = self.previous_mode
        if not rebought:
            self.mothership = EDVehicleFactory.unknown_vehicle()
            self.piloted_vehicle = self.mothership
        self._touch()

    def update_vehicle_if_obsolete(self, vehicle, piloted=True):
        """
        Update vehicle if it's different from the current one.

        Args:
            vehicle (EDVehicle): The new vehicle.
            piloted (bool): Whether the player is piloting it.

        Returns:
            bool: True if updated.
        """
        updated = False
        if piloted:
            if self.piloted_vehicle is None or self.piloted_vehicle.type != vehicle.type:
                self.piloted_vehicle = vehicle
                updated = True
        else:
            if self.mothership is None or self.mothership.type != vehicle.type:
                self.mothership = vehicle
                updated = True
        
        if updated:
            self._touch()
        return updated

    def in_solo_or_private(self):
        """
        Returns:
            bool: True if in Solo or Private Group.
        """
        return self.game_mode in ["Solo", "Group"]

    def in_open(self):
        """
        Returns:
            bool: True if in Open.
        """
        return self.game_mode == "Open"

    def is_wingmate(self, name):
        """
        Check if a commander is a wingmate.

        Args:
            name (str): Commander name.

        Returns:
            bool: True if in wing.
        """
        return name in self.wing.wingmates

    def join_wing(self, wingmates):
        """
        Join a wing.

        Args:
            wingmates (list): List of wingmate names.
        """
        self.wing.wingmates = set(wingmates)
        self._touch()

    def add_to_wing(self, wingmate):
        """
        Add a wingmate.

        Args:
            wingmate (str): Wingmate name.
        """
        self.wing.wingmates.add(wingmate)
        self._touch()

    def leave_wing(self):
        """
        Leave the wing.
        """
        self.wing.wingmates = set()
        self._touch()
