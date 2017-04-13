"""Test the development app object and the testing app object."""
import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    """Test the basic app object."""

    def setUp(self):
        """Setup app for testing before each test case."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Delete app and db instances after each test case."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """Test that a current app exist."""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """Test that the current app is the testing environment."""
        self.assertTrue(current_app.config['TESTING'])
