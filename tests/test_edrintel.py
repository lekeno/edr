import unittest
from unittest.mock import MagicMock, patch
from edr.controllers.edrintel import EDRIntelManager
from edr.controllers.edrserver import CommsJammedError

class TestEDRIntelManager(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.player.in_open.return_value = True
        self.mock_client.player.powerplay = "TestPower"
        
        self.intel_manager = EDRIntelManager(self.mock_client)

    def test_who_found(self):
        mock_profile = MagicMock()
        mock_profile.cid = "123"
        mock_profile.short_profile.return_value = "Wanted by Federation"
        self.mock_client.cmdr.return_value = mock_profile
        
        self.mock_client.edrlegal.summarize.return_value = {"overview": "5,000 CR Bounty"}

        self.intel_manager.who("Jameson")
        
        self.mock_client.cmdr.assert_called_with("Jameson", False, check_inara_server=True)
        self.mock_client.edrlegal.summarize.assert_called_with("123")
        self.mock_client._EDRClient__intel.assert_called()
        
        # Verify the details passed to __intel contains both profile and legal overview
        args, kwargs = self.mock_client._EDRClient__intel.call_args
        details = args[1]
        self.assertEqual(len(details), 2)
        self.assertEqual(details[0], "Wanted by Federation")
        self.assertEqual(details[1], "5,000 CR Bounty")

    def test_who_not_found(self):
        self.mock_client.cmdr.return_value = None
        
        self.intel_manager.who("Nobody")
        
        self.mock_client._EDRClient__intel.assert_called()
        args, kwargs = self.mock_client._EDRClient__intel.call_args
        self.assertIn("No info", args[1][0])

    def test_who_comms_jammed(self):
        self.mock_client.cmdr.side_effect = CommsJammedError("test")
        
        self.intel_manager.who("Jammer")
        
        self.mock_client._EDRClient__commsjammed.assert_called_once()

    def test_where_found(self):
        mock_opp_outlaws = MagicMock()
        mock_opp_outlaws.where.return_value = {"timestamp": 1000, "readable": ["Seen in Sol"]}
        
        mock_opp_enemies = MagicMock()
        mock_opp_enemies.where.return_value = {"timestamp": 2000, "readable": ["Seen in Achenar earlier"]}

        self.mock_client.edropponents = {"OUTLAWS": mock_opp_outlaws, "ENEMIES": mock_opp_enemies}
        
        self.intel_manager.where("Target")
        
        # Should pick the latest timestamp (2000)
        self.mock_client._EDRClient__intel.assert_called()
        args, kwargs = self.mock_client._EDRClient__intel.call_args
        self.assertEqual(args[1], ["Seen in Achenar earlier"])

    def test_where_comms_jammed(self):
        mock_opp = MagicMock()
        mock_opp.where.side_effect = CommsJammedError("test")
        self.mock_client.edropponents = {"OUTLAWS": mock_opp}
        
        self.intel_manager.where("Jammer")
        
        self.mock_client._EDRClient__commsjammed.assert_called_once()

if __name__ == '__main__':
    unittest.main()
