import sys
import os

# Add project and edr directories to sys.path
current_dir = os.path.dirname(__file__)
edr_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
root_dir = os.path.abspath(os.path.join(edr_dir, os.pardir))
sys.path.insert(0, root_dir)
sys.path.insert(0, edr_dir)

from unittest import TestCase, main
from edcargo import EDCargo # EDR_INTERNAL

class TestEDCargo(TestCase):
    def setUp(self):
        self.cargo = EDCargo()

    def test_update(self):
        event = {
            "Inventory": [
                {"Name": "Gold", "Count": 5},
                {"Name": "Silver", "Count": 12},
                {"Name": None, "Count": 3},
            ]
        }
        self.cargo.update(event)
        self.assertEqual(self.cargo.how_many("Gold"), 5)
        self.assertEqual(self.cargo.how_many("Silver"), 12)
        # Items with no name should be ignored
        self.assertEqual(self.cargo.how_many(None), 0)
        self.assertEqual(self.cargo.how_many(""), 0)

    def test_collect_valid(self):
        # Only "CollectCargo" events should affect inventory
        event = {"event": "CollectCargo", "Type": "Gold"}
        self.cargo.collect(event)
        self.assertEqual(self.cargo.how_many("Gold"), 1)
        # Collect again should increment
        self.cargo.collect(event)
        self.assertEqual(self.cargo.how_many("Gold"), 2)

    def test_collect_invalid_event(self):
        event = {"event": "OtherEvent", "Type": "Gold"}
        self.cargo.collect(event)
        self.assertEqual(self.cargo.how_many("Gold"), 0)

    def test_eject_valid(self):
        # Prepare inventory
        self.cargo.inventory = {"Gold": 5, "Silver": 3}
        eject_event = {"event": "EjectCargo", "Type": "Gold", "Count": 2}
        self.cargo.eject(eject_event)
        self.assertEqual(self.cargo.how_many("Gold"), 3)
        # Eject more than available should floor at 0
        eject_event2 = {"event": "EjectCargo", "Type": "Silver", "Count": 5}
        self.cargo.eject(eject_event2)
        self.assertEqual(self.cargo.how_many("Silver"), 0)

    def test_how_many(self):
        self.cargo.inventory = {"Platinum": 7}
        self.assertEqual(self.cargo.how_many("Platinum"), 7)
        self.assertEqual(self.cargo.how_many("Nonexistent"), 0)

if __name__ == '__main__':
    main()
