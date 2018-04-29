from decimal import Decimal

from xchange import exceptions
from xchange.constants import currencies
from xchange.models.utils import (
    sorted_list, restricted_to_values,
    normalized_symbol, normalized_symbol_pair,
    contracts_to_crypto, crypto_to_contracts
)


class BaseExchangeModel(dict):
    schema = {}

    def __init__(self, json_response):
        super(BaseExchangeModel, self).__init__()
        parsed_response = self.normalize_response(json_response)
        self.assign_dynamic_attributes(parsed_response)

    def __getattr__(self, key):
        return self[key]

    def normalize_response(self, json_response):
        """As this is the base class, don't perform any transformation"""
        return json_response

    def assign_dynamic_attributes(self, parsed_response):
        """
        Dynamically assign fields in the response as attributes
        of the Model.
        For each field, a formatting function is applied according
        to the provided "schema".
        """
        for field, value in parsed_response.items():
            func = self.schema.get(field)
            if not func:
                raise ValueError('{} unknown field: "{}"'.format(type(self), field))
            self[field] = func(value)


class Ticker(BaseExchangeModel):
    schema = {
        'ask': Decimal,
        'bid': Decimal,
        'low': Decimal,
        'high': Decimal,
        'last': Decimal,
        'volume': Decimal,
    }


class OrderBook(BaseExchangeModel):
    """
    Normalized format:
    {
        "asks": [
            # (price_in_btc, amount_in_btc),
            (Decimal('4630.12300'), Decimal('0.014')),
            (Decimal('4620.23450'), Decimal('0.456')),
        ],
        "bids": [
            # (price_in_btc, amount_in_btc),
            (Decimal('4610.54856'), Decimal('0.078')),
            (Decimal('4600.78952'), Decimal('0.125')),
        ]
    }
    """
    schema = {
        'asks': sorted_list(key=lambda l: l[0], sorting_type='desc'),
        'bids': sorted_list(key=lambda l: l[0], sorting_type='desc'),
    }

    def get_average_prices(self, balance):
        """
        Returns a tuple (price_asks, price_bids), with the average
        price calculated based on the orders available
        until covering given balance.
        Calculates the average prices using the cheapest "asks"
        orders, and the highest "bids" ones.
        """
        balance = Decimal(balance)

        def calculate_weighted_average(operation, order_list, balance):
            amounts = [t[1] for t in order_list]
            if sum(amounts) < balance:
                raise exceptions.InsufficientMarketDepth(
                    'No depth in {} for amount: {}'.format(operation, balance))

            if operation == 'asks':
                # when checking the "asks" list, we want to
                # iterate orders from cheapest to highest
                order_list = list(reversed(order_list))
            accum = Decimal(0.0)

            # most of the times last used order in the orderbook
            # is partially used. we need to know which was the portion
            # used from that order to calculate the weighted average
            rest = balance

            for index, price_tuple in enumerate(order_list):
                amount = price_tuple[1]
                accum += amount
                if accum >= balance:
                    break
                rest -= amount

            # get the sub list representing only the necessary
            # orders to fulfill the balance amount
            sub_list = order_list[:index + 1]

            # change the last used order in the list, to just
            # the needed rest amount
            sub_list[-1] = (sub_list[-1][0], Decimal(rest))

            sub_list_amounts = [t[1] for t in sub_list]
            return sum(x * y for x, y in sub_list) / sum(sub_list_amounts)

        return (
            calculate_weighted_average('asks', self.asks, balance),
            calculate_weighted_average('bids', self.bids, balance),
        )


class AccountBalance(BaseExchangeModel):
    schema = {
        'symbol': normalized_symbol,
        'amount': Decimal,
    }


class Order(BaseExchangeModel):
    schema = {
        'id': str,
        'action': restricted_to_values(('sell', 'buy')),
        'amount': Decimal,
        'price': Decimal,
        'symbol_pair': normalized_symbol_pair,
        'type': restricted_to_values(('limit', 'market')),
        'status': restricted_to_values(('open', 'closed')),
    }


class Position(BaseExchangeModel):
    schema = {
        'id': str,
        'action': restricted_to_values(('sell', 'buy')),
        'amount': Decimal,
        'price': Decimal,
        'symbol_pair': normalized_symbol_pair,
        'profit_loss': Decimal,
    }
