
import unittest
from unittest.mock import patch, mock_open
import json
from edr.core.helpcontent import HelpContent

class TestHelpContent(unittest.TestCase):
    def test_default_content(self):
        hc = HelpContent()
        self.assertIn("about", hc.content)
        self.assertIn("basics", hc.content)
        self.assertEqual(hc.get("about"), HelpContent.DEFAULT_CONTENT["about"])

    def test_custom_content(self):
        mock_data = json.dumps({"custom": {"header": "Custom", "details": ["Detail"]}})
        with patch('edr.core.helpcontent.open', mock_open(read_data=mock_data)):
             with patch('edr.core.helpcontent.os.path.abspath') as mock_abspath:
                mock_abspath.return_value = "/path/to/edr"
                hc = HelpContent("custom.json")
                self.assertIn("custom", hc.content)
                self.assertEqual(hc.get("custom")["header"], "Custom")

    def test_get_missing(self):
        hc = HelpContent()
        self.assertIsNone(hc.get("nonexistent"))

if __name__ == '__main__':
    unittest.main()
