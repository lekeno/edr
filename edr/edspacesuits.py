from edtime import EDTime
import edrconfig

'''
Additional values when on foot:
  Oxygen: (0.0 .. 1.0)
  Health: (0.0 .. 1.0)
  Temperature (kelvin)
  SelectedWeapon: name
 Gravity: (relative to 1G) 
'''

class EDSpaceSuit(object):
    def __init__(self, suit_type="UnknownSuit"):
        self.type = suit_type
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._health = {u"value": 1.0, u"timestamp": now}
        self._oxygen = {u"value": 1.0, u"timestamp": now}
        self._low_oxygen = {u"value": False, u"timestamp": now}
        self._low_health = {u"value": False, u"timestamp": now}
        self.shield_up = True
        self.fight = {u"value": False, "large": False, u"timestamp": now}
        self._attacked = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        config = edrconfig.EDR_CONFIG
        self.fight_staleness_threshold = config.instance_fight_staleness_threshold()
        self.danger_staleness_threshold = config.instance_danger_staleness_threshold()
        
    @property
    def health(self):
        return self._health["value"]

    @health.setter
    def health(self, new_value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._health = {u"value": new_value, u"timestamp": now}

    @property
    def oxygen(self):
        return self._oxygen["value"]

    @oxygen.setter
    def oxygen(self, new_value):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._oxygen = {u"value": new_value, u"timestamp": now}

    @property
    def low_health(self):
        return self._low_oxygen["value"]

    @low_health.setter
    def low_health(self, low):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._low_health = {"timestamp": now, "value": low}

    @property
    def low_oxygen(self):
        return self._low_oxygen["value"]

    @low_oxygen.setter
    def low_oxygen(self, low):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._low_oxygen = {"timestamp": now, "value": low}

    def json(self):
        result = {
            u"timestamp": int(self.timestamp * 1000),
            u"type": self.type,
            u"health": self.__js_t_v(self._health),
            u"oxygen": self.__js_t_v(self._oxygen),
            u"shieldUp": self.shield_up,
            u"lowHealth":self.__js_t_v(self._low_health),
            u"lowOxygen":self.__js_t_v(self._low_oxygen),
        }
        
        return result

    def __js_t_v(self, t_v):
        result = t_v.copy()
        result["timestamp"] = int(t_v["timestamp"]*1000)
        return result

    def __repr__(self):
        return str(self.__dict__)

    def reset(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.health = 100.0
        self.oxygen = 100.0
        self.shield_up = True
        self.fight = {u"value": False, u"large": False, u"timestamp": now}
        # self._hardpoints_deployed = {u"value": False, u"timestamp": now} ? SelectedWeapon?
        self._attacked = {u"value": False, u"timestamp": now}
        self.heat_damaged = {u"value": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
        
    def destroy(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self.health = 0.0

    def attacked(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._attacked = {u"value": True, u"timestamp": now}

    def under_attack(self):
        if self._attacked["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._attacked["timestamp"]) and ((now - self._attacked["timestamp"]) <= self.danger_staleness_threshold)
        return False

    def safe(self):
        now = EDTime.py_epoch_now()
        self._attacked = {u"value": False, u"timestamp": now}
        self.fight = {u"value": False, "large": False, u"timestamp": now}
        self._in_danger = {u"value": False, u"timestamp": now}
    
    def unsafe(self):
        now = EDTime.py_epoch_now()
        self._in_danger = {u"value": True, u"timestamp": now}

    def in_danger(self):
        if self._in_danger["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self._in_danger["timestamp"]) and ((now - self._in_danger["timestamp"]) <= self.danger_staleness_threshold)
        return False

    def shield_state(self, is_up):
        if not is_up:
            self.shield_health = 0.0
        self.shield_up = is_up

    def skirmish(self):
        now = EDTime.py_epoch_now()
        self.fight = {u"value": True, "large": False, u"timestamp": now}

    def battle(self):
        now = EDTime.py_epoch_now()
        self.fight = {u"value": True, "large": True, u"timestamp": now}

    def in_a_fight(self):
        if self.fight["value"]:
            now = EDTime.py_epoch_now()
            return (now >= self.fight["timestamp"]) and ((now - self.fight["timestamp"]) <= self.fight_staleness_threshold)
        return False

    def __eq__(self, other):
        if not isinstance(other, EDSpaceSuit):
            return False
        return self.__dict__ == other.__dict__
        
    def __ne__(self, other):
        return not self.__eq__(other)