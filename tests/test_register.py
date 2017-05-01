"""Testing all things registration through the API."""
import json
import unittest
from app import create_app, db
from app.models import User
from flask import url_for


class ApiRegistration(unittest.TestCase):
    """Test user registration through the API."""

    def setUp(self):
        """Setup app for testing before each test case."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        """Delete app and db instances after each test case."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def content_type_header(self):
        """Setup and Content-Type header."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def test_basic_register(self):
        """Test a basic registration process."""
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": "123456",
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        email = json_response["email"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(msg, "Registration Successful.")
        self.assertEqual(email, "ichat@yahoo.com")

    def test_different_password_confirm_password(self):
        """Test that password and confirm_password must always be equal."""
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": "123456",
                "confirm_password": "12356",
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        self.assertEqual(response.status_code, 400)
        self.assertEqual(msg, "The request is invalid or inconsistent."
                         " password and confirm_password do not match.")

    def test_register_twice(self):
        """Test registration of a user with same email twice."""
        # save a user first like he already registered
        user = User(first_name='ichiato', last_name='ikikin',
                    email='ichat@yahoo.com', password='password')
        user.save()
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": "123456",
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        self.assertEqual(response.status_code, 400)
        self.assertEqual(msg, "The request is invalid or inconsistent."
                         " User already registered.Try login.")

    def test_register_with_missing_key(self):
        """Test Registration of users with one or more missing keys."""
        post_data = json.dumps({
                "firstname": "ichiato",
                "email": "ichat@yahoo.com",
                "password": "123456",
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        self.assertEqual(msg, "The request is invalid or inconsistent."
                         " required key not provided")
        self.assertEqual(response.status_code, 400)

    def test_register_with_bad_email(self):
        """Test registration with invalid email pattern."""
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichatyahoo.com",
                "password": "123456",
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        self.assertEqual(msg, "The request is invalid or inconsistent."
                         " Not a valid email format.")
        self.assertEqual(response.status_code, 400)

    def test_register_with_int_password(self):
        """Test registration with passwords as integers."""
        post_data = json.dumps({
                "firstname": "ichiato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": "123456",
                "confirm_password": 123456,
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        self.assertEqual(msg, "The request is invalid or inconsistent. Invalid"
                         " password format. Passwords can only be strings.")
        self.assertEqual(response.status_code, 400)

    def test_register_with_int_name(self):
        """Test registration with name as Integer."""
        post_data = json.dumps({
                "firstname": "ich34ato",
                "lastname": "ikikin",
                "email": "ichat@yahoo.com",
                "password": "123456",
                "confirm_password": "123456",
        })
        header = self.content_type_header()
        response = self.client.post(url_for("api.new_user"), headers=header,
                                    data=post_data)
        json_response = json.loads(response.data.decode("utf-8"))
        msg = json_response["message"]
        self.assertEqual(response.status_code, 400)
        self.assertEqual(msg, "The request is invalid or inconsistent. Invalid"
                         " name format. Name should include only one or more"
                         " alphabets.")
