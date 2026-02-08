
import unittest
from unittest.mock import patch, MagicMock
from edrmarket import EDRMarket

class TestEDRMarket(unittest.TestCase):
    def setUp(self):
        self.market = EDRMarket()

    def test_normalize_commodity_name(self):
        self.assertEqual(self.market.normalize_commodity_name("$gold_name;"), "gold")
        self.assertEqual(self.market.normalize_commodity_name("$silver_name"), "silver")
        self.assertEqual(self.market.normalize_commodity_name("indite"), "indite")
        self.assertEqual(self.market.normalize_commodity_name("$palladium_name;"), "palladium")
    
    @patch('edrmarket.EDMarketReader')
    def test_update_success(self, MockReader):
        # Mock the reader
        mock_reader_instance = MockReader.return_value
        market_data = {
            'timestamp': '2025-01-01T12:00:00Z',
            'StarSystem': 'Sol',
            'StationName': 'Abraham Lincoln',
            'StationType': 'Orbis',
            'CarrierDockingAccess': 'all',
            'MarketID': 12345,
            'Items': [
                {
                    'Name': '$gold_name;',
                    'MeanPrice': 9000,
                    'BuyPrice': 9500,
                    'Stock': 100,
                    'StockBracket': 2,
                    'SellPrice': 9200,
                    'Demand': 500,
                    'DemandBracket': 3
                }
            ]
        }
        mock_reader_instance.process.return_value = market_data
        
        # Run update
        result = self.market.update()
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.market.system, 'Sol')
        self.assertEqual(self.market.station_name, 'Abraham Lincoln')
        self.assertEqual(self.market.market_id, 12345)
        self.assertIn('gold', self.market.commodities)
        self.assertEqual(self.market.commodities['gold']['buyPrice'], 9500)

    @patch('edrmarket.EDMarketReader')
    def test_update_failure(self, MockReader):
        MockReader.return_value.process.return_value = None
        result = self.market.update()
        self.assertFalse(result)

    def test_noteworthy_filtering(self):
        # Setup fake data
        self.market.PRICE_THRESHOLDS = {
            "gold": {"buyThreshold": 4000, "sellThreshold": 10000},
            "voidopal": {"buyThreshold": 200000, "sellThreshold": 800000}
        }
        self.market.access = "all"
        
        # Case 1: Gold is cheap (noteworthy buy)
        self.market.commodities = {
            "gold": {"name": "gold", "buyPrice": 3000, "sellPrice": 3200}, # Cheap!
            "silver": {"name": "silver", "buyPrice": 500, "sellPrice": 550} # Ignored
        }
        self.market._noteworthyfy()
        self.assertIn("gold", self.market.noteworthy_commodities)
        self.assertNotIn("silver", self.market.noteworthy_commodities)

        # Case 2: Gold is average (not noteworthy)
        self.market.commodities = {
            "gold": {"name": "gold", "buyPrice": 5000, "sellPrice": 5200}
        }
        self.market._noteworthyfy()
        self.assertNotIn("gold", self.market.noteworthy_commodities)

        # Case 3: Void Opals are expensive (noteworthy sell - based on buyPrice logic in code, wait logic says buyPrice >= sellThreshold? That seems to imply we are selling TO station? Or buying FROM station?
        # Code: commodity['buyPrice'] >= self.PRICE_THRESHOLDS[name]["sellThreshold"]
        # If I can buy it for X, and X is >= SellThreshold... that seems odd.
        # Usually:
        # If I can BUY for LOW, it's good (Buy < BuyThreshold).
        # If I can SELL for HIGH, it's good (Sell > SellThreshold).
        # But the code checks `commodity['buyPrice']` for both.
        # Let's preserve logic for now, but ensure test matches code.
        
        self.market.commodities = {
            "gold": {"name": "gold", "buyPrice": 12000, "sellPrice": 11000} # buyPrice > 10000
        }
        self.market._noteworthyfy()
        self.assertIn("gold", self.market.noteworthy_commodities)

if __name__ == '__main__':
    unittest.main()
