from edr.utils.edtime import EDTime  # EDR_INTERNAL
from .edvehicles import EDVehicleFactory  # EDR_INTERNAL


class EDInstance:
    """
    Represents a game instance (island) in Elite Dangerous.
    Tracks players and NPCs present in the current instance.
    """

    def __init__(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.last_check_timestamp = None
        self._touched = True
        self.players = {}
        self.npcs = {}
        self.npc_names_to_npcs = {}

    def reset(self):
        """Reset the instance state."""
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.players = {}
        self.npcs = {}
        self.npc_names_to_npcs = {}
        self._touched = True

    def player(self, cmdr_name):
        """Retrieve a player object by CMDR name."""
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()]["player"]

    def npc(self, name, rank=None, ship_internal_name=None):
        """Retrieve an NPC pilot object by name/rank/ship."""
        hopefully_unique_name = "{}{}{}".format(name, rank, EDVehicleFactory.canonicalize(ship_internal_name) if ship_internal_name else "")
        if hopefully_unique_name in self.npcs:
            return self.npcs[hopefully_unique_name]["pilot"]
        if name in self.npc_names_to_npcs:
            return self.npcs[next(iter(self.npc_names_to_npcs[name]))]["pilot"]
        return None

    def blip(self, cmdr_name):
        """Get the presence record (timestamp, player) for a CMDR."""
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()]

    def player_in(self, cmdr):
        """Register a player entering the instance."""
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.players[cmdr.name.lower()] = {"timestamp": now, "player": cmdr}
        self._touched = True

    def player_out(self, cmdr_name):
        """Register a player leaving the instance."""
        now = EDTime.py_epoch_now()
        try:
            del self.players[cmdr_name.lower()]
            self.timestamp = now
            self._touched = True
        except KeyError:
            pass

    def npc_in(self, pilot):
        """Register an NPC entering the instance."""
        now = EDTime.py_epoch_now()
        self.timestamp = now
        hopefully_unique_name = "{}{}{}".format(pilot.name, pilot.rank, pilot.vehicle.name if pilot.vehicle else "")
        self.npcs[hopefully_unique_name] = {"timestamp": now, "pilot": pilot}
        if pilot.name in self.npc_names_to_npcs:
            self.npc_names_to_npcs[pilot.name].add(hopefully_unique_name)
        else:
            self.npc_names_to_npcs[pilot.name] = set([hopefully_unique_name])
        self._touched = True

    def npc_out(self, name, ship_internal_name=None, rank=None):
        """Register an NPC leaving the instance."""
        now = EDTime.py_epoch_now()
        try:
            if ship_internal_name:
                hopefully_unique_name = "{}{}{}".format(name, rank, EDVehicleFactory.canonicalize(ship_internal_name))
                del self.npcs[hopefully_unique_name]
                self.npc_names_to_npcs[name].remove(hopefully_unique_name)
            else:
                for hopefully_unique_name in self.npc_names_to_npcs[name]:
                    del self.npcs[hopefully_unique_name]
                del self.npc_names_to_npcs[name]
                self.timestamp = now
                self._touched = True
        except KeyError:
            pass

    def __repr__(self):
        return str(self.__dict__)

    def is_void_of_player(self):
        """Check if no other players are present."""
        return not self.players

    def is_totally_empty(self):
        """Check if the instance is empty of both players and NPCs."""
        return not self.players and not self.npcs

    def any_player_beside(self, cmdr_names):
        """Check if any players other than the listed ones are present."""
        if not cmdr_names:
            return not self.is_void_of_player()

        canonical_cmdr_names = [c.lower() for c in cmdr_names]
        for cmdr_name in self.players:
            if cmdr_name.lower() not in canonical_cmdr_names:
                return True
        return False

    def presence_of_outlaw_players(self, edrcmdrs, bounty_threshold=10000, karma_threshold=-200, ignorables=None):
        """Check for players with high bounties or low karma."""
        canonical_ignorables = [c.lower() for c in ignorables] if ignorables else []
        for cmdr_name in self.players:
            if cmdr_name.lower() in canonical_ignorables:
                continue
            profile = None
            try:
                profile = edrcmdrs.cmdr(cmdr_name)
                if profile.karma <= karma_threshold:
                    return True
            except Exception:
                pass
            the_player = self.players[cmdr_name]["player"]
            if the_player.bounty and the_player.bounty >= bounty_threshold:
                return True if not profile else not(profile.is_friend() or profile.is_ally())
        return False

    def players_nb(self):
        """Return the number of players present."""
        return len(self.players)

    def noteworthy_changes_json(self):
        """Return JSON representation of changes since the last check."""
        now = EDTime.py_epoch_now()
        if not self._touched:
            return None
        players = []
        for cmdr_name in self.players:
            timestamp, player = self.players[cmdr_name.lower()].values()
            if timestamp is None or self.last_check_timestamp is None or timestamp >= self.last_check_timestamp:
                players.append(player.json())
        self.last_check_timestamp = now
        self._touched = False
        return {
            "timestamp": int(self.timestamp * 1000),
            "players": players
        }

    def json(self):
        """Return full JSON state of the instance."""
        # TODO refactor
        result = {}
        for cmdr_name in self.players:
            timestamp, player = self.players[cmdr_name.lower()].values()
            if cmdr_name.lower() in self.players and self.players[cmdr_name.lower()]["player"].is_targeted():
                now = EDTime.py_epoch_now()
                timestamp = now
            result[cmdr_name.lower()] = {"timestamp": int(timestamp*1000), "player": player.json()}
        return result

    def debug_repr(self):
        """Return debugging string representation."""
        result = []
        result.append("{} ; last_check:{} ; touched: {}".format(
            EDTime.t_minus(self.timestamp*1000),
            EDTime.t_minus(self.last_check_timestamp*1000) if self.last_check_timestamp else "",
            self._touched
        ))
        
        from edr.utils.edtime import EDTime
        now = EDTime.py_epoch_now()

        for cmdr_name in self.players:
            timestamp, player = self.players[cmdr_name.lower()].values()
            if hasattr(player, 'is_targeted') and player.is_targeted():
                timestamp = now
            result.append("Cmdr {} at {}: {} {}".format(
                cmdr_name, 
                EDTime.t_minus(timestamp*1000), 
                "[TGT]" if hasattr(player, 'is_targeted') and player.is_targeted() else "", 
                player.json()
            ))

        for name in self.npcs:
            timestamp, pilot = self.npcs[name.lower()].values()
            if hasattr(pilot, 'is_targeted') and pilot.is_targeted():
                timestamp = now
            result.append("NPC {} at {}: {} {}".format(
                name, 
                EDTime.t_minus(timestamp*1000), 
                "[TGT]" if hasattr(pilot, 'is_targeted') and pilot.is_targeted() else "", 
                pilot.json()
            ))
        return result
