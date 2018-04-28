import re
from decimal import Decimal

import responses

from tests import BaseXchangeTestCase
from tests.fixtures import bitfinex
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies
from xchange.models.bitfinex import (
    BitfinexTicker, BitfinexOrderBook, BitfinexAccountBalance)



class BaseBitfinexClientTestCase(BaseXchangeTestCase):
    def setUp(self):
        super().setUp()
        self.ClientClass = ExchangeClientFactory.get_client(exchanges.BITFINEX)
        self.client = self.ClientClass('API_KEY', 'API_SECRET')

        for fixture in bitfinex.FIXTURE_RESPONSES:
            responses.add(
                method=fixture['method'],
                url=re.compile(fixture['url_regex']),
                json=fixture['json'],
                status=fixture['status'],
                content_type=fixture['content_type'])


class BitfinexClientTickerTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_get_ticker(self):
        ticker = self.client.get_ticker(currencies.BTC_USD)
        expected = {
            'ask': Decimal('9398.2'),
            'bid': Decimal('9398.1'),
            'high': Decimal('9500.0'),
            'last': Decimal('9398.1'),
            'low': Decimal('8750.0'),
            'volume': Decimal('44197.286828289994')
        }
        self.assertEqual(ticker, expected)
        self.assertEqual(type(ticker), BitfinexTicker)


class BitfinexClientOrderBookTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_get_order_book(self):
        order_book = self.client.get_order_book(currencies.BTC_USD)
        expected = {
        'asks': [
            (Decimal('9329'), Decimal('7.50897281')),
            (Decimal('9328.7'), Decimal('0.08')),
            (Decimal('9327.4'), Decimal('0.09694343')),
            (Decimal('9327.3'), Decimal('0.31'))],
        'bids': [
            (Decimal('9327.1'), Decimal('0.15')),
            (Decimal('9326.9'), Decimal('0.10915328')),
            (Decimal('9326.8'), Decimal('0.34')),
            (Decimal('9326.2'), Decimal('0.57462657')),
            (Decimal('9326.1'), Decimal('0.01975221'))]
        }
        self.assertEqual(order_book, expected)
        self.assertEqual(type(order_book), BitfinexOrderBook)


class BitfinexClientAccountBalanceTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_get_account_balance(self):
        balance = self.client.get_account_balance()
        expected = [
            {'amount': Decimal('0.0'), 'symbol': 'bfx'},
            {'amount': Decimal('0.01209215'), 'symbol': 'btc'},
            {'amount': Decimal('0.00009361'), 'symbol': 'usd'}
        ]
        self.assertEqual(balance, expected)

        self.assertEqual(type(balance), list)
        for obj in balance:
            self.assertEqual(type(obj), BitfinexAccountBalance)
