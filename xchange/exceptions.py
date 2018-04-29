
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


# exchange exceptions

class BitfinexException(BaseXchangeException):
    pass


class OkexException(Exception):
    pass
