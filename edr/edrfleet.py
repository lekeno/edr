
import os
import sys
import sqlite3
import math

import os
from edvehicles import EDVehicleFactory
from edtime import EDTime
from edrlog import EDR_LOG



class EDRFleet(object):

    SHIP_TYPE_LUT = {
        "fdl": "ferdelance",
        "cobra": "cobramkiii",
        "t6": "type6",
        "t7": "type7",
        "t8": "type8",
        "t9": "type9",
        "t10": "type9_military",
        "t11": "lakonminer",
        "panther": "panthermkii",
        "aspx": "asp",
        "clipper": "empire_trader",
        "dropship": "federation_dropship",
        "beluga": "belugaliner",
        "conda": "anaconda",
        "corvette": "federation_corvette",
        "dbs": "diamondback",
        "courier": "empira_courier",
        "dbx": "diamondbackxl",
        "fas": "federation_dropship_mkii",
        "fgs": "federation_gunship",
        "gunship": "federation_gunship",
        "viper iv": "viper_mkiv",
        "viper 4": "viper_mkiv",
        "cobra iv": "cobramkiv",
        "cobra 4": "cobramkiv",
        "cobra v": "cobramkv",
        "cobra 5": "cobramkv",
        "keelie": "independant_trader",
        "keelback": "independant_trader",
        "asps": "asp_scout",
        "chieftain": "typex",
        "chief": "typex",
        "crusader": "typex_2",
        "challenger": "typex_3",
        "krait": "krait_mkii",
        "phantom": "krait_light",
        "python 2": "python_nx",
        "python II": "python_nx",
    }


    def __init__(self):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'fleet')
        try:
            self.db = sqlite3.connect(path)
            cursor = self.db.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS
                        ships(id INTEGER PRIMARY KEY, type TEXT, localised TEXT, name TEXT,
                        star_system TEXT, ship_market_id INTEGER, value INTEGER, hot INTEGER, piloted INTEGER DEFAULT 0, eta INTEGER DEFAULT 0)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS
                        transits(id INTEGER PRIMARY KEY AUTOINCREMENT, ship_id INTEGER, eta INTEGER, source_system TEXT,
                        destination_system TEXT, source_market_id INTEGER, destination_market_id INTEGER)''')
            self.db.commit()
        except:
            EDR_LOG.log(u"Couldn't open/create the fleet database", "ERROR")
            self.db = None
    
    def update(self, event):
        if self.db is None:
            return
        local_system = event.get("StarSystem", None)
        local_station = event.get("StationName", None)
        local_market_id = event.get("MarketID", None)
        if not local_station or not local_system or not local_market_id:
            return

        here = event.get("ShipsHere", [])
        try:
            cursor = self.db.cursor()
            cursor.execute('DROP TABLE ships')
            cursor.execute('''CREATE TABLE
                      ships(id INTEGER PRIMARY KEY, type TEXT, localised TEXT, name TEXT,
                      star_system TEXT, ship_market_id INTEGER, value INTEGER, hot INTEGER, piloted INTEGER DEFAULT 0, eta INTEGER DEFAULT 0)''')
            self.db.commit()
            for stored_ship in here:
                ship_id = stored_ship.get("ShipID", None)
                ship_type = stored_ship.get("ShipType", "").lower()
                name = stored_ship.get("Name", "").lower()
                localised_type = stored_ship.get("ShipType_Localised", ship_type).lower()
                value = stored_ship.get("Value", None)
                hot = 1 if stored_ship.get("hot", False) else 0
                self.db.execute('''INSERT INTO ships(id, type, localised, name, star_system, ship_market_id, value, hot)
                        VALUES(?,?,?,?,?,?,?,?)''', (ship_id, ship_type, localised_type, name, local_system, local_market_id, value, hot))
            
            remote = event.get("ShipsRemote", [])                
            for stored_ship in remote:
                system = stored_ship.get("StarSystem", "").lower()
                market_id = stored_ship.get("ShipMarketID", None)
                ship_id = stored_ship.get("ShipID", None)
                ship_type = stored_ship.get("ShipType", "").lower()
                name = stored_ship.get("Name", "").lower()
                localised_type = stored_ship.get("ShipType_Localised", ship_type).lower()
                value = stored_ship.get("Value", None)
                hot = 1 if stored_ship.get("hot", False) else 0
                self.db.execute('''INSERT INTO ships(id, type, localised, name, star_system, ship_market_id, value, hot)
                        VALUES(?,?,?,?,?,?,?,?)''', (ship_id, ship_type, localised_type, name, system, market_id, value, hot))
            self.db.commit()
            self.__update()
        except sqlite3.IntegrityError:
            pass

    def where(self, type_or_name):
        if self.db is None:
            return
        self.__update()
        ship_type = self.SHIP_TYPE_LUT.get(type_or_name.lower(), type_or_name)
        check = self.db.execute("SELECT id from ships limit 1")
        if not check.fetchone():
            return False
        cursor = self.db.execute('SELECT name, localised, star_system, eta, ship_market_id FROM ships WHERE (type=? OR name=? OR localised=?) and piloted=0', (ship_type.lower(), type_or_name.lower(), type_or_name.lower(),))
        return cursor.fetchall()

    def sell(self, sell_event):
        if self.db is None:
            return
        if sell_event.get("event", None) not in ["ShipyardSell", "SellShipOnREbuy"]:
            return
        self.__sold(sell_event["SellShipID"])

    def buy(self, buy_event, star_system, storing_ship_name):
        if self.db is None:
            return
        if buy_event.get("event", None) != "ShipyardBuy":
            return
        
        market_id = buy_event.get("MarketID", None)
        if buy_event.get("StoreShipID", None):
            try:
                storing_ship_id = buy_event["StoreShipID"]
                ship_type = buy_event["StoreOldShip"].lower()
                localised = EDVehicleFactory.canonicalize(ship_type)
                self.db.execute('''INSERT INTO ships(id, type, localised, name, star_system, ship_market_id, value, hot)
                            VALUES(?,?,?,?,?,?,?,?)''', (storing_ship_id, ship_type, localised, storing_ship_name, star_system, market_id, 0, 0))
                self.db.execute('DELETE from transits WHERE ship_id=?', (storing_ship_id, ))
                self.db.commit()
            except sqlite3.IntegrityError:
                pass
        elif buy_event.get("SellShipID", None):
            self.__sold(buy_event["SellShipID"])

    def new(self, new_event, star_system):
        if self.db is None:
            return
        if new_event.get("event", None) != "ShipyardNew":
            return
        ship_id = new_event.get("NewShipID", None)
        ship_type = new_event.get("ShipType", "").lower()
        name = ""
        localised_type = new_event.get("ShipType_Localised", ship_type).lower()
        value = 0
        hot = 0
        piloted = 1
        market_id = None
        self.db.execute('''INSERT INTO ships(id, type, localised, name, star_system, ship_market_id, value, hot, piloted)
                        VALUES(?,?,?,?,?,?,?,?,?)''', (ship_id, ship_type, localised_type, name, star_system, market_id, value, hot, piloted))

    def __sold(self, ship_id):
        if self.db is None:
            return
        self.db.execute('DELETE from ships WHERE id=?', (ship_id, ))
        self.db.execute('DELETE from transits WHERE ship_id=?', (ship_id, ))
        self.db.commit()

    def rename(self, rename_event):
        if self.db is None:
            return
        if rename_event.get("event", None) != "SetUserShipName":
            return
        
        ship_id = rename_event["ShipID"]
        ship_name = rename_event["UserShipName"]
        self.db.execute('UPDATE ships SET piloted=0 WHERE piloted=1')
        self.db.execute('UPDATE ships SET name=?, piloted=1 WHERE id=?', (ship_name, ship_id))
        self.db.commit()

    def swap(self, swap_event, star_system, storing_ship_name):
        if self.db is None:
            return
        if swap_event.get("event", None) != "ShipyardSwap":
            return
        
        if "SellShipID" in swap_event:
            self.__sold(swap_event["SellShipID"])
        else:
            try:
                storing_ship_id = swap_event.get("StoreShipID", None)
                ship_type = swap_event.get("StoreOldShip", None).lower()
                localised = EDVehicleFactory.canonicalize(ship_type)
                market_id = swap_event.get("MarketID", None)
                self.db.execute('''INSERT INTO ships(id, type, localised, name, star_system, ship_market_id, value, hot)
                            VALUES(?,?,?,?,?,?,?,?)''', (storing_ship_id, ship_type, localised, storing_ship_name, star_system, market_id, 0, 0))
                self.db.execute('DELETE from transits WHERE ship_id=?', (storing_ship_id, ))
            except sqlite3.IntegrityError:
                # TODO edge case after using Apex?
                pass
        
        piloting_ship_id = swap_event.get("ShipID", None)
        self.db.execute('UPDATE ships SET ship_market_id="", star_system="", piloted=1, eta=0 WHERE id=?', (piloting_ship_id,))
        self.db.execute('DELETE from transits WHERE ship_id=?', (piloting_ship_id, ))
        self.db.commit()


    def transfer(self, transfer_event, dst_system, dst_market_id=""):
        if self.db is None:
            return
        if transfer_event.get("event", None) != "ShipyardTransfer":
            return

        ship_id = transfer_event.get("ShipID", None)
        src_system = transfer_event.get("System", None)
        src_market_id = transfer_event.get("MarketID", None)
        distance = transfer_event.get("Distance", None)
        eta = EDTime.eta_transfer(distance)
        self.db.execute('DELETE from transits WHERE ship_id=?', (ship_id, ))
        self.db.execute('''INSERT INTO transits(ship_id, eta, source_system, source_market_id, destination_system, destination_market_id)
                            VALUES (?,?,?,?,?,?)''', (ship_id, eta, src_system, src_market_id, dst_system, dst_market_id))
        self.db.execute('UPDATE ships SET ship_market_id=?, star_system=?, piloted=0, eta=? WHERE id=?', (dst_market_id, dst_system, eta, ship_id, ))
        self.db.commit()
        self.__update()

    def __update(self):
        now = EDTime.py_epoch_now()
        transits = self.db.execute('SELECT id, ship_id, destination_system, destination_market_id FROM transits WHERE eta<=?', (now,))
        for transit in transits:
            self.db.execute('UPDATE ships SET star_system=?, ship_market_id=?, eta=0 WHERE id=?', (transit[2], transit[3], transit[1],))
            self.db.execute('DELETE from transits WHERE id=?', (transit[0],))
        
        now = EDTime.py_epoch_now()
        transits = self.db.execute('SELECT id, ship_id, destination_system, destination_market_id, eta FROM transits WHERE eta>?', (now,))
        for transit in transits:
            self.db.execute('UPDATE ships SET star_system=?, ship_market_id=?, eta=? WHERE id=?', (transit[2], transit[3], transit[4], transit[1],))
        self.db.commit()