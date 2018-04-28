from decimal import Decimal

from xchange.constants import currencies


class InsufficientMarketDepth(Exception):
    pass


def object_of_class(class_name):
    def func(obj):
        if obj.__class__.__name__ != class_name:
            raise ValueError('"{}" is not a valid class'.format(obj))
        return obj
    return func


def sorted_list(key, sorting_type):
    def func(original_list):
        reverse = False if sorting_type == 'asc' else True
        return sorted(original_list, key=key, reverse=reverse)
    return func


def restricted_to_values(values_list):
    def func(original_value):
        original_value = original_value.lower()
        if original_value not in values_list:
            raise ValueError('"{}" is not a valid value'.format(original_value))
        return original_value
    return func


def normalized_symbol(original_symbol):
    mapping = currencies.SYMBOL_VARIANTS
    original_symbol = original_symbol.lower()
    if original_symbol in mapping.keys():
        # no need to normalize, symbol is already valid
        return original_symbol
    for symbol, variants in mapping.items():
        if original_symbol in variants:
            return symbol
    raise ValueError('Could not normalize {} symbol'.format(original_symbol))


def normalized_symbol_pair(original_pair):
    mapping = {
        'btc_usd': ('btc_usd', 'btcusd', 'xbtusd', 'xxbtzusd',
                    'btc0929', 'btc1229'),
        'eth_usd': ('eth_usd', 'ethusd'),
    }
    original_pair = original_pair.lower()
    for pair, variants in mapping.items():
        if original_pair in variants:
            return pair
    raise ValueError('Could not normalize {} symbol pair'.format(original_pair))


def contracts_to_crypto(amount_in_contracts, crypto_last_price, unit_amount):
    """
    Transforms the amount of contracts to amount of given cryptos based
    on the `unit_amount` and last price of the coin.

    `unit_amount` is the price in USD of each contract.

    amount_in_crypto = amount_in_contracts * (unit_amount / crypto_last_price)
    """
    # convert all given values to Decimal
    amount_in_contracts, crypto_last_price, unit_amount = list(
        map(Decimal, [amount_in_contracts, crypto_last_price, unit_amount]))
    return amount_in_contracts * (unit_amount / crypto_last_price)


def crypto_to_contracts(amount_in_crypto, crypto_last_price, unit_amount):
    """
    Transforms the amount of given crypto to amount of contracts based
    on the `unit_amount` and last price of the coin.
    It rounds the amount of contracts to the nearest lower amount,
    because contracts can not be operated partially.
    ie: If contracts amount ends up being Decimal(1.6873),
        it returns Decimal(1).

    `unit_amount` is the price in USD of each contract.

    amount_in_contracts = (amount_in_crypto * crypto_last_price) / unit_amount
    """
    # convert all given values to Decimal
    amount_in_crypto, crypto_last_price, unit_amount = list(
        map(Decimal, [amount_in_crypto, crypto_last_price, unit_amount]))
    amount_in_contracts = (amount_in_crypto * crypto_last_price) / unit_amount
    return Decimal(int(amount_in_contracts))


# exchange models


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
        for key, value in parsed_response.items():
            func = self.schema.get(key)
            if not func:
                raise ValueError('{} unknown field: {}'.format(type(self), key))
            if func:
                value = func(value)
            self[key] = value


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
                raise InsufficientMarketDepth(
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
