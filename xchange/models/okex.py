from decimal import Decimal

from xchange.models.base import (Ticker, AccountBalance, OrderBook, Order,
                                 Position, contracts_to_crypto)


class OkexTicker(Ticker):
    """
    Original JSON response (transformed):
    {'date': '1506170137',
     'ticker': {
        'buy': 3740.31,
        'coin_vol': 0,
        'contract_id': 20171229012,
        'day_high': 0,
        'day_low': 0,
        'high': 3785.06,
        'last': 3740.31,
        'low': 3453.04,
        'sell': 3742.24,
        'unit_amount': 100,
        'vol': 3181196}}
    """
    def normalize_response(self, json_response):
        return {
            'ask': json_response['ticker']['sell'],
            'bid': json_response['ticker']['buy'],
            'low': json_response['ticker']['low'],
            'high': json_response['ticker']['high'],
            'last': json_response['ticker']['last'],
            'volume': json_response['ticker']['vol'],
        }


class OkexOrderBook(OrderBook):
    """
    Original JSON response format:
    {
        "asks": [
            # [price_in_btc, amount_in_contracts]
            [411.8, 6],
            [411.75, 11],
            [411.6, 22],
            [411.5, 9],
            [411.3, 16]
        ],
        "bids": [
            [410.65, 12],
            [410.64, 3],
            [410.19, 15],
            [410.18, 40],
            [410.09, 10]
        ]
    }
    """
    TICKER = None
    SYMBOL = None
    CONTRACT_UNIT_AMOUNTS = None

    def normalize_response(self, json_response):
        if all([self.TICKER, self.SYMBOL, self.CONTRACT_UNIT_AMOUNTS]):
            # if class atributes are provided, all contract amounts
            # are transformed to BTC amounts based on the ticker last price.
            last_price = self.TICKER.last
            unit_amount = self.CONTRACT_UNIT_AMOUNTS[self.SYMBOL]
            return {
                'asks': [(Decimal(str(doc[0])),
                          contracts_to_crypto(Decimal(str(doc[1])), last_price, unit_amount))
                         for doc in json_response['asks']],
                'bids': [(Decimal(str(doc[0])),
                          contracts_to_crypto(Decimal(str(doc[1])), last_price, unit_amount))
                         for doc in json_response['bids']],
            }
        else:
            return {
                'asks': [(Decimal(str(doc[0])), Decimal(str(doc[1])))
                         for doc in json_response['asks']],
                'bids': [(Decimal(str(doc[0])), Decimal(str(doc[1])))
                         for doc in json_response['bids']],
            }


class OkexAccountBalance(AccountBalance):
    """
    Response items format:
    {
        'amount': 0.162,
        'currency': 'btc',
    }
    """
    def normalize_response(self, json_response):
        return {
            'symbol': json_response['currency'],
            'amount': json_response['amount']
        }


class OkexOrder(Order):
    ORDER_STATUS = {
        -1: 'closed',  # cancelled
        0: 'open',  # unfilled
        1: 'open',  # partially_filled
        2: 'closed',  # fully_filled
        4: 'open',  # cancel_requested
    }
    ORDER_TYPE = {
        1: 'buy',  # open_long
        2: 'sell',  # open_short
        3: 'buy',  # close_long
        4: 'sell',  # close_short
    }
    """
    Response items format (transformed):
    {'amount': 1,
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
     'unit_amount': 100}
    """
    def normalize_response(self, json_response):
        order = {
            'id': json_response['order_id']
        }
        keys = ['type', 'amount', 'price', 'symbol', 'status']
        if all([k in json_response for k in keys]):
            order.update({
            'action': self.ORDER_TYPE[json_response['type']],
            'amount': json_response['amount'],
            'price': json_response['price'],
            'symbol_pair': json_response['symbol'],
            'type': 'limit',
            'status': self.ORDER_STATUS[json_response['status']]
        })
        return order


class OkexPosition(Position):
    """
    Response items format (transformed):
    [{'action': 'buy',
      'amount': 1,
      'id': None,
      'price': 4269.38,
      'profit_loss': -7.03e-06,
      'symbol_pair': 'btc_usd'},
     {'action': 'sell',
      'amount': 1,
      'id': None,
      'price': 4266.363325,
      'profit_loss': -5.432e-05,
      'symbol_pair': 'btc_usd'}]
    """
    def normalize_response(self, json_response):
        return {
            'id': json_response['id'],
            'action': json_response['action'],
            'amount': json_response['amount'],
            'price': json_response['price'],
            'symbol_pair': json_response['symbol_pair'],
            'profit_loss': json_response['profit_loss'],
        }
