import re
from decimal import Decimal

import responses

from tests import BaseXchangeTestCase
from tests.fixtures import bitfinex
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies
from xchange.exceptions import BitfinexException, InvalidSymbolPairException
from xchange.models.bitfinex import (
    BitfinexTicker, BitfinexOrderBook, BitfinexAccountBalance, BitfinexOrder,
    BitfinexPosition)


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
        with self.assertRaisesRegexp(ValueError,
                                     'Invalid "usd_usd" value, expected any of'):
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

    @responses.activate
    def test_get_account_balance_symbol_pair(self):
        balance = self.client.get_account_balance(currencies.BTC)
        expected = {'amount': Decimal('0.01209215'), 'symbol': 'btc'}
        self.assertEqual(balance, expected)
        self.assertEqual(type(balance), BitfinexAccountBalance)


class BitfinexGetOpenOrdersTestCase(BaseBitfinexClientTestCase):

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


class BitfinexOpenOrderTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_open_order(self):
        fixture = {
            'avg_execution_price': '0.0',
            'cid': 77112547681,
            'cid_date': '2017-08-20',
            'exchange': 'bitfinex',
            'executed_amount': '0.0',
            'gid': None,
            'id': 3438135637,
            'is_cancelled': False,
            'is_hidden': False,
            'is_live': True,
            'oco_order': None,
            'order_id': 3434679437,
            'original_amount': '0.01209215',
            'price': '4118.0',
            'remaining_amount': '0.01209215',
            'side': 'sell',
            'src': 'api',
            'symbol': 'btcusd',
            'timestamp': '1503225464.317116079',
            'type': 'limit',
            'was_forced': False
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/order/new'),
            json=fixture,
            status=200,
            content_type='application/json')
        order = self.client.open_order(
            action=exchanges.SELL,
            amount='0.01209215',
            symbol_pair=currencies.BTC_USD,
            price='4118.0',
            order_type=exchanges.LIMIT)
        expected = {
            'id': '3438135637',
            'action': 'sell',
            'amount': Decimal('0.01209215'),
            'price': Decimal('4118.0'),
            'status': 'open',
            'symbol_pair': 'btc_usd',
            'type': 'limit'
        }
        self.assertEqual(order, expected)
        self.assertEqual(type(order), BitfinexOrder)

    @responses.activate
    def test_open_order_bad_request(self):
        fixture = {'message': 'Key price should be a decimal string.'}
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/order/new'),
            json=fixture,
            status=400,
            content_type='application/json')
        with self.assertRaisesRegexp(BitfinexException, 'Got 400 response with content:'):
            self.client.open_order(
                action=exchanges.SELL,
                amount='0.01209215',
                symbol_pair=currencies.BTC_USD,
                price='0.000000',  # won't work
                order_type=exchanges.LIMIT)


class BitfinexCancelOrderTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_cancel_order(self):
        order_id = 3439467895
        fixture = {'result': 'Order {} submitted for cancellation; waiting for confirmation.'.format(order_id)}
        responses.add(
            method='POST',
            url=re.compile('https://api\.bitfinex\.com/v1/order/cancel'),
            json=fixture,
            status=200,
            content_type='application/json')
        response = self.client.cancel_order(order_id)
        expected = {
            'result': 'Order 3439467895 submitted for cancellation; waiting for confirmation.'}
        self.assertEqual(response, expected)

    @responses.activate
    def test_cancel_all_orders(self):
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
        fixture = {'result': 'Orders cancelled'}
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/order/cancel/multi'),
            json=fixture,
            status=200,
            content_type='application/json')
        response = self.client.cancel_all_orders(currencies.BTC_USD)
        self.assertEqual(response, fixture)


class BitfinexGetOpenPositionsTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_get_open_positions(self):
        fixture = [
            {
                'id': 34589787,
                'amount': '-0.01209215',
                'base': '4118.0',
                'pl': '-0.10928401484',
                'status': 'ACTIVE',
                'swap': '0.0',
                'symbol': 'btcusd',
                'timestamp': '1503264460.0'
            }
        ]
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/positions'),
            json=fixture,
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.BTC_USD)
        expected = [
            {
                'id': '34589787',
                'action': 'sell',
                'amount': Decimal('0.01209215'),
                'price': Decimal('4118.0'),
                'profit_loss': Decimal('-0.10928401484'),
                'symbol_pair': 'btc_usd'
            }
        ]
        self.assertEqual(positions, expected)
        self.assertEqual(len(positions), 1)
        self.assertEqual(type(positions), list)
        for obj in positions:
            self.assertEqual(type(obj), BitfinexPosition)

    @responses.activate
    def test_get_open_positions_filters_symbol_pair(self):
        fixture = [
            {
                'id': 34589787,
                'amount': '-0.01209215',
                'base': '4118.0',
                'pl': '-0.10928401484',
                'status': 'ACTIVE',
                'swap': '0.0',
                'symbol': 'btcusd',
                'timestamp': '1503264460.0'
            },
            {
                'id': 34546527,
                'amount': '-0.01209215',
                'base': '4118.0',
                'pl': '-0.10928401484',
                'status': 'ACTIVE',
                'swap': '0.0',
                'symbol': 'ethusd',
                'timestamp': '1503264460.0'
            },
        ]
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/positions'),
            json=fixture,
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.ETH_USD)
        expected = [
            {
                'id': '34546527',
                'action': 'sell',
                'amount': Decimal('0.01209215'),
                'price': Decimal('4118.0'),
                'profit_loss': Decimal('-0.10928401484'),
                'symbol_pair': 'eth_usd'
            }
        ]
        self.assertEqual(positions, expected)
        self.assertEqual(len(positions), 1)
        self.assertEqual(type(positions), list)
        for obj in positions:
            self.assertEqual(type(obj), BitfinexPosition)

    @responses.activate
    def test_get_open_positions_no_open_position(self):
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/positions'),
            json=[],
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.BTC_USD)
        self.assertEqual(positions, [])
        self.assertEqual(len(positions), 0)
        self.assertEqual(type(positions), list)


class BitfinexClosePositionTestCase(BaseBitfinexClientTestCase):

    @responses.activate
    def test_close_position(self):
        fixture = {
            'avg_execution_price': '0.0',
            'cid': 81742456868,
            'cid_date': '2017-09-16',
            'exchange': 'bitfinex',
            'executed_amount': '0.0',
            'gid': None,
            'id': 3848456981,
            'is_cancelled': False,
            'is_hidden': False,
            'is_live': True,
            'oco_order': None,
            'order_id': 3841546911,
            'original_amount': '0.005',
            'price': '3710.5',
            'remaining_amount': '0.005',
            'side': 'buy',
            'src': 'api',
            'symbol': 'btcusd',
            'timestamp': '1505601744.272215012',
            'type': 'market',
            'was_forced': False
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/order/new'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = [
            {
                'id': 34589787,
                'amount': '-0.01209215',
                'base': '4118.0',
                'pl': '-0.10928401484',
                'status': 'ACTIVE',
                'swap': '0.0',
                'symbol': 'btcusd',
                'timestamp': '1503264460.0'
            }
        ]
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/positions'),
            json=fixture,
            status=200,
            content_type='application/json')
        order = self.client.close_position(
            position_id='34589787',
            symbol_pair=currencies.BTC_USD)
        expected = {
            'action': 'buy',
            'amount': Decimal('0.005'),
            'id': '3848456981',
            'price': Decimal('3710.5'),
            'status': 'open',
            'symbol_pair': 'btc_usd',
            'type': 'market'
        }
        self.assertEqual(order, expected)
        self.assertEqual(type(order), BitfinexOrder)

    @responses.activate
    def test_close_all_positions(self):
        fixture = [
            {
                'id': 34589787,
                'amount': '-0.01209215',
                'base': '4118.0',
                'pl': '-0.10928401484',
                'status': 'ACTIVE',
                'swap': '0.0',
                'symbol': 'btcusd',
                'timestamp': '1503264460.0'
            }
        ]
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/positions'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = {
            'avg_execution_price': '0.0',
            'cid': 81742456868,
            'cid_date': '2017-09-16',
            'exchange': 'bitfinex',
            'executed_amount': '0.0',
            'gid': None,
            'id': 3848456981,
            'is_cancelled': False,
            'is_hidden': False,
            'is_live': True,
            'oco_order': None,
            'order_id': 3841546911,
            'original_amount': '0.005',
            'price': '3710.5',
            'remaining_amount': '0.005',
            'side': 'buy',
            'src': 'api',
            'symbol': 'btcusd',
            'timestamp': '1505601744.272215012',
            'type': 'market',
            'was_forced': False
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.bitfinex.com/v1/order/new'),
            json=fixture,
            status=200,
            content_type='application/json')
        self.client.close_all_positions(currencies.BTC_USD)
