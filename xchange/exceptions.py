
class BaseXchangeException(Exception):
    pass


class InvalidSymbolException(BaseXchangeException):
    pass


class InvalidSymbolPairException(BaseXchangeException):
    pass

# exchange exceptions

class BitfinexException(BaseXchangeException):
    pass


class OkexException(Exception):
    pass
