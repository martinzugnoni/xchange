FIXTURE_RESPONSES = [
    {
        'method': 'GET',
        'url_regex': 'https://www\.okex\.com/api/v1/future_ticker\.do\?symbol=\w+&contract_type=\w+',
        'status': 200,
        'content_type': 'application/json',
        'json': {
            'date': '1524951607',
            'ticker': {
                'buy': 100.51,
                'coin_vol': 0,
                'contract_id': 201806290000034,
                'day_high': 0,
                'day_low': 0,
                'high': 9480,
                'last': 9312.34,
                'low': 8800,
                'sell': 9314.66,
                'unit_amount': 100,
                'vol': 16185076.0
            }
        }
    },
    {
        'method': 'GET',
        'url_regex': 'https://www\.okex\.com/api/v1/future_depth\.do\?size=\d+&symbol=\w+&contract_type=\w+',
        'status': 200,
        'content_type': 'application/json',
        'json': {
            'asks': [
                [9315.49, 5],
                [9315.47, 77],
                [9315.45, 49],
                [9315.06, 10],
                [9314.78, 10]],
            'bids': [
                [9314.58, 115],
                [9313.3, 82],
                [9313.04, 93],
                [9311.73, 50],
                [9311.42, 64],
                [9310.96, 9],
            ]
        }
    },
    {
        'method': 'POST',
        'url_regex': 'https://www\.okex\.com/api/v1/future_userinfo\.do\?\w+',
        'status': 200,
        'content_type': 'application/json',
        'json': {
            'info': {
                'btc': {
                    'account_rights': 0.01645887,
                    'keep_deposit': 0,
                    'profit_real': 0.00052895,
                    'profit_unreal': 0,
                    'risk_rate': 10000
                },
                'ltc': {
                    'account_rights': 0,
                    'keep_deposit': 0,
                    'profit_real': 0,
                    'profit_unreal': 0,
                    'risk_rate': 10000
                }
            },
            'result': True
        }
    },
]
