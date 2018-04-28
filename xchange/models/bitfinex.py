from decimal import Decimal

from xchange.models.base import (Ticker, AccountBalance, OrderBook, Order,
                                 Position)


class BitfinexTicker(Ticker):
    """
    Original JSON response:
    {'ask': '3780.2',
     'bid': '3780.1',
     'low': '3490.0',
     'high': '3808.7',
     'last_price': '3780.2',
     'volume': '41981.56526245',
     'mid': '3780.15',
     'timestamp': '1506170236.287525866'}
    """
    def normalize_response(self, json_response):
        return {
            'ask': json_response['ask'],
            'bid': json_response['bid'],
            'low': json_response['low'],
            'high': json_response['high'],
            'last': json_response['last_price'],
            'volume': json_response['volume'],
        }


class BitfinexAccountBalance(AccountBalance):
    """
    Response items format:
    {
        'amount': '0.0',
        'available': '0.0',
        'currency': 'btc',
        'type': 'deposit'
    },
    """
    def normalize_response(self, json_response):
        return {
            'symbol': json_response['currency'],
            'amount': json_response['available']
        }


class BitfinexOrderBook(OrderBook):
    """
    Original JSON response format:
    {
        "asks": [
            {"price": "4610.6", "amount": "14.96", "timestamp": "1504020265.0"},
            {"price": "4610.7", "amount": "2.27682022", "timestamp": "1504020081.0"},
            {"price": "4611.0", "amount": "5.0", "timestamp": "1504020166.0"},
            ...
        ],
        "bids": [
            {"price": "4610.4", "amount": "1.538", "timestamp": "1504020260.0"},
            {"price": "4610.2", "amount": "0.37226385", "timestamp": "1504020265.0"},
            {"price": "4608.1", "amount": "0.094174", "timestamp": "1504020261.0"},
            ...
        ]
    }
    """

    def normalize_response(self, json_response):
        return {
            'asks': [(Decimal(doc['price']), Decimal(doc['amount']))
                     for doc in json_response['asks']],
            'bids': [(Decimal(doc['price']), Decimal(doc['amount']))
                     for doc in json_response['bids']],
        }


class BitfinexOrder(Order):
    """
    Response items format:
    {'avg_execution_price': '0.0',
      'cid': 81351934272,
      'cid_date': '2017-09-16',
      'exchange': None,
      'executed_amount': '0.0',
      'gid': None,
      'id': 3848275544,
      'is_cancelled': False,
      'is_hidden': False,
      'is_live': True,
      'oco_order': None,
      'original_amount': '1.0',
      'price': '2.0',
      'remaining_amount': '1.0',
      'side': 'buy',
      'src': 'web',
      'symbol': 'btcusd',
      'timestamp': '1505601352.0',
      'type': 'limit',
      'was_forced': False}
    """
    def normalize_response(self, json_response):
        return {
            'id': json_response['id'],
            'action': json_response['side'],
            'amount': json_response['original_amount'],
            'price': json_response['price'],
            'symbol_pair': json_response['symbol'],
            'type': json_response['type'],
            'status': 'open' if json_response['is_live'] else 'closed'
        }


class BitfinexPosition(Position):
    """
    Response items format:
    {'amount': u'-0.01209215',  # (-) sell (+) buy
     'base': u'4118.0',  # real "price" the position was opened
     'id': 36860087,
     'pl': u'-0.10928401484',
     'status': u'ACTIVE',
     'swap': u'0.0',
     'symbol': u'btcusd',
     'timestamp': u'1503264460.0'}]
    """
    def normalize_response(self, json_response):
        if Decimal(json_response['amount']) > 0:
            action = 'buy'
        else:
            action = 'sell'
        return {
            'id': json_response['id'],
            'action': action,
            'amount': abs(Decimal(json_response['amount'])),
            'price': json_response['base'],
            'symbol_pair': json_response['symbol'],
            'profit_loss': json_response['pl'],
        }
