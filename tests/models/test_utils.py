from decimal import Decimal

from tests import BaseXchangeTestCase
from xchange.constants import currencies
from xchange.models.utils import (
    object_of_class, sorted_list, restricted_to_values,
    normalized_symbol, normalized_symbol_pair,
    contracts_to_crypto, crypto_to_contracts
)

class ValidatorsTestCase(BaseXchangeTestCase):

    def test_object_of_class(self):
        func = object_of_class('Decimal')
        func(Decimal('10.2'))
        with self.assertRaises(ValueError):
            func('Hello World!')

    def test_sorted_list_asc(self):
        func = sorted_list(lambda x: x['value'], 'asc')
        l = [
            {'value': 10, 'result': True},
            {'value': 100, 'result': False},
            {'value': 30, 'result': True},
        ]
        result = func(l)
        self.assertEqual(
            result,
            [
                {'result': True, 'value': 10},
                {'result': True, 'value': 30},
                {'result': False, 'value': 100}
            ]
        )

    def test_sorted_list_desc(self):
        func = sorted_list(lambda x: x['value'], 'desc')
        l = [
            {'value': 10, 'result': True},
            {'value': 100, 'result': False},
            {'value': 30, 'result': True},
        ]
        result = func(l)
        self.assertEqual(
            result,
            [
                {'result': False, 'value': 100},
                {'result': True, 'value': 30},
                {'result': True, 'value': 10}
            ]
        )

    def test_restricted_to_values(self):
        func = restricted_to_values(['Hello', 'World'])
        func('Hello')
        func('World')
        with self.assertRaises(ValueError):
            func('foobar')


class NormalizersTestCase(BaseXchangeTestCase):

    def test_normalized_symbol(self):
        self.assertEqual(normalized_symbol(currencies.USD), currencies.USD)
        self.assertEqual(normalized_symbol('zusd'), currencies.USD)
        with self.assertRaises(ValueError):
            normalized_symbol('foobar')

    def test_normalized_symbol_pair(self):
        self.assertEqual(normalized_symbol_pair(currencies.BTC_USD), currencies.BTC_USD)
        self.assertEqual(normalized_symbol_pair('xbtusd'), currencies.BTC_USD)
        with self.assertRaises(ValueError):
            normalized_symbol_pair('foobar')


class ConvertersTestCase(BaseXchangeTestCase):

    def test_contracts_to_crypto(self):
        amount_in_crypto = contracts_to_crypto(
            amount_in_contracts=3,
            crypto_last_price=8000,
            unit_amount=100
        )
        # amount_in_crypto = amount_in_contracts * (unit_amount / crypto_last_price)
        # 0.0375 = 3 * (100 / 8000)
        self.assertEqual(amount_in_crypto,  Decimal('0.0375'))

    def test_crypto_to_contracts(self):
        amount_in_contracts = crypto_to_contracts(
            amount_in_crypto=Decimal('0.0375'),
            crypto_last_price=8000,
            unit_amount=100
        )
        # amount_in_contracts = (amount_in_crypto * crypto_last_price) / unit_amount
        # 3 = (0.0375 * 8000) / 100
        self.assertEqual(amount_in_contracts,  3)
