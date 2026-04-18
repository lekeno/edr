
import unittest
from unittest.mock import patch, mock_open
import json
from edr.models import edrlandables

class TestEDRLandables(unittest.TestCase):
    def setUp(self):
        edrlandables.EDRLandables._MAPS = None

    def tearDown(self):
        edrlandables.EDRLandables._MAPS = None

    @patch('builtins.open', new_callable=mock_open, read_data='{"system": {"station": {"type": {"map": "map_data"}}}}')
    @patch('json.load')
    def test_load_maps_success(self, mock_json_load, mock_file):
        expected_data = {"system": {"station": {"type": {"map": "map_data"}}}}
        mock_json_load.return_value = expected_data
        
        maps = edrlandables.EDRLandables.load_maps()
        self.assertEqual(maps, expected_data)
        # Verify it only loads once
        maps2 = edrlandables.EDRLandables.load_maps()
        self.assertIs(maps, maps2)
        mock_file.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_maps_failure(self, mock_file):
        maps = edrlandables.EDRLandables.load_maps()
        self.assertEqual(maps, {})

    @patch('edr.models.edrlandables.EDRLandables.load_maps')
    def test_map_for_exact_match(self, mock_load_maps):
        mock_load_maps.return_value = {
            "sol": {
                "earth": {
                    "planet": {"map": "earth_map"}
                }
            }
        }
        
        result = edrlandables.EDRLandables.map_for("Sol", "Earth", "planet")
        self.assertEqual(result, {"map": "earth_map"})

    @patch('edr.models.edrlandables.EDRLandables.load_maps')
    def test_map_for_system_not_found(self, mock_load_maps):
        mock_load_maps.return_value = {
            "sol": {}
        }
        
        # Should fallback to "*" logic if implemented, or return empty
        # In current code:
        # if not star_system or star_system.lower() not in maps: star_system = "*"
        # locations = maps.get(c_star_system, {}) -> if "*" logic applies, it uses "*"
        
        # Case 1: System not found, no "*" in map
        result = edrlandables.EDRLandables.map_for("Unknown", "Place", "Type")
        self.assertEqual(result, {})

    @patch('edr.models.edrlandables.EDRLandables.load_maps')
    def test_map_for_location_fallback(self, mock_load_maps):
        mock_load_maps.return_value = {
            "sol": {
                "earth": {"planet": {"map": "earth_map"}},
                "*": {"planet": {"map": "default_sol_map"}} # Fallback for unknown location in known system?
                # Code says: if c_location_name not in locations: c_location_name = "*"
            }
        }
        
        # Known system, unknown location
        result = edrlandables.EDRLandables.map_for("Sol", "Mars", "planet")
        self.assertEqual(result, {"map": "default_sol_map"})

    @patch('edr.models.edrlandables.EDRLandables.load_maps')
    def test_map_for_global_fallback(self, mock_load_maps):
        mock_load_maps.return_value = {
            "*": {
                "*": {
                    "station": {"map": "generic_station_map"},
                    "soon tm": {"map": "very_generic_map"}
                }
            }
        }
        
        # Unknown system, unknown location
        result = edrlandables.EDRLandables.map_for("Unknown", "Place", "station")
        self.assertEqual(result, {"map": "generic_station_map"})

        # Unknown system, unknown location, unknown type
        result = edrlandables.EDRLandables.map_for("Unknown", "Place", "unknown_type")
        self.assertEqual(result, {"map": "very_generic_map"})
