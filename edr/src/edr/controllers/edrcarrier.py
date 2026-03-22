import re
import json
import datetime
import itertools
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c
from edr.utils.edtime import EDTime
from edr.utils.clippy import copy
from edr.utils.edrutils import simplified_body_name, pretty_print_number
from edr.models.edsitu import EDPlanetaryLocation

class EDRCarrierManager:
    def __init__(self, edr_client):
        self.client = edr_client

    def __summarize_fc_market(self, sale_orders, purchase_orders, max_len=2048):
        remaining = max_len
        details_purchases = []
        details_sales = []
        if sale_orders:
            sale_orders_with_value = [[sale_orders[order], self.client.player.remlok_helmet.how_useful(order), order] for order in sale_orders if self.client.player.remlok_helmet.how_useful(order) >= 0]
            sorted_sale_orders = sorted(sale_orders_with_value, key=lambda b: b[1], reverse=True)
            for order in sorted_sale_orders:
                quantity = pretty_print_number(order[0]["quantity"])
                item = order[0]["l10n"][:21].capitalize()
                price = pretty_print_number(order[0]["price"])
                worthy = self.client.player.remlok_helmet.worthiness_odyssey_material(order[2])
                if worthy:
                    details_sales.append(f'{quantity: >5} {item: <21} {price: >7} {worthy: >15}')
                else:
                    details_sales.append(f'{quantity: >5} {item: <21} {price: >7}')

        for order in purchase_orders:
            quantity = pretty_print_number(purchase_orders[order]["quantity"])
            item = purchase_orders[order]["l10n"][:21].capitalize()
            price = pretty_print_number(purchase_orders[order]["price"])
            details_purchases.append(f'{quantity: >5} {item: <21} {price: >7}')

        
        header_sales = ""
        if details_sales:
            header_sales += _(f'{"Units": >5} {"Item": <21} {"Credits": >7} {"Worthiness*": >15}\n')
            header_sales += _(f'{" [Selling] ":-^50}\n')
            

        header_purchases = ""                
        if details_purchases:
            if header_sales:
                header_purchases += "\n\n"
                header_purchases += _(f'{" [Buying] ":-^50}\n')
            else:
                header_purchases += _(f'{"Units": >5} {"Item": <15} {"Credits": >7}\n')
                header_purchases += _(f'{" [Buying] ":-^50}\n')
            
        opening = "```"
        closing = "```"
        summary = opening
        summary_footer = closing
        if details_sales:
            summary_footer = "\n\n*: b=blueprint u=upgrades x=trading e=eng. unlocks"
            summary_footer += closing
        
        included_sales = []
        included_purchases = []
        remaining -= len(summary) + len(header_sales) + len(header_purchases) + len(summary_footer) 
        for s,p in itertools.zip_longest(details_sales, details_purchases):
            if remaining <= 0:
                break
            if s and len(s) <= remaining:
                included_sales.append(s)
                remaining -= len(s)+1
            if p and len(p) <= remaining:
                included_purchases.append(p)
                remaining -= len(p)+1
        
        if included_sales:
            summary += header_sales
            summary += "\n".join(included_sales)
    
        if included_purchases:
            summary += header_purchases
            summary += "\n".join(included_purchases)

        summary += summary_footer
        return summary

    def fleet_carrier_update(self):
        """
        Update Fleet Carrier market data (if owner).
        """
        if self.client.player.fleet_carrier.has_market_changed():
            timeframe = 60*15
            market = self.client.player.fleet_carrier.json_market(timeframe)
            text_summary = self.client.player.fleet_carrier.text_summary(timeframe)
            details = []
            if market.get("sales", None):
                details.append(_("{} sale orders").format(len(market["sales"])))
            if market.get("purchases", None):
                details.append(_("{} purchase orders").format(len(market["purchases"])))
            
            fc = self.client.server.fc(self.client.player.fleet_carrier.callsign, self.client.player.fleet_carrier.name, self.client.player.fleet_carrier.position, may_create=True)
            if market and fc:
                if self.client.player.fleet_carrier.is_open_to_all():
                    fc_id = list(fc)[0] if fc else None
                    market["owner"] = self.client.player.name
                    if self.client.server.report_fc_market(fc_id, market):
                        details.append(_("Access: all => Market info sent."))
                    else:
                        EDR_LOG.debug("Failed to report FC market update.")
                else:
                    EDR_LOG.debug("Skip reporting FC market given that the FC is not open to all.")
                sale_orders = self.client.player.fleet_carrier.sale_orders_within(timeframe)
                purchase_orders = self.client.player.fleet_carrier.purchase_orders_within(timeframe)
                summary = self.__summarize_fc_market(sale_orders, purchase_orders)
                market["summary"] = summary
                if self.client.edrdiscord.fc_market_update(market):
                    details.append(_("Sent FC trading info to your discord channel."))

            self.client.player.fleet_carrier.acknowledge_market()

            if details:
                copy(text_summary)
                details.append(_("Summary placed in the clipboard"))
                self.client._EDRClient__notify(_("Fleet Carrier status summary"), details, clear_before=True)

    def carrier_trade(self, entry):
        """
        Handle Carrier Trade Order events.

        Args:
            entry (dict): The journal event.
        """
        if entry.get("event", "") != "CarrierTradeOrder":
            return
        item = entry.get("Commodity", None)
        if item is None:
            return
        description = self.client.player.describe_item(item)
        if description:
            l_item = entry.get("Commodity_Localised", item)
            self.client._EDRClient__notify(_("Trading Insights for {}").format(l_item), description, clear_before=True)
        
        self.client.player.fleet_carrier.trade_order(entry)

