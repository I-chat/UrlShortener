import unittest
from flask import current_app, url_for
from app import create_app, db
from app.api import auth
from app.models import User, ShortUrl, LongUrl
from base64 import b64encode
import json
from flask_sqlalchemy import sqlalchemy


class ApiAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.user = User(first_name='ichiato', last_name='ikikin',
                         email='ichiato@yahoo.com', password='password')

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
                (token).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_verify_password_with_token(self):
        self.user.save()
        email_header = self.api_email_auth_headers('ichiato@yahoo.com',
                                                   'password')
        response = self.client.get(url_for('api.get_token'),
                                   headers=email_header)
        json_response = json.loads(response.data.decode('utf-8'))
        token = json_response['token']
        response2 = auth.verify_password(token, '')
        self.assertTrue(response2)

    def test_anonymous_user_get_token(self):
        header = self.api_email_auth_headers('', '')
        response = self.client.get(url_for('api.get_token'), headers=header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'Authentication required!'
                         ' Anonymous users are not allowed access to this'
                         ' resource.')
        self.assertEqual(response.status_code, 403)

    def test_invalid_user(self):
        self.user.save()
        header = self.api_email_auth_headers('seni2@andela.com', '123456')
        response = self.client.get(url_for('api.get_token'), headers=header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'The authentication credentials sent with the'
                         ' request are invalid or insufficient for the'
                         ' request.')
        self.assertEqual(response.status_code, 401)

    def test_get_token(self):
        self.user.save()
        header = self.api_email_auth_headers('ichiato@yahoo.com', 'password')
        response = self.client.get(url_for('api.get_token'), headers=header)
        json_response = json.loads(response.data.decode('utf-8'))
        token = json_response['token']
        self.assertTrue(token)
        self.assertEqual(response.status_code, 201)
