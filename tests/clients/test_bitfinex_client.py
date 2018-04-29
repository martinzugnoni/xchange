import re
from decimal import Decimal

import responses

from tests import BaseXchangeTestCase
from tests.fixtures import bitfinex
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies
from xchange.exceptions import BitfinexException, InvalidSymbolPairException
from xchange.models.bitfinex import (
    BitfinexTicker, BitfinexOrderBook, BitfinexAccountBalance, BitfinexOrder)



class BaseBitfinexClientTestCase(BaseXchangeTestCase):
    def setUp(self):
        super(BaseBitfinexClientTestCase, self).setUp()
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

    @responses.activate
    def test_get_ticker_invalid_symbol_pair(self):
        with self.assertRaisesRegexp(InvalidSymbolPairException,
                                     'Given symbol pair "usd_usd" is not valid'):
            self.client.get_ticker('usd_usd')


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


class BitfinexOpenOrdersTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_get_open_orders(self):
        fixture = [
            {
                'avg_execution_price': '0.0',
                'cid': 85481934272,
                'cid_date': '2017-09-16',
                'exchange': None,
                'executed_amount': '0.0',
                'gid': None,
                'id': 3864975544,
                'is_cancelled': False,
                'is_hidden': False,
                'is_live': True,
                'oco_order': None,
                'original_amount': '1.0',
                'price': '2.0',
                'remaining_amount': '1.0',
                'side': 'buy',
                'src': 'web',
                'symbol': 'btcusd',
                'timestamp': '1505625352.0',
                'type': 'limit',
                'was_forced': False
            }
        ]
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/orders'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.BTC_USD)
        expected = [
            {
                'action': 'buy',
                'amount': Decimal('1.0'),
                'id': '3864975544',
                'price': Decimal('2.0'),
                'status': 'open',
                'symbol_pair': 'btc_usd',
                'type': 'limit'
            }
        ]
        self.assertEqual(type(open_orders), list)
        for obj in open_orders:
            self.assertEqual(type(obj), BitfinexOrder)
        self.assertEqual(open_orders, expected)

    @responses.activate
    def test_get_open_orders_filters_by_symbol_pair(self):
        fixture = [
            {
                'avg_execution_price': '0.0',
                'cid': 85481934272,
                'cid_date': '2017-09-16',
                'exchange': None,
                'executed_amount': '0.0',
                'gid': None,
                'id': 3864975544,
                'is_cancelled': False,
                'is_hidden': False,
                'is_live': True,
                'oco_order': None,
                'original_amount': '1.0',
                'price': '2.0',
                'remaining_amount': '1.0',
                'side': 'buy',
                'src': 'web',
                'symbol': 'btcusd',
                'timestamp': '1505625352.0',
                'type': 'limit',
                'was_forced': False
            },
            {
                'avg_execution_price': '0.0',
                'cid': 85478964272,
                'cid_date': '2017-09-16',
                'exchange': None,
                'executed_amount': '0.0',
                'gid': None,
                'id': 3864421544,
                'is_cancelled': False,
                'is_hidden': False,
                'is_live': True,
                'oco_order': None,
                'original_amount': '1.0',
                'price': '2.0',
                'remaining_amount': '1.0',
                'side': 'buy',
                'src': 'web',
                'symbol': 'ethusd',
                'timestamp': '1505625352.0',
                'type': 'limit',
                'was_forced': False
            },
        ]
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/orders'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.ETH_USD)
        expected = [
            {
                'action': 'buy',
                'amount': Decimal('1.0'),
                'id': '3864421544',
                'price': Decimal('2.0'),
                'status': 'open',
                'symbol_pair': 'eth_usd',
                'type': 'limit'
            }
        ]
        self.assertEqual(type(open_orders), list)
        self.assertEqual(len(open_orders), 1)
        for obj in open_orders:
            self.assertEqual(type(obj), BitfinexOrder)
        self.assertEqual(open_orders, expected)

    @responses.activate
    def test_get_open_orders_empty_response(self):
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/orders'),
            json=[],  # no open orders
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.BTC_USD)
        self.assertEqual(type(open_orders), list)
        self.assertEqual(open_orders, [])
