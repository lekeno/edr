import unittest
from unittest.mock import Mock, patch
import sys
import os

# Setup paths
# Setup paths
# Add 'edr' directory to sys.path so we can import modules directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'edr')))

from edreconbox import EDReconBox # EDR_INTERNAL

class TestEDReconBox(unittest.TestCase):
    def setUp(self):
        # Patching 'edreconbox.EDTime' because we import edreconbox as a top-level module
        # via sys.path modification that includes the 'edr' directory.
        self.edtime_patch = patch('edreconbox.EDTime')
        self.mock_edtime = self.edtime_patch.start()
        self.mock_edtime.py_epoch_now.return_value = 1000

        self.box = EDReconBox()

    def tearDown(self):
        self.edtime_patch.stop()

    def test_initial_state(self):
        self.assertFalse(self.box.active)
        self.assertFalse(self.box.advertised)
        self.assertEqual(self.box.sequence, "")
        self.assertIsNotNone(self.box.keycode)

    def test_process_signal_sequence(self):
        # Default required_length is 4
        # Sequence logic:
        # value = "1" if is_high else "0"
        # Appends if sequence empty and value="1", or if value != last char
        
        # 1. High signal (should start sequence)
        self.mock_edtime.py_epoch_now.return_value = 1000
        res = self.box.process_signal(True) # "1"
        self.assertFalse(res)
        self.assertEqual(self.box.sequence, "1")

        # 2. Low signal 
        self.mock_edtime.py_epoch_now.return_value = 1001
        res = self.box.process_signal(False) # "0"
        self.assertFalse(res)
        self.assertEqual(self.box.sequence, "10")

        # 3. High signal
        self.mock_edtime.py_epoch_now.return_value = 1002
        res = self.box.process_signal(True) # "1"
        self.assertFalse(res)
        self.assertEqual(self.box.sequence, "101")
        
        # 4. Low signal (length 4 reached)
        self.mock_edtime.py_epoch_now.return_value = 1003
        res = self.box.process_signal(False) # "0"
        self.assertTrue(res) # Should activate
        self.assertTrue(self.box.active)
        self.assertEqual(self.box.sequence, "") # Clears sequence

    def test_process_signal_stale(self):
        # Start sequence
        self.box.process_signal(True) # "1"
        self.assertEqual(self.box.sequence, "1")
        
        # Advance time beyond cut_after (default 5)
        self.mock_edtime.py_epoch_now.return_value = 1000 + 6
        
        # Next signal
        self.box.process_signal(False) 
        # Should clear previous sequence because it was stale
        # Then start new sequence?
        # Logic: 
        # if stale: clear
        # value="0". If sequence empty and value="1"... 
        # Since value is "0", and sequence is empty (after clear), it shouldn't start?
        
        self.assertEqual(self.box.sequence, "") 

    def test_ignored_duplicate_signal(self):
        self.box.process_signal(True) # "1"
        self.assertEqual(self.box.sequence, "1")
        
        self.box.process_signal(True) # "1" again
        # Logic: (self.sequence != "" and self.sequence[-1] != value)
        # "1" != "1" is False.
        # So "1" is NOT appended.
        self.assertEqual(self.box.sequence, "1")

    def test_activate_reset(self):
        self.box.activate()
        self.assertTrue(self.box.active)
        self.assertTrue(self.box.forced)
        
        self.box.reset()
        self.assertFalse(self.box.active)
        self.assertFalse(self.box.forced)
        self.assertEqual(self.box.sequence, "")

