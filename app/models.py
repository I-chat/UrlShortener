"""SQLalchemy database models."""
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import generate_password_hash, check_password_hash

from . import login_manager
from app import db

relationship_table = db.Table('relationship',
                              db.Column('user_id', db.Integer,
                                        db.ForeignKey('users.id'),
                                        nullable=False),
                              db.Column('long_url_id', db.Integer,
                                        db.ForeignKey('long_url.id'),
                                        nullable=False))


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

    @login_manager.user_loader
    def load_user(user_id):
        """Return a user object if available or None otherwise."""
        return User.query.get(int(user_id))

    def __repr__(self):
        """Represent objects with a readable format."""
        return "<User(email='%s')>" % self.email


class AnonymousUser(AnonymousUserMixin):
    """Create an User with AnonymousUserMixin properties."""

    @staticmethod
    def create_anonymous_user():
        """Create anonymous user."""
        anonymous_user = User(first_name='AnonymousUser',
                              last_name='AnonymousUser', email='AnonymousUser')
        anonymous_user.save()
        return anonymous_user


class ShortUrl(db.Model):
    """Map ShortUrl class to short_url table in the database."""

    __tablename__ = 'short_url'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    no_of_visits = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean(), default=False, index=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp(),
                             nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="short_urls")
    long_url_id = db.Column(db.Integer, db.ForeignKey('long_url.id'),
                            nullable=False)
    long_url = db.relationship("LongUrl", back_populates="short_urls")
    logs = db.relationship("UrlActivityLogs", back_populates="short_url")

    def change_long_url(self, long_url, user):
        """Change the target url of a short_url and commit to database."""
        new_long_url = LongUrl.query.filter_by(url=long_url).first()
        old_long_url = self.long_url
        if new_long_url in user.long_urls:
            short_url = [short_url for short_url in user.short_urls if
                         short_url.long_url_id == new_long_url.id][0]
            return short_url
        elif not new_long_url:
            new_long_url = LongUrl(url=long_url)
            db.session.add(new_long_url)
            db.session.commit()
            old_long_url.users.remove(user)
            self.long_url = new_long_url
            new_long_url.users.append(user)
        if not old_long_url.users:
            db.session.delete(old_long_url)
        self.long_url = new_long_url
        new_long_url.users.append(user)
        self.no_of_visits = 0
        db.session.commit()
        return True

    @staticmethod
    def sort_short_url_by_date_added():
        """Sort the short_urls based on how recently they were added.

        Sorts the list of short_urls queried from the ShortUrl
        table based on how recently they were added.
        """
        short_urls = ShortUrl.query.order_by(
            db.desc(ShortUrl.date_created)).filter_by(deleted=False).all()
        return [{'Date_added': x.date_created, 'Times_visted': x.no_of_visits,
                'short_url': x.url} for x in short_urls]

    @staticmethod
    def sort_shorturl_by_popularity():
        """Sort the short_urls based on popularity.

        Sorts the list of short_urls queried from the ShortUrl
        table based on the number of visits.
        """
        short_urls = ShortUrl.query.order_by(db.desc(
                        ShortUrl.no_of_visits)).filter_by(deleted=False).all()
        return [{'Times_visted': x.no_of_visits, 'date_added': x.date_created,
                'short_url': x.url} for x in short_urls]

    @staticmethod
    def find_url(short_url, request):
        """Query the database for a given short_url.

        It also counts the number of times it finds the short_url that is
        active and not deleted.
        """
        short_url = ShortUrl.query.filter_by(url=short_url,
                                             deleted=False).first()
        if short_url and short_url.is_active:
            short_url.no_of_visits += 1
            short_url.long_url.no_of_visits += 1
            ip = request.remote_addr
            if request.user_agent:
                browser = request.user_agent.browser
                platform = request.user_agent.platform
            else:
                platform = None
                browser = request.headers['User-Agent']
            log = UrlActivityLogs(ip=ip, browser=browser, platform=platform,
                                  short_url_id=short_url.id)
            db.session.add(log)
            db.session.commit()
        return short_url

    def __repr__(self):
        """Represent objects with a readable format."""
        return "<ShortUrl(short_url='%s')>" % self.url


class LongUrl(db.Model):
    """Map the LongUrl class to the long_url table in the database."""

    __tablename__ = 'long_url'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True)
    no_of_visits = db.Column(db.Integer, default=0)
    users = db.relationship("User", secondary=relationship_table,
                            back_populates="long_urls")
    short_urls = db.relationship("ShortUrl", back_populates="long_url")

    @staticmethod
    def sort_longurl_by_popularity():
        """Sort the long_urls based on popularity.

        Sorts the list of long_urls queried from the LongtUrl
        table based on the number of visits.
        """
        long_urls = LongUrl.query.order_by(
                                db.desc(LongUrl.no_of_visits)).all()
        return [{'Times_visted': x.no_of_visits,
                'long_url': x.url} for x in long_urls]

    @staticmethod
    def sort_long_url_by_date_added():
        """Sort the long_urls based on how recently they were added.

        Sorts the list of long_urls queried from the LongUrl
        table based on how recently they were added.
        """
        long_urls = LongUrl.query.order_by(
                                db.desc(LongUrl.date_created)).all()
        return [{'Date_added': x.date_created, 'Times_visted': x.no_of_visits,
                'long_url': x.long_url} for x in long_urls]

    def __repr__(self):
        """Represent objects with a readable format."""
        return "<LongUrl(long_url='%s')>" % self.url


class UrlActivityLogs(db.Model):
    """Map the class to the activity_logs table in the database."""

    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    platform = db.Column(db.String())
    browser = db.Column(db.String)
    country_name = db.Column(db.String(64))
    region_name = db.Column(db.String(64))
    city = db.Column(db.String(64))
    latitude = db.Column(db.Float(6))
    longitude = db.Column(db.Float(6))
    short_url_id = db.Column(db.Integer, db.ForeignKey('short_url.id'),
                             nullable=False)
    short_url = db.relationship("ShortUrl", back_populates="logs")
