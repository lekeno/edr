import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrguidance import EDRGuidanceManager
from edr.controllers.edrserver import CommsJammedError

class TestEDRGuidanceManager(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.player.in_open.return_value = True
        self.mock_client.player.body = "Earth"
        self.mock_client.player.star_system = "Sol"
        
        self.guidance_manager = EDRGuidanceManager(self.mock_client)

    def test_notams(self):
        self.mock_client.edrsystems.systems_with_active_notams.return_value = ["Lave", "Diso"]
        
        self.guidance_manager.notams()
        
        self.mock_client.edrsystems.systems_with_active_notams.assert_called_once()
        self.mock_client._EDRClient__sitrep.assert_called()
        args, kwargs = self.mock_client._EDRClient__sitrep.call_args
        self.assertIn("Lave; Diso", args[1][0])

    def test_notam(self):
        self.mock_client.edrsystems.active_notams.return_value = ["Griefer activity reported"]
        
        self.guidance_manager.notam("Lave")
        
        self.mock_client.edrsystems.active_notams.assert_called_with("Lave")
        self.mock_client._EDRClient__sitrep.assert_called()
        args, kwargs = self.mock_client._EDRClient__sitrep.call_args
        self.assertEqual(args[1], ["Griefer activity reported"])

    def test_sitreps(self):
        self.mock_client.edrsystems.systems_with_recent_activity.return_value = {"High Traffic": ["Shinrarta Dezhra"]}
        
        self.guidance_manager.sitreps()
        
        self.mock_client.edrsystems.systems_with_recent_activity.assert_called_once()
        self.mock_client._EDRClient__sitrep.assert_called()
        args, kwargs = self.mock_client._EDRClient__sitrep.call_args
        self.assertIn("High Traffic: Shinrarta Dezhra", args[1][0])

    def test_distance(self):
        self.mock_client.edrsystems.distance.return_value = 10.5
        self.mock_client.edrsystems.jumping_time.return_value = 60
        self.mock_client.edrsystems.transfer_time.return_value = 600
        
        self.guidance_manager.distance("Sol", "Alpha Centauri")
        
        self.mock_client.edrsystems.distance.assert_called_with("Sol", "Alpha Centauri")
        self.mock_client._EDRClient__notify.assert_called()
        args, kwargs = self.mock_client._EDRClient__notify.call_args
        self.assertEqual(args[0], "Distance")
        self.assertTrue(any("10.5ly" in s for s in args[1]))

    def test_distance_fail(self):
        self.mock_client.edrsystems.distance.side_effect = ValueError()
        
        self.guidance_manager.distance("Sol", "InvalidSystem")
        
        self.mock_client._EDRClient__notify.assert_called()
        args, kwargs = self.mock_client._EDRClient__notify.call_args
        self.assertTrue(any("Couldn't calculate a distance" in s for s in args[1]))

    @patch('edr.controllers.edrguidance.copy')
    def test_navigation(self, mock_copy):
        self.guidance_manager.navigation(45.0, 90.0, "Testing")
        
        self.assertEqual(self.mock_client.player.planetary_destination.latitude, 45.0)
        self.assertEqual(self.mock_client.player.planetary_destination.longitude, 90.0)
        self.mock_client._EDRClient__notify.assert_called()
        
        # Verify JSON clipboard export
        mock_copy.assert_called_once()
        import json
        payload = json.loads(mock_copy.call_args[0][0])
        self.assertIn("sol", payload)
        self.assertIn("earth", payload["sol"])
        self.assertEqual(payload["sol"]["earth"][0]["title"], "Testing")

if __name__ == '__main__':
    unittest.main()
