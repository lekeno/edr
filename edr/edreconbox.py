from __future__ import absolute_import

from edtime import EDTime
import random
import plug
import json
import utils2to3

class EDReconBox(object):

    RECOGNIZED_SEQUENCES = { "LnlnLnln": "distress", "LNlNLNlN": "distress", "lNlnlNln": "tracking", "LNLnLNLn": "tracking" }

    def __init__(self):
        self.sequence = ""
        self.last_change = None
        self.cut_after = 5
        self.distress = False
        self.required_length = 4
        self.max_length = 10
        self.advertised = False
        self.forced = False
        self.keycode = EDReconBox.gen_keycode()
        self.waypoints = []
        self.tracking = True # TODO
        self.should_record_wp = False
        self.previous = {"cargoscoop": False, "value": ""}

    def process_signal(self, flags):
        if flags & plug.FlagsSupercruise:
            self._clear_sequence()
            return False

        if self.tracking:
            cargoscoop_deployed = flags & plug.FlagsCargoScoopDeployed
            self.should_record_wp = cargoscoop_deployed and not self.previous["cargoscoop"]
            self.previous["cargoscoop"] = cargoscoop_deployed 

        if self._is_sequence_stale():
            self._clear_sequence()

        if len(self.sequence) >= self.max_length:
            self._clear_sequence()

        lights_on = flags & plug.FlagsLightsOn
        nightvision_on = flags & plug.FlagsNightVision

        value = "L" if lights_on else "l"
        value += "N" if nightvision_on else "n" 
        if (self.sequence == "" and (lights_on or nightvision_on)) or (self.sequence != "" and self.previous["value"] != value):
            self.sequence += value
            self.last_change = EDTime.py_epoch_now()
            self.previous["value"] = value
         
        if self.sequence in self.RECOGNIZED_SEQUENCES:
            if self.RECOGNIZED_SEQUENCES[self.sequence] == "distress":
                self.distress = not self.distress
            elif self.RECOGNIZED_SEQUENCES[self.sequence] == "tracking":
                self.tracking = not self.tracking
                if not self.tracking or not self.distress: # TODO temp
                    self._save_waypoints()
            self._clear_sequence()
            return True
        return False

    def distress_mode(self):
        self.distress = True
        self.forced = True
    
    def reset(self):
        self.sequence = ""
        self.last_change = None
        self.distress = False
        self.advertised = False
        self.forced = False
        self.keycode = EDReconBox.gen_keycode()
        self.waypoints = []
        self.should_record_wp = False

    @staticmethod
    def gen_keycode():
        prefix = random.choice(["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"])
        suffix = random.randint(0,999)
        return u"{}-{}".format(prefix, suffix)

    def _is_sequence_stale(self):
        if self.last_change is None:
            return False
        now = EDTime.py_epoch_now()
        return (now - self.last_change) > self.cut_after

    def _clear_sequence(self):
        self.last_change = None
        self.sequence = ""

    def process_waypoint(self, waypoint):
        if self.tracking and self.should_record_wp:
            self._record_wp(waypoint)

    def _record_wp(self, waypoint):
        self.waypoints.append(waypoint)
        self.should_record_wp = False

    def _save_waypoints(self):
        EDR_WAYPOINTS_PATH = utils2to3.abspathmaker(__file__, 'private', 'waypoints.json')  # TODO data? public? perso? folder
        with open(EDR_WAYPOINTS_PATH, 'w') as outfile:
            json.dump(self.waypoints, outfile)
        print(self.waypoints) # TODO temp

