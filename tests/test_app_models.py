import unittest
from flask import current_app
from app import create_app, db
from app.models import User, ShortUrl, LongUrl


class AppModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.u = User(first_name='seni', last_name='abdulahi',
                      username='ichat', email='seni@andel.com',
                      password='123456')
        self.u2 = User(first_name='seni', last_name='abdulahi',
                       username='ichat', email='seni2@andel.com',
                       password='123456')
        self.s = ShortUrl(short_url="nfdjf")
        self.s2 = ShortUrl(short_url="hjf97")
        self.long_url = LongUrl(long_url=""
                                "https://docs.python.org/3/contents.html")
        self.long_url2 = LongUrl(long_url="https://repl.it/languages/python3")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        self.assertIsNotNone(self.u.password_hash)

    def test_no_password_getter(self):
        with self.assertRaises(AttributeError):
            self.u.password

    def test_password_verification(self):
        self.assertTrue(self.u.verify_password('123456'))
        self.assertFalse(self.u.verify_password('password'))

    def test_password_salts_are_random(self):
        self.assertTrue(self.u.password_hash != self.u2.password_hash)

    def test_saving_null_to_users_table(self):
        u = User(password="123456")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.add(u)
            db.session.commit()

    def test_token_generation(self):
        self.assertIsInstance(self.u.generate_auth_token(34), bytes)

    def test_token_verification(self):
        db.session.add(self.u, self.u2)
        db.session.commit()
        u_token = self.u.generate_auth_token(1)
        self.assertNotEqual(self.u.verify_auth_token(u_token), self.u2)
        self.assertEqual(self.u.verify_auth_token(u_token), self.u)
        sleep(2)
        self.assertIsNone(self.u.verify_auth_token(u_token))
        self.assertIsNone(self.u.verify_auth_token('jdjdje230920093944334j'))

    def test_saving_user_to_db(self):
        self.u.save()
        db_u = User.query.filter_by(email='seni@andel.com').first()
        self.assertIs(self.u, db_u)
        self.assertIsInstance(db_u, User)

    def test_shorturl_not_saving_without_longurl(self):
        db.session.add(self.s)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    def test_shorturl_is_active_defualts(self):
        self.long_url.short_urls.append(self.s)
        self.u.short_urls.append(self.s)
        self.long_url.users.append(self.u)
        db.session.add(self.s)
        db.session.commit()
        self.assertTrue(self.s.is_active)
        self.s.is_active = False
        self.assertFalse(self.s.is_active)

    def test_shorturl_longurl_relationship(self):
        self.long_url.short_urls.append(self.s)
        self.long_url.short_urls.append(self.s2)
        self.u.short_urls.append(self.s)
        self.u.short_urls.append(self.s2)
        self.long_url.users.append(self.u)
        self.long_url2.short_urls.append(self.s)
        self.long_url2.users.append(self.u)
        db.session.add_all([self.u, self.s, self.s2, self.long_url,
                            self.long_url2])
        db.session.commit()
        self.assertEqual(self.s.long_url_id, self.long_url2.id)
        self.assertNotEqual(self.s.long_url_id, self.long_url.id)
        self.assertEqual(self.s2.long_url_id, self.long_url.id)
