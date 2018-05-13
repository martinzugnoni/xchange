import re
from decimal import Decimal

import responses

from tests import BaseXchangeTestCase
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies
from xchange.exceptions import KrakenException, InvalidSymbolPairException
from xchange.models.kraken import (
    KrakenTicker, KrakenOrderBook, KrakenAccountBalance, KrakenOrder,
    KrakenOrder, KrakenPosition)


class BaseKrakenClientTestCase(BaseXchangeTestCase):
    def setUp(self):
        super(BaseKrakenClientTestCase, self).setUp()
        self.ClientClass = ExchangeClientFactory.get_client(exchanges.KRAKEN)
        self.client = self.ClientClass('a' * 56, 'b' * 88)


class KrakenClientTickerTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_get_ticker(self):
        fixture = {
            'error': [],
            'result': {
                'XETHZUSD': {
                    'a': ['775.97000', '8', '8.000'],
                    'b': ['774.04000', '2', '2.000'],
                    'c': ['774.23000', '0.00000032'],
                    'h': ['830.00000', '830.00000'],
                    'l': ['751.11000', '751.11000'],
                    'o': '812.50000',
                    'p': ['785.05276', '787.06592'],
                    't': [17253, 19730],
                    'v': ['41641.65603874', '46704.54167467']
                }
            }
        }
        responses.add(
            method='GET',
            url=re.compile('https://api.kraken.com/0/public/Ticker'),
            json=fixture,
            status=200,
            content_type='application/json')
        ticker = self.client.get_ticker(currencies.BTC_USD)
        expected = {
            'ask': Decimal('775.97000'),
            'bid': Decimal('774.04000'),
            'low': Decimal('751.11000'),
            'high': Decimal('830.00000'),
            'last': Decimal('774.23000'),
            'volume': Decimal('41641.65603874')
        }
        self.assertEqual(ticker, expected)
        self.assertEqual(type(ticker), KrakenTicker)

    @responses.activate
    def test_get_ticker_invalid_symbol_pair(self):
        with self.assertRaisesRegexp(ValueError,
                                     'Invalid "usd_usd" value, expected any of'):
            self.client.get_ticker('usd_usd')


class KrakenClientOrderBookTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_get_order_book(self):
        fixture = {
            'error': [],
            'result': {
                'XETHZUSD': {
                    'asks': [
                        ['775.78000', '4.798', 1525637947],
                        ['775.82000', '4.398', 1525637948],
                        ['775.91000', '5.000', 1525637926],
                        ['775.93000', '0.579', 1525637923],
                        ['775.95000', '5.000', 1525637927]],
                    'bids': [
                        ['774.45000', '0.167', 1525637949],
                        ['773.73000', '2.699', 1525637947],
                        ['773.72000', '1.495', 1525637945],
                        ['773.70000', '12.808', 1525637947],
                        ['773.62000', '103.411', 1525637846]
                    ]
                }
            }
        }
        responses.add(
            method='GET',
            url=re.compile('https://api.kraken.com/0/public/Depth'),
            json=fixture,
            status=200,
            content_type='application/json')
        order_book = self.client.get_order_book(currencies.BTC_USD)
        expected = {
            'asks': [
                (Decimal('775.95000'), Decimal('5.000')),
                (Decimal('775.93000'), Decimal('0.579')),
                (Decimal('775.91000'), Decimal('5.000')),
                (Decimal('775.82000'), Decimal('4.398')),
                (Decimal('775.78000'), Decimal('4.798'))
            ],
            'bids': [
                (Decimal('774.45000'), Decimal('0.167')),
                (Decimal('773.73000'), Decimal('2.699')),
                (Decimal('773.72000'), Decimal('1.495')),
                (Decimal('773.70000'), Decimal('12.808')),
                (Decimal('773.62000'), Decimal('103.411'))
            ]
        }
        self.assertEqual(order_book, expected)
        self.assertEqual(type(order_book), KrakenOrderBook)


class KrakenClientAccountBalanceTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_get_account_balance(self):
        fixture = {
            'error': [],
            'result': {
                'XETH': '0.0382000000',
                'XLTC': '0.0000050700',
                'XXBT': '0.0000043204',
                'ZUSD': '0.0807'
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/Balance'),
            json=fixture,
            status=200,
            content_type='application/json')
        balance = self.client.get_account_balance()
        expected = [
            {'amount': Decimal('0.0382000000'), 'symbol': 'eth'},
            {'amount': Decimal('0.0000050700'), 'symbol': 'ltc'},
            {'amount': Decimal('0.0000043204'), 'symbol': 'btc'},
            {'amount': Decimal('0.0807'), 'symbol': 'usd'}
        ]
        self.assertEqual(
            sorted(balance, key=lambda x: x['symbol']),
            sorted(expected, key=lambda x: x['symbol'])
        )

        self.assertEqual(type(balance), list)
        for obj in balance:
            self.assertEqual(type(obj), KrakenAccountBalance)

    @responses.activate
    def test_get_account_balance_symbol_pair(self):
        fixture = {
            'error': [],
            'result': {
                'XETH': '0.0382000000',
                'XLTC': '0.0000050700',
                'XXBT': '0.0000043204',
                'ZUSD': '0.0807'
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/Balance'),
            json=fixture,
            status=200,
            content_type='application/json')
        balance = self.client.get_account_balance(currencies.BTC)
        expected = {'symbol': 'btc', 'amount': Decimal('0.0000043204')}
        self.assertEqual(balance, expected)
        self.assertEqual(type(balance), KrakenAccountBalance)


class KrakenGetOpenOrdersTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_get_open_orders(self):
        fixture =  {
            'error': [],
            'result': {
                'open': {
                    'ODF2C3-ABCDE-HUDKEN': {
                        'cost': '0.00000',
                        'descr': {
                            'close': '',
                            'leverage': '2:1',
                            'order': 'sell '
                            '0.02000000 '
                            'ETHUSD @ '
                            'limit 900.00 '
                            'with 2:1 '
                            'leverage',
                            'ordertype': 'limit',
                            'pair': 'ETHUSD',
                            'price': '900.00',
                            'price2': '0',
                            'type': 'sell'
                        },
                        'expiretm': 0,
                        'fee': '0.00000',
                        'limitprice': '0.00000',
                        'misc': '',
                        'oflags': 'fciq',
                        'opentm': 1525638064.8332,
                        'price': '0.00000',
                        'refid': None,
                        'starttm': 0,
                        'status': 'open',
                        'stopprice': '0.00000',
                        'userref': 7886259,
                        'vol': '0.02000000',
                        'vol_exec': '0.00000000'
                    }
                }
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenOrders'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.ETH_USD)
        expected =  [
            {
                'id': 'ODF2C3-ABCDE-HUDKEN',
                'action': 'sell',
                'amount': Decimal('0.02000000'),
                'price': Decimal('900.00'),
                'symbol_pair': 'eth_usd',
                'type': 'limit',
                'status': 'open'
            }
        ]
        self.assertEqual(type(open_orders), list)
        for obj in open_orders:
            self.assertEqual(type(obj), KrakenOrder)
        self.assertEqual(open_orders, expected)

    @responses.activate
    def test_get_open_orders_filters_by_symbol_pair(self):
        fixture =  {
            'error': [],
            'result': {
                'open': {
                    'ODF2C3-ABCDE-HUDKEN': {
                        'cost': '0.00000',
                        'descr': {
                            'close': '',
                            'leverage': '2:1',
                            'order': 'sell '
                            '0.02000000 '
                            'ETHUSD @ '
                            'limit 900.00 '
                            'with 2:1 '
                            'leverage',
                            'ordertype': 'limit',
                            'pair': 'ETHUSD',
                            'price': '900.00',
                            'price2': '0',
                            'type': 'sell'
                        },
                        'expiretm': 0,
                        'fee': '0.00000',
                        'limitprice': '0.00000',
                        'misc': '',
                        'oflags': 'fciq',
                        'opentm': 1525638064.8332,
                        'price': '0.00000',
                        'refid': None,
                        'starttm': 0,
                        'status': 'open',
                        'stopprice': '0.00000',
                        'userref': 7886259,
                        'vol': '0.02000000',
                        'vol_exec': '0.00000000'
                    },
                    'ODF2C3-FGHIJ-HUDKEN': {
                        'cost': '0.00000',
                        'descr': {
                            'close': '',
                            'leverage': '2:1',
                            'order': 'sell '
                            '0.02000000 '
                            'BTCUSD @ '
                            'limit 900.00 '
                            'with 2:1 '
                            'leverage',
                            'ordertype': 'limit',
                            'pair': 'BTCUSD',
                            'price': '900.00',
                            'price2': '0',
                            'type': 'sell'
                        },
                        'expiretm': 0,
                        'fee': '0.00000',
                        'limitprice': '0.00000',
                        'misc': '',
                        'oflags': 'fciq',
                        'opentm': 1525638064.8332,
                        'price': '0.00000',
                        'refid': None,
                        'starttm': 0,
                        'status': 'open',
                        'stopprice': '0.00000',
                        'userref': 7886259,
                        'vol': '0.02000000',
                        'vol_exec': '0.00000000'
                    },
                }
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenOrders'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.BTC_USD)
        expected =  [
            {
                'id': 'ODF2C3-FGHIJ-HUDKEN',
                'action': 'sell',
                'amount': Decimal('0.02000000'),
                'price': Decimal('900.00'),
                'symbol_pair': 'btc_usd',
                'type': 'limit',
                'status': 'open'
            }
        ]
        self.assertEqual(type(open_orders), list)
        self.assertEqual(len(open_orders), 1)
        for obj in open_orders:
            self.assertEqual(type(obj), KrakenOrder)
        self.assertEqual(open_orders, expected)

    @responses.activate
    def test_get_open_orders_empty_response(self):
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenOrders'),
            json={'error': [], 'result': {'open': {}}},
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.BTC_USD)
        self.assertEqual(type(open_orders), list)
        self.assertEqual(open_orders, [])


class KrakenOpenOrderTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_open_order(self):
        fixture = {
            'error': [],
            'result': {
                'descr': {
                    'order': 'sell 0.02000000 ETHUSD @ limit 900.00 with 2:1 leverage'
                },
                'txid': ['ODF2C3-OVVBA-HUDKEN']
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/AddOrder'),
            json=fixture,
            status=200,
            content_type='application/json')
        order = self.client.open_order(
            action=exchanges.SELL,
            amount='0.01209215',
            symbol_pair=currencies.BTC_USD,
            price='4118.0',
            order_type=exchanges.LIMIT)
        expected = {'id': 'ODF2C3-OVVBA-HUDKEN'}
        self.assertEqual(order, expected)
        self.assertEqual(type(order), KrakenOrder)

    @responses.activate
    def test_open_order_bad_request(self):
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/AddOrder'),
            json={},
            status=400,
            content_type='application/json')
        with self.assertRaisesRegexp(KrakenException, 'Got 400 response with content:'):
            self.client.open_order(
                action=exchanges.SELL,
                amount='0.01209215',
                symbol_pair=currencies.BTC_USD,
                price='0.000000',  # won't work
                order_type=exchanges.LIMIT)


class KrakenCancelOrderTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_cancel_order(self):
        order_id = 3439467895
        fixture = {'error': [], 'result': {'count': 1}}
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/CancelOrder'),
            json=fixture,
            status=200,
            content_type='application/json')
        response = self.client.cancel_order(order_id)
        self.assertEqual(response, fixture)

    @responses.activate
    def test_cancel_all_orders(self):
        fixture = {'error': [], 'result': {'count': 2}}
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/CancelOrder'),
            json=fixture,
            status=200,
            content_type='application/json')
        response = self.client.cancel_all_orders(currencies.BTC_USD)
        self.assertEqual(response, fixture)


class KrakenGetOpenPositionsTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_get_open_positions(self):
        fixture = {
            'error': [],
            'result': {
                'TZESOY-ABCDE-V3K2B3': {
                    'cost': '15.48400',
                    'fee': '0.04336',
                    'margin': '7.74200',
                    'misc': '',
                    'net': '-0.0178',
                    'oflags': '',
                    'ordertxid': 'O4M6JE-W3LHA-66LKK4',
                    'ordertype': 'market',
                    'pair': 'XETHZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1525653978',
                    'terms': '0.0200% per 4 hours',
                    'time': 1525639578.5486,
                    'type': 'sell',
                    'value': '15.50',
                    'vol': '0.02000000',
                    'vol_closed': '0.00000000'
                }
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenPositions'),
            json=fixture,
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.ETH_USD)
        expected = [
            {
                'action': 'sell',
                'amount': Decimal('0.02000000'),
                'id': 'TZESOY-ABCDE-V3K2B3',
                'price': Decimal('774.2'),
                'profit_loss': Decimal('-0.0178'),
                'symbol_pair': 'eth_usd'
            }
        ]
        self.assertEqual(positions, expected)
        self.assertEqual(len(positions), 1)
        self.assertEqual(type(positions), list)
        for obj in positions:
            self.assertEqual(type(obj), KrakenPosition)

    @responses.activate
    def test_get_open_positions_filters_symbol_pair(self):
        fixture = {
            'error': [],
            'result': {
                'TZESOY-ABCDE-V3K2B3': {
                    'cost': '15.48400',
                    'fee': '0.04336',
                    'margin': '7.74200',
                    'misc': '',
                    'net': '-0.0178',
                    'oflags': '',
                    'ordertxid': 'O4M6JE-W3LHA-66LKK4',
                    'ordertype': 'market',
                    'pair': 'XETHZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1525653978',
                    'terms': '0.0200% per 4 hours',
                    'time': 1525639578.5486,
                    'type': 'sell',
                    'value': '15.50',
                    'vol': '0.02000000',
                    'vol_closed': '0.00000000'
                },
                'TZESOY-FGHIJ-V3K2B3': {
                    'cost': '15.48400',
                    'fee': '0.04336',
                    'margin': '7.74200',
                    'misc': '',
                    'net': '-0.0178',
                    'oflags': '',
                    'ordertxid': 'O4M6JE-AHUSY-66LKK4',
                    'ordertype': 'market',
                    'pair': 'XXBTZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1525653978',
                    'terms': '0.0200% per 4 hours',
                    'time': 1525639578.5486,
                    'type': 'sell',
                    'value': '15.50',
                    'vol': '0.02000000',
                    'vol_closed': '0.00000000'
                },
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenPositions'),
            json=fixture,
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.ETH_USD)
        expected = [
            {
                'action': 'sell',
                'amount': Decimal('0.02000000'),
                'id': 'TZESOY-ABCDE-V3K2B3',
                'price': Decimal('774.2'),
                'profit_loss': Decimal('-0.0178'),
                'symbol_pair': 'eth_usd'
            }
        ]
        self.assertEqual(positions, expected)
        self.assertEqual(len(positions), 1)
        self.assertEqual(type(positions), list)
        for obj in positions:
            self.assertEqual(type(obj), KrakenPosition)

    @responses.activate
    def test_get_open_positions_no_open_position(self):
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenPositions'),
            json={'error': [], 'result': {}},
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.BTC_USD)
        self.assertEqual(positions, [])
        self.assertEqual(len(positions), 0)
        self.assertEqual(type(positions), list)


class KrakenClosePositionTestCase(BaseKrakenClientTestCase):
    @responses.activate
    def test_close_position(self):
        fixture = {
            'error': [],
            'result': {
                'TZESOY-ABCDE-V3K2B3': {
                    'cost': '15.48400',
                    'fee': '0.04336',
                    'margin': '7.74200',
                    'misc': '',
                    'net': '-0.0178',
                    'oflags': '',
                    'ordertxid': 'O4M6JE-W3LHA-66LKK4',
                    'ordertype': 'market',
                    'pair': 'XETHZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1525653978',
                    'terms': '0.0200% per 4 hours',
                    'time': 1525639578.5486,
                    'type': 'sell',
                    'value': '15.50',
                    'vol': '0.02000000',
                    'vol_closed': '0.00000000'
                }
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenPositions'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = {
            'error': [],
            'result': {
                'descr': {
                    'order': 'sell 0.02000000 ETHUSD @ limit 900.00 with 2:1 leverage'
                },
                'txid': ['ODF2C3-QUIOA-HUDKEN']
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/AddOrder'),
            json=fixture,
            status=200,
            content_type='application/json')
        order = self.client.close_position(
            position_id='TZESOY-ABCDE-V3K2B3',
            symbol_pair=currencies.ETH_USD)
        expected = {'id': 'ODF2C3-QUIOA-HUDKEN'}
        self.assertEqual(order, expected)
        self.assertEqual(type(order), KrakenOrder)

    @responses.activate
    def test_close_position_id_not_found(self):
        fixture = {
            'error': [],
            'result': {
                'TZESOY-ABCDE-V3K2B3': {
                    'cost': '15.48400',
                    'fee': '0.04336',
                    'margin': '7.74200',
                    'misc': '',
                    'net': '-0.0178',
                    'oflags': '',
                    'ordertxid': 'O4M6JE-W3LHA-66LKK4',
                    'ordertype': 'market',
                    'pair': 'XETHZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1525653978',
                    'terms': '0.0200% per 4 hours',
                    'time': 1525639578.5486,
                    'type': 'sell',
                    'value': '15.50',
                    'vol': '0.02000000',
                    'vol_closed': '0.00000000'
                }
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenPositions'),
            json=fixture,
            status=200,
            content_type='application/json')
        with self.assertRaisesRegexp(KrakenException, 'Could not find position with ID: "WONT-BE-FOUND"'):
            order = self.client.close_position(
                position_id='WONT-BE-FOUND',
                symbol_pair=currencies.ETH_USD)

    @responses.activate
    def test_close_all_positions(self):
        fixture = {
            'error': [],
            'result': {
                'TZESOY-ABCDE-V3K2B3': {
                    'cost': '15.48400',
                    'fee': '0.04336',
                    'margin': '7.74200',
                    'misc': '',
                    'net': '-0.0178',
                    'oflags': '',
                    'ordertxid': 'O4M6JE-W3LHA-66LKK4',
                    'ordertype': 'market',
                    'pair': 'XETHZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1525653978',
                    'terms': '0.0200% per 4 hours',
                    'time': 1525639578.5486,
                    'type': 'sell',
                    'value': '15.50',
                    'vol': '0.02000000',
                    'vol_closed': '0.00000000'
                }
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/OpenPositions'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = {
            'error': [],
            'result': {
                'descr': {
                    'order': 'sell 0.02000000 ETHUSD @ limit 900.00 with 2:1 leverage'
                },
                'txid': ['ODF2C3-QUIOA-HUDKEN']
            }
        }
        responses.add(
            method='POST',
            url=re.compile('https://api.kraken.com/0/private/AddOrder'),
            json=fixture,
            status=200,
            content_type='application/json')
        self.client.close_all_positions(currencies.BTC_USD)
