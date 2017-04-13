import validators
import dotenv
from app import db
from . import api
from flask import request, abort, jsonify, g, redirect, url_for
from ..models import User, LongUrl, ShortUrl
from .auth import auth
from werkzeug.exceptions import BadRequest
from voluptuous import MultipleInvalid
from .urlshortener import UrlShortener
from .validators import valid_url


dotenv.load()
SITE_URL = dotenv.get('SITE_URL')


@api.route('/shorten', methods=['POST'])
@auth.login_required
def shorten_url():
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)

    try:
        valid_url(request.json)
    except MultipleInvalid:
        abort(400, "Incomplete or too many required keys provided.")
    except BadRequest:
        abort(400, "The request does not contain a body.")

    long_url = request.json.get('url')

    if request.json.get('vanity_string') and not g.current_user.is_anonymous:
        vanity_string = request.json.get('vanity_string')
        short_url = generate_and_save_urls(long_url, g.current_user,
                                           vanity_string)
        return jsonify({'id': short_url.id,
                        'short_url': SITE_URL + short_url.short_url}), 201

    if g.current_user.is_anonymous:
        user = User.query.filter_by(email='AnonymousUser').first()
        if not user:
            user = User(first_name='AnonymousUser', last_name='AnonymousUser',
                        email='AnonymousUser')
            user.save()
    else:
        user = g.current_user

    short_url = generate_and_save_urls(long_url, user)
    return jsonify({'id': short_url.id,
                    'short_url': SITE_URL + short_url.short_url}), 201


def generate_and_save_urls(url, user, vanity_string=None):

    if url in [x.long_url for x in user.long_urls]:
        long_url = LongUrl.query.filter_by(long_url=url).first()
        return [short_url for short_url in
                user.short_urls if short_url.long_url_id == long_url.id][0]

    elif vanity_string:
        short_url = ShortUrl.query.filter_by(short_url=vanity_string).first()
        if short_url:
            abort(400, "Vanity string already in use. Pick another.")
        save_data = UrlShortener.save_url(vanity_string, url, user)
        return save_data
    else:
        short_url = UrlShortener.generate_short_url()
        save_data = UrlShortener.save_url(short_url, url, user)
        return save_data


@api.route('/<shorturl>')
@auth.login_required
def get_url(shorturl):
    """  Given a short url, the code looks up the short url in database
         and if found redirects to the long url path.
         if not found sends a 404 page not found.
    """
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)
    short_url = UrlShortener.findurl(shorturl)
    if short_url and short_url.deleted:
        abort(404, "URL deleted.")
    elif short_url and not short_url.is_active:
        abort(400, "URL is inactive.")
    elif short_url and short_url.is_active:
        return redirect(short_url.long_url.long_url, code=302)
    else:
        abort(404)


@api.route('/<int:id>/toogle_longurl/', methods=['PUT'])
@auth.login_required
def change_long_url(id):
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)

    try:
        valid_url(request.json)
    except MultipleInvalid:
        abort(400, "Incomplete or too many required keys provided.")
    except BadRequest:
        abort(400, "The request does not contain a body.")

    try:
        short_url = [short_url for short_url in g.current_user.short_urls
                     if short_url.id == id and not short_url.deleted][0]
    except IndexError:
        abort(404)

    long_url = request.json.get('url')
    UrlShortener.change_long_url(long_url, short_url)
    return jsonify({'message': "Tagert url change was successful."}), 200


@api.route('/<int:id>/toogle_active/', methods=['PUT'])
@auth.login_required
def toogle_is_active(id):
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)
    try:
        short_url = [short_url for short_url in g.current_user.short_urls
                     if short_url.id == id][0]
    except IndexError:
        abort(404)
    if short_url.is_active:
        short_url.is_active = False
        output = "Deactivation Successful."
    else:
        short_url.is_active = True
        output = "Activation Successful."
    db.session.commit()
    return jsonify({'message': output}), 200


@api.route('/<string:url_type>/<string:sort_type>')
@auth.login_required
def sort_urls(url_type, sort_type):
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)
    if sort_type == 'popularity' and url_type == 'shorturl':
        shorturl_list = UrlShortener.sort_shorturl_by_popularity()
        return jsonify({'url_list': shorturl_list}), 200
    elif sort_type == 'popularity' and url_type == 'longurl':
        longurl_list = UrlShortener.sort_longurl_by_popularity()
        return jsonify({'url_list': longurl_list}), 200
    elif sort_type == 'date' and url_type == 'shorturl':
        shorturl_list = UrlShortener.sort_short_url_by_date_added()
        return jsonify({'url_list': shorturl_list}), 200
    else:
        abort(400, "Invalid endpoint.")


@api.route('/<int:id>/delete', methods=['DELETE'])
@auth.login_required
def delete_urls(id):
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)
    try:
        short_url = [short_url for short_url in g.current_user.short_urls
                     if short_url.id == id][0]
    except IndexError:
        abort(404)
    if short_url.deleted:
        abort(404)
    short_url.deleted = True
    db.session.commit()
    return jsonify({'message': 'Deleted'})
