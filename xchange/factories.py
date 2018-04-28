import importlib

from xchange.clients import BitfinexClient
from xchange.constants import exchanges


class ExchangeClientFactory:

    @classmethod
    def get_client(self, exchange_name):
        if not exchange_name in exchanges.EXCHANGES:
            raise NotImplementedError(
                'Client for exchange "{}" is not implemented'.format(exchange_name))

        namespace = 'xchange.clients.{}'.format(exchange_name)
        clients_module = importlib.import_module(namespace)
        ClientClass = getattr(
            clients_module,
            '{}Client'.format(exchange_name.title())
        )
        return ClientClass
