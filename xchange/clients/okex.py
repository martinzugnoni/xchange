import logging
import hashlib
from decimal import Decimal

from cached_property import cached_property_with_ttl

from xchange.clients.base import BaseExchangeClient
from xchange.models.base import crypto_to_contracts
from xchange.models.okex import (
    OkexTicker, OkexOrderBook, OkexAccountBalance, OkexOrder, OkexPosition)
from xchange import exceptions
from xchange.constants import currencies
from xchange import decorators


class OkexClient(BaseExchangeClient):
    BASE_API_URL = 'https://www.okex.com/api'
    ERROR_CLASS = exceptions.OkexException
    SYMBOLS_MAPPING = {
        currencies.BTC_USD: 'btc_usd',
        currencies.ETH_USD: 'eth_usd',
        currencies.LTC_USD: 'ltc_usd',
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
        'ltc_usd': 10,
    }

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_params(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'
        data = sign + 'secret_key=' + self.api_secret
        return hashlib.md5(data.encode("utf8")).hexdigest().upper()

    # FIXME: Try to find a better way of caching ticker responses
    #        without duplicating properties for each symbol_pair
    @cached_property_with_ttl(ttl=60)  # cache invalidates after 1 minute
    def btc_usd_ticker(self):
        return self.get_ticker(currencies.BTC_USD)

    @cached_property_with_ttl(ttl=60)
    def eth_usd_ticker(self):
        return self.get_ticker(currencies.ETH_USD)

    @cached_property_with_ttl(ttl=60)
    def ltc_usd_ticker(self):
        return self.get_ticker(currencies.LTC_USD)

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

    @decorators.is_valid_argument('symbol_pair')
    def get_ticker(self, symbol_pair):
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        return self._get('/v1/future_ticker.do?symbol={}&contract_type=quarter'
                         ''.format(symbol_pair), model_class=OkexTicker)

    @decorators.is_valid_argument('symbol_pair')
    def get_order_book(self, symbol_pair):
        symbol_pair = self.SYMBOLS_MAPPING[symbol_pair]
        OkexOrderBook.TICKER = getattr(self, '{}_ticker'.format(symbol_pair))
        OkexOrderBook.SYMBOL = symbol_pair
        OkexOrderBook.CONTRACT_UNIT_AMOUNTS = self.CONTRACT_UNIT_AMOUNTS
        return self._get('/v1/future_depth.do?size=100&symbol={}&contract_type=quarter'
                         ''.format(symbol_pair), model_class=OkexOrderBook)

    # authenticated endpoints

    def get_account_balance(self):
        path = '/v1/future_userinfo.do'
        params = {}
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params,
                          transformation=self._transform_account_balance,
                          model_class=OkexAccountBalance)

    def get_open_orders(self, symbol_pair):
        path = '/v1/future_order_info.do'
        symbol_pair = self.SYMBOLS[symbol_pair]
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
        return self._post(path, params=params,
                          transformation=self._transform_open_orders,
                          model_class=OkexOrder)

    def open_order(self, action, amount, symbol_pair, price, order_type,
                   amount_in_contracts=None):
        path = '/v1/future_trade.do'
        symbol_pair = self.SYMBOLS[symbol_pair]
        action = (self.ACTION['open_short']
                  if action == 'sell'
                  else self.ACTION['open_long'])

        amount_in_contracts = (
            amount_in_contracts or
            crypto_to_contracts(amount,
                                getattr(self, '{}_ticker'.format(symbol_pair)).last,
                                self.CONTRACT_UNIT_AMOUNTS[symbol_pair]))
        # FIXME: this should not happen with greater amounts
        if amount_in_contracts < 1:
            amount_in_contracts = Decimal('1.0')

        match_price = 1 if order_type == 'market' else 0
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
            'price': float(Decimal(price)),
            'match_price': match_price,  # if market, 'price' field is ignored
            'amount': int(amount_in_contracts),
            'type': action,
            'lever_rate': 10,  # default
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params)

    def cancel_order(self, order_id):
        # FIXME: don't hardcode btc_usd here
        path = '/v1/future_cancel.do'
        params = {
            'symbol': 'btc_usd',
            'contract_type': 'quarter',
            'order_id': int(order_id),
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params)

    def cancel_all_orders(self, symbol_pair):
        symbol_pair = self.SYMBOLS[symbol_pair]
        orders = yield Task(self.get_open_orders, symbol_pair=symbol_pair)
        if not orders:
            return
        order_ids = ','.join([order.id for order in orders])
        log.info('{}'.format(order_ids))
        path = '/v1/future_cancel.do'
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
            'order_id': order_ids,
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        yield self._post(path, params=params)

    def cancel_all_orders_sync(self, symbol_pair):
        symbol_pair = self.SYMBOLS[symbol_pair]
        orders = self.get_open_orders(symbol_pair=symbol_pair)
        if not orders:
            return
        order_ids = ','.join([order.id for order in orders])
        log.info('{}'.format(order_ids))
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
        symbol_pair = self.SYMBOLS[symbol_pair]
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

    def close_position(self, action, amount, symbol_pair, price, order_type,
                       amount_in_contracts=None):
        path = '/v1/future_trade.do'
        symbol_pair = self.SYMBOLS[symbol_pair]
        action = (self.ACTION['close_short']
                  if action == 'sell'
                  else self.ACTION['close_long'])

        amount_in_contracts = (
            amount_in_contracts or
            crypto_to_contracts(amount,
                                getattr(self, '{}_ticker'.format(symbol_pair)).last,
                                self.CONTRACT_UNIT_AMOUNTS[symbol_pair]))

        match_price = 1 if order_type == 'market' else 0
        params = {
            'symbol': symbol_pair,
            'contract_type': 'quarter',
            'price': float(Decimal(price)),
            'match_price': match_price,  # if market, 'price' field is ignored
            'amount': int(amount_in_contracts),
            'type': action,
            'lever_rate': 10,  # default
        }
        params['api_key'] = self.api_key
        params['sign'] = self._sign_params(params)
        return self._post(path, params=params)

    def close_all_positions(self, symbol_pair):
        positions = yield Task(self.get_open_positions, symbol_pair=symbol_pair)
        if not positions:
            return
        for position in positions:
            self.close_position(
                action=position.action,
                amount=None,
                amount_in_contracts=str(position.amount),
                symbol_pair=position.symbol_pair,
                price=str(position.price),
                order_type='market'
            )

    def close_all_positions_sync(self, symbol_pair):
        positions = self.get_open_positions(symbol_pair=symbol_pair)
        if not positions:
            return
        for position in positions:
            self.close_position(
                action=position.action,
                amount=None,
                amount_in_contracts=str(position.amount),
                symbol_pair=position.symbol_pair,
                price=str(position.price),
                order_type='market'
            )
