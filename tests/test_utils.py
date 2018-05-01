from decimal import Decimal

from xchange import exceptions
from tests import BaseXchangeTestCase
from xchange.constants import exchanges
from xchange.models.base import OrderBook
from xchange.utils import volume_weighted_average_price


class VolumeWeightedAveragePriceTestCase(BaseXchangeTestCase):

    def test_volume_weighted_average_price_buy_order(self):
        order_book = OrderBook({
            "asks": [
                # (price_in_btc, amount_in_btc),
                (Decimal('9000'), Decimal('0.1')),
                (Decimal('8000'), Decimal('0.4')),
                (Decimal('7000'), Decimal('0.3')),
            ],
            "bids": [
                # (price_in_btc, amount_in_btc),
                (Decimal('4610.54856'), Decimal('0.078')),
                (Decimal('4600.78952'), Decimal('0.125')),
                (Decimal('4598.24567'), Decimal('0.458')),
            ]
        })
        avg_price = volume_weighted_average_price(
            exchanges.BUY,
            order_book,
            Decimal('0.5')
        )
        # (7000 * 0.3 + 8000 * 0.2) / 0.5 = 7400
        self.assertEqual(avg_price, Decimal('7400'))

    def test_volume_weighted_average_price_sell_order(self):
        order_book = OrderBook({
            "asks": [
                # (price_in_btc, amount_in_btc),
                (Decimal('4630.12300'), Decimal('0.014')),
                (Decimal('4620.23450'), Decimal('0.456')),
                (Decimal('4615.21356'), Decimal('0.315')),
            ],
            "bids": [
                # (price_in_btc, amount_in_btc),
                (Decimal('3000'), Decimal('0.3')),
                (Decimal('2000'), Decimal('0.4')),
                (Decimal('1000'), Decimal('0.1')),
            ]
        })
        avg_price = volume_weighted_average_price(
            exchanges.SELL,
            order_book,
            Decimal('0.5')
        )
        # (3000 * 0.3 + 2000 * 0.2) / 0.5 = 2600
        self.assertEqual(avg_price, Decimal('2600'))

    def test_volume_weighted_average_price_no_market_depth(self):
        order_book = OrderBook({
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
        with self.assertRaisesRegexp(exceptions.InsufficientMarketDepth,
                                     'Not enough depth in OrderBook to sell 2.0 volume'):
            volume_weighted_average_price(
                exchanges.SELL,
                order_book,
                Decimal('2.0')
            )
