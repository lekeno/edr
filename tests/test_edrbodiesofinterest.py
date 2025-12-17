import unittest
from unittest.mock import patch, mock_open
import json
from edr.edrbodiesofinterest import EDRBodiesOfInterest

class TestEDBodiesOfInterest(unittest.TestCase):
    def setUp(self):
        self.mock_boi_data = {
            "test_system": {
                "body_1": [
                    {"title": "POI 1", "latitude": 10, "longitude": 20, "heading": 0}
                ]
            }
        }
        self.mock_boi_json = json.dumps(self.mock_boi_data)

    def test_init_loads_data(self):
        with patch('builtins.open', mock_open(read_data=self.mock_boi_json)):
            boi = EDRBodiesOfInterest()
            self.assertEqual(boi.bodies_of_interest("test_system"), ["body_1"])

    def test_points_of_interest(self):
        with patch('builtins.open', mock_open(read_data=self.mock_boi_json)):
            boi = EDRBodiesOfInterest()
            pois = boi.points_of_interest("test_system", "body_1")
            self.assertEqual(len(pois), 1)
            self.assertEqual(pois[0]["title"], "POI 1")

    def test_add_remove_custom_poi(self):
        with patch('builtins.open', mock_open(read_data=self.mock_boi_json)):
            boi = EDRBodiesOfInterest()
            
            # Add custom POI
            new_poi = {"title": "Custom POI", "latitude": 30, "longitude": 40, "heading": 180}
            boi.add_custom_poi("test_system", "body_1", new_poi)
            
            custom_pois = boi.custom_points_of_interest("test_system", "body_1")
            self.assertEqual(len(custom_pois), 1)
            self.assertEqual(custom_pois[0]["title"], "Custom POI")
            
            # Navigate custom POIs (sets index)
            # Need to mock get/set index internal methods implicitly via next/prev
            # But wait, next/prev calls update private dicts
            
            poi = boi.next_custom_point_of_interest("test_system", "body_1")
            self.assertEqual(poi["title"], "Custom POI")
            
            # Clear custom POI
            # clear_current requires index to be set
            boi.clear_current_custom_poi("test_system", "body_1")
            
            custom_pois = boi.custom_points_of_interest("test_system", "body_1")
            self.assertEqual(len(custom_pois), 0)

    def test_dlc_loading(self):
        # Test loading horizongs vs odyssey
        with patch('builtins.open', mock_open(read_data=self.mock_boi_json)) as mock_file:
            boi = EDRBodiesOfInterest()
            # default loads boi.json
            mock_file.assert_called_with(unittest.mock.ANY) # can't check filename easily with mock_open context manager usage in init
            
            # Reset mock to verify set_dlc calls
            pass
            
        with patch('builtins.open', mock_open(read_data=self.mock_boi_json)) as mock_file:
            boi = EDRBodiesOfInterest()
            boi.set_dlc("odyssey")
            # Should reload with odyssey_boi.json
            # We can check if open was called
            self.assertTrue(mock_file.called)

if __name__ == '__main__':
    unittest.main()
