import time
import hmac
import json
import base64
import hashlib

from xchange.clients.base import BaseExchangeClient
from xchange.models.bitfinex import (
    BitfinexOrderBook, BitfinexAccountBalance, BitfinexOrder, BitfinexTicker,
    BitfinexPosition)
from xchange.constants import currencies
from xchange import decorators
from xchange import exceptions


class BitfinexClient(BaseExchangeClient):
    BASE_API_URL = 'https://api.bitfinex.com'
    ERROR_CLASS = exceptions.BitfinexException
    SYMBOLS_MAPPING = {
        currencies.BTC_USD: 'btcusd',
        currencies.ETH_USD: 'ethusd',
        currencies.LTC_USD: 'ltcusd',
    }

    def _sign_payload(self, payload):
        payload_dump = json.dumps(payload)
        data = base64.standard_b64encode(payload_dump.encode('utf8'))
        hash = hmac.new(self.api_secret.encode('utf8'), data, hashlib.sha384)
        signature = hash.hexdigest()
        return {
            "X-BFX-APIKEY": self.api_key,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }

    # transformation functions

    def _transform_account_balance(self, json_response):
        """
        Original JSON response:
        [
            {'amount': '0.0', 'available': '0.0', 'currency': 'btc', 'type': 'deposit'},
            {'amount': '0.0', 'available': '0.0', 'currency': 'btc', 'type': 'exchange'},
            {'amount': '0.0', 'available': '0.0', 'currency': 'btc', 'type': 'trading'},
            {'amount': '0.0', 'available': '0.0', 'currency': 'iot', 'type': 'deposit'},
            ...
        ]
        """
        # only take care of trading balances
        return [doc for doc in json_response if doc['type'] == 'trading']

    # public endpoints

    @decorators.is_valid_argument('symbol_pair')
    def get_ticker(self, symbol_pair):
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        return self._get('/v1/pubticker/{}'.format(symbol_pair),
                         model_class=BitfinexTicker)

    @decorators.is_valid_argument('symbol_pair')
    def get_order_book(self, symbol_pair):
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        return self._get('/v1/book/{}'.format(symbol_pair),
                         model_class=BitfinexOrderBook)

    # authenticated endpoints

    def get_account_balance(self):
        path = '/v1/balances'
        payload = {
            'request': path,
            'nonce': str(time.time())
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload,
                          transformation=self._transform_account_balance,
                          model_class=BitfinexAccountBalance)

    @decorators.is_valid_argument('symbol_pair')
    def get_open_orders(self, symbol_pair):
        path = '/v1/orders'
        payload = {
            'request': path,
            'nonce': str(time.time())
        }
        signed_payload = self._sign_payload(payload)
        data = self._post(path, headers=signed_payload,
                          model_class=BitfinexOrder)
        return [order for order in data
                if order['symbol_pair'] == symbol_pair]

    @decorators.is_valid_argument('action')
    @decorators.is_valid_argument('symbol_pair', arg_position=2)
    @decorators.is_valid_argument('order_type', arg_position=4)
    def open_order(self, action, amount, symbol_pair, price, order_type):
        path = '/v1/order/new'
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        payload = {
            'request': path,
            'nonce': str(time.time()),
            'side': action,
            'amount': amount,
            'symbol': symbol_pair,
            'price': price,
            'type': order_type,
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload,
                          model_class=BitfinexOrder)

    def cancel_order(self, order_id):
        path = '/v1/order/cancel'
        order_id = int(order_id)
        payload = {
            'request': path,
            'nonce': str(time.time()),
            'order_id': order_id
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload)

    def cancel_all_orders(self, symbol_pair):
        path = '/v1/order/cancel/all'
        payload = {
            'request': path,
            'nonce': str(time.time()),
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload)

    cancel_all_orders_sync = cancel_all_orders

    def get_open_positions(self, symbol_pair):
        path = '/v1/positions'
        payload = {
            'request': path,
            'nonce': str(time.time()),
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload,
                          model_class=BitfinexPosition)

    def close_position(self, action, amount, symbol_pair, price, order_type):
        path = '/v1/order/new'
        symbol_pair = self.SYMBOLS[symbol_pair]

        # as we want to close the possition,
        # we need to performe the opposite action to the given one.
        action = 'sell' if action == 'buy' else 'buy'

        payload = {
            'request': path,
            'nonce': str(time.time()),
            'side': action,
            'amount': amount,
            'symbol': symbol_pair,
            'price': price,
            'type': order_type,
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload,
                          model_class=BitfinexOrder)

    def close_all_positions(self, symbol_pair):
        positions = self.get_open_positions(symbol_pair=symbol_pair)
        if not positions:
            return
        for position in positions:
            self.close_position(
                action=position.action,
                amount=str(position.amount),
                symbol_pair=position.symbol_pair,
                price=str(position.price),
                order_type='market'
            )
