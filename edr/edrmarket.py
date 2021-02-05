import EDMarketReader

# TODO PRICE_THRESHOLDS static + from server?
# TODO connect things from load.py
# TODO submit noteworthy commodity prices
# TODO server side alerts
# TODO realtime client side alerts similar to !outlaws ?

class EDRMarket(object):
    def __init__(self):
        self.market_id = None
        self.system = None
        self.commodities = {}
        self.noteworthy_commodities = {}
        self.access = None
        self.stationName = None
        self.stationType = None
        self.timestamp = None

    def update(self):
        reader = EDMarketReader()
        market_info = reader.process()
        if not market_info:
            return False

        self.timestamp = entry['timestamp']
        self.system = entry['StarSystem']
        self.stationName = entry['StationName']
        self.stationType = entry['StationType']
        self.access = entry.get("CarrierDockingAccess", "all")
        self.marketId = entry['MarketID']
        items: List[Mapping[str, Any]] = entry.get('Items') or []
        commodities: Sequence[OrderedDictT[AnyStr, Any]] = sorted((OrderedDict([
            ('name',          self.normalize_commodity_name(commodity['Name'])),
            ('meanPrice',     commodity['MeanPrice']),
            ('buyPrice',      commodity['BuyPrice']),
            ('stock',         commodity['Stock']),
            ('stockBracket',  commodity['StockBracket']),
            ('sellPrice',     commodity['SellPrice']),
            ('demand',        commodity['Demand']),
            ('demandBracket', commodity['DemandBracket']),
        ]) for commodity in items), key=lambda c: c['name'])
        
        self.commodities = commodities
        self.__noteworthyfy()
        return True

    def __noteworthyfy(self):
        self.noteworthy_commodities = {}
        if self.access != "all":
            return

        for name in self.commodities:
            if name not in self.PRICE_THRESHOLDS:
                continue

            commodity = self.commodities[name]
            if (commodity['buyPrice'] <= self.PRICE_THRESHOLDS[name]["buyThreshold"] or commodity['buyPrice'] >= self.PRICE_THRESHOLDS[name]["sellThreshold"]):
                self.noteworthy_commodities[name] = commodity

    def normalize_commodity_name(self, name):
        normalized = name.lower()
        
        if normalized.endswith(u"_name"):
            useless_suffix_length = len(u"_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith(u"_name;"):
            useless_suffix_length = len(u"_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith(u"$"):
            normalized = normalized[1:]

        return normalized
