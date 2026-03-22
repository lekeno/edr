import sys
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from edr.controllers.edrcarrier import EDRCarrierManager

class MockEDRClient:
    def __init__(self):
        self.player = MagicMock()
        self.edrdiscord = MagicMock()
        self.server = MagicMock()
        
    def _EDRClient__notify(self, header, details, clear_before=False, sfx=True):
        self.last_notify = (header, details)


class TestEDRCarrierManager(unittest.TestCase):
    def setUp(self):
        self.client = MockEDRClient()
        self.manager = EDRCarrierManager(self.client)

    def test_carrier_trade(self):
        entry = {"event": "CarrierTradeOrder", "Commodity": "gold", "Commodity_Localised": "Gold"}
        self.client.player.describe_item.return_value = ["Gold is good"]
        self.manager.carrier_trade(entry)
        self.client.player.fleet_carrier.trade_order.assert_called_with(entry)
        self.assertEqual(self.client.last_notify[0], "Trading Insights for Gold")

    def test_fleet_carrier_update_no_change(self):
        self.client.player.fleet_carrier.has_market_changed.return_value = False
        self.manager.fleet_carrier_update()
        self.client.player.fleet_carrier.json_market.assert_not_called()

if __name__ == '__main__':
    unittest.main()
