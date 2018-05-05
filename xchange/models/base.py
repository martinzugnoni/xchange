from xchange import exceptions
from xchange.constants import currencies
from xchange.models.utils import (
    as_decimal, sorted_list, restricted_to_values,
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
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                'Object {} has not attribute "{}"'
                ''.format(self.__class__.__name__, key))

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
                raise ValueError(
                    'Unknown field "{}" for class {}'
                    ''.format(field, self.__class__.__name__))
            self[field] = func(value)


class Ticker(BaseExchangeModel):
    schema = {
        'ask': as_decimal,
        'bid': as_decimal,
        'low': as_decimal,
        'high': as_decimal,
        'last': as_decimal,
        'volume': as_decimal,
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


class AccountBalance(BaseExchangeModel):
    schema = {
        'symbol': normalized_symbol,
        'amount': as_decimal,
    }


class Order(BaseExchangeModel):
    schema = {
        'id': str,
        'action': restricted_to_values(('sell', 'buy')),
        'amount': as_decimal,
        'price': as_decimal,
        'symbol_pair': normalized_symbol_pair,
        'type': restricted_to_values(('limit', 'market')),
        'status': restricted_to_values(('open', 'closed')),
    }


class Position(BaseExchangeModel):
    schema = {
        'id': str,
        'action': restricted_to_values(('sell', 'buy')),
        'amount': as_decimal,
        'price': as_decimal,
        'symbol_pair': normalized_symbol_pair,
        'profit_loss': as_decimal,
    }
