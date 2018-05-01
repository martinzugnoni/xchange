from decimal import Decimal

from tests import BaseXchangeTestCase
from xchange.validators import *


class IsRestrictedToValuesTestCase(BaseXchangeTestCase):

    def test_is_restricted_to_values_matches(self):
        is_restricted_to_values(1, (1, 2, 3))
        is_restricted_to_values("Hello", ("Hello", "World"))

    def test_is_restricted_to_values_dont_match(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid "Hello" value'):
            is_restricted_to_values("Hello", (1, 2, 3))
        with self.assertRaisesRegexp(ValueError, 'Invalid "1" value'):
            is_restricted_to_values(1, ("Hello", 2, 3, 4))

    def test_is_restricted_to_values_invalid_usage(self):
        with self.assertRaises(AssertionError):
            is_restricted_to_values("Hello", False)


class IsInstanceTestCase(BaseXchangeTestCase):

    def test_is_instance_matches(self):
        is_instance(True, (bool))
        is_instance(1, (int))
        is_instance("Hello", (str, int))
        is_instance("Hello", str)

    def test_is_instance_dont_match(self):
        with self.assertRaises(ValueError):
            is_instance(True, (float, str))
        with self.assertRaises(ValueError):
            is_instance("Hello", int)

    def test_is_instance_dont_invalid_usage(self):
        with self.assertRaises(AssertionError):
            is_instance(True, "Hello")
        with self.assertRaises(AssertionError):
            is_instance(True, (1, "Hello"))


class PassesTestTestCase(BaseXchangeTestCase):

    def test_passes_test_matches(self):
        passes_test(10, lambda x: x > 5)
        passes_test("Hello", lambda x: isinstance(x, str))
        passes_test("Hello", lambda x: len(x) == 5)
        passes_test("1.23", lambda x: Decimal(x))

    def test_passes_test_dont_match(self):
        with self.assertRaisesRegexp(ValueError, "Given value didn't pass provided test"):
            passes_test(10, lambda x: x > 15)
        with self.assertRaisesRegexp(ValueError, "Given value didn't pass provided test"):
            passes_test("Hello", lambda x: len(x) == 10)

    def test_passes_test_invalid_usage(self):
        with self.assertRaises(AssertionError):
            passes_test(1, "Hello")
        with self.assertRaises(AssertionError):
            passes_test(1, (1, 2, 3))
        with self.assertRaises(AssertionError):
            passes_test(1, None)
