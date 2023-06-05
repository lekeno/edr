from __future__ import absolute_import
import copy
from pickle import TRUE
import re

import edtime
from edrlog import EDRLog
from edri18n import _
EDRLOG = EDRLog()

class EDRFleetCarrier(object):
    def __init__(self):
        self.id = None
        self.type = "FleetCarrier"
        self.callsign = None
        self.name = None
        self.access = "none"
        self.allow_notorious = False
        self._position = {"system": None, "body": None}
        self.departure = {
            "time": None, 
            "destination": None,
            "body": None,
            "requested": None,
            "lockdown": None
        }
        self.decommission_time = None
        self.purchase_orders = {}
        self.sale_orders = {}
        self.market_updated = False
        self.fuel_level = None
        self.decommission = False
        self.space_usage = {}
        self.finance = {}
        self.services = {}
        self.ship_packs = {}
        self.module_packs = {}
        self.bar = None


    def __reset(self):
        self.id = None
        self.type = "FleetCarrier"
        self.callsign = None
        self.name = None
        self.access = "none"
        self.allow_notorious = False
        self._position = {"system": None, "body": None}
        self.departure = {"time": None, "destination": None}
        self.decommission_time = None
        self.purchase_orders = {}
        self.sale_orders = {}
        self.market_updated = False
        self.fuel_level = None
        self.decommission = False
        self.space_usage = {}
        self.finance = {}
        self.services = {}
        self.ship_packs = {}
        self.module_packs = {}


    def bought(self, buy_event):
        self.__reset()
        self.id = buy_event.get("CarrierID", None)
        self.callsign = buy_event.get("Callsign", None)
        self._position["system"] = buy_event.get("Location", None)

    def update_from_location_or_docking(self, entry):
        if not entry.get("event", None) in ["Location", "Docked"]:
            return False

        if entry.get("StationType", None) != "FleetCarrier":
            return False

        if self.id and self.id != entry.get("MarketID", None):
            self.__reset()
        
        self.id = entry.get("MarketID", None)
        self.callsign = entry.get("StationName", None)
        self.name = entry.get("Name", None)
        self._position = {
            "system": entry.get("StarSystem", None),
            "body": entry.get("Body", None)
        }
        # TODO "StationServices":[ "dock", "autodock", "commodities", "contacts", "exploration", "outfitting", "crewlounge", "rearm", "refuel", "repair", "shipyard", "engineer", "flightcontroller", "stationoperations", "stationMenu", "carriermanagement", "carrierfuel", "livery", "voucherredemption", "socialspace", "bartender", "vistagenomics", "pioneersupplies" ],
        return True
    
    def update_from_stats(self, fc_stats_event):
        if self.id and self.id != fc_stats_event.get("CarrierID", None):
            self.__reset()
        self.id = fc_stats_event.get("CarrierID", None)
        self.callsign = fc_stats_event.get("Callsign", None)
        self.name = fc_stats_event.get("Name", None)
        self.access = fc_stats_event.get("DockingAccess", "none")
        self.allow_notorious = fc_stats_event.get("AllowNotorious", False)
        self.fuel_level = fc_stats_event.get("FuelLevel", None)
        self.decommission = fc_stats_event.get("PendingDecommission", False)
        self.space_usage = fc_stats_event.get("SpaceUsage", {})
        self.finance = fc_stats_event.get("Finance", {})
        if fc_stats_event.get("Crew", {}):
            for crew_description in fc_stats_event["Crew"]:
                self.__tweak_service(crew_description)
        self.ship_packs = fc_stats_event.get("ShipPacks", {})
        self.module_packs = fc_stats_event.get("ModulePacks", {})

    def update_from_fcmaterials(self, fc_materials_event):
        if self.id and self.id != fc_materials_event.get("MarketID", None):
            self.__reset()
        self.id = fc_materials_event.get("MarketID", None)
        self.callsign = fc_materials_event.get("CarrierID", None)
        self.name = fc_materials_event.get("CarrierName", None)
        self.bar = EDRFleetCarrierBar()
        return self.bar.from_fcmaterials(fc_materials_event)
        
    def jump_requested(self, jump_request_event):
        if self.id and self.id != jump_request_event.get("CarrierID", None):
            self.__reset()
        self.id = jump_request_event.get("CarrierID", None)
        self.__update_position()
        request_time = edtime.EDTime()
        request_time.from_journal_timestamp(jump_request_event["timestamp"])
        jump_time = edtime.EDTime()
        lockdown_time = edtime.EDTime()
        if "DepartureTime" in jump_request_event:
            jump_time.from_journal_timestamp(jump_request_event["DepartureTime"])
            lockdown_time.from_journal_timestamp(jump_request_event["DepartureTime"])
            lockdown_time.rewind(60*3+20)
        else:
            jump_time.from_journal_timestamp(jump_request_event["timestamp"])
            jump_time.advance(60*15)
            lockdown_time.from_journal_timestamp(jump_request_event["timestamp"])
            lockdown_time.advance(60*(15-3)-20)
        
        request_time_epoch = request_time.as_py_epoch()
        jump_time_epoch = jump_time.as_py_epoch()
        lockdown_time_epoch = jump_time.as_py_epoch()

        self.departure = {
            "requested": request_time_epoch,
            "time": jump_time_epoch,
            "lockdown": lockdown_time_epoch,
            "destination": jump_request_event.get("SystemName", None),
            "body": jump_request_event.get("Body", None),
        }

    def jump_cancelled(self, jump_cancel_event):
        if self.id and self.id != jump_cancel_event.get("CarrierID", None):
            self.__reset()
        self.id = jump_cancel_event.get("CarrierID", None)
        self.departure = {"time": None, "destination": None}
        self.__update_position()

    @property
    def position(self):
        self.__update_position()
        return self._position["system"]

    def __update_position(self):
        now = edtime.EDTime.py_epoch_now()
        if self.decommission_time and now > self.decommission_time:
            self.__reset()
            return

        if self.is_parked():
            return
        
        if now < self.departure["time"]:
            return
        
        self._position["system"] = self.departure["destination"]
        self.departure = {
            "time": None, 
            "destination": None,
            "body": None,
            "requested": None,
            "lockdown": None
        }

    def update_docking_permissions(self, event):
        if self.id and self.id != event.get("CarrierID", None):
            self.__reset()
        self.id = event.get("CarrierID", None)
        self.access = event.get("DockingAccess", "none")
        self.allow_notorious = event.get("AllowNotorious", False)

    def update_from_jump_if_relevant(self, event):
        if self.id is None or self.id != event.get("MarketID", None):
            return
        self._position = {"system": event.get("StarSystem", None), "body": event.get("Body", None)}
        self.departure = {
            "time": None, 
            "destination": None,
            "body": None,
            "requested": None,
            "lockdown": None
        }

    def update_star_system_if_relevant(self, star_system, market_id, station_name):
        if market_id is None and station_name is None:
            return False
        if (self.id == market_id) or (self.callsign == station_name):
            self._position["system"] = star_system
            return True
        if (self.id == None) and market_id and station_name:
            self.id = market_id
            self.callsign = station_name
            self._position["system"] = star_system
            return True
        return False

    def cancel_decommission(self, event):
        if self.id and self.id != event.get("CarrierID", None):
            self.__reset()
        self.id = event.get("CarrierID", None)

    def decommission_requested(self, event):
        if self.id and self.id != event.get("CarrierID", None):
            self.__reset()
        self.id = event.get("CarrierID", None)
        self.decommission_time = event.get("ScrapTime", None)

    def is_parked(self):
        return self.departure["destination"] is None or self.departure["time"] is None

    def is_open_to_all(self, include_notorious=False):
        return self.access == "all" and self.allow_notorious if include_notorious else True

    def json_jump_schedule(self):
        self.__update_position()
        if self.id is None:
            return None

        if self.is_parked():
            return None

        return self.json_status()

    def json_status(self):
        self.__update_position()
        if self.id is None:
            return None

        return {
            "id": self.id,
            "callsign": self.callsign,
            "name": self.name,
            "requested": self.departure["requested"] * 1000 if self.departure["requested"] else None,
            "from": self.position,
            "to": self.departure["destination"],
            "body": self.departure["body"],
            "lockdown": self.departure["lockdown"] * 1000 if self.departure["lockdown"] else None,
            "at": self.departure["time"] * 1000 if self.departure["time"] else None,
            "access": self.access,
            "allow_notorious": self.allow_notorious
        }

    # TODO see if market.json reflects the market of fleet carriers, including one's own
    # Market event + market.json file
    # perhaps tell the player if the market has a useful item (e.g. eng mats)
    # TODO hint about complementing certain blueprints/upgrade/pinned odyssey things?
    # TODO timestamp on market orders
    def trade_order(self, entry):
        if entry.get("event", None) != "CarrierTradeOrder":
            return False

        if entry.get("Commodity", None) is None:
            return False
        
        item = entry["Commodity"]
        if entry.get("CarrierID", None) != self.id:
            return False
        
        if entry.get("CancelTrade",False) == True:
            return self.__cancel_order(item)

        if entry.get("PurchaseOrder", 0) > 0:
            return self.__purchase_order(item, entry.get("Commodity_Localised", item), entry["Price"], entry["PurchaseOrder"])

        if entry.get("SaleOrder", 0) > 0:
            return self.__sale_order(item, entry.get("Commodity_Localised", item), entry["Price"], entry["SaleOrder"])
        
    def __cancel_order(self, item):
        try:
            del self.sale_orders[item]
            self.market_updated = True
        except:
            pass

        try:
            del self.purchase_orders[item]
            self.market_updated = True
        except:
            pass
    
    def __purchase_order(self, item, localized_item, price, quantity):
        now = edtime.EDTime.py_epoch_now()
        self.purchase_orders[item] = {"price": price, "quantity": quantity, "l10n": localized_item, "timestamp": now}
        self.market_updated = True
        try:
            del self.sale_orders[item]
        except:
            pass

    def __sale_order(self, item, localized_item, price, quantity):
        now = edtime.EDTime.py_epoch_now()
        self.sale_orders[item] = {"price": price, "quantity": quantity, "l10n": localized_item, "timestamp": now}
        self.market_updated = True
        try:
            del self.purchase_orders[item]
        except:
            pass
    
    def json_market(self, timeframe=None):
        self.__update_position()
        if self.id is None:
            return None

        since = edtime.EDTime.js_epoch_now()
        if timeframe:
            since -= timeframe*1000
        return {
            "id": self.id,
            "callsign": self.callsign,
            "name": self.name,
            "location": self._position,
            "access": self.access,
            "allow_notorious": self.allow_notorious,
            "sales": self.sale_orders_within(timeframe),
            "purchases": self.purchase_orders_within(timeframe),
            "timestamp": since
        }

    def sale_orders_within(self, timeframe):
        all = copy.deepcopy(self.sale_orders)
        if timeframe is None:
            return all
        threshold = edtime.EDTime.py_epoch_now() - timeframe
        return {item: values for item, values in all.items() if values["timestamp"] >= threshold}
        

    def purchase_orders_within(self, timeframe):
        all = copy.deepcopy(self.purchase_orders)
        if timeframe is None:
            return all
        threshold = edtime.EDTime.py_epoch_now() - timeframe
        return {item: values for item, values in all.items() if values["timestamp"] >= threshold}

    def text_summary(self, timeframe=None):
        self.__update_position()
        if self.id is None:
            return None

        header = _("Fleet Carrier [{}] - {}").format(self.callsign, self.name)
        key_info = _("Location:  \t{}\nAccess:    \t{}\nNotorious: \t{}").format(self.position, self.access, _("allowed") if self.allow_notorious else _("disallowed"))
        # TODO add services, tax, etc.
        details_purchases = []
        details_sales = []
        orders = self.purchase_orders_within(timeframe)
        for order in orders:
            quantity = orders[order]["quantity"]
            item = orders[order]["l10n"][:30]
            price = orders[order]["price"]
            details_purchases.append(f'{quantity: >8} {item: <30} {price: >10n}')

        orders = self.sale_orders_within(timeframe)
        for order in orders:
            quantity = orders[order]["quantity"]
            item = orders[order]["l10n"][:30]
            price = orders[order]["price"]
            details_sales.append(f'{quantity: >8} {item: <30} {price: >10n}')

        summary = header
        summary += "\n"
        summary += key_info
        summary += "\n"
        if details_sales:
            summary += "\n"
            summary += _("[Selling]\n")
            summary += _(f'{"Quantity": >8} {"Item": <30} {"Price (cr)": >10}\n')
            summary += "\n".join(details_sales)
            summary += "\n"
        if details_purchases:
            summary += "\n"
            summary += _("[Buying]\n")
            summary += _(f'{"Quantity": >8} {"Item": <30} {"Price (cr)": >10}\n')
            summary += "\n".join(details_purchases)
            summary += "\n"

        timestamp = edtime.EDTime()
        summary += _("\n ----===<<  As of {}   -   Info provided by ED Recon  >>===----").format(timestamp.as_journal_timestamp())
        
        return summary

    def acknowledge_market(self):
        self.market_updated = False

    def has_market_changed(self):
        return self.market_updated

    def tweak_crew_service(self, entry):
        if entry.get("event", None) != "CarrierCrewServices":
            return False

        if entry.get("CarrierID", None) != self.id:
            return False

        service = entry.get("CrewRole", None)
        operation = entry.get("Operation", None)
        crew = entry.get("CrewName", None)
        if not (service and operation and crew):
            return False
        
        operation = operation.lower()
        if operation == "activate":
            if self.services[service.lower()]:
                self.services[service.lower()]["active"] = True
                self.services[service.lower()]["enabled"] = True
            else:
                self.services[service.lower()] = {"active": True, "crew": crew, "enabled": True}
        elif operation == "deactivate":
            if self.services[service.lower()]:
                self.services[service.lower()]["active"] = False
            else:
                self.services[service.lower()] = {"active": False, "crew": crew, "enabled": True}
        elif operation == "replace":
            if self.services[service.lower()]:
                self.services[service.lower()]["crew"] = crew
            else:
                self.services[service.lower()] = {"active": True, "crew": crew, "enabled": True}
        elif operation == "pause":
            if self.services[service.lower()]:
                self.services[service.lower()]["active"] = True
                self.services[service.lower()]["enabled"] = False
            else:
                self.services[service.lower()] = {"active": True, "crew": crew, "enabled": False}
        elif operation == "resume":
            if self.services[service.lower()]:
                self.services[service.lower()]["active"] = True
                self.services[service.lower()]["enabled"] = True
            else:
                self.services[service.lower()] = {"active": True, "crew": crew, "enabled": True}


    def __tweak_service(self, crew__description):
        role = crew__description.get("CrewRole", None)
        activated = crew__description.get("Activated", False)
        enabled = crew__description.get("Enabled", False)
        name = crew__description.get("CrewName", None)
        if not role:
            return
        role = role.lower()
        if role not in self.services:
            self.services[role] = {"active": activated, "enabled": enabled, "crew": name}
        else:
            self.services[role]["active"] = activated
            self.services[role]["enabled"] = enabled
            if name:
                self.services[role]["crew"] = name

