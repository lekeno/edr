# coding= utf-8
from __future__ import absolute_import

class EDCargo(object):
    def __init__(self):
        self.inventory = {}

    def update(self, cargo_event):
        ed_inventory = cargo_event.get("Inventory", [])
        for item in ed_inventory:
            name = item.get("Name", None)
            self.inventory[name] = item.get("Count", 0)

    def collect(self, collect_event):
        if collect_event.get("event", None) != "CollectCargo":
            return
        
        name = collect_event.get("Type", None)
        if name:
            self.inventory[name] += 1

    def eject(self, eject_event):
        if eject_event.get("event", None) != "EjectCargo":
            return
        
        name = eject_event.get("Type", None)
        quantity = eject_event.get("Count", None)
        if name and quantity:
            self.inventory[name] -= quantity

    def how_many(self, item_name):
        item_count = self.inventory.get(item_name, 0)
        return item_count
