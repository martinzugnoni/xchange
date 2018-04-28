from tests import BaseXchangeTestCase
from xchange.factories import ExchangeClientFactory
from xchange.constants import exchanges
from xchange.clients import BitfinexClient


class ClientFactoryTestCase(BaseXchangeTestCase):

    def test_create_client_class(self):
        ClientClass = ExchangeClientFactory.get_client(exchanges.BITFINEX)
        self.assertEqual(ClientClass, BitfinexClient)

    def test_create_client_not_implemented(self):
        exchange_name = 'wontwork'
        error_msg = 'Client for exchange "{}" is not implemented'.format(exchange_name)
        with self.assertRaisesRegexp(NotImplementedError, error_msg):
            ExchangeClientFactory.get_client(exchange_name)
