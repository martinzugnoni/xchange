from decimal import Decimal

from tests import BaseXchangeTestCase
from xchange.decorators import is_valid_argument
from xchange.constants import currencies, exchanges
from xchange.exceptions import *


class IsValidArgumentDecoratorTestCase(BaseXchangeTestCase):

    def test_default(self):
        """Should search for the argument in the arg position '0' by default"""
        class Foo:
            @is_valid_argument('symbol_pair')
            def bar(self, symbol_pair):
                pass

        f = Foo()
        f.bar(currencies.BTC_USD)
        with self.assertRaises(InvalidSymbolPairException):
            f.bar('usd_usd')

    def test_custom_arg_position(self):
        """Should look for argument in `arg_position` if it's provided"""
        class Foo:
            @is_valid_argument('symbol_pair', arg_position=2)
            def bar(self, first_arg, second_arg, symbol_pair):
                pass

        f = Foo()
        f.bar(None, None, currencies.BTC_USD)
        with self.assertRaises(InvalidSymbolPairException):
            f.bar(None, None, 'usd_usd')

    def test_keyword_argument(self):
        """Should look for argument in the kwargs if arg_position is None"""
        class Foo:
            @is_valid_argument('symbol_pair', arg_position=None)
            def bar(self, first_arg, second_arg, symbol_pair=None):
                pass

        f = Foo()
        f.bar(None, None, symbol_pair=currencies.BTC_USD)
        with self.assertRaises(InvalidSymbolPairException):
            f.bar(None, None, symbol_pair='usd_usd')

    def test_valid_action(self):
        """Should validate `action` argument properly"""
        class Foo:
            @is_valid_argument('action')
            def bar(self, action):
                pass

        f = Foo()
        f.bar(exchanges.BUY)
        with self.assertRaises(InvalidActionException):
            f.bar('buysell')

    def test_valid_order_type(self):
        """Should validate `action` argument properly"""
        class Foo:
            @is_valid_argument('order_type')
            def bar(self, action):
                pass

        f = Foo()
        f.bar(exchanges.LIMIT)
        with self.assertRaises(InvalidOrderTypeException):
            f.bar('limitmarket')

    def test_valid_amount_in_contracts(self):
        """Should validate `amount_in_contracts` argument properly"""
        class Foo:
            @is_valid_argument('amount_in_contracts')
            def bar(self, amount_in_contracts=None):
                pass

        f = Foo()
        f.bar(amount_in_contracts=1)
        f.bar(amount_in_contracts=None)
        with self.assertRaises(InvalidAmountContractsException):
            f.bar(amount_in_contracts=0)
        with self.assertRaises(InvalidAmountContractsException):
            f.bar(amount_in_contracts='something-else')

    def test_valid_amount(self):
        """Should validate `amount` argument properly"""
        class Foo:
            @is_valid_argument('amount')
            def bar(self, amount):
                pass

        f = Foo()
        f.bar(1)
        f.bar('1.0')
        f.bar('10')
        f.bar(Decimal('100.20'))
        with self.assertRaises(InvalidAmountException):
            f.bar('somthingelse')
        with self.assertRaises(InvalidAmountException):
            f.bar(False)
        with self.assertRaises(InvalidAmountException):
            f.bar(None)

    def test_valid_price(self):
        """Should validate `price` argument properly"""
        class Foo:
            @is_valid_argument('price')
            def bar(self, price):
                pass

        f = Foo()
        f.bar(1)
        f.bar('1.0')
        f.bar('10')
        f.bar(Decimal('100.20'))
        with self.assertRaises(InvalidPriceException):
            f.bar('somthingelse')
        with self.assertRaises(InvalidPriceException):
            f.bar(False)
        with self.assertRaises(InvalidPriceException):
            f.bar(None)
