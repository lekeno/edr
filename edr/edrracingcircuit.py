from edtime import EDTime

class EDRRacingCircuit(object):
    def __init__(self, properties):
        self.waypoints = properties.get("waypoints", [])
        self.type = properties.get("type", None)
        self.category = properties.get("category", None)
        self.laps = properties.get("laps", None)
        self.radius = properties.get("radius", 0.100)
        self.max_altitude = properties.get("altitude", 1000)
        self._current_wp = 0
        self.start_time = None
        self.lap_times = []
        self.best = {"lap": None, "race": None}
    
    def restart(self):
        self.start_time = None
        self._current_wp = 0
        self.lap_times = []
    
    def reset(self):
        self.restart()
        self.best = {"lap": None, "race": None}

    def current_waypoint(self):
        if self._is_finished():
            return None
        return self.waypoints[self._current_wp]

    def advance(self):
        now = EDTime.py_epoch_now()
        if not self.waypoints:
            return False

        if len(self.waypoints) == 1:
            return False
        
        if self._current_wp is None:
            return False

        if self._current_wp == 0 and len(self.lap_times) == 0:
            self.start_time = now

        self._current_wp = (self._current_wp + 1)
        if self._current_wp >= len(self.waypoints):
            if len(self.lap_times) <= self.laps:
                previous_laps_total = sum(self.lap_times) if self.lap_times else 0
                lap_time = now - self.start_time - previous_laps_total
                self.lap_times.append(lap_time)
                self.best["lap"] = min(lap_time, self.best["lap"] or now)
            if self._is_finished():
                self._current_wp = None
                self.best["race"] = min(now - self.start_time, self.best["race"] or now)
                return False
            self._current_wp = 0
        return True

    def _is_finished(self):
        if self.type == "loop":
            return len(self.lap_times) >= self.laps
        return self._curent_wp is None or self._current_wp >= len(self.waypoints)