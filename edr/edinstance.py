import edtime

class EDInstance(object):
    def __init__(self):
        now = edtime.EDTime.py_epoch_now()
        self.timestamp = now
        self.last_check_timestamp = None
        self._touched = True
        self.players = {}

    def reset(self):
        now = edtime.EDTime.py_epoch_now()
        self.timestamp = now
        self.players = {}
        self._touched = True

    def player(self, cmdr_name):
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()]["player"]

    def blip(self, cmdr_name):
        if cmdr_name.lower() not in self.players:
            return None
        return self.players[cmdr_name.lower()]

    def player_in(self, cmdr):
        now = edtime.EDTime.py_epoch_now()
        self.timestamp = now
        self.players[cmdr.name.lower()] = {"timestamp": now, "player": cmdr}
        self._touched = True

    def player_out(self, cmdr_name):
        now = edtime.EDTime.py_epoch_now()
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
        for player in self.players:
            if player.lower() not in canonical_cmdr_names:
                return True
        return False

    def players_nb(self):
        return len(self.players)

    def noteworthy_changes_json(self):
        now = edtime.EDTime.py_epoch_now()
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
            result[cmdr_name.lower()] = {"timestamp": int(timestamp*1000), "player": player.json()}
        return result