import edtime
import random

class EDReconBox(object):
    def __init__(self):
        self.sequence = ""
        self.last_change = None
        self.cut_after = 5
        self.active = False
        self.required_length = 4
        self.advertised = False
        self.keycode = EDReconBox.gen_keycode()

    def process_signal(self, is_high):
        if self._is_sequence_stale():
            self._clear_sequence()

        value = "1" if is_high else "0"
        if (self.sequence == "" and value == "1") or (self.sequence != "" and self.sequence[-1] != value):
            self.sequence += value
            self.last_change = edtime.EDTime.py_epoch_now()
         
        length = len(self.sequence)
        if length >= self.required_length:
            self.active = not self.active
            self._clear_sequence()
            return True
        return False

    def reset(self):
        self.sequence = ""
        self.last_change = None
        self.active = False
        self.advertised = False
        self.keycode = EDReconBox.gen_keycode()

    @staticmethod
    def gen_keycode():
        prefix = random.choice(["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "x-ray", "yankee", "zulu"])
        suffix = random.randint(0,999)
        return u"{}-{}".format(prefix, suffix)

    def _is_sequence_stale(self):
        if self.last_change is None:
            return False
        now = edtime.EDTime.py_epoch_now()
        return (now - self.last_change) > self.cut_after

    def _clear_sequence(self):
        self.last_change = None
        self.sequence = ""

