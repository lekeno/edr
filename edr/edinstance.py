from __future__ import absolute_import

from edtime import EDTime
from edvehicles import EDVehicleFactory

class EDInstance(object):
    def __init__(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.last_check_timestamp = None
        self._touched = True
        self.players = {}
        self.npcs = {}
        self.npc_names_to_npcs = {}

    def reset(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.players = {}
        self.npcs = {}
        self.npc_names_to_npcs = {}
        self._touched = True

    def player(self, cmdr_name):
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()][u"player"]

    def npc(self, name, rank=None, ship_internal_name=None):
        hopefully_unique_name = "{}{}{}".format(name, rank, EDVehicleFactory.canonicalize(ship_internal_name) if ship_internal_name else "")
        if hopefully_unique_name in self.npcs:
            return self.npcs[hopefully_unique_name][u"pilot"]
        if name in self.npc_names_to_npcs:
            return self.npcs[next(iter(self.npc_names_to_npcs[name]))][u"pilot"]
        return None

    def blip(self, cmdr_name):
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()]

    def player_in(self, cmdr):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.players[cmdr.name.lower()] = {u"timestamp": now, u"player": cmdr}
        self._touched = True

    def player_out(self, cmdr_name):
        now = EDTime.py_epoch_now()
        try:
            del self.players[cmdr_name.lower()]
            self.timestamp = now
            self._touched = True
        except KeyError:
            pass

    def npc_in(self, pilot):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        hopefully_unique_name = "{}{}{}".format(pilot.name, pilot.rank, pilot.vehicle.name if pilot.vehicle else "")
        self.npcs[hopefully_unique_name] = {u"timestamp": now, u"pilot": pilot}
        if pilot.name in self.npc_names_to_npcs:
            self.npc_names_to_npcs[pilot.name].add(hopefully_unique_name)
        else:
            self.npc_names_to_npcs[pilot.name] = set([hopefully_unique_name])
        self._touched = True

    def npc_out(self, name, ship_internal_name=None, rank=None):
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
        return not self.players

    def is_totally_empty(self):
        return not self.players and not self.npcs

    def any_player_beside(self, cmdr_names):
        if not cmdr_names:
            return not self.is_void_of_player()

        canonical_cmdr_names = [c.lower() for c in cmdr_names]
        for cmdr_name in self.players:
            if cmdr_name.lower() not in canonical_cmdr_names:
                return True
        return False

    def presence_of_outlaw_players(self, edrcmdrs, bounty_threshold=10000, karma_threshold=-200, ignorables=None):
        canonical_ignorables = [c.lower() for c in ignorables]
        for cmdr_name in self.players:
            if cmdr_name.lower() in canonical_ignorables:
                continue
            profile = None
            try:
                profile = edrcmdrs.cmdr(cmdr_name)
                if profile.karma <= karma_threshold:
                    return True
            except:
                pass
            the_player = self.players[cmdr_name]["player"]
            if the_player.bounty and the_player.bounty >= bounty_threshold:
                return True if not profile else not(profile.is_friend() or profile.is_ally())

    def players_nb(self):
        return len(self.players)

    def noteworthy_changes_json(self):
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
        result = {}
        for cmdr_name in self.players:
            timestamp, player = self.players[cmdr_name.lower()].values()
            if cmdr_name.is_targeted():
                now = EDTime.py_epoch_now()
                timestamp = now
            result[cmdr_name.lower()] = {"timestamp": int(timestamp*1000), "player": player.json()}
        return result

    def debug_repr(self):
        result = []
        result.append(u"{} ; last_check:{} ; touched: {}".format(EDTime.t_minus(self.timestamp*1000), EDTime.t_minus(self.last_check_timestamp*1000) if self.last_check_timestamp else "", self._touched))
        for cmdr_name in self.players:
            timestamp, player = self.players[cmdr_name.lower()].values()
            now = EDTime.py_epoch_now()
            if player.is_targeted():
                timestamp = now
            result.append(u"Cmdr {} at {}: {} {}".format(cmdr_name, EDTime.t_minus(timestamp*1000), "[TGT]" if player.is_targeted() else "", player.json()))

        for name in self.npcs:
            timestamp, pilot = self.npcs[name.lower()].values()
            now = EDTime.py_epoch_now()
            if pilot.is_targeted():
                timestamp = now
            result.append(u"NPC {} at {}: {} {}".format(name, EDTime.t_minus(timestamp*1000), "[TGT]" if pilot.is_targeted() else "", pilot.json()))
        return result