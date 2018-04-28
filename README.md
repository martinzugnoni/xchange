# xchange
Many cryptocurrency exchange APIs, a single and unified API client 🙌

```
>>> from xchange import ExchangeClientFactory

>>> BitfinexClient = ExchangeClientFactory.get_client(exchanges.BITFINEX)
>>> client = BitfinexClient(api_key, api_secret)

>>> client.get_ticker(currencies.BTC)
{
  'ask': Decimal,
  'bid': Decimal,
  'low': Decimal,
  'high': Decimal,
  'last': Decimal,
  'volume': Decimal,
}
```
