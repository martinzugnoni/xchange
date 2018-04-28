import re
import responses
from decimal import Decimal

from tests import BaseXchangeTestCase
from tests.fixtures import okex
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies
from xchange.models.okex import (
    OkexTicker, OkexOrderBook, OkexAccountBalance)


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
