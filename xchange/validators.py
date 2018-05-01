import collections


def is_restricted_to_values(value, valid_values):
    assert isinstance(valid_values, collections.Iterable)
    if not value in valid_values:
        raise ValueError('Invalid "{}" value, expected any of: {}'
                         ''.format(value, valid_values))


def is_instance(value, instance_types):
    assert isinstance(instance_types, (type, collections.Iterable))
    if isinstance(instance_types, collections.Iterable):
        assert all([isinstance(elem, type) for elem in instance_types])
    if not isinstance(value, instance_types):
        raise ValueError('Invalid type "{}" for given value, expected any of: {}'
                         ''.format(type(value), instance_types))


def passes_test(value, test_func):
    assert callable(test_func)
    try:
        assert test_func(value)
    except AssertionError:
        raise ValueError("Given value didn't pass provided test")
