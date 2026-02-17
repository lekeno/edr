
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import tkinter as tk

# Mocking tkinter is notoriously hard if we want to test widgets.
# We'll just try to instantiate if possible, or mock the whole class.
# Since we are in a headless env, we might not have a display.

class TestEDRTogglingPanel(unittest.TestCase):
    @patch('tkinter.Frame')
    @patch('tkinter.Label')
    @patch('tkinter.Text')
    @patch('tkinter.Checkbutton')
    def test_instantiation(self, mock_chk, mock_txt, mock_lbl, mock_frame):
        # Mock imported modules before importing the module under test
        with patch.dict(sys.modules, {'ttkHyperlinkLabel': MagicMock()}):
            from edr.ui import edrtogglingpanel
            
            # We need to mock IGMConfig too as it is used in __init__
            with patch('edr.ui.edrtogglingpanel.IGMConfig') as mock_conf:
                 # Set up the mock config to return valid RBG values
                 mock_conf.return_value.rgb.return_value = 'black'
                 mock_conf.return_value.len.return_value = 100
                 mock_conf.return_value.body_rows.return_value = 10
                 
                 callback = Mock()
                 status = Mock()
                 show = Mock()

                 panel = edrtogglingpanel.EDRTogglingPanel(status, show, callback)
                 self.assertIsNotNone(panel)

if __name__ == '__main__':
    unittest.main()
