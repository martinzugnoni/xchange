
class BaseXchangeException(Exception):
    pass


class InvalidSymbolException(BaseXchangeException):
    pass


class InvalidSymbolPairException(BaseXchangeException):
    pass


class InvalidActionException(BaseXchangeException):
    pass


class InvalidAmountException(BaseXchangeException):
    pass


class InvalidPriceException(BaseXchangeException):
    pass


class InvalidOrderTypeException(BaseXchangeException):
    pass


class InvalidAmountContractsException(BaseXchangeException):
    pass


class InsufficientMarketDepth(BaseXchangeException):
    pass


class TimeoutException(BaseXchangeException):
    pass


# exchange exceptions
class BitfinexException(BaseXchangeException):
    pass


class OkexException(BaseXchangeException):
    pass


class KrakenException(BaseXchangeException):
    pass
