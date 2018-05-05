from decimal import Decimal

from xchange.constants import currencies


def as_decimal(value):
    return Decimal(str(value))


def object_of_class(class_name):
    def func(obj):
        if obj.__class__.__name__ != class_name:
            raise ValueError('"{}" is not a valid class'.format(obj))
        return obj
    return func


def sorted_list(key, sorting_type):
    def func(original_list):
        reverse = False if sorting_type == 'asc' else True
        return sorted(original_list, key=key, reverse=reverse)
    return func


def restricted_to_values(values_list):
    values_list = [elem.lower() for elem in values_list]
    def func(original_value):
        original_value = original_value.lower()
        if original_value not in values_list:
            raise ValueError('"{}" is not a valid value'.format(original_value))
        return original_value
    return func


def normalized_symbol(original_symbol):
    mapping = currencies.SYMBOL_VARIANTS
    original_symbol = original_symbol.lower()
    if original_symbol in mapping.keys():
        # no need to normalize, symbol is already valid
        return original_symbol
    for symbol, variants in mapping.items():
        if original_symbol in variants:
            return symbol
    raise ValueError('Could not normalize {} symbol'.format(original_symbol))


def normalized_symbol_pair(original_pair):
    mapping = currencies.SYMBOL_PAIR_VARIANTS
    original_pair = original_pair.lower()
    if original_pair in mapping.keys():
        # no need to normalize, symbol pair is already valid
        return original_pair
    for pair, variants in mapping.items():
        if original_pair in variants:
            return pair
    raise ValueError('Could not normalize {} symbol pair'.format(original_pair))


def contracts_to_crypto(amount_in_contracts, crypto_last_price, unit_amount):
    """
    Transforms the amount of contracts to amount of given cryptos based
    on the `unit_amount` and last price of the coin.

    `unit_amount` is the price in USD of each contract.

    amount_in_crypto = amount_in_contracts * (unit_amount / crypto_last_price)
    """
    # convert all given values to Decimal
    amount_in_contracts, crypto_last_price, unit_amount = list(
        map(Decimal, [amount_in_contracts, crypto_last_price, unit_amount]))
    return amount_in_contracts * (unit_amount / crypto_last_price)


def crypto_to_contracts(amount_in_crypto, crypto_last_price, unit_amount):
    """
    Transforms the amount of given crypto to amount of contracts based
    on the `unit_amount` and last price of the coin.
    It rounds the amount of contracts to the nearest lower amount,
    because contracts can not be operated partially.
    ie: If contracts amount ends up being Decimal(1.6873),
        it returns Decimal(1).

    `unit_amount` is the price in USD of each contract.

    amount_in_contracts = (amount_in_crypto * crypto_last_price) / unit_amount
    """
    # convert all given values to Decimal
    amount_in_crypto, crypto_last_price, unit_amount = list(
        map(Decimal, [amount_in_crypto, crypto_last_price, unit_amount]))
    amount_in_contracts = (amount_in_crypto * crypto_last_price) / unit_amount
    return Decimal(int(amount_in_contracts))
