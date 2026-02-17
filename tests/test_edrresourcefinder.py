
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from edr.controllers import edrresourcefinder

class TestEDRResourceFinder(unittest.TestCase):
    def setUp(self):
        self.edr_systems = Mock()
        self.edr_factions = Mock()
        self.finder = edrresourcefinder.EDRResourceFinder(self.edr_systems, self.edr_factions)

    def test_canonical_name(self):
        self.assertEqual(self.finder.canonical_name("ant"), "antimony")
        self.assertEqual(self.finder.canonical_name("Antimony"), "antimony")
        self.assertIsNone(self.finder.canonical_name("Unobtanium"))

    def test_recognized_candidates(self):
        matches = self.finder.recognized_candidates("ant")
        self.assertIn("antimony", matches)
        self.assertIn("ant", matches)

    def test_mission_reward_only(self):
        # The result from mission_reward_only is a list of translated strings (mocks likely return the key if not configured otherwise, or we can just check structure)
        result = self.finder.resource_near("biotech conductors", "Sol", None)
        # We expect a list
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        # Check if the text mimics what we see in source, assuming default mock behavior for _
        # If _ returns the string as is:
        self.assertTrue(any("Mission reward only" in str(line) for line in result))

    @patch('edr.controllers.edrresourcefinder.copy')
    def test_from_dav_hope(self, mock_copy):
        self.edr_systems.distance.return_value = 100
        # Mocking the _ function to just return the string
        with patch('edr.controllers.edrresourcefinder._', side_effect=lambda x: x):
            result = self.finder.from_dav_hope("chemical manipulators", "Sol", None)
            self.assertTrue(any("Dav's Hope" in line for line in result))
            mock_copy.assert_called_with("Hyades Sector DR-V c2-23")

    @patch('edr.controllers.edrresourcefinder.copy')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"name": "SelPlanet", "coords": {"x":0,"y":0,"z":0}, "planet": "1", "gravity": 1.0, "distanceToArrival": 100}]')
    @patch('json.loads')
    def test_recommend_prospecting_planet_selenium(self, mock_json_loads, mock_file, mock_copy):
        mock_json_loads.return_value = [{"name": "SelPlanet", "coords": {"x":0,"y":0,"z":0}, "planet": "1", "gravity": 1.0, "distanceToArrival": 100}]
        self.edr_systems.distance_with_coords.return_value = 10
        
        with patch('edr.controllers.edrresourcefinder._', side_effect=lambda x: x):
            result = self.finder.recommend_prospecting_planet_for_selenium("selenium", "Sol", None)
            self.assertTrue(result)
            self.assertTrue(any("SelPlanet" in line for line in result))

if __name__ == '__main__':
    unittest.main()
