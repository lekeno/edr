
from edtime import EDTime
import random

class EDReconBox(object):
    def __init__(self):
        self.sequence = ""
        self.last_change = None
        self.cut_after = 5
        self.active = False
        self.required_length = 4
        self.advertised = False
        self.forced = False
        self.keycode = EDReconBox.gen_keycode()

    def process_signal(self, is_high):
        if self._is_sequence_stale():
            self._clear_sequence()

        value = "1" if is_high else "0"
        if (self.sequence == "" and value == "1") or (self.sequence != "" and self.sequence[-1] != value):
            self.sequence += value
            self.last_change = EDTime.py_epoch_now()
         
        length = len(self.sequence)
        if length >= self.required_length:
            self.active = not self.active
            self._clear_sequence()
            return True
        return False

    def activate(self):
        self.active = True
        self.forced = True
    
    def reset(self):
        self.sequence = ""
        self.last_change = None
        self.active = False
        self.advertised = False
        self.forced = False
        self.keycode = EDReconBox.gen_keycode()

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

