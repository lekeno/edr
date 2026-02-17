
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edrfleetcarrier import EDRFleetCarrier, EDRFleetCarrierBar

class TestEDRFleetCarrier(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.models.edrfleetcarrier.EDTime')
        self.mock_time = self.time_patch.start()
        self.mock_time.py_epoch_now.return_value = 1000
        self.mock_time.js_epoch_now.return_value = 1000000
        
        # Mock instance returned by EDTime() constructor
        self.mock_time_instance = MagicMock()
        self.mock_time_instance.as_py_epoch.return_value = 1000
        self.mock_time_instance.as_journal_timestamp.return_value = "2022-01-01T12:00:00Z"
        self.mock_time.return_value = self.mock_time_instance

        self.i18n_patch = patch('edr.models.edrfleetcarrier._', side_effect=lambda x: x)
        self.mock_i18n = self.i18n_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        self.i18n_patch.stop()

    def test_update_from_location(self):
        carrier = EDRFleetCarrier()
        event = {
            "event": "Location",
            "StationType": "FleetCarrier",
            "MarketID": 12345,
            "StationName": "FC-1",
            "Name": "Carrier One",
            "StarSystem": "Sol",
            "Body": "Earth"
        }
        
        result = carrier.update_from_location_or_docking(event)
        self.assertTrue(result)
        self.assertEqual(carrier.id, 12345)
        self.assertEqual(carrier.callsign, "FC-1")
        self.assertEqual(carrier.name, "Carrier One")
        self.assertEqual(carrier.position, "Sol")
        
        # Non-carrier Location
        event["StationType"] = "Coriolis"
        result = carrier.update_from_location_or_docking(event)
        self.assertFalse(result)

    def test_update_from_stats(self):
        carrier = EDRFleetCarrier()
        event = {
            "CarrierID": 12345,
            "Callsign": "FC-1",
            "Name": "Carrier One",
            "DockingAccess": "all",
            "AllowNotorious": True,
            "FuelLevel": 500,
            "JumpRangeCurr": 400.5,
            "SpaceUsage": {"Cargo": 100}
        }
        
        carrier.update_from_stats(event)
        self.assertEqual(carrier.id, 12345)
        self.assertEqual(carrier.access, "all")
        self.assertTrue(carrier.allow_notorious)
        self.assertEqual(carrier.fuel_level, 500)
        self.assertEqual(carrier.space_usage["Cargo"], 100)

    def test_jump_requested(self):
        carrier = EDRFleetCarrier()
        # Mocking time objects specifically for this method
        self.mock_time_instance.as_py_epoch.side_effect = [1000, 2000, 3000] # request, jump, lockdown
        
        event = {
            "CarrierID": 12345,
            "timestamp": "2022-01-01T12:00:00Z",
            "SystemName": "Beagle Point",
            "Body": "Beagle Point 1"
        }
        
        carrier.jump_requested(event)
        self.assertEqual(carrier.id, 12345)
        self.assertEqual(carrier.departure["destination"], "Beagle Point")
        # Check computed times
        self.assertEqual(carrier.departure["requested"], 1000)
        self.assertEqual(carrier.departure["time"], 2000)
        
    def test_jump_cancelled(self):
        carrier = EDRFleetCarrier()
        carrier.id = 12345
        carrier.departure["destination"] = "Beagle Point"
        
        event = {"CarrierID": 12345}
        carrier.jump_cancelled(event)
        
        self.assertIsNone(carrier.departure["destination"])
        self.assertIsNone(carrier.departure["time"])

    def test_trade_orders(self):
        carrier = EDRFleetCarrier()
        carrier.id = 12345
        
        # Purchase Order
        buy_event = {
            "event": "CarrierTradeOrder",
            "CarrierID": 12345,
            "Commodity": "gold",
            "Commodity_Localised": "Gold",
            "Price": 50000,
            "PurchaseOrder": 10
        }
        
        carrier.trade_order(buy_event)
        self.assertIn("gold", carrier.purchase_orders)
        self.assertEqual(carrier.purchase_orders["gold"]["quantity"], 10)
        self.assertTrue(carrier.market_updated)
        
        # Sale Order
        sell_event = {
            "event": "CarrierTradeOrder",
            "CarrierID": 12345,
            "Commodity": "silver",
            "Price": 30000,
            "SaleOrder": 20
        }
        
        carrier.trade_order(sell_event)
        self.assertIn("silver", carrier.sale_orders)
        self.assertEqual(carrier.sale_orders["silver"]["quantity"], 20)

        # Cancel Trade
        cancel_event = {
            "event": "CarrierTradeOrder",
            "CarrierID": 12345,
            "Commodity": "gold",
            "CancelTrade": True
        }
        carrier.trade_order(cancel_event)
        self.assertNotIn("gold", carrier.purchase_orders)

    def test_json_market(self):
        carrier = EDRFleetCarrier()
        carrier.id = 12345
        carrier.purchase_orders["gold"] = {"timestamp": 1000, "price": 100, "quantity": 10, "l10n": "Gold"}
        
        json_data = carrier.json_market()
        self.assertEqual(json_data["id"], 12345)
        self.assertIn("gold", json_data["purchases"])
        self.assertEqual(json_data["purchases"]["gold"]["price"], 100)

class TestEDRFleetCarrierBar(unittest.TestCase):
    def setUp(self):
        self.time_patch = patch('edr.models.edrfleetcarrier.EDTime')
        self.mock_time = self.time_patch.start()
        
    def tearDown(self):
        self.time_patch.stop()

    def test_from_fcmaterials(self):
        bar = EDRFleetCarrierBar()
        event = {
            "event": "FCMaterials",
            "Items": [
                {"Name": "$mechanicalcomponents_name;", "Price": 1000, "Stock": 5, "Demand": 0},
                {"Name": "$tungsten_name;", "Price": 500, "Stock": 0, "Demand": 10}
            ]
        }
        
        result = bar.from_fcmaterials(event)
        self.assertTrue(result)
        self.assertTrue(bar.updated)
        self.assertIn("mechanicalcomponents", bar.items)
        self.assertEqual(bar.items["mechanicalcomponents"]["stock"], 5)
        self.assertIn("tungsten", bar.items)
        self.assertEqual(bar.items["tungsten"]["demand"], 10)

    def test_items_filtering(self):
        bar = EDRFleetCarrierBar()
        bar.items = {
            "stock_only": {"stock": 10, "demand": 0},
            "demand_only": {"stock": 0, "demand": 10},
            "both": {"stock": 5, "demand": 5},
            "neither": {"stock": 0, "demand": 0} # Should not happen based on logic but for testing
        }
        
        in_stock = bar.items_in_stock()
        self.assertIn("stock_only", in_stock)
        self.assertIn("both", in_stock)
        self.assertNotIn("demand_only", in_stock)
        
        in_demand = bar.items_in_demand()
        self.assertIn("demand_only", in_demand)
        self.assertIn("both", in_demand)
        self.assertNotIn("stock_only", in_demand)

if __name__ == '__main__':
    unittest.main()
