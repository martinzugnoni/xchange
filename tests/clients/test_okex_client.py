import re
import responses
from decimal import Decimal

from tests import BaseXchangeTestCase
from tests.fixtures import okex
from xchange.exceptions import *
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies
from xchange.models.okex import (
    OkexTicker, OkexOrderBook, OkexAccountBalance, OkexOrder)


class BaseOkexClientTestCase(BaseXchangeTestCase):
    def setUp(self):
        super(BaseOkexClientTestCase, self).setUp()
        self.ClientClass = ExchangeClientFactory.get_client(exchanges.OKEX)
        self.client = self.ClientClass('API_KEY', 'API_SECRET')

        for fixture in okex.FIXTURE_RESPONSES:
            responses.add(
                method=fixture['method'],
                url=re.compile(fixture['url_regex']),
                json=fixture['json'],
                status=fixture['status'],
                content_type=fixture['content_type'],
                match_querystring=True)


class OkexClientTickerTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_get_ticker(self):
        ticker = self.client.get_ticker(currencies.BTC_USD)
        expected = {
            'ask': Decimal('9314.65999999999985448084771633148193359375'),
            'bid': Decimal('100.5100000000000051159076974727213382720947265625'),
            'high': Decimal('9480'),
            'last': Decimal('9312.34000000000014551915228366851806640625'),
            'low': Decimal('8800'),
            'volume': Decimal('16185076')
        }
        self.assertEqual(ticker, expected)
        self.assertEqual(type(ticker), OkexTicker)


class OkexClientOrderBookTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_get_order_book(self):
        order_book = self.client.get_order_book(currencies.BTC_USD)
        expected = {
            'asks': [
                (Decimal('9315.489999999999781721271574497222900390625'),
                Decimal('0.05369219766460416954135662055')),
                (Decimal('9315.469999999999345163814723491668701171875'),
                Decimal('0.8268598440349042109368919565')),
                (Decimal('9315.45000000000072759576141834259033203125'),
                Decimal('0.5261835371131208615052948814')),
                (Decimal('9315.059999999999490682967007160186767578125'),
                Decimal('0.1073843953292083390827132411')),
                (Decimal('9314.780000000000654836185276508331298828125'),
                Decimal('0.1073843953292083390827132411'))],
            'bids': [
                (Decimal('9314.579999999999927240423858165740966796875'),
                Decimal('1.234920546285895899451202273')),
                (Decimal('9313.29999999999927240423858165740966796875'),
                Decimal('0.8805520416995083804782485770')),
                (Decimal('9313.0400000000008731149137020111083984375'),
                Decimal('0.9986748765616375534692331422')),
                (Decimal('9311.72999999999956344254314899444580078125'),
                Decimal('0.5369219766460416954135662055')),
                (Decimal('9311.420000000000072759576141834259033203125'),
                Decimal('0.6872601301069333701293647430')),
                (Decimal('9310.9599999999991268850862979888916015625'),
                Decimal('0.09664595579628750517444191699'))
            ]
        }
        self.assertEqual(order_book, expected)
        self.assertEqual(type(order_book), OkexOrderBook)


class OkexClientAccountBalanceTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_get_account_balance(self):
        balance = self.client.get_account_balance()
        expected = [
            {'amount': Decimal('0.01645887000000000044419579126042663119733333587646484375'), 'symbol': 'btc'},
            {'amount': Decimal('0'), 'symbol': 'ltc'}
        ]
        self.assertEqual(
            sorted(balance, key=lambda x: x['symbol']),
            sorted(expected, key=lambda x: x['symbol']))
        self.assertEqual(type(balance), list)
        for obj in balance:
            self.assertEqual(type(obj), OkexAccountBalance)


class OkexGetOpenOrdersTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_get_open_orders(self):
        fixture = {
            'orders': [
                {
                    'amount': 1,
                    'contract_name': 'BTC0929',
                    'create_date': 1503614569000,
                    'deal_amount': 0,
                    'fee': 0,
                    'lever_rate': 10,
                    'order_id': 8934112485,
                    'price': 5000,
                    'price_avg': 0,
                    'status': 0,
                    'symbol': 'btc_usd',
                    'type': 2,
                    'unit_amount': 100
                }
            ],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_order_info\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.BTC_USD)
        expected = [
            {
                'id': '8934112485',
                'action': 'sell',
                'amount': Decimal('1'),
                'price': Decimal('5000'),
                'status': 'open',
                'symbol_pair': 'btc_usd',
                'type': 'limit'
            }
        ]
        self.assertEqual(type(open_orders), list)
        for obj in open_orders:
            self.assertEqual(type(obj), OkexOrder)
        self.assertEqual(open_orders, expected)

    @responses.activate
    def test_get_open_orders_filters_by_symbol_pair(self):
        fixture = {
            'orders': [
                {
                    'amount': 1,
                    'contract_name': 'BTC0929',
                    'create_date': 1503614569000,
                    'deal_amount': 0,
                    'fee': 0,
                    'lever_rate': 10,
                    'order_id': 8934112485,
                    'price': 5000,
                    'price_avg': 0,
                    'status': 0,
                    'symbol': 'btc_usd',
                    'type': 2,
                    'unit_amount': 100
                },
                {
                    'amount': 1,
                    'contract_name': 'ETH0929',
                    'create_date': 1503614569000,
                    'deal_amount': 0,
                    'fee': 0,
                    'lever_rate': 10,
                    'order_id': 8934112485,
                    'price': 5000,
                    'price_avg': 0,
                    'status': 0,
                    'symbol': 'eth_usd',
                    'type': 2,
                    'unit_amount': 100
                },
            ],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_order_info\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.ETH_USD)
        expected = [
            {
                'id': '8934112485',
                'action': 'sell',
                'amount': Decimal('1'),
                'price': Decimal('5000'),
                'status': 'open',
                'symbol_pair': 'eth_usd',
                'type': 'limit'
            }
        ]
        self.assertEqual(type(open_orders), list)
        self.assertEqual(len(open_orders), 1)
        for obj in open_orders:
            self.assertEqual(type(obj), OkexOrder)
        self.assertEqual(open_orders, expected)

    @responses.activate
    def test_get_open_orders_no_open_orders(self):
        fixture = {'orders': [], 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_order_info\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        open_orders = self.client.get_open_orders(currencies.BTC_USD)
        self.assertEqual(type(open_orders), list)
        self.assertEqual(len(open_orders), 0)
        self.assertEqual(open_orders, [])


class OkexOpenOrderTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_open_order(self):
        fixture = {'order_id': 8931546905, 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_trade\.do'),
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
            'id': '8931546905'
        }
        self.assertEqual(order, expected)
        self.assertEqual(type(order), OkexOrder)

    @responses.activate
    def test_open_order_amount_in_contracts(self):
        fixture = {'order_id': 8931458965, 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_trade\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        order = self.client.open_order(
            action=exchanges.SELL,
            amount='2',
            amount_in_contracts=True,
            symbol_pair=currencies.BTC_USD,
            price='4118.0',
            order_type=exchanges.LIMIT)
        expected = {
            'id': '8931458965'
        }
        self.assertEqual(order, expected)
        self.assertEqual(type(order), OkexOrder)

    @responses.activate
    def test_open_order_amount_in_contracts_too_small(self):
        fixture = {'order_id': 8931458965, 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_trade\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        with self.assertRaisesRegexp(ValueError,
                                     "Given value didn't pass provided test"):
            self.client.open_order(
                action=exchanges.SELL,
                amount='0.021',  # must be greater or equal to 1
                amount_in_contracts=True,
                symbol_pair=currencies.BTC_USD,
                price='4118.0',
                order_type=exchanges.LIMIT)


class OkexCancelOrderTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_cancel_order(self):
        fixture = {
            'orders': [
                {
                    'order_id': 8934112485,
                    'amount': 1,
                    'contract_name': 'BTC0929',
                    'create_date': 1503614569000,
                    'deal_amount': 0,
                    'fee': 0,
                    'lever_rate': 10,
                    'price': 5000,
                    'price_avg': 0,
                    'status': 0,
                    'symbol': 'btc_usd',
                    'type': 2,
                    'unit_amount': 100
                }
            ],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_order_info\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = {'order_id': '8934112485', 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_cancel\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        response = self.client.cancel_order(8934112485)
        self.assertEqual(response, fixture)

    @responses.activate
    def test_cancel_order_id_not_found(self):
        fixture = {
            'orders': [],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_order_info\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        with self.assertRaisesRegexp(ValueError, 'Could not find order with ID "8934112485"'):
            self.client.cancel_order(8934112485)

    @responses.activate
    def test_cancel_all_orders(self):
        fixture = {
            'orders': [
                {
                    'order_id': 8934112485,
                    'amount': 1,
                    'contract_name': 'BTC0929',
                    'create_date': 1503614569000,
                    'deal_amount': 0,
                    'fee': 0,
                    'lever_rate': 10,
                    'price': 5000,
                    'price_avg': 0,
                    'status': 0,
                    'symbol': 'btc_usd',
                    'type': 2,
                    'unit_amount': 100
                },
                {
                    'order_id': 8913469485,
                    'amount': 1,
                    'contract_name': 'BTC0929',
                    'create_date': 1503254699000,
                    'deal_amount': 0,
                    'fee': 0,
                    'lever_rate': 10,
                    'price': 5000,
                    'price_avg': 0,
                    'status': 0,
                    'symbol': 'btc_usd',
                    'type': 2,
                    'unit_amount': 100
                },
            ],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_order_info\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = {'order_id': '8934112485,8913469485', 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_cancel\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        response = self.client.cancel_all_orders(currencies.BTC_USD)
        self.assertEqual(response, fixture)


class OkexGetOpenPositionsTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_get_open_positions(self):
        fixture = {
            'force_liqu_price': '10,604.11',
            'holding': [{
                'buy_amount': 0,
                'buy_available': 0,
                'buy_price_avg': 3348,
                'buy_price_cost': 3348,
                'buy_profit_real': 0.00052895,
                'contract_id': 20171222465,
                'contract_type': 'quarter',
                'create_date': 1505469260000,
                'lever_rate': 20,
                'sell_amount': 1,
                'sell_available': 1,
                'sell_price_avg': 3896.13,
                'sell_price_cost': 3896.13,
                'sell_profit_real': -0.1,
                'symbol': 'btc_usd'
            }],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_position\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.BTC_USD)
        expected = [
            {
                'action': 'sell',
                'amount': Decimal('1'),
                'id': 'None',
                'price': Decimal('3896.1300000000001091393642127513885498046875'),
                'profit_loss': Decimal('-0.1000000000000000055511151231257827021181583404541015625'),
                'symbol_pair': 'btc_usd'
            }
        ]
        self.assertEqual(positions, expected)

    @responses.activate
    def test_get_open_positions_no_positions(self):
        fixture = {
            'force_liqu_price': '0.00',
            'holding': [{
                'buy_amount': 0,
                'buy_available': 0,
                'buy_price_avg': 3348,
                'buy_price_cost': 3348,
                'buy_profit_real': 0.00052895,
                'contract_id': 20171453212,
                'contract_type': 'quarter',
                'create_date': 1505612590000,
                'lever_rate': 20,
                'sell_amount': 0,
                'sell_available': 0,
                'sell_price_avg': 3896.13,
                'sell_price_cost': 3896.13,
                'sell_profit_real': 0.00010698,
                'symbol': 'btc_usd'
            }],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_position\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        positions = self.client.get_open_positions(currencies.BTC_USD)
        expected = []
        self.assertEqual(positions, expected)


class OkexClosePositionTestCase(BaseOkexClientTestCase):

    @responses.activate
    def test_close_position(self):
        fixture = {'order_id': 8931546905, 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_trade\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        order = self.client.close_position(
            action=exchanges.SELL,
            amount='0.01209215',
            symbol_pair=currencies.BTC_USD,
            price='4118.0',
            order_type=exchanges.MARKET)
        expected = {
            'id': '8931546905'
        }
        self.assertEqual(order, expected)
        self.assertEqual(type(order), OkexOrder)

    @responses.activate
    def test_close_all_positions(self):
        fixture = {
            'force_liqu_price': '10,604.11',
            'holding': [{
                'buy_amount': 0,
                'buy_available': 0,
                'buy_price_avg': 3348,
                'buy_price_cost': 3348,
                'buy_profit_real': 0.00052895,
                'contract_id': 20171222465,
                'contract_type': 'quarter',
                'create_date': 1505469260000,
                'lever_rate': 20,
                'sell_amount': 1,
                'sell_available': 1,
                'sell_price_avg': 3896.13,
                'sell_price_cost': 3896.13,
                'sell_profit_real': -0.1,
                'symbol': 'btc_usd'
            }],
            'result': True
        }
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_position\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        fixture = {'order_id': 8945328905, 'result': True}
        responses.add(
            method='POST',
            url=re.compile('https://www\.okex\.com/api/v1/future_trade\.do'),
            json=fixture,
            status=200,
            content_type='application/json')
        self.client.close_all_positions(currencies.BTC_USD)
