from . import login_manager
from app import db
from flask import current_app
from flask_login import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import generate_password_hash, check_password_hash

relationship_table = db.Table('relationship',
                              db.Column('user_id', db.Integer,
                                        db.ForeignKey('users.id'),
                                        nullable=False),
                              db.Column('long_url_id', db.Integer,
                                        db.ForeignKey('long_url.id'),
                                        nullable=False))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    short_urls = db.relationship("ShortUrl", back_populates="user")
    long_urls = db.relationship("LongUrl", secondary=relationship_table,
                                back_populates="users")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return "<User(username='%s')>" % self.email


class ShortUrl(db.Model):
    __tablename__ = 'short_url'

    short_url = db.Column(db.String, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="short_urls")
    long_url_id = db.Column(db.Integer, db.ForeignKey('long_url.id'),
                            nullable=False)
    long_url = db.relationship("LongUrl", back_populates="short_urls")

    def __repr__(self):
        return "<ShortUrl(short_url='%s')>" % self.short_url


class LongUrl(db.Model):
    __tablename__ = 'long_url'
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String, unique=True)
    users = db.relationship("User", secondary=relationship_table,
                            back_populates="long_urls")
    short_urls = db.relationship("ShortUrl", back_populates="long_url")

    def __repr__(self):
        return "<LongUrl(long_url='%s')>" % self.long_url
