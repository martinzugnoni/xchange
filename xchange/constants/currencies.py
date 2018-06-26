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
    BCH: ('bcc', ),
    BTG: (),
    ETH: ('xeth', ),
    ETC: (),
    LTC: ('xltc', ),
    IOT: (),
    BFX: (),
    XRP: (),
    EOS: (),
}

BTC_USD = '{}_{}'.format(BTC, USD)
ETH_USD = '{}_{}'.format(ETH, USD)
ETC_USD = '{}_{}'.format(ETC, USD)
LTC_USD = '{}_{}'.format(LTC, USD)
BCH_USD = '{}_{}'.format(BCH, USD)
XRP_USD = '{}_{}'.format(XRP, USD)
EOS_USD = '{}_{}'.format(EOS, USD)
BTG_USD = '{}_{}'.format(BTG, USD)

SYMBOL_PAIRS = [
    BTC_USD,
    ETH_USD,
    ETC_USD,
    LTC_USD,
    BCH_USD,
    XRP_USD,
    EOS_USD,
    BTG_USD,
]
SYMBOL_PAIR_VARIANTS = {
    BTC_USD: ('btcusd', 'xbtusd', 'xxbtzusd', 'btc0929', 'btc1229', ),
    ETH_USD: ('ethusd', 'eth0511', 'eth0518', 'eth0629', 'xethzusd', ),
    LTC_USD: ('ltcusd', 'ltc0511', 'ltc0518', 'ltc0629'),
    BCH_USD: ('bchusd', 'bccusd'),
    XRP_USD: ('xrpusd', ),
    EOS_USD: ('eosusd', ),
    BTG_USD: ('btgusd', ),
    ETC_USD: ('etcusd', ),
}
