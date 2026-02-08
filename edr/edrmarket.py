from collections import OrderedDict

from edmarketreader import EDMarketReader  # EDR_INTERNAL


class EDRMarket:
    """
    Manages market data processing for a station.
    """
    # TODO PRICE_THRESHOLDS static + from server?
    # TODO connect things from load.py
    # TODO submit noteworthy commodity prices
    # TODO server side alerts
    # TODO realtime client side alerts similar to !outlaws ?

    PRICE_THRESHOLDS = {}  # Placeholder for price thresholds

    def __init__(self):
        """Initialize the market data handler."""
        self.market_id = None
        self.system = None
        self.commodities = {}
        self.noteworthy_commodities = {}
        self.access = None
        self.station_name = None
        self.station_type = None
        self.timestamp = None

    def update(self):
        """
        Update market data using the EDMarketReader.

        Returns:
            bool: True if data was successfully processed, False otherwise.
        """
        reader = EDMarketReader()
        market_info = reader.process()
        if not market_info:
            return False

        self.timestamp = market_info.get('timestamp')
        self.system = market_info.get('StarSystem')
        self.station_name = market_info.get('StationName')
        self.station_type = market_info.get('StationType')
        self.access = market_info.get("CarrierDockingAccess", "all")
        self.market_id = market_info.get('MarketID')

        items = market_info.get('Items') or []
        commodities = sorted((OrderedDict([
            ('name',          self.normalize_commodity_name(commodity.get('Name', ''))),
            ('meanPrice',     commodity.get('MeanPrice', 0)),
            ('buyPrice',      commodity.get('BuyPrice', 0)),
            ('stock',         commodity.get('Stock', 0)),
            ('stockBracket',  commodity.get('StockBracket', 0)),
            ('sellPrice',     commodity.get('SellPrice', 0)),
            ('demand',        commodity.get('Demand', 0)),
            ('demandBracket', commodity.get('DemandBracket', 0)),
        ]) for commodity in items), key=lambda c: c['name'])

        self.commodities = {c['name']: c for c in commodities}
        self._noteworthyfy()
        return True

    def _noteworthyfy(self):
        """Identify commodities with noteworthy prices."""
        self.noteworthy_commodities = {}
        if self.access != "all":
            return

        for name in self.commodities:
            if name not in self.PRICE_THRESHOLDS:
                continue

            commodity = self.commodities[name]
            thresholds = self.PRICE_THRESHOLDS[name]
            if (commodity['buyPrice'] <= thresholds.get("buyThreshold", 0) or
                    commodity['buyPrice'] >= thresholds.get("sellThreshold", float('inf'))):
                self.noteworthy_commodities[name] = commodity

    def normalize_commodity_name(self, name):
        """
        Normalize commodity name by lowercasing and removing suffixes/prefixes.

        Args:
            name (str): The raw commodity name.

        Returns:
            str: The normalized commodity name.
        """
        normalized = name.lower()

        if normalized.endswith("_name"):
            useless_suffix_length = len("_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith("_name;"):
            useless_suffix_length = len("_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith("$"):
            normalized = normalized[1:]

        return normalized