class EDRFleetCarrierBar(object):
    def __init__(self):
        self.items = {}
        self.updated = False
        self.timestamp = edtime.EDTime()
    
    def from_fcmaterials(self, entry):
        self.items = {}

        if entry.get("event", "") != "FCMaterials":
            return False

        items = entry.get("Items", [])
        self.timestamp = edtime.EDTime()
        self.updated = True
        for item in items:
            listing = item
            if listing["Stock"] > 0 or listing["Demand"] > 0:
                name_regex = r"^\$([a-z]+)_name;$"
                m = re.match(name_regex, listing["Name"])
                if m:
                    name = m.group(1)
                    self.items[name] = {
                        "price": listing["Price"],
                        "stock": listing["Stock"],
                        "demand": listing["Demand"]
                    }

        return True

    def acknowledge(self):
        self.bar_updated = False

    def has_changed(self):
        return self.updated
    
    def items_in_stock(self):
        in_stock = {}
        for item in self.items:
            if self.items[item]["stock"] > 0:
                in_stock[item] = copy.deepcopy(self.items[item])

        return in_stock

    def items_in_demand(self):
        in_demand = {}
        for item in self.items:
            if self.items[item]["demand"] > 0:
                in_demand[item] = copy.deepcopy(self.items[item])

        return in_demand

