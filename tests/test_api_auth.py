"""Testing all things authentication through the API."""
from base64 import b64encode
import json
import unittest

from flask import url_for

from app import create_app, db
from app.api import auth
from app.models import User


class ApiAuthentication(unittest.TestCase):
    """Test all authentication through the API."""

    def setUp(self):
        """Setup app for testing before each test case."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.user = User(first_name='ichiato', last_name='ikikin',
                         email='ichiato@yahoo.com', password='password')

    def tearDown(self):
        """Delete app and db instances after each test case."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def api_email_auth_headers(self, email, password):
        """Setup an authorization header with email and password."""
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def api_token_auth_headers(self, token):
        """Setup an authorization header with a token."""
        return {
            'Authorization': 'Basic ' + b64encode(
                (token).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_verify_password_with_token(self):
        """Test verify_password function with valid token."""
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
        """Test the possibility of an anonymous user getting a valid token."""
        header = self.api_email_auth_headers('', '')
        response = self.client.get(url_for('api.get_token'), headers=header)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'Permission required! You are not allowed'
                         ' access to this resource.')
        self.assertEqual(response.status_code, 403)

    def test_invalid_user(self):
        """Test the possibility of getting a token with invalid credentials."""
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
        """Test the possibility of getting a token with valid credentials."""
        self.user.save()
        header = self.api_email_auth_headers('ichiato@yahoo.com', 'password')
        response = self.client.get(url_for('api.get_token'), headers=header)
        json_response = json.loads(response.data.decode('utf-8'))
        token = json_response['token']
        self.assertTrue(token)
        self.assertEqual(response.status_code, 201)
