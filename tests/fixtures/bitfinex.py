FIXTURE_RESPONSES = [
    {
        'method': 'GET',
        'url_regex': 'https://api.bitfinex.com/v1/pubticker/\w+',
        'status': 200,
        'content_type': 'application/json',
        'json': {
            'mid': '9398.15',
            'bid': '9398.1',
            'ask': '9398.2',
            'last_price': '9398.1',
            'low': '8750.0',
            'high': '9500.0',
            'volume': '44197.286828289994',
            'timestamp': '1524948715.1223445'
        }
    },
    {
        'method': 'GET',
        'url_regex': 'https://api.bitfinex.com/v1/book/\w+',
        'status': 200,
        'content_type': 'application/json',
        'json': {
            'asks': [
                {'amount': '0.31', 'price': '9327.3', 'timestamp': '1524950439.0'},
                {'amount': '0.09694343', 'price': '9327.4', 'timestamp': '1524950439.0'},
                {'amount': '0.08', 'price': '9328.7', 'timestamp': '1524950439.0'},
                {'amount': '7.50897281', 'price': '9329', 'timestamp': '1524950439.0'}
            ],
            'bids': [
                {'amount': '0.15', 'price': '9327.1', 'timestamp': '1524950439.0'},
                {'amount': '0.10915328', 'price': '9326.9', 'timestamp': '1524950439.0'},
                {'amount': '0.34', 'price': '9326.8', 'timestamp': '1524950439.0'},
                {'amount': '0.57462657', 'price': '9326.2', 'timestamp': '1524950439.0'},
                {'amount': '0.01975221', 'price': '9326.1', 'timestamp': '1524950439.0'}
            ]
        }
    },
    {
        'method': 'POST',
        'url_regex': 'https://api.bitfinex.com/v1/balances',
        'status': 200,
        'content_type': 'application/json',
        'json': [
            {'amount': '0.0', 'available': '0.0', 'currency': 'btc', 'type': 'deposit'},
            {'amount': '0.0', 'available': '0.0', 'currency': 'btc', 'type': 'exchange'},
            {'amount': '0.0', 'available': '0.0', 'currency': 'usd', 'type': 'exchange'},
            {'amount': '0.0', 'available': '0.0', 'currency': 'bfx', 'type': 'trading'},
            {'amount': '0.01209215', 'available': '0.01209215', 'currency': 'btc', 'type': 'trading'},
            {'amount': '0.00009361', 'available': '0.00009361', 'currency': 'usd', 'type': 'trading'}
        ]
    },
]
