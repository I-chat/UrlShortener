import unittest
from flask import current_app, url_for
from app import create_app, db
from app.models import User
from base64 import b64encode
import json


class ApiShorten(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.user = User(first_name='ichiato', last_name='ikikin',
                         email='ichiato@yahoo.com', password='password')
        self.post_data = json.dumps({
            "url": "http://www.andela.com",
            })
        self.post_data2 = json.dumps({})
        self.post_data3 = json.dumps({
            "url": "http://www.andela.com",
            "vanity_string": "python"
            })

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def api_email_auth_headers(self, email, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def api_token_auth_headers(self, token):
        return {
            'Authorization': 'Basic ' + b64encode(
                (token + ':' + '').encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_anonymous_user_shorten_via_api(self):
        response = self.client.post(url_for('api.shorten_url'),
                                    data=self.post_data)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'Permission required! You are not allowed'
                         ' access to this resource.')
        self.assertEqual(403, response.status_code)

    def test_registered_user_shorten_via_api(self):
        self.user.save()
        email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                   'password')
        token_response = self.client.get(url_for('api.get_token'),
                                         headers=email_header)
        json_token_response = json.loads(token_response.data.decode('utf-8'))
        token = json_token_response['token']
        token_header = self.api_token_auth_headers(token)
        shorten_response_with_email_auth = self.client.post(
            url_for('api.shorten_url'), headers=email_header,
            data=self.post_data)
        shorten_response_with_token_auth = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=self.post_data)
        json_shorten_response_with_email = json.loads(
            shorten_response_with_email_auth.data.decode('utf-8'))
        email_msg = json_shorten_response_with_email['message']
        json_shorten_response_with_token = json.loads(
            shorten_response_with_token_auth.data.decode('utf-8'))
        self.assertEqual(email_msg, 'Permission required! You are not allowed'
                         ' access to this resource.')
        self.assertIn('short_url', json_shorten_response_with_token)
        self.assertEqual(403, shorten_response_with_email_auth.status_code)
        self.assertEqual(201, shorten_response_with_token_auth.status_code)

    def test_registered_user_with_no_body(self):
        self.user.save()
        email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                   'password')
        token_response = self.client.get(url_for('api.get_token'),
                                         headers=email_header)
        json_token_response = json.loads(token_response.data.decode('utf-8'))
        token = json_token_response['token']
        token_header = self.api_token_auth_headers(token)
        shorten_response_with_token_auth = self.client.post(
                            url_for('api.shorten_url'), headers=token_header)
        json_shorten_response_with_token = json.loads(
            shorten_response_with_token_auth.data.decode('utf-8'))
        msg = json_shorten_response_with_token['message']
        self.assertEqual(msg, 'The request is invalid or inconsistent.'
                         ' The request does not contain a body.')
        self.assertEqual(400, shorten_response_with_token_auth.status_code)

    def test_registered_user_with_bad_body(self):
        self.user.save()
        email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                   'password')
        token_response = self.client.get(url_for('api.get_token'),
                                         headers=email_header)
        json_token_response = json.loads(token_response.data.decode('utf-8'))
        token = json_token_response['token']
        token_header = self.api_token_auth_headers(token)
        shorten_response_with_token_auth = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=self.post_data2)
        json_shorten_response_with_token = json.loads(
            shorten_response_with_token_auth.data.decode('utf-8'))
        msg = json_shorten_response_with_token['message']
        self.assertEqual(msg, 'The request is invalid or inconsistent.'
                         ' Incomplete or too many required keys provided.')
        self.assertEqual(400, shorten_response_with_token_auth.status_code)

    def test_registered_user_with_vanity_string(self):
        self.user.save()
        email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                   'password')
        token_response = self.client.get(url_for('api.get_token'),
                                         headers=email_header)
        json_token_response = json.loads(token_response.data.decode('utf-8'))
        token = json_token_response['token']
        token_header = self.api_token_auth_headers(token)
        shorten_response_with_token_auth = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=self.post_data3)
        json_shorten_response_with_token = json.loads(
            shorten_response_with_token_auth.data.decode('utf-8'))
        short_url = json_shorten_response_with_token['short_url']
        self.assertIn('python', short_url)
        self.assertIn('short_url', json_shorten_response_with_token)
        self.assertEqual(201, shorten_response_with_token_auth.status_code)

    def test_user_shortening_same_url_twice(self):
        self.user.save()
        email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                   'password')
        token_response = self.client.get(url_for('api.get_token'),
                                         headers=email_header)
        json_token_response = json.loads(token_response.data.decode('utf-8'))
        token = json_token_response['token']
        token_header = self.api_token_auth_headers(token)
        shorten_response_with_token_auth = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=self.post_data)
        shorten_response_with_token_auth2 = self.client.post(
                            url_for('api.shorten_url'), headers=token_header,
                            data=self.post_data)
        json_shorten_response_with_token = json.loads(
            shorten_response_with_token_auth.data.decode('utf-8'))
        json_shorten_response_with_token2 = json.loads(
            shorten_response_with_token_auth2.data.decode('utf-8'))
        short_url = json_shorten_response_with_token['short_url']
        short_url2 = json_shorten_response_with_token2['short_url']
        self.assertEqual(short_url, short_url2)
        self.assertEqual(201, shorten_response_with_token_auth.status_code)
        self.assertEqual(201, shorten_response_with_token_auth2.status_code)
