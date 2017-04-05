import unittest
from app import create_app, db
from app.models import User, ShortUrl, LongUrl
from datetime import datetime
from flask import current_app
from flask_sqlalchemy import sqlalchemy
from time import sleep


class AppModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(first_name='seni', last_name='abdulahi',
                         email='seni@andela.com', password='123456')
        self.user2 = User(first_name='seni', last_name='abdulahi',
                          email='seni2@andel.com', password='123456')
        self.short_url = ShortUrl(short_url="nfdjf")
        self.short_url2 = ShortUrl(short_url="hjf97")
        self.long_url = LongUrl(long_url=""
                                "https://docs.python.org/3/contents.html")
        self.long_url2 = LongUrl(long_url="https://repl.it/languages/python3")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        self.assertIsNotNone(self.user.password_hash)

    def test_no_password_getter(self):
        with self.assertRaises(AttributeError):
            self.user.password

    def test_password_verification(self):
        self.assertTrue(self.user.verify_password('123456'))
        self.assertFalse(self.user.verify_password('password'))

    def test_password_salts_are_random(self):
        self.assertTrue(self.user.password_hash != self.user2.password_hash)

    def test_saving_null_to_users_table(self):
        user = User(password="123456")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(user)
            db.session.commit()

    def test_token_generation(self):
        self.assertIsInstance(self.user.generate_auth_token(34), bytes)

    def test_token_verification(self):
        db.session.add(self.user, self.user2)
        db.session.commit()
        user_token = self.user.generate_auth_token(1)
        self.assertNotEqual(self.user.verify_auth_token(user_token),
                            self.user2)
        self.assertEqual(self.user.verify_auth_token(user_token), self.user)
        sleep(2)
        self.assertIsNone(self.user.verify_auth_token(user_token))
        self.assertIsNone(self.
                          user.verify_auth_token('jdjdje230920093944334j'))

    def test_shorturl_time_saving(self):
        self.long_url.short_urls.append(self.short_url)
        self.user.short_urls.append(self.short_url)
        self.long_url.users.append(self.user)
        db.session.add(self.short_url)
        db.session.commit()
        self.assertIs(type(self.short_url.when), datetime)

    def test_saving_user_to_db(self):
        self.user.save()
        db_user = User.query.filter_by(email='seni@andela.com').first()
        self.assertIs(self.user, db_user)
        self.assertIsInstance(db_user, User)

    def test_shorturl_not_saving_without_longurl(self):
        db.session.add(self.short_url)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    def test_shorturl_is_active_defualts(self):
        self.long_url.short_urls.append(self.short_url)
        self.user.short_urls.append(self.short_url)
        self.long_url.users.append(self.user)
        db.session.add(self.short_url)
        db.session.commit()
        self.assertTrue(self.short_url.is_active)
        self.short_url.is_active = False
        self.assertFalse(self.short_url.is_active)

    def test_shorturl_longurl_relationship(self):
        self.long_url.short_urls.append(self.short_url)
        self.long_url.short_urls.append(self.short_url2)
        self.user.short_urls.append(self.short_url)
        self.user.short_urls.append(self.short_url2)
        self.long_url.users.append(self.user)
        self.long_url2.short_urls.append(self.short_url)
        self.long_url2.users.append(self.user)
        db.session.add_all([self.user, self.short_url, self.short_url2,
                            self.long_url, self.long_url2])
        db.session.commit()
        self.assertEqual(self.short_url.long_url_id, self.long_url2.id)
        self.assertNotEqual(self.short_url.long_url_id, self.long_url.id)
        self.assertEqual(self.short_url2.long_url_id, self.long_url.id)

    def test_shorturl_user_relationship(self):
        self.user.short_urls.append(self.short_url)
        self.user2.short_urls.append(self.short_url)
        self.user.short_urls.append(self.short_url2)
        self.long_url.short_urls.append(self.short_url)
        self.long_url.short_urls.append(self.short_url2)
        db.session.add_all([self.user, self.user2, self.short_url,
                            self.short_url2])
        db.session.commit()
        self.assertEqual(self.short_url.user_id, self.user2.id)
        self.assertNotEqual(self.short_url.user_id, self.user.id)
        self.assertEqual(self.short_url2.user_id, self.user.id)

    def test_longurl_user_relationship(self):
        self.long_url.users.append(self.user)
        self.long_url.users.append(self.user2)
        self.user.long_urls.append(self.long_url2)
        db.session.add_all([self.long_url, self.long_url2, self.user,
                            self.user2])
        self.assertEqual(self.long_url.users, [self.user, self.user2])
        self.assertEqual(self.user.long_urls, [self.long_url, self.long_url2])
