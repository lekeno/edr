
import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
from edr.models.edrinventory import EDRInventory

class TestEDRInventory(unittest.TestCase):
    def setUp(self):
        # Mock the open calls in __init__ to avoid reading/writing real cache files
        # We need to mock 'open' specifically for the cache files, but let it work for others if needed.
        # However, EDRInventory __init__ tries to load pickles immediately.
        pass

    @patch('edr.models.edrinventory.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_initialization(self, mock_file, mock_pickle):
        # Setup mock pickle to return empty dicts
        mock_pickle.load.return_value = {}
        
        inventory = EDRInventory()
        self.assertTrue(inventory.stale_or_incorrect()) # Not initialized with event data yet
        
        # Verify it tried to open the cache files
        self.assertTrue(mock_file.called)

    @patch('edr.models.edrinventory.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_add_subtract(self, mock_file, mock_pickle):
        mock_pickle.load.return_value = {}
        inventory = EDRInventory()
        
        # Test adding a raw material
        inventory.add("Raw", "iron", 10)
        self.assertEqual(inventory.raw["iron"], 10)
        self.assertEqual(inventory.count("iron"), 10)
        
        # Test subtracting
        inventory.substract("Raw", "iron", 5)
        self.assertEqual(inventory.raw["iron"], 5)
        
        # Test removing by subtracting all
        inventory.substract("Raw", "iron", 5)
        self.assertNotIn("iron", inventory.raw)

    @patch('edr.models.edrinventory.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_backpack(self, mock_file, mock_pickle):
        mock_pickle.load.return_value = {}
        inventory = EDRInventory()
        
        # Initialize backpack
        backpack_event = {
            "event": "Backpack",
            "Items": [{"Name": "healthpack", "Count": 5}],
            "Components": [{"Name": "circuitboard", "Count": 2}]
        }
        inventory.initialize(backpack_event)
        
        self.assertEqual(inventory.backpack["item"]["healthpack"], 5)
        self.assertEqual(inventory.backpack["component"]["circuitboard"], 2)
        
        # Test backpack change (Added)
        change_event = {
            "event": "BackpackChange",
            "Added": [{"Name": "healthpack", "Type": "Item", "Count": 2}]
        }
        inventory.backpack_change(change_event)
        self.assertEqual(inventory.backpack["item"]["healthpack"], 7)
        
        # Test backpack change (Removed)
        change_event_remove = {
            "event": "BackpackChange",
            "Removed": [{"Name": "circuitboard", "Type": "Component", "Count": 1}]
        }
        inventory.backpack_change(change_event_remove)
        self.assertEqual(inventory.backpack["component"]["circuitboard"], 1)

    @patch('edr.models.edrinventory.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_initialize_locker(self, mock_file, mock_pickle):
        mock_pickle.load.return_value = {}
        inventory = EDRInventory()
        
        locker_event = {
            "event": "ShipLocker",
            "Items": [{"Name": "consumable", "Count": 10}], # generic name for test
            "Data": [{"Name": "opticalfibre", "Count": 5}] # wrong category in test data, but checking logic
        }
        # Note: opticalfibre is actually a Component in the LUT, but let's stick to what's in the event for structure testing.
        # Actually EDRInventory uses __c_name and LUT to put things in correct dicts usually, 
        # but initialize_locker iterates over specific keys in the event ("Items", "Data", etc).
        
        # Let's use real items
        locker_event = {
            "event": "ShipLocker",
            "Items": [{"Name": "healthpack", "Count": 5}],
            "Components": [{"Name": "circuitboard", "Count": 10}]
        }
        
        inventory.initialize(locker_event)
        self.assertEqual(inventory.items["healthpack"], 5)
        self.assertEqual(inventory.components["circuitboard"], 10)

    @patch('edr.models.edrinventory.pickle')
    @patch('builtins.open', new_callable=mock_open)
    def test_readable_name(self, mock_file, mock_pickle):
        mock_pickle.load.return_value = {}
        inventory = EDRInventory()
        
        self.assertEqual(inventory.readable_name("iron"), "Iron")
        self.assertEqual(inventory.readable_name("unknown_mat"), "unknown_mat")

if __name__ == '__main__':
    unittest.main()