
import unittest
from unittest.mock import MagicMock, patch
from edr.models.edrmarket import EDRMarket

class TestEDRMarket(unittest.TestCase):
    def setUp(self):
        self.reader_patch = patch('edr.models.edrmarket.EDMarketReader')
        self.mock_reader_cls = self.reader_patch.start()
        self.mock_reader = self.mock_reader_cls.return_value

    def tearDown(self):
        self.reader_patch.stop()
        EDRMarket.PRICE_THRESHOLDS = {}

    def test_init(self):
        market = EDRMarket()
        self.assertIsNone(market.market_id)
        self.assertEqual(market.commodities, {})

    def test_update_success(self):
        market = EDRMarket()
        
        market_data = {
            'timestamp': "2022-01-01T12:00:00Z",
            'StarSystem': "Sol",
            'StationName': "Galileo",
            'StationType': "Orbis",
            'CarrierDockingAccess': "all",
            'MarketID': 12345,
            'Items': [
                {
                    'Name': 'gold', 'MeanPrice': 10000, 
                    'BuyPrice': 9000, 'Stock': 100, 
                    'SellPrice': 11000, 'Demand': 50
                },
                {
                    'Name': 'silver', 'MeanPrice': 5000, 
                    'BuyPrice': 4500, 'Stock': 200, 
                    'SellPrice': 5500, 'Demand': 100
                }
            ]
        }
        self.mock_reader.process.return_value = market_data
        
        result = market.update()
        
        self.assertTrue(result)
        self.assertEqual(market.market_id, 12345)
        self.assertEqual(market.system, "Sol")
        self.assertEqual(market.station_name, "Galileo")
        self.assertIn("gold", market.commodities)
        self.assertIn("silver", market.commodities)
        self.assertEqual(market.commodities["gold"]["stock"], 100)

    def test_update_failure(self):
        market = EDRMarket()
        self.mock_reader.process.return_value = None
        
        result = market.update()
        self.assertFalse(result)

    def test_normalization(self):
        market = EDRMarket()
        self.assertEqual(market.normalize_commodity_name("Gold"), "gold")
        self.assertEqual(market.normalize_commodity_name("$gold_name;"), "gold")
        self.assertEqual(market.normalize_commodity_name("biowaste"), "biowaste")

    def test_noteworthy(self):
        market = EDRMarket()
        
        # Inject thresholds
        EDRMarket.PRICE_THRESHOLDS = {
            "gold": {"buyThreshold": 8000, "sellThreshold": 12000},
            "voidopals": {"sellThreshold": 500000}
        }
        
        market_data = {
            'Items': [
                {'Name': 'gold', 'BuyPrice': 7000, 'SellPrice': 9000}, # Buy is low enough -> noteworthy
                {'Name': 'silver', 'BuyPrice': 4000, 'SellPrice': 5000}, # No threshold
                {'Name': 'voidopals', 'BuyPrice': 100000, 'SellPrice': 600000} # Sell is high enough -> noteworthy
            ],
            'CarrierDockingAccess': "all"
        }
        self.mock_reader.process.return_value = market_data
        
        market.update()
        
        self.assertIn("gold", market.noteworthy_commodities)
        self.assertIn("voidopals", market.noteworthy_commodities)
        self.assertNotIn("silver", market.noteworthy_commodities)

    def test_noteworthy_ignore_private(self):
        market = EDRMarket()
        EDRMarket.PRICE_THRESHOLDS = {
            "gold": {"buyThreshold": 8000}
        }
        
        market_data = {
            'Items': [{'Name': 'gold', 'BuyPrice': 7000}],
            'CarrierDockingAccess': "squadron" # Not "all"
        }
        self.mock_reader.process.return_value = market_data
        
        market.update()
        
        self.assertEqual(len(market.noteworthy_commodities), 0)

if __name__ == '__main__':
    unittest.main()
