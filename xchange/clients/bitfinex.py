import time
import hmac
import json
import base64
import hashlib
from decimal import Decimal

from xchange import exceptions
from xchange.constants import currencies, exchanges
from xchange.clients.base import BaseExchangeClient
from xchange.validators import is_restricted_to_values, is_instance, passes_test
from xchange.models.bitfinex import (
    BitfinexOrderBook, BitfinexAccountBalance, BitfinexOrder, BitfinexTicker,
    BitfinexPosition)


class BitfinexClient(BaseExchangeClient):
    BASE_API_URL = 'https://api.bitfinex.com'
    ERROR_CLASS = exceptions.BitfinexException
    SYMBOLS_MAPPING = {
        currencies.BTC_USD: 'btcusd',
        currencies.ETH_USD: 'ethusd',
        currencies.ETC_USD: 'etcusd',
        currencies.LTC_USD: 'ltcusd',
        currencies.BCH_USD: 'babusd', # Bitcoin Cash ABC
        currencies.XRP_USD: 'xrpusd',
        currencies.EOS_USD: 'eosusd',
        currencies.BTG_USD: 'btgusd',
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

    def get_ticker(self, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        return self._get('/v1/pubticker/{}'.format(symbol_pair),
                         model_class=BitfinexTicker, **kwargs)

    def get_order_book(self, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        return self._get('/v1/book/{}'.format(symbol_pair),
                         model_class=BitfinexOrderBook, **kwargs)

    # authenticated endpoints

    def get_account_balance(self, symbol=None, **kwargs):
        is_restricted_to_values(symbol, currencies.SYMBOLS + [None])

        path = '/v1/balances'
        payload = {
            'request': path,
            'nonce': str(time.time())
        }
        signed_payload = self._sign_payload(payload)
        data = self._post(path, headers=signed_payload,
                          transformation=self._transform_account_balance,
                          model_class=BitfinexAccountBalance, **kwargs)
        if symbol is None:
            return data
        for symbol_balance in data:
            if symbol_balance.symbol == symbol:
                return symbol_balance
        return self._empty_account_balance(symbol)

    def get_open_orders(self, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/v1/orders'
        payload = {
            'request': path,
            'nonce': str(time.time())
        }
        signed_payload = self._sign_payload(payload)
        data = self._post(path, headers=signed_payload,
                          model_class=BitfinexOrder, **kwargs)
        return [order for order in data
                if order['symbol_pair'] == symbol_pair]

    def open_order(self, action, amount, symbol_pair,
                   price, order_type, **kwargs):
        """
        Creates a new Order.

        :action:
            exchanges.ACTIONS choice
        :amount:
            Decimal, float, integer or string representing number value.
        :symbol_pair:
            currencies.SYMBOL_PAIRS choice
        :price:
            Decimal, float, integer or string representing number value.
        :order_type:
            exchanges.ORDER_TYPES choice
        """
        # validate arguments
        is_restricted_to_values(action, exchanges.ACTIONS)

        is_instance(amount, (Decimal, float, int, str))
        passes_test(amount, lambda x: Decimal(x))

        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        is_instance(price, (Decimal, float, int, str))
        passes_test(price, lambda x: isinstance(Decimal(x), Decimal))

        is_restricted_to_values(order_type, exchanges.ORDER_TYPES)

        path = '/v1/order/new'
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        payload = {
            'request': path,
            'nonce': str(time.time()),
            'side': action,
            'amount': str(amount),
            'symbol': symbol_pair,
            'price': str(price),
            'type': order_type,
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload,
                          model_class=BitfinexOrder, **kwargs)

    def cancel_order(self, order_id, **kwargs):
        path = '/v1/order/cancel'
        order_id = int(order_id)
        payload = {
            'request': path,
            'nonce': str(time.time()),
            'order_id': order_id
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload, **kwargs)

    def cancel_all_orders(self, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/v1/order/cancel/multi'
        orders = self.get_open_orders(symbol_pair=symbol_pair)
        if not orders:
            return
        payload = {
            'request': path,
            'nonce': str(time.time()),
            'order_ids': [order.id for order in orders]
        }
        signed_payload = self._sign_payload(payload)
        return self._post(path, headers=signed_payload, **kwargs)

    def get_open_positions(self, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/v1/positions'
        payload = {
            'request': path,
            'nonce': str(time.time()),
        }
        signed_payload = self._sign_payload(payload)
        positions = self._post(path, headers=signed_payload,
                               model_class=BitfinexPosition, **kwargs)
        return [pos for pos in positions
                if pos['symbol_pair'] == symbol_pair]

    def close_position(self, position_id, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        positions = self.get_open_positions(symbol_pair)
        try:
            pos = [pos for pos in positions if pos.id == position_id][0]
        except IndexError:
            raise self.ERROR_CLASS('Could not find position with '
                                   'ID: "{}"'.format(position_id))

        # as we want to close the position,
        # we need to performe the opposite action to the given one.
        action = exchanges.SELL if pos.action == exchanges.BUY else exchanges.BUY

        return self.open_order(
            action, pos.amount, pos.symbol_pair, pos.price,
            exchanges.MARKET, **kwargs)

    def close_all_positions(self, symbol_pair, **kwargs):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        positions = self.get_open_positions(symbol_pair=symbol_pair)
        for pos in positions:
            self.close_position(pos.id, pos.symbol_pair, **kwargs)
