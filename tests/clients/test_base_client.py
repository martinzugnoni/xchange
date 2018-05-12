import re
from decimal import Decimal

import responses

from tests import BaseXchangeTestCase
from xchange.clients.base import BaseExchangeClient
from xchange.exceptions import BaseXchangeException


class BaseClientTestCase(BaseXchangeTestCase):
    def setUp(self):
        super(BaseClientTestCase, self).setUp()
        self.client = BaseExchangeClient('API_KEY', 'API_SECRET')
        self.client.BASE_API_URL = 'https://xchage-testing.url'
        self.client.ERROR_CLASS = BaseXchangeException

    def test_init_arguments(self):
        self.assertEqual(self.client.api_key, 'API_KEY')
        self.assertEqual(self.client.api_secret, 'API_SECRET')

    def test_client_interface(self):
        methods = [
            # internal
            '_get',
            '_post',
            '_request',

            # non-authenticated
            'get_ticker',
            'get_order_book',

            # authenticated
            'get_account_balance',
            'get_open_orders',
            'get_open_positions',
            'get_order_status',
            'open_order',
            'cancel_order',
            'cancel_all_orders',
            'close_position',
            'close_all_positions',
        ]
        for method in methods:
            self.assertTrue(getattr(self.client, method) is not None)

    def test_client_interface_not_implement(self):
        methods = [
            ('get_ticker', ('symbol_pair', )),
            ('get_order_book', ('symbol_pair', )),
            ('get_account_balance', ()),
            ('get_open_orders', ('symbol_pair', )),
            ('get_open_positions', ('symbol_pair', )),
            ('get_order_status', ('order_id', )),
            ('open_order', ('action', 'amount', 'symbol_pair', 'price', 'order_type')),
            ('cancel_order', ('order_id', )),
            ('cancel_all_orders', ('symbol_pair', )),
            ('close_position', ('position_id', 'symbol_pair', )),
            ('close_all_positions', ('symbol_pair', )),
        ]
        for method, args in methods:
            with self.assertRaises(NotImplementedError):
                getattr(self.client, method)(**{arg_name: None for arg_name in args})

    @responses.activate
    def test_get_request_raw_data(self):
        """Should return response data as plain JSON when no model_class is provided"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._get(path='/test-get-method', model_class=None)
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_get_server_error(self):
        """Should raise client ERROR_CLASS when status code is 500"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            json={'success': False, 'msg': 'Something went wrong.'},
            status=500,
            content_type='application/json')
        with self.assertRaisesRegexp(BaseXchangeException, 'Got 500 response with content:'):
            self.client._get(path='/test-get-method', model_class=None)

    @responses.activate
    def test_get_bad_request(self):
        """Should raise client ERROR_CLASS when status code is 400"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            json={'success': False, 'msg': 'Invalid request params.'},
            status=400,
            content_type='application/json')
        with self.assertRaisesRegexp(BaseXchangeException, 'Got 400 response with content:'):
            self.client._get(path='/test-get-method', model_class=None)

    @responses.activate
    def test_get_empty_response_content(self):
        """Should return None when the response content is empty"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            body='',
            status=200,
            content_type='text/html')
        data = self.client._get(path='/test-get-method', model_class=None)
        self.assertEqual(data, None)

    @responses.activate
    def test_get_invalid_json_response_content(self):
        """Should raise client ERROR_CLASS when response JSON is badly formatted"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            body='{"not-valid-json"}',
            status=200,
            content_type='application/json')
        with self.assertRaisesRegexp(BaseXchangeException, 'Could not decode JSON response'):
            self.client._get(path='/test-get-method', model_class=None)

    @responses.activate
    def test_get_valid_response_code_with_error_message(self):
        """Should raise client ERROR_CLASS when status_code is 200 but response content includes error message"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            json={'error': 'Something went wrong.'},
            status=200,
            content_type='application/json')
        with self.assertRaisesRegexp(BaseXchangeException, 'Something went wrong'):
            self.client._get(path='/test-get-method', model_class=None)

    @responses.activate
    def test_get_apply_transformation_function(self):
        """Should apply transformation function to the response content if it's provided"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            json={'number': 100},
            status=200,
            content_type='application/json')
        transformation = lambda x: {'number': x['number']* 2}
        data = self.client._get(path='/test-get-method',
                                model_class=None, transformation=transformation)
        self.assertEqual(data, {'number': 200})

    @responses.activate
    def test_get_headers(self):
        """Should pass headers to the request when they are provided"""
        responses.add(
            method='GET',
            url='{}/test-get-method'.format(self.client.BASE_API_URL),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._get(
            path='/test-get-method',
            model_class=None,
            headers={'X-CUSTOM-HEADER': 'xchange'}
        )
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_get_custom_params(self):
        """Should add params to the URL when they are provided"""
        responses.add(
            method='GET',
            url=re.compile('{}/test-get-method\?custom_param=1'
                           ''.format(self.client.BASE_API_URL.replace('.', '\.'))),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json',
            match_querystring=True)
        data = self.client._get(
            path='/test-get-method',
            model_class=None,
            params={'custom_param': 1}
        )
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_post_request(self):
        """Should return response as plain JSON when POSTing with no model_class"""
        responses.add(
            method='POST',
            url='{}/test-post-method'.format(self.client.BASE_API_URL),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._post(
            path='/test-post-method',
            model_class=None)
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_post_headers(self):
        """Should pass headers to the POST request when provided"""
        responses.add(
            method='POST',
            url='{}/test-post-method'.format(self.client.BASE_API_URL),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._post(
            path='/test-post-method',
            model_class=None,
            headers={'X-CUSTOM-HEADER': 'xchange'}
        )
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_post_custom_params(self):
        """Should pass params to the POST request when provided"""
        responses.add(
            method='POST',
            url=re.compile('{}/test-post-method\?custom_param=1'
                           ''.format(self.client.BASE_API_URL.replace('.', '\.'))),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._post(
            path='/test-post-method',
            model_class=None,
            params={'custom_param': 1}
        )
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_post_body(self):
        """Should pass body to the POST request if provided"""
        responses.add(
            method='POST',
            url='{}/test-post-method'.format(self.client.BASE_API_URL),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._post(
            path='/test-post-method',
            model_class=None,
            body={'send-this': 'as-body'}
        )
        self.assertEqual(data, {'msg': 'All good.', 'success': True})

    @responses.activate
    def test_post_all_params_together(self):
        """Should pass all valid params to the POST request when they are provided"""
        responses.add(
            method='POST',
            url='{}/test-post-method'.format(self.client.BASE_API_URL),
            json={'success': True, 'msg': 'All good.'},
            status=200,
            content_type='application/json')
        data = self.client._post(
            path='/test-post-method',
            model_class=None,
            params={'custom_param': 1},
            body={'send-this': 'as-body'},
            headers={'X-CUSTOM-HEADER': 'xchange'}
        )
        self.assertEqual(data, {'msg': 'All good.', 'success': True})
