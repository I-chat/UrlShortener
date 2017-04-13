import random
import string

from ..models import ShortUrl, LongUrl
from app import db


class UrlShortener(object):

    @staticmethod
    def save_url(short_url, long_url, user):
        long_url_exist = LongUrl.query.filter_by(long_url=long_url).first()

        if long_url_exist:
            shorturl = ShortUrl(short_url=short_url,
                                long_url_id=long_url_exist.id)
            user.short_urls.append(shorturl)
            long_url_exist.users.append(user)
            db.session.commit()
            return shorturl
        else:
            long_url = LongUrl(long_url=long_url)
            db.session.add(long_url)
            db.session.commit()
            shorturl = ShortUrl(short_url=short_url, long_url_id=long_url.id)
            user.short_urls.append(shorturl)
            long_url.users.append(user)
            db.session.commit()
            return shorturl

    @staticmethod
    def change_long_url(long_url, short_url):
        if not LongUrl.query.filter_by(long_url=long_url).first():
            long_url = LongUrl(long_url=long_url)
            db.session.add(long_url)
            db.session.commit()
            short_url.long_url = long_url
        else:
            long_url_id = LongUrl.query.filter_by(long_url=long_url).first().id
            short_url.long_url_id = long_url_id
        short_url.when = db.func.current_timestamp()
        short_url.no_of_visits = 0
        db.session.commit()
        return True

    @staticmethod
    def generate_short_url(length=6):
        short_url = ''.join(random.choice(
            string.ascii_letters + string.digits) for _ in range(6))
        while ShortUrl.query.filter_by(short_url=short_url).first():
            short_url = ''.join(random.choice(
                string.ascii_letters + string.digits) for _ in range(6))
        return(short_url)

    @staticmethod
    def findurl(short_url):
        short_url = ShortUrl.query.filter_by(short_url=short_url).first()
        if short_url and not short_url.deleted and short_url.is_active:
            short_url.no_of_visits += 1
            db.session.commit()
        return short_url

    @staticmethod
    def sort_shorturl_by_popularity():
        short_urls = ShortUrl.query.order_by(db.desc(
                        ShortUrl.no_of_visits)).filter_by(deleted=False).all()
        return [{'Times_visted': x.no_of_visits, 'date_added': x.when,
                'short_url': x.short_url} for x in short_urls]

    @staticmethod
    def sort_longurl_by_popularity():
        long_urls = LongUrl.query.order_by(
                                db.desc(LongUrl.no_of_visits)).all()
        return [{'Times_visted': x.no_of_visits,
                'long_url': x.long_url} for x in long_urls]

    @staticmethod
    def sort_long_url_by_date_added():
        long_urls = LongUrl.query.order_by(
                                db.desc(LongUrl.when)).all()
        return [{'Date_added': x.when, 'Times_visted': x.no_of_visits,
                'long_url': x.long_url} for x in long_urls]

    @staticmethod
    def sort_short_url_by_date_added():
        short_urls = ShortUrl.query.order_by(db.desc(ShortUrl.when)).filter_by(
                                             deleted=False).all()
        return [{'Date_added': x.when, 'Times_visted': x.no_of_visits,
                'short_url': x.short_url} for x in short_urls]