from tests import BaseXchangeTestCase
from xchange.decorators import is_valid_argument
from xchange.constants import currencies
from xchange.exceptions import InvalidSymbolPairException


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
