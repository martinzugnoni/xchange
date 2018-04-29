import importlib
from functools import wraps

from xchange.constants import currencies, exchanges
from xchange import exceptions


def _validate_action(value):
    if not value in exchanges.ACTIONS:
        raise exceptions.InvalidActionException(
            'Given order action "{}" is invalid, use: {}'
            ''.format(value, ', '.join(exchanges.ACTIONS)))


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


def is_valid_argument(arg_name, arg_position=0):
    def wrapper(original_func):
        @wraps(original_func)
        def wrapped(self, *args, **kwargs):
            assert arg_position is None or isinstance(arg_position, int)
            arg_value = kwargs.get(arg_name)
            if arg_value is None:
                arg_value = args[arg_position]
            module = importlib.import_module(__name__)
            getattr(module, '_validate_{}'.format(arg_name))(arg_value)
            return original_func(self, *args, **kwargs)
        return wrapped
    return wrapper
