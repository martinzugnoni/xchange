USD = 'usd'
BTC = 'btc'
BCH = 'bch'
BTG = 'btg'
ETH = 'eth'
ETC = 'etc'
LTC = 'ltc'
IOT = 'iot'
BFX = 'bfx'
XRP = 'xrp'
EOS = 'eos'

SYMBOLS = [
    USD,
    BTC,
    BCH,
    BTG,
    ETH,
    ETC,
    LTC,
    IOT,
    BFX,
    XRP,
    EOS,
]
SYMBOL_VARIANTS = {
    USD: ('zusd', ),
    BTC: ('xxbt', ),
    BCH: ('bcc', 'bcc'),
    BTG: (),
    ETH: (),
    ETC: (),
    LTC: (),
    IOT: (),
    BFX: (),
    XRP: (),
    EOS: (),
}

BTC_USD = '{}_{}'.format(BTC, USD)
ETH_USD = '{}_{}'.format(ETH, USD)
LTC_USD = '{}_{}'.format(LTC, USD)

SYMBOL_PAIRS = [
    BTC_USD,
    ETH_USD,
    LTC_USD
]
SYMBOL_PAIR_VARIANTS = {
    BTC_USD: ('btcusd', 'xbtusd', 'xxbtzusd', 'btc0929', 'btc1229', ),
    ETH_USD: ('ethusd', 'eth0511', 'eth0518', 'eth0629'),
    LTC_USD: ('ltcusd', 'ltc0511', 'ltc0518', 'ltc0629'),
}
