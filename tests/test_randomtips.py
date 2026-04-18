
import unittest
from unittest.mock import patch, mock_open
import json
from edr.utils.randomtips import RandomTips

class TestRandomTips(unittest.TestCase):
    def test_default_tips(self):
        rt = RandomTips()
        self.assertIn("edr", rt.tips) # Check for key
        
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "Selected Tip"
            self.assertEqual(rt.tip("edr"), "Selected Tip")

    def test_custom_tips(self):
        mock_data = json.dumps({"custom": ["Custom Tip 1", "Custom Tip 2"]})
        with patch('edr.utils.randomtips.open', mock_open(read_data=mock_data)):
             with patch('edr.utils.randomtips.os.path.abspath') as mock_abspath:
                mock_abspath.return_value = "/path/to/edr"
                rt = RandomTips("custom.json")
                
                with patch('random.choice') as mock_choice:
                    mock_choice.return_value = "Custom Tip 1"
                    self.assertEqual(rt.tip("custom"), "Custom Tip 1")

    def test_missing_category_random_selection(self):
        rt = RandomTips()
        with patch('random.choice') as mock_choice:
            # First choice selects category, second choice selects tip
            mock_choice.side_effect = ["edr", "Random EDR Tip"]
            self.assertEqual(rt.tip("nonexistent"), "Random EDR Tip")

if __name__ == '__main__':
    unittest.main()
