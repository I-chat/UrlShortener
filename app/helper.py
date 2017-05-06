"""Url shortener helper to help implement various functionalities.

Helps keep the code base DRY.
"""
import random
import string

from flask import abort
from .models import ShortUrl, LongUrl
from app import db


class UrlSaver(object):
    """Handles the various functionalities implemented."""

    @staticmethod
    def generate_and_save_urls(url, user, vanity_string=None):
        """Help manage the generating and saving of urls."""
        if url in [x.url for x in user.long_urls]:
            long_url = LongUrl.query.filter_by(url=url).first()
            return [short_url for short_url in
                    user.short_urls if short_url.long_url_id == long_url.id][0]

        elif vanity_string:
            short_url = ShortUrl.query.filter_by(url=vanity_string).first()
            if short_url:
                abort(400, "Vanity string already in use. Pick another.")
            save_data = UrlSaver.save_url(vanity_string, url, user)
            return save_data
        else:
            short_url = UrlSaver.generate_short_url()
            save_data = UrlSaver.save_url(short_url, url, user)
            return save_data

    @staticmethod
    def save_url(short_url, url, user):
        """Save and append short and long urls to their various tables."""
        long_url = LongUrl.query.filter_by(url=url).first()

        if not long_url:
            long_url = LongUrl(url=url)
            db.session.add(long_url)
            db.session.commit()
        shorturl = ShortUrl(url=short_url, long_url_id=long_url.id)
        user.short_urls.append(shorturl)
        long_url.users.append(user)
        db.session.commit()
        return shorturl

    @staticmethod
    def generate_short_url(length=6):
        """Generate a unique short_url."""
        short_url = ''.join(random.choice(
            string.ascii_letters + string.digits) for _ in range(6))
        while ShortUrl.query.filter_by(url=short_url).first():
            short_url = ''.join(random.choice(
                string.ascii_letters + string.digits) for _ in range(6))
        return(short_url)
