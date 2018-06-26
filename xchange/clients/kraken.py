import time
import hmac
import base64
import hashlib
from decimal import Decimal
try:
    from urllib.parse import urlencode
except ImportError:
     from urllib import urlencode

from xchange import exceptions
from xchange.constants import exchanges, currencies
from xchange.clients.base import BaseExchangeClient
from xchange.validators import is_restricted_to_values, is_instance, passes_test
from xchange.models.kraken import (
    KrakenOrderBook, KrakenAccountBalance, KrakenOrder, KrakenTicker,
    KrakenPosition)


class KrakenClient(BaseExchangeClient):
    USERREF = 7886259  # random number
    BASE_API_URL = 'https://api.kraken.com'
    ERROR_CLASS = exceptions.KrakenException
    SYMBOLS_MAPPING = {
        currencies.BTC_USD: 'XBTUSD',
        currencies.ETH_USD: 'ETHUSD',
        currencies.ETC_USD: 'ETCUSD',
        currencies.LTC_USD: 'LTCUSD',

        currencies.BCH_USD: 'BCHUSD',
        currencies.XRP_USD: 'XRPUSD',
        currencies.EOS_USD: 'EOSUSD',
    }

    def _sign_payload(self, urlpath, payload):
        postdata = urlencode(payload)
        encoded = (str(payload['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(base64.b64decode(self.api_secret),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())
        return sigdigest.decode()

    def get_userref(self, symbol_pair):
        """
        TODO: Explain this
        """
        index = sorted(self.SYMBOLS_MAPPING).index(symbol_pair)
        return int('{}{}'.format(self.USERREF, index))

    # transformation functions

    def _transform_ticker(self, json_response):
        """
        Original JSON reponse:
        {'error': [],
         'result': {'XXBTZUSD': {
             'a': ['3809.00000', '1', '1.000'],
             'b': ['3803.60000', '1', '1.000'],
             'c': ['3809.30000', '0.08000000'],
             'h': ['3830.30000', '3830.30000'],
             'l': ['3570.10000', '3525.10000'],
             'o': '3606.80000',
             'p': ['3717.00933', '3650.22371'],
             't': [6565, 14224],
             'v': ['2204.84583619', '4523.49526430']}}}
        """
        for symbol, ticker in json_response['result'].items():
            # as we will always get only one ticker dict, return the first
            # one in the iteration.
            return ticker

    def _transform_account_balance(self, json_response):
        """
        Original JSON response:
        {'error': [], 'result': {'XXBT': '0.0142771914', 'ZUSD': '0.0000'}}
        """
        return [
            {'currency': key, 'amount': value}
            for key, value in json_response['result'].items()
        ]

    def _transform_new_order(self, json_response):
        """
        Original JSON response:
        {'error': [],
         'result': {'descr': {'order': 'sell 0.02000000 ETHUSD @ limit 900.00 with 2:1 '
                                       'leverage'},
                    'txid': ['ODF2C3-OVVBA-HAYTEN']}}
        """
        return {
            'id': json_response['result']['txid'][0]
        }

    def _transform_open_orders(self, json_response):
        """
        Original JSON response:
        {
            'error': [],
            'result': {
                'open': {
                    'OGYUJ3-LSWJV-4OD4DU': {
                        'cost': '0.00000',
                        'descr': {
                            'leverage': 'none',
                            'order': 'sell 0.00500000 XBTUSD @ limit 5000.0',
                            'ordertype': 'limit',
                            'pair': 'XBTUSD',
                            'price': '5000.0',
                            'price2': '0',
                            'type': 'sell'
                        },
                        'expiretm': 0,
                        'fee': '0.00000',
                        'misc': '',
                        'oflags': 'fciq',
                        'opentm': 1505603660.2901,
                        'price': '0.00000',
                        'refid': None,
                        'starttm': 0,
                        'status': 'open',
                        'userref': None,
                        'vol': '0.00500000',
                        'vol_exec': '0.00000000'
                    }
                }
            }
        }
        """
        transformed_response = []
        for status, orders_dict in json_response['result'].items():
            for order_id, order_data in orders_dict.items():
                order_data['id'] = order_id
                order_data['status'] = status
                transformed_response.append(order_data)
        return transformed_response

    def _transform_open_positions(self, json_response):
        """
        Original JSON response:
        {
            'error': [],
            'result': {
                'TZNYBD-GOE2N-4LTHWQ': {
                    'cost': '18.67650',
                    'fee': '0.05043',
                    'margin': '9.33825',
                    'misc': '',
                    'net': '+0.0352',
                    'oflags': '',
                    'ordertxid': 'OJF4YH-EPNOR-PKWMGG',
                    'ordertype': 'market',
                    'pair': 'XXBTZUSD',
                    'posstatus': 'open',
                    'rollovertm': '1505618241',
                    'terms': '0.0100% per 4 hours',
                    'time': 1505603841.1963,
                    'type': 'sell',
                    'value': '18.6',
                    'vol': '0.00500000',
                    'vol_closed': '0.00000000'
                }
            }
        }
        """
        transformed_response = []
        for position_id, position_dict in json_response['result'].items():
            position_dict['id'] = position_id
            transformed_response.append(position_dict)
        return transformed_response

    # public endpoints

    def get_ticker(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        params = {'pair': symbol_pair}
        return self._get('/0/public/Ticker', params=params,
                         transformation=self._transform_ticker,
                         model_class=KrakenTicker)

    def get_order_book(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        params = {'pair': symbol_pair}
        return self._get('/0/public/Depth', params=params,
                         model_class=KrakenOrderBook)

    # authenticated endpoints

    def get_account_balance(self, symbol=None):
        is_restricted_to_values(symbol, currencies.SYMBOLS + [None])

        path = '/0/private/Balance'
        payload = {
            'nonce': int(1000 * time.time()),
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign_payload(path, payload)
        }
        data = self._post(path, headers=headers, body=payload,
                          transformation=self._transform_account_balance,
                          model_class=KrakenAccountBalance)

        if symbol is None:
            return data
        for symbol_balance in data:
            if symbol_balance.symbol == symbol:
                return symbol_balance
        return self._empty_account_balance(symbol)

    def get_open_orders(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/0/private/OpenOrders'
        payload = {
            'nonce': int(1000 * time.time()),
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign_payload(path, payload)
        }
        data = self._post(path, headers=headers, body=payload,
                          transformation=self._transform_open_orders,
                          model_class=KrakenOrder)
        return [order for order in data
                if order['symbol_pair'] == symbol_pair]

    def open_order(self, action, amount, symbol_pair, price, order_type):
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

        path = '/0/private/AddOrder'
        userref = self.get_userref(symbol_pair)
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        payload = {
            'pair': symbol_pair,
            'type': action,
            'ordertype': order_type,
            'price': Decimal(str(price)),
            'volume': Decimal(str(amount)),
            'leverage': 2,
            'nonce': int(1000 * time.time()),
            'userref': userref,
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign_payload(path, payload)
        }
        return self._post(path, headers=headers, body=payload,
                          transformation=self._transform_new_order,
                          model_class=KrakenOrder)

    def cancel_order(self, order_id):
        path = '/0/private/CancelOrder'
        payload = {
            'nonce': int(1000 * time.time()),
            'txid': order_id
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign_payload(path, payload)
        }
        return self._post(path, headers=headers, body=payload)

    def cancel_all_orders(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/0/private/CancelOrder'
        payload = {
            'nonce': int(1000 * time.time()),
            'txid': self.get_userref(symbol_pair)
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign_payload(path, payload)
        }
        return self._post(path, headers=headers, body=payload)

    def get_open_positions(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/0/private/OpenPositions'
        payload = {
            'nonce': int(1000 * time.time()),
            'docalcs': True,
        }
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign_payload(path, payload)
        }
        positions = self._post(path, headers=headers, body=payload,
                               transformation=self._transform_open_positions,
                               model_class=KrakenPosition)
        return [pos for pos in positions
                if pos['symbol_pair'] == symbol_pair]

    def close_position(self, position_id, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        positions = self.get_open_positions(symbol_pair)
        try:
            pos = [pos for pos in positions if pos.id == position_id][0]
        except IndexError:
            raise self.ERROR_CLASS('Could not find position with ID: "{}"'.format(position_id))

        # as we want to close the position,
        # we need to performe the opposite action to the given one.
        action = exchanges.SELL if pos.action == exchanges.BUY else exchanges.BUY

        return self.open_order(
            action, pos.amount, pos.symbol_pair, pos.price, exchanges.MARKET)

    def close_all_positions(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        positions = self.get_open_positions(symbol_pair=symbol_pair)
        for pos in positions:
            self.close_position(pos.id, pos.symbol_pair)
