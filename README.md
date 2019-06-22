# xchange
![Travis status](https://travis-ci.org/martinzugnoni/xchange.svg?branch=master)
![Coverage](https://codecov.io/gh/martinzugnoni/xchange/branch/master/graphs/badge.svg?branch=master)

Many cryptocurrency exchange APIs, a single and unified API client 🙌

## Installation

The project is hosted in PyPi, and you can install it using `pip` or `pip3`:

```
pip3 install xchange
```

## Example of usage

```python
>>> import os
>>> from xchange.factories import ExchangeClientFactory
>>> from xchange.constants import exchanges, currencies

# construct your API client
>>> ClientClass = ExchangeClientFactory.get_client(exchanges.KRAKEN)
>>> client = ClientClass(**{
...     "api_key": os.environ.get('KRAKEN_KEY'),
...     "api_secret": os.environ.get('KRAKEN_SECRET')
... })

# request API resources in an unified way
>>> ticker = client.get_ticker(currencies.BTC_USD)

>>> ticker
{'ask': Decimal('8590.00000'),
 'bid': Decimal('8589.90000'),
 'low': Decimal('8317.90000'),
 'high': Decimal('8610.00000'),
 'last': Decimal('8590.00000'),
 'volume': Decimal('1856.51064490')}

# API responses are wrapped into normalized models
>>> type(ticker)
<class 'xchange.models.kraken.KrakenTicker'>

# dynamic attribute assignation of response fields
>>> ticker.last
Decimal('8638.10000')
```

## Polymorphic requests

```python
>>> for exchange in exchanges.EXCHANGES:
...     client = ExchangeClientFactory.get_client(exchange)(**{
...         "api_key": "YOUR_KEY",
...         "api_secret": "YOUR_SECRET"
...     })
...     ticker = client.get_ticker(currencies.BTC_USD)
...     print("%s: $%d" % (exchange, ticker.last))
...

bitfinex: $8633
okex: $8749
kraken: $8633
```
