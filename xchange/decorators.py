import importlib
from functools import wraps

from xchange.constants import currencies
from xchange import exceptions


def _validate_symbol_pair(value):
    if not value in currencies.SYMBOL_PAIRS:
        raise exceptions.InvalidSymbolPairException(
            'Given symbol pair "{}" is not valid'.format(symbol))


def is_valid_argument(arg_name, arg_position=0):
    def wrapper(original_func):
        @wraps(original_func)
        def wrapped(self, *args, **kwargs):
            assert arg_position is None or isinstance(arg_position, int)
            if arg_position is None:
                # look up in keyword arguments
                arg_value = kwargs.get(arg_name)
            else:
                arg_value = args[arg_position]
            module = importlib.import_module(__name__)
            getattr(module, '_validate_{}'.format(arg_name))(arg_value)
            return original_func(self, *args, **kwargs)
        return wrapped
    return wrapper
