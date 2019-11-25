from __future__ import absolute_import

from .edtime import EDTime

class EDInstance(object):
    def __init__(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.last_check_timestamp = None
        self._touched = True
        self.players = {}

    def reset(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.players = {}
        self._touched = True

    def player(self, cmdr_name):
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()][u"player"]

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

    def __repr__(self):
        return str(self.__dict__)

    def is_empty(self):
        return not self.players

    def anyone_beside(self, cmdr_names):
        if not cmdr_names:
            return not self.is_empty()

        canonical_cmdr_names = [c.lower() for c in cmdr_names]
        for cmdr_name in self.players:
            if cmdr_name.lower() not in canonical_cmdr_names:
                return True
        return False

    def presence_of_outlaws(self, edrcmdrs, bounty_threshold=10000, karma_threshold=-200, ignorables=None):
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
            if the_player.bounty >= bounty_threshold:
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
            if timestamp >= self.last_check_timestamp:
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
            if cmdr_name.targeted:
                now = EDTime.py_epoch_now()
                timestamp = now
            result[cmdr_name.lower()] = {"timestamp": int(timestamp*1000), "player": player.json()}
        return result

    def debug_repr(self):
        result = []
        result.append(u"T:{} ; last_check:{} ; touched: {}".format(EDTime.t_minus(self.timestamp*1000), EDTime.t_minus(self.last_check_timestamp*1000) if self.last_check_timestamp else "", self._touched))
        for cmdr_name in self.players:
            timestamp, player = self.players[cmdr_name.lower()].values()
            now = EDTime.py_epoch_now()
            if player.targeted:
                timestamp = now
            result.append(u"{} at {}: {} {}".format(cmdr_name, EDTime.t_minus(timestamp*1000), "[TGT]" if player.targeted else "", player.json()))
        return result