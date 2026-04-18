
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edinstance import EDInstance

class TestEDInstance(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.models.edinstance.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.py_epoch_now.return_value = 1000

        self.vehicle_factory_patch = patch('edr.models.edinstance.EDVehicleFactory')
        self.mock_vehicle_factory = self.vehicle_factory_patch.start()
        self.mock_vehicle_factory.canonicalize.side_effect = lambda x: x.lower() if x else ""

    def tearDown(self):
        self.time_patch.stop()
        self.vehicle_factory_patch.stop()

    def test_initialization(self):
        instance = EDInstance()
        self.assertEqual(instance.timestamp, 1000)
        self.assertTrue(instance.is_void_of_player())
        self.assertTrue(instance.is_totally_empty())

    def test_player_tracking(self):
        instance = EDInstance()
        cmdr = MagicMock()
        cmdr.name = "CmdrTest"
        cmdr.json.return_value = {"name": "CmdrTest"}

        # Player In
        self.mock_time.py_epoch_now.return_value = 1001
        instance.player_in(cmdr)
        
        self.assertFalse(instance.is_void_of_player())
        self.assertEqual(instance.players_nb(), 1)
        self.assertEqual(instance.player("CmdrTest"), cmdr)
        
        # Player Out
        self.mock_time.py_epoch_now.return_value = 1002
        instance.player_out("CmdrTest")
        
        self.assertTrue(instance.is_void_of_player())
        self.assertEqual(instance.players_nb(), 0)

    def test_npc_tracking(self):
        instance = EDInstance()
        pilot = MagicMock()
        pilot.name = "Pirate"
        pilot.rank = "Elite"
        pilot.vehicle.name = "anaconda"

        # NPC In
        instance.npc_in(pilot)
        self.assertFalse(instance.is_totally_empty())
        
        # Retrieve NPC
        # ideally we should mock EDVehicleFactory to ensure consistent name generation
        # but let's assume the key generation works as expected: "PirateEliteAnaconda"
        retrieved = instance.npc("Pirate", "Elite", "Anaconda")
        self.assertEqual(retrieved, pilot)
        
        # NPC Out
        # npc_out(self, name, ship_internal_name=None, rank=None)
        instance.npc_out("Pirate", "Anaconda", "Elite")
        self.assertTrue(instance.is_totally_empty())

    def test_reset(self):
        instance = EDInstance()
        cmdr = MagicMock()
        cmdr.name = "CmdrTest"
        instance.player_in(cmdr)
        
        instance.reset()
        self.assertTrue(instance.is_void_of_player())
        self.assertTrue(instance.is_totally_empty())

    def test_any_player_beside(self):
        instance = EDInstance()
        cmdr1 = MagicMock()
        cmdr1.name = "Cmdr1"
        cmdr2 = MagicMock()
        cmdr2.name = "Cmdr2"
        
        instance.player_in(cmdr1)
        instance.player_in(cmdr2)
        
        self.assertTrue(instance.any_player_beside(["Cmdr1"]))
        self.assertFalse(instance.any_player_beside(["Cmdr1", "Cmdr2"]))

    def test_json_and_noteworthy(self):
        instance = EDInstance()
        cmdr = MagicMock()
        cmdr.name = "CmdrTest"
        cmdr.json.return_value = {"name": "CmdrTest"}
        
        instance.player_in(cmdr)
        
        # JSON
        state = instance.json()
        self.assertIn("cmdrtest", state)
        
        # Noteworthy changes
        changes = instance.noteworthy_changes_json()
        self.assertIsNotNone(changes)
        self.assertEqual(len(changes["players"]), 1)
        
        # Second call, no changes, should be None
        changes = instance.noteworthy_changes_json()
        self.assertIsNone(changes)

    def test_presence_of_outlaw(self):
        instance = EDInstance()
        cmdr = MagicMock()
        cmdr.name = "Outlaw"
        cmdr.bounty = 100000
        instance.player_in(cmdr)
        
        mock_edrcmdrs = MagicMock()
        mock_profile = MagicMock()
        mock_profile.is_friend.return_value = False
        mock_profile.is_ally.return_value = False
        mock_edrcmdrs.cmdr.return_value = mock_profile
        
        self.assertTrue(instance.presence_of_outlaw_players(mock_edrcmdrs))

if __name__ == '__main__':
    unittest.main()