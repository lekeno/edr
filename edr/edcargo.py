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

    def how_many(self, item_name):
        item = self.inventory.get(item_name, {"Count": 0})
        return item["Count"]
