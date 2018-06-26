import logging
import hashlib
from decimal import Decimal

from cached_property import cached_property_with_ttl

from xchange import exceptions
from xchange.constants import currencies, exchanges
from xchange.clients.base import BaseExchangeClient
from xchange.models.base import crypto_to_contracts
from xchange.validators import is_restricted_to_values, is_instance, passes_test
from xchange.models.okex import (
    OkexTicker, OkexOrderBook, OkexAccountBalance, OkexOrder, OkexPosition)


class OkexClient(BaseExchangeClient):
    BASE_API_URL = 'https://www.okex.com/api'
    ERROR_CLASS = exceptions.OkexException
    SYMBOLS_MAPPING = {
        currencies.BTC_USD: 'btc_usd',
        currencies.ETH_USD: 'eth_usd',
        currencies.ETC_USD: 'etc_usd',
        currencies.LTC_USD: 'ltc_usd',
        currencies.BCH_USD: 'bch_usd',
        currencies.XRP_USD: 'xrp_usd',
        currencies.EOS_USD: 'eos_usd',
        currencies.BTG_USD: 'btg_usd',
    }
    ORDER_STATUS = {
        'unfilled': 1,
        'filled': 2
    }
    ACTION = {
        'open_long': 1,
        'open_short': 2,
        'close_long': 3,
        'close_short': 4,
    }
    CONTRACT_UNIT_AMOUNTS = {
        'btc_usd': 100,
        'eth_usd': 10,
        'etc_usd': 10,
        'ltc_usd': 10,
        'bch_usd': 10,
        'xrp_usd': 10,
        'eos_usd': 10,
        'btg_usd': 10,
    }

    def _sign_params(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'
        data = sign + 'secret_key=' + self.api_secret
        return hashlib.md5(data.encode("utf8")).hexdigest().upper()

    # transformation functions
    def _transform_account_balance(self, json_response):
        """
        Original JSON response:
        {'info': {
              'btc': {
                   'account_rights': 0.01628945,
                   'keep_deposit': 0,
                   'profit_real': -0.00031059,
                   'profit_unreal': 0,
                   'risk_rate': 10000},
              'ltc': {
                   'account_rights': 0,
                   'keep_deposit': 0,
                   'profit_real': 0,
                   'profit_unreal': 0,
                   'risk_rate': 10000}},
              'result': True}
        """
        return [
            {'currency': key, 'amount': value['account_rights']}
            for key, value in json_response['info'].items()
        ]

    def _transform_open_orders(self, json_response):
        """
        Original JSON response:

        # without open orders
        {'orders': [], 'result': True}

        # with open orders
        {'orders': [{
           'amount': 1,
           'contract_name': 'BTC1229',
           'create_date': 1506188792000,
           'deal_amount': 0,
           'fee': 0,
           'lever_rate': 20,
           'order_id': 10602289748,
           'price': 3000,
           'price_avg': 0,
           'status': 0,
           'symbol': 'btc_usd',
           'type': 1,
           'unit_amount': 100}],
         'result': True}
        """
        return json_response['orders']

    def _transform_open_positions(self, json_response):
        """
        Original JSON response:
        {'force_liqu_price': '0.00',
         'holding': [{'buy_amount': 0,
                    'buy_available': 0,
                    'buy_price_avg': 3620.31999724,
                    'buy_price_cost': 3620.31999724,
                    'buy_profit_real': 0,
                    'contract_id': 20171229012,
                    'contract_type': 'quarter',
                    'create_date': 1505609260000,
                    'lever_rate': 20,
                    'sell_amount': 0,
                    'sell_available': 0,
                    'sell_price_avg': 3930.07,
                    'sell_price_cost': 3930.07,
                    'sell_profit_real': 0,
                    'symbol': 'btc_usd'}],
         'result': True}
        """
        positions_data = json_response['holding']
        if not positions_data:
            return []
        positions = []
        if positions_data[0]['buy_amount']:
            positions.append({
                'id': None,
                'action': 'buy',
                'amount': positions_data[0]['buy_amount'],
                'price': positions_data[0]['buy_price_cost'],
                'symbol_pair': positions_data[0]['symbol'],
                'profit_loss': positions_data[0]['buy_profit_real'],
            })
        if positions_data[0]['sell_amount']:
            positions.append({
                'id': None,
                'action': 'sell',
                'amount': positions_data[0]['sell_amount'],
                'price': positions_data[0]['sell_price_cost'],
                'symbol_pair': positions_data[0]['symbol'],
                'profit_loss': positions_data[0]['sell_profit_real'],
            })
        return positions

    # public endpoints

    def get_ticker(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        return self._get('/v1/future_ticker.do?symbol={}&contract_type=quarter'
                         ''.format(symbol_pair), model_class=OkexTicker)

    def get_order_book(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        OkexOrderBook.TICKER = getattr(self, '{}_ticker'.format(symbol_pair))
        OkexOrderBook.SYMBOL = symbol_pair
        OkexOrderBook.CONTRACT_UNIT_AMOUNTS = self.CONTRACT_UNIT_AMOUNTS
        return self._get('/v1/future_depth.do?size=100&symbol={}&contract_type=quarter'
                         ''.format(symbol_pair), model_class=OkexOrderBook)

    # authenticated endpoints

    def get_account_balance(self, symbol=None):
        is_restricted_to_values(symbol, currencies.SYMBOLS + [None])

        path = '/v1/future_userinfo.do'
        params = {}
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        data = self._post(path, params=params,
                          transformation=self._transform_account_balance,
                          model_class=OkexAccountBalance)
        if symbol is None:
            return data
        for symbol_balance in data:
            if symbol_balance.symbol == symbol:
                return symbol_balance
        raise self.ERROR_CLASS('Symbol "{}" was not found in the account balance'.format(symbol))

    def get_open_orders(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        path = '/v1/future_order_info.do'
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
            'status': self.ORDER_STATUS['unfilled'],
            'order_id': -1,  # all orders with given "status"
            'current_page': 1,
            'page_length': 50,
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        data = self._post(path, params=params,
                          transformation=self._transform_open_orders,
                          model_class=OkexOrder)
        return [order for order in data
                if order['symbol_pair'] == symbol_pair]

    def open_order(self, action, amount, symbol_pair, price, order_type,
                   amount_in_contracts=False, closing=False):
        """
        Creates a new Order.

        :action:
            exchanges.ACTIONS choice
        :amount:
            Decimal, float, integer or string representing number value.
            If `amount_in_contracts == True`, `amount` needs to be an
            integer number greater or equal to 1.
        :symbol_pair:
            currencies.SYMBOL_PAIRS choice
        :price:
            Decimal, float, integer or string representing number value.
        :order_type:
            exchanges.ORDER_TYPES choice
        :amount_in_contracts:
            (True|False) Whether the `amount`  argument is expressed in cryptos or contracts
        :closing:
            (True|False) Whether the order we are opening is to close an existing position or not
        """
        # validate arguments
        is_restricted_to_values(action, exchanges.ACTIONS)

        is_instance(amount, (Decimal, float, int, str))
        passes_test(amount, lambda x: Decimal(x))
        if amount_in_contracts:
            passes_test(amount, lambda x: Decimal(x) >= 1)

        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        is_instance(price, (Decimal, float, int, str))
        passes_test(price, lambda x: Decimal(x))

        is_restricted_to_values(order_type, exchanges.ORDER_TYPES)

        is_instance(amount_in_contracts, bool)
        is_instance(closing, bool)

        path = '/v1/future_trade.do'
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        if closing:
            action = (self.ACTION['close_long']
                      if action == exchanges.SELL
                      else self.ACTION['close_short'])
        else:
            action = (self.ACTION['open_short']
                      if action == exchanges.SELL
                      else self.ACTION['open_long'])

        if not amount_in_contracts:
            amount = crypto_to_contracts(
                amount,
                getattr(self, '{}_ticker'.format(symbol_pair)).last,
                self.CONTRACT_UNIT_AMOUNTS[symbol_pair])

        match_price = 1 if order_type == 'market' else 0
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
            'price': float(Decimal(price)),
            'match_price': match_price,  # if market, 'price' field is ignored
            'amount': int(amount),  # in contracts
            'type': action,
            'lever_rate': 10,  # default
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params, model_class=OkexOrder)

    def cancel_order(self, order_id):
        is_instance(order_id, (str, ))
        passes_test(order_id, lambda x: int(x))

        # NOTE: OKEX doesn't provide a way of getting all orders from any
        #       symbol pair. We need to loop through all of them until we find it.
        order = None
        for symbol_pair in currencies.SYMBOL_PAIRS:
            orders = self.get_open_orders(symbol_pair=symbol_pair)
            orders = [order for order in orders if int(order.id) == int(order_id)]
            if orders:
                # found order in current symbol pair, no need to keep iterating
                order = orders[0]
                break

        if not order:
            raise ValueError('Could not find order with ID "{}"'.format(order_id))

        path = '/v1/future_cancel.do'
        params = {
            'symbol': order.symbol_pair,
            'contract_type': 'quarter',
            'order_id': int(order_id),
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params)

    def cancel_all_orders(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        orders = self.get_open_orders(symbol_pair=symbol_pair)
        if not orders:
            return

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        order_ids = ','.join([order.id for order in orders])
        path = '/v1/future_cancel.do'
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
            'order_id': order_ids,
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params)

    def get_open_positions(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        path = '/v1/future_position.do'
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params,
                          transformation=self._transform_open_positions,
                          model_class=OkexPosition)

    def close_position(self, position_id, symbol_pair):
        raise NotImplementedError('OKEX API does not support position IDs')

    def close_all_positions(self, symbol_pair):
        is_restricted_to_values(symbol_pair, currencies.SYMBOL_PAIRS)

        positions = self.get_open_positions(symbol_pair=symbol_pair)
        for pos in positions:
            # as we want to close the position,
            # we need to performe the opposite action to the given one.
            action = exchanges.SELL if pos.action == exchanges.BUY else exchanges.BUY
            self.open_order(
                action, pos.amount, pos.symbol_pair, pos.price, exchanges.MARKET,
                amount_in_contracts=True, closing=True)


# OkexClient.btc_usd_ticker = cached_property_with_ttl(ttl=60)(lambda self: self.get_ticker(currencies.BTC_USD))
for symbol_pair in OkexClient.SYMBOLS_MAPPING:
    attr_name = '{}_ticker'.format(symbol_pair)
    fun = lambda self: self.get_ticker(symbol_pair)
    fun.__name__ = attr_name
    setattr(OkexClient, attr_name, cached_property_with_ttl(ttl=60)(fun))
