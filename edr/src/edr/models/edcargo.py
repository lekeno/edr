from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL


class EDCargo:
    """
    Tracks the inventory of cargo for a commander.
    """

    def __init__(self):
        """Initialize with an empty inventory."""
        self.inventory = {}

    def update(self, cargo_event):
        """Update the entire inventory from a Cargo event.

        Args:
            cargo_event (dict): The event dictionary containing the inventory list.
        """
        try:
            ed_inventory = cargo_event.get("Inventory", [])
            for item in ed_inventory:
                name = item.get("Name", None)
                if name:
                    self.inventory[name] = item.get("Count", 0)

        except Exception as e:
            EDR_LOG.exception(f"Couldn't process cargo event {cargo_event}: {e}")

    def collect(self, collect_event):
        """Update inventory after collecting an item.

        Args:
            collect_event (dict): The CollectCargo event dictionary.
        """
        if collect_event.get("event", None) != "CollectCargo":
            return

        name = collect_event.get("Type", None)
        if name:
            self.inventory[name] = 1 + self.inventory.get(name, 0)

    def eject(self, eject_event):
        """Update inventory after ejecting an item.

        Args:
            eject_event (dict): The EjectCargo event dictionary.
        """
        if eject_event.get("event", None) != "EjectCargo":
            return

        name = eject_event.get("Type", None)
        quantity = eject_event.get("Count", None)
        if name and quantity:
            self.inventory[name] = max(0, self.inventory.get(name, quantity) - quantity)

    def how_many(self, item_name):
        """Count the quantity of a specific item in the inventory.

        Args:
            item_name (str): The name of the item.

        Returns:
            int: The count of the item, defaults to 0.
        """
        item_count = self.inventory.get(item_name, 0)
        return item_count
