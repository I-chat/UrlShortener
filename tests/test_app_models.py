import unittest
from flask import current_app
from app import create_app, db
from app.models import User, ShortUrl, LongUrl


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='password')
        self.assertIsNotNone(u.password_hash, msg=None)

    def test_no_password_getter(self):
        u = User(password='password')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='password')
        self.assertTrue(u.verify_password('password'))
        self.assertFalse(u.verify_password('123456'))

    def test_password_salts_are_random(self):
        u = User(password='password')
        u2 = User(password='password')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_saving_null_to_users_table(self):
        u = User(password="123456")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(u)
            db.session.commit()
