import requests
from requests.adapters import HTTPAdapter
from decimal import Decimal
try:
    from urllib.parse import urlencode
except ImportError:
     from urllib import urlencode
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from .. import exceptions


class BaseExchangeClient:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def _get(self, path, headers=None, params=None,
             transformation=None, model_class=None, **kwargs):
        if params:
            path += '?' + urlencode(params)
        return self._request(
            'GET',
            path=path,
            headers=headers,
            model_class=model_class,
            transformation=transformation, **kwargs
        )

    def _post(self, path, headers=None, params=None, body=None,
              transformation=None, model_class=None, **kwargs):
        if params:
            path += '?' + urlencode(params)
        if body:
            body = urlencode(body)
        return self._request(
            'POST',
            path=path,
            body=body,
            headers=headers,
            model_class=model_class,
            transformation=transformation, **kwargs
        )

    def _request(self, method, path, headers=None, body=None,
                 transformation=None, model_class=None, timeout=3,
                 max_retries=0):
        request = requests.Request(
            method=method,
            url=self.BASE_API_URL + path,
            data=body)
        if headers:
            request.headers.update(headers)

        session = requests.Session()
        if max_retries:
            adapter = HTTPAdapter(max_retries=max_retries)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

        try:
            response = session.send(
                request.prepare(),
                timeout=timeout)
        except requests.exceptions.ConnectTimeout:
            raise exceptions.TimeoutException()

        return self._process_response(
            response, model_class, transformation)

    def _process_response(self, response, model_class=None, transformation=None):
        # check for error-related status codes
        if response.status_code != requests.status_codes.codes.ok:
            raise self.ERROR_CLASS(
                'Got {} response with content: {}'
                ''.format(response.status_code, response.content)
            )

        # if response content is None, avoid data processing
        if not response.content:
            return

        # make sure it's a JSON valid response
        try:
            data = response.json()
        except JSONDecodeError as exc:
            raise self.ERROR_CLASS(
                'Could not decode JSON response, got: {}'.format(exc))

        if isinstance(data, dict):
            # some APIs return 200 status code, but include the error
            # detail as part of the response payload
            if (data.get('error') or
                    data.get('error_code') or
                    ('result' in data and data['result'] == False)):
                raise self.ERROR_CLASS(data)

        # if a transformation function was provided, replace the original
        # JSON response with the result of the transformation function
        if transformation:
            data = transformation(data)

        # when model_class is not provided, return the raw response data
        if not model_class:
            return data

        # create model instances using the response JSON data
        if isinstance(data, list):
            data = list(map(model_class, data))
        else:
            data = model_class(data)
        return data

    def _empty_account_balance(self, symbol):
        return {'symbol': symbol, 'amount': Decimal('0')}

    # public endpoints

    def get_ticker(self, symbol_pair, **kwargs):
        raise NotImplementedError

    def get_order_book(self, symbol_pair, **kwargs):
        raise NotImplementedError

    # authenticated endpoints

    def get_account_balance(self, symbol=None, **kwargs):
        raise NotImplementedError

    def get_open_orders(self, symbol_pair, **kwargs):
        raise NotImplementedError

    def get_open_positions(self, symbol_pair, **kwargs):
        raise NotImplementedError

    def get_order_status(self, order_id, **kwargs):
        raise NotImplementedError

    def open_order(self, action, amount, symbol_pair,
                   price, order_type, **kwargs):
        raise NotImplementedError

    def cancel_order(self, order_id, **kwargs):
        raise NotImplementedError

    def cancel_all_orders(self, symbol_pair, **kwargs):
        raise NotImplementedError

    def close_position(self, position_id, symbol_pair, **kwargs):
        raise NotImplementedError

    def close_all_positions(self, symbol_pair, **kwargs):
        raise NotImplementedError
