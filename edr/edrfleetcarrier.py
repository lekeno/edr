from __future__ import absolute_import
import edtime
from edrlog import EDRLog
EDRLOG = EDRLog()

class EDRFleetCarrier(object):
    def __init__(self):
        self.id = None
        self.callsign = None
        self.name = None
        self.access = "none"
        self.allow_notorious = False
        self._position = {"system": None, "body": None}
        self.departure = {"time": None, "destination": None}
        self.decommission_time = None

    def __reset(self):
        self.id = None
        self.callsign = None
        self.name = None
        self.access = "none"
        self.allow_notorious = False
        self._position = {"system": None, "body": None}
        self.departure = {"time": None, "destination": None}
        self.decommission_time = None

    def bought(self, buy_event):
        self.__reset()
        self.id = buy_event.get("CarrierID", None)
        self.callsign = buy_event.get("Callsign", None)
        self._position["system"] = buy_event.get("Location", None)

    def update_from_stats(self, fc_stats_event):
        if self.id and self.id != fc_stats_event.get("CarrierID", None):
            self.__reset()
        self.id = fc_stats_event.get("CarrierID", None)
        self.callsign = fc_stats_event.get("Callsign", None)
        self.name = fc_stats_event.get("Name", None)
        self.access = fc_stats_event.get("DockingAccess", "none")
        self.allow_notorious = fc_stats_event.get("AllowNotorious", False)

    def jump_requested(self, jump_request_event):
        if self.id and self.id != jump_request_event.get("CarrierId", None):
            self.__reset()
        self.id = jump_request_event.get("CarrierID", None)
        self.__update_position()
        request_time = edtime.EDTime.from_journal_timestamp(jump_request_event["timestamp"])
        jump_time = request_time.as_epoch_py() + 60*15
       
        self.departure = {
            "time": jump_time,
            "destination": jump_request_event.get("SystemName", None)}

    @property
    def position(self):
        self.__update_position(self)
        return self._position["system"]

    def __update_position(self):
        now = edtime.EDTime.py_epoch_now()
        if self.decommission_time and now > self.decommission_time:
            self.__reset()
            return

        if self.departure["destination"] is None:
            return
        
        if now < self.departure["time"]:
            return
        
        self._position["system"] = self.departure["destination"]
        self.departure = {"time": None, "destination": None}

    def update_docking_permissions(self, event):
        if self.id and self.id != event.get("CarrierId", None):
            self.__reset()
        self.id = event.get("CarrierID", None)
        self.access = event.get("DockingAccess", "none")
        self.allow_notorious = event.get("AllowNotorious", False)

    def update_from_jump_if_relevant(self, event):
        if self.id is None or self.id != event.get("MarketID", None):
            return
        self._position = {"system": event.get("StarSystem", None), "body": event.get("Body", None)}
        self.departure = {"time": None, "destination": None}

    def cancel_decommission(self, event):
        if self.id and self.id != event.get("CarrierId", None):
            self.__reset()
        self.id = event.get("CarrierID", None)

    def decommission_requested(self, event):
        if self.id and self.id != event.get("CarrierId", None):
            self.__reset()
        self.id = event.get("CarrierID", None)
        self.decommission_time = event.get("ScrapTime", None)

    def json_jump_schedule(self):
        return {
            "id": self.id,
            "callsign": self.callsign,
            "name": self.name,
            "from": self.position,
            "to": self.departure["destination"],
            "at": self.departure["time"]
            "access": self.access,
            "allow_notorious": self.allow_notorious
        }

    # TODO persistence
