import json
import requests
from urllib.parse import urlencode


class BaseExchangeClient:

    def _get(self, path, headers=None, params=None,
             transformation=None, model_class=None):
        if params:
            path += '?' + urlencode(params)
        return self._request(
            'GET',
            path=path,
            headers=headers,
            model_class=model_class,
            transformation=transformation
        )

    def _post(self, path, headers=None, params=None, body=None,
              transformation=None, model_class=None):
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
            transformation=transformation
        )

    def _request(self, method, path, headers=None, body=None,
                 transformation=None, model_class=None):
        request = requests.Request(
            method=method,
            url=self.BASE_API_URL + path,
            data=body)
        if headers:
            request.headers.update(headers)
        session = requests.Session()
        response = session.send(request.prepare())
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

    # public endpoints

    def get_ticker(self, symbol_pair):
        raise NotImplementedError

    def get_order_book(self, symbol_pair):
        raise NotImplementedError

    # authenticated endpoints

    def get_account_balance(self):
        raise NotImplementedError

    def get_open_orders(self):
        raise NotImplementedError

    def get_open_positions(self):
        raise NotImplementedError

    def get_order_status(self, order_id):
        raise NotImplementedError

    def open_order(self, action, amount, symbol_pair, price, order_type):
        raise NotImplementedError

    def cancel_order(self, order_id):
        raise NotImplementedError

    def cancel_all_orders(self):
        raise NotImplementedError

    def close_position(self, action, amount, symbol_pair, price, order_type):
        raise NotImplementedError

    def close_all_positions(self):
        raise NotImplementedError
