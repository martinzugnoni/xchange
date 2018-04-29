from decimal import Decimal

from tests import BaseXchangeTestCase
from xchange.models.base import (
    Ticker, OrderBook
)

class TickerTestCase(BaseXchangeTestCase):

    def test_ticker(self):
        ticker = Ticker({
            'ask': '9314.65',
            'bid': '100.51',
            'high': '9480',
            'last': '9312.34',
            'low': '8800',
            'volume': '16185076',
        })
        self.assertEqual(ticker.ask, Decimal('9314.65'))
        self.assertEqual(ticker.bid, Decimal('100.51'))
        self.assertEqual(ticker.high, Decimal('9480'))
        self.assertEqual(ticker.last, Decimal('9312.34'))
        self.assertEqual(ticker.low, Decimal('8800'))
        self.assertEqual(ticker.volume, Decimal('16185076'))

        with self.assertRaisesRegexp(AttributeError,
                                     'Object Ticker has not attribute "foobar"'):
            ticker.foobar

    def test_ticker_invalid_data(self):
        with self.assertRaisesRegexp(ValueError,
                                     'Unknown field "foo" for class Ticker'):
            Ticker({
                'foo': 'bar'
            })


class OrderBookTestCase(BaseXchangeTestCase):

    def test_order_book(self):
        order_book = OrderBook({
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
        })
        self.assertEqual(type(order_book.asks), list)
        self.assertEqual(type(order_book.bids), list)

        with self.assertRaisesRegexp(AttributeError,
                                     'Object OrderBook has not attribute "foobar"'):
            order_book.foobar

    def test_order_book_invalid_data(self):
        with self.assertRaisesRegexp(ValueError,
                                     'Unknown field "foo" for class OrderBook'):
            OrderBook({
                'foo': 'bar'
            })
