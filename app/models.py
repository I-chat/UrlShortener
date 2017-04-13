"""SQLalchemy database models."""
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


log_table = db.Table('visits', db.Column('short_url_id', db.Integer,
                                         db.ForeignKey('short_url.id'),
                                         nullable=False),
                     db.Column('log_id', db.Integer, db.ForeignKey(
                                    'activity_logs.id'), nullable=False))


class User(UserMixin, db.Model):
    """Map the User class to the users table in the database."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    short_urls = db.relationship("ShortUrl", back_populates="user")
    long_urls = db.relationship("LongUrl", secondary=relationship_table,
                                back_populates="users")

    @property
    def password(self):
        """Raise error when reading a User password attribute."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Convert passwords to hashed values."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verify passwords with the hashed equivalent."""
        return check_password_hash(self.password_hash, password)

    def save(self):
        """Save a user to database."""
        db.session.add(self)
        db.session.commit()

    def generate_auth_token(self, expiration):
        """Generate a random token with an expiration time."""
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """Verify token."""
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
        """Represent objects with a readable format."""
        return "<User(email='%s')>" % self.email


class ShortUrl(db.Model):
    """Map ShortUrl class to short_url table in the database."""

    __tablename__ = 'short_url'

    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    no_of_visits = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean(), default=False, index=True)
    when = db.Column(db.DateTime, default=db.func.current_timestamp(),
                     nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="short_urls")
    long_url_id = db.Column(db.Integer, db.ForeignKey('long_url.id'),
                            nullable=False)
    long_url = db.relationship("LongUrl", back_populates="short_urls")
    logs = db.relationship('UrlActivityLogs', secondary=log_table,
                           back_populates='short_urls')

    def __repr__(self):
        """Represent objects with a readable format."""
        return "<ShortUrl(short_url='%s')>" % self.short_url


class LongUrl(db.Model):
    """Map the LongUrl class to the long_url table in the database."""

    __tablename__ = 'long_url'
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String, unique=True)
    no_of_visits = db.Column(db.Integer, default=0)
    users = db.relationship("User", secondary=relationship_table,
                            back_populates="long_urls")
    short_urls = db.relationship("ShortUrl", back_populates="long_url")

    def __repr__(self):
        """Represent objects with a readable format."""
        return "<LongUrl(long_url='%s')>" % self.long_url


class UrlActivityLogs(db.Model):
    """Map the class to the activity_logs table in the database."""

    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    country_name = db.Column(db.String(64))
    region_name = db.Column(db.String(64))
    city = db.Column(db.String(64))
    latitude = db.Column(db.Float(6))
    longitude = db.Column(db.Float(6))
    short_urls = db.relationship('ShortUrl', secondary=log_table,
                                 back_populates='logs')
