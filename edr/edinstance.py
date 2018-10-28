import edtime

class EDInstance(object):
    def __init__(self):
        now = edtime.EDTime.py_epoch_now()
        self.timestamp = now
        self.players = {}

    def reset(self):
        self.players = {}

    def player(self, cmdr_name):
        if cmdr_name.lower() not in self.players:
            return False
        return self.players[cmdr_name.lower()]["player"]

    def player_in(self, cmdr):
        now = edtime.EDTime.py_epoch_now()
        self.timestamp = now
        self.players[cmdr.name.lower()] = {"timestamp": now, "player": cmdr}

    def player_out(self, cmdr_name):
        now = edtime.EDTime.py_epoch_now()
        try:
            del self.players[cmdr_name.lower()]
            self.timestamp = now
        except KeyError:
            pass

    def __repr__(self):
        return str(self.__dict__)

    def json(self):
        players = {}
        for cmdr_name in self.players:
            players.append(
                self.players[cmdr_name].json()
            )
        return {
            "timestamp": int(self.timestamp * 1000),
            "players": players
        }