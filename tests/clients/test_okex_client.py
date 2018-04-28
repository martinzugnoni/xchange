from tests import BaseXchangeTestCase
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges, currencies


class BaseOkexClientTestCase(BaseXchangeTestCase):
    def setUp(self):
        super().setUp()
        self.ClientClass = ExchangeClientFactory.get_client(exchanges.OKEX)
        self.client = self.ClientClass('API_KEY', 'API_SECRET')


class OkexClientTickerTestCase(BaseOkexClientTestCase):

    def test_get_ticker(self):
        ticker = self.client.get_ticker(currencies.BTC_USD)


class OkexClientOrderBookTestCase(BaseOkexClientTestCase):

    def test_get_order_book(self):
        order_book = self.client.get_order_book(currencies.BTC_USD)


class OkexClientAccountBalanceTestCase(BaseOkexClientTestCase):

    def test_get_account_balance(self):
        balance = self.client.get_account_balance()
