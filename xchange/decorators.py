import importlib
from functools import wraps
from decimal import Decimal, InvalidOperation

from xchange.constants import currencies, exchanges
from xchange import exceptions


def _validate_action(value):
    if not value in exchanges.ACTIONS:
        raise exceptions.InvalidActionException(
            'Given order action "{}" is invalid, use: {}'
            ''.format(value, ', '.join(exchanges.ACTIONS)))


def _validate_numeric_argument(value, ExceptionClass):
    exc = ExceptionClass(
        'Given amount "{}" is invalid, use: valid `int` value'.format(value))
    if not type(value) in [str, int, float, Decimal]:
        raise exc
    try:
        Decimal(value)
    except InvalidOperation:
        raise exc


def _validate_amount(value):
    _validate_numeric_argument(value, exceptions.InvalidAmountException)


def _validate_price(value):
    _validate_numeric_argument(value, exceptions.InvalidPriceException)


def _validate_symbol_pair(value):
    if not value in currencies.SYMBOL_PAIRS:
        raise exceptions.InvalidSymbolPairException(
            'Given symbol pair "{}" is invalid, use {}'
            ''.format(value, ', '.join(currencies.SYMBOL_PAIRS)))


def _validate_order_type(value):
    if not value in exchanges.ORDER_TYPES:
        raise exceptions.InvalidOrderTypeException(
            'Given order type "{}" is invalid, use: {}'
            ''.format(value, ', '.join(exchanges.ORDER_TYPES)))


def _validate_amount_in_contracts(value):
    if value is None:
        return
    if not isinstance(value, int) or not value > 0:
        raise exceptions.InvalidAmountContractsException(
            'Given amount_in_contracts value "{}" is invalid, use: '
            '`int` values greater than 0'.format(value))


def is_valid_argument(arg_name, arg_position=0):
    def wrapper(original_func):
        @wraps(original_func)
        def wrapped(self, *args, **kwargs):
            assert arg_position is None or isinstance(arg_position, int)
            if arg_name in kwargs:
                arg_value = kwargs[arg_name]
            else:
                try:
                    arg_value = args[arg_position]
                except IndexError:
                    arg_value = None
            module = importlib.import_module(__name__)
            getattr(module, '_validate_{}'.format(arg_name))(arg_value)
            return original_func(self, *args, **kwargs)
        return wrapped
    return wrapper
