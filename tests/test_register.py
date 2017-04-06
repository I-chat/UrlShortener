import json
import unittest
from app import create_app, db
from app.models import User
from flask import current_app, url_for
from flask_sqlalchemy import sqlalchemy


class ApiAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def content_type_header(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_basic_register(self):
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": '123456',
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for('api.new_user'), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        email = json_response['email']
        self.assertEqual(response.status_code, 201)
        self.assertEqual(msg, "Registration Successful.")
        self.assertEqual(email, "ichat@yahoo.com")

    def test_different_password_confirm_password(self):
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": '123456',
                "confirm_password": "12356",
        })
        header = self.content_type_header()
        response = self.client.post(url_for('api.new_user'), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(msg, 'The request is invalid or inconsistent.'
                         ' password and confirm_password do not match.')

    def test_register_twice(self):
        # save a user first like he already registered
        user = User(first_name='ichiato', last_name='ikikin',
                    email='ichat@yahoo.com', password='password')
        user.save()
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": '123456',
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for('api.new_user'), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(msg, 'The request is invalid or inconsistent.'
                         ' User already registered.Try login')

    def test_register_with_missing_key(self):
        post_data = json.dumps({
                "firstname": "ichiato",
                "email": "ichat@yahoo.com",
                "password": '123456',
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for('api.new_user'), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode('utf-8'))
        msg = json_response['message']
        self.assertEqual(msg, 'The request is invalid or inconsistent.'
                         ' Incomplete number of reqired keys provided.')
        self.assertEqual(response.status_code, 400)
