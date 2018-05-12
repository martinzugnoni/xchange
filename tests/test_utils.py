from decimal import Decimal

from xchange import exceptions
from tests import BaseXchangeTestCase
from xchange.constants import exchanges
from xchange.models.base import OrderBook
from xchange.utils import volume_weighted_average_price, worst_order_price


class VolumeWeightedAveragePriceTestCase(BaseXchangeTestCase):

    def setUp(self):
        self.order_book = OrderBook({
            "asks": [
                # (price_in_btc, amount_in_btc),
                (Decimal('9000'), Decimal('0.1')),
                (Decimal('8000'), Decimal('0.4')),
                (Decimal('7000'), Decimal('0.3')),
            ],
            "bids": [
                # (price_in_btc, amount_in_btc),
                (Decimal('3000'), Decimal('0.3')),
                (Decimal('2000'), Decimal('0.4')),
                (Decimal('1000'), Decimal('0.1')),
            ]
        })

    def test_volume_weighted_average_price_buy_order(self):
        avg_price = volume_weighted_average_price(
            exchanges.BUY,
            self.order_book,
            Decimal('0.5')
        )
        # (7000 * 0.3 + 8000 * 0.2) / 0.5 = 7400
        self.assertEqual(avg_price, Decimal('7400'))

    def test_volume_weighted_average_price_sell_order(self):
        avg_price = volume_weighted_average_price(
            exchanges.SELL,
            self.order_book,
            Decimal('0.5')
        )
        # (3000 * 0.3 + 2000 * 0.2) / 0.5 = 2600
        self.assertEqual(avg_price, Decimal('2600'))

    def test_volume_weighted_average_price_no_market_depth(self):
        with self.assertRaisesRegexp(exceptions.InsufficientMarketDepth,
                                     'Not enough depth in OrderBook to sell 2.0 volume'):
            volume_weighted_average_price(
                exchanges.SELL,
                self.order_book,
                Decimal('2.0')
            )


class WorstOrderPriceTestCase(BaseXchangeTestCase):

    def setUp(self):
        self.order_book = OrderBook({
            "asks": [
                # (price_in_btc, amount_in_btc),
                (Decimal('9000'), Decimal('0.1')),
                (Decimal('8000'), Decimal('0.4')),
                (Decimal('7000'), Decimal('0.3')),
            ],
            "bids": [
                # (price_in_btc, amount_in_btc),
                (Decimal('3000'), Decimal('0.3')),
                (Decimal('2000'), Decimal('0.4')),
                (Decimal('1000'), Decimal('0.1')),
            ]
        })

    def test_worst_order_price_buy_order(self):
        worst_price = worst_order_price(
            exchanges.BUY,
            self.order_book,
            Decimal('0.5')
        )
        self.assertEqual(worst_price, Decimal('8000'))

    def test_worst_order_price_buy_order_limit_amount(self):
        worst_price = worst_order_price(
            exchanges.BUY,
            self.order_book,
            Decimal('0.3')
        )
        self.assertEqual(worst_price, Decimal('7000'))

    def test_worst_order_price_sell_order(self):
        worst_price = worst_order_price(
            exchanges.SELL,
            self.order_book,
            Decimal('0.5')
        )
        self.assertEqual(worst_price, Decimal('2000'))

    def test_worst_order_price_sell_order_limit_amount(self):
        worst_price = worst_order_price(
            exchanges.SELL,
            self.order_book,
            Decimal('0.3')
        )
        self.assertEqual(worst_price, Decimal('3000'))

    def test_worst_order_price_no_market_depth(self):
        with self.assertRaisesRegexp(exceptions.InsufficientMarketDepth,
                                     'Not enough depth in OrderBook to sell 2.0 volume'):
            worst_order_price(
                exchanges.SELL,
                self.order_book,
                Decimal('2.0')
            )
