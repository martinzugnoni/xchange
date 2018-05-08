from decimal import Decimal

from xchange.models.base import (
    Ticker, AccountBalance, OrderBook, Order, Position)


class KrakenTicker(Ticker):
    """
    Original JSON response (transformed):
    {'a': ['3809.00000', '1', '1.000'],
     'b': ['3803.60000', '1', '1.000'],
     'c': ['3809.30000', '0.08000000'],
     'h': ['3830.30000', '3830.30000'],
     'l': ['3570.10000', '3525.10000'],
     'o': '3606.80000',
     'p': ['3717.00933', '3650.22371'],
     't': [6565, 14224],
     'v': ['2204.84583619', '4523.49526430']}
    """
    def normalize_response(self, json_response):
        return {
            'ask': json_response['a'][0],
            'bid': json_response['b'][0],
            'low': json_response['l'][0],
            'high': json_response['h'][0],
            'last': json_response['c'][0],
            'volume': json_response['v'][0],
        }


class KrakenOrderBook(OrderBook):
    """
    Original JSON response format:
    {
        "error": [],
        "result": {
            "XXBTZUSD": {
                "asks": [
                    ["4626.12300", "0.014", 1504020172],
                    ["4628.80800", "0.100", 1504020185],
                    ["4638.00000", "2.939", 1504020185],
                    ...
                ],
                "bids": [
                    ["4626.00600", "0.003", 1504020190],
                    ["4626.00000", "1.410", 1504020191],
                    ["4613.57900", "3.659", 1504020156],
                    ...
                ]
            }
        }
    }
    """

    def normalize_response(self, json_response):
        symbol = list(json_response['result'].keys())[0]
        return {
            'asks': [(Decimal(str(l[0])), Decimal(str(l[1])))
                     for l in json_response['result'][symbol]['asks']],
            'bids': [(Decimal(str(l[0])), Decimal(str(l[1])))
                     for l in json_response['result'][symbol]['bids']],
        }


class KrakenAccountBalance(AccountBalance):
    """
    Response items format:
    {
        'amount': '0.0',
        'currency': 'ZUSD',
    }
    """
    def normalize_response(self, json_response):
        return {
            'symbol': json_response['currency'],
            'amount': json_response['amount']
        }


class KrakenOrder(Order):
    """
    Response items format (transformed):
    {'id': 'OGYUJ3-LSWJV-4OD4DU',
     'status': 'open',
     'cost': '0.00000',
     'descr': {
       'leverage': 'none',
       'order': 'sell 0.00500000 XBTUSD @ limit 5000.0',
       'ordertype': 'limit',
       'pair': 'XBTUSD',
       'price': '5000.0',
       'price2': '0',
       'type': 'sell'},
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
     'vol_exec': '0.00000000'}
    """
    def normalize_response(self, json_response):
        order = {
            'id': json_response['id']
        }
        keys = ['descr', 'vol', 'status']
        if all([k in json_response for k in keys]):
            order.update({
                'action': json_response['descr']['type'],
                'amount': json_response['vol'],
                'price': json_response['descr']['price'],
                'symbol_pair': json_response['descr']['pair'],
                'type': json_response['descr']['ordertype'],
                'status': json_response['status']
            })
        return order


class KrakenPosition(Position):
    """
    Response items format:
    {'cost': '62.82690',
     'fee': '0.16963',
     'id': 'T3Y3IJ-YAMOG-YJAOJN',
     'margin': '31.41345',
     'misc': '',
     'net': '-0.0153',
     'oflags': '',
     'ordertxid': 'OHUWBX-E54D5-J5VMWY',
     'ordertype': 'market',
     'pair': 'XXBTZUSD',
     'posstatus': 'open',
     'rollovertm': '1506307875',
     'terms': '0.0100% per 4 hours',
     'time': 1506293475.2531,
     'type': 'buy',
     'value': '62.8',
     'vol': '0.01700000',
     'vol_closed': '0.00000000'}
    """
    def normalize_response(self, json_response):
        return {
            'id': json_response['id'],
            'action': json_response['type'],
            'amount': json_response['vol'],
            'price': Decimal(str(json_response['cost'])) / Decimal(str(json_response['vol'])),
            'symbol_pair': json_response['pair'],
            'profit_loss': json_response['net'],
        }
