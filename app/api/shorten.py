"""URL shortening module.

The module is for all endpoints that manages all services related
to url shortening.
"""

import dotenv
from flask import request, abort, jsonify, g, redirect
from werkzeug.exceptions import BadRequest
from . import api
from app import db
from ..models import LongUrl, ShortUrl
from .auth import auth
from ..helper import UrlSaver
from .validators import valid_url
from voluptuous import MultipleInvalid


dotenv.load()
site_url = dotenv.get('SITE_URL')


@api.route('/shorten', methods=['POST'])
@auth.login_required
def shorten_url():
    """An endpoint which shortens a long url.

    It makes use of a vanity string if supplied by a registered user.
    """
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
        short_url = UrlSaver.generate_and_save_urls(long_url, g.current_user,
                                                    vanity_string)
        return jsonify({'id': short_url.id,
                        'short_url': site_url + short_url.short_url}), 201

    user = g.current_user

    short_url = UrlSaver.generate_and_save_urls(long_url, user)
    return jsonify({'id': short_url.id,
                    'short_url': site_url + short_url.short_url}), 201


@api.route('/<shorturl>')
@auth.login_required
def get_url(shorturl):
    """Redirect short_urls to their long_url version.

    Given a short url, the code looks up the short url in database
    and if found redirects to the long url path. if not found sends a 404
    status_code.
    """
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)
    short_url = ShortUrl.findurl(shorturl)
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
    """Update target url of a given short_url."""
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
    short_url.change_long_url(long_url)
    return jsonify({'message': "Tagert url change was successful."}), 200


@api.route('/<int:id>/toogle_active/', methods=['PUT'])
@auth.login_required
def toogle_is_active(id):
    """Deactivate or activate a users short_url."""
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
    """Return short_urls based popularity and recently added."""
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)
    if sort_type == 'popularity' and url_type == 'shorturl':
        shorturl_list = ShortUrl.sort_shorturl_by_popularity()
        return jsonify({'url_list': shorturl_list}), 200
    elif sort_type == 'popularity' and url_type == 'longurl':
        longurl_list = LongUrl.sort_longurl_by_popularity()
        return jsonify({'url_list': longurl_list}), 200
    elif sort_type == 'date' and url_type == 'shorturl':
        shorturl_list = ShortUrl.sort_short_url_by_date_added()
        return jsonify({'url_list': shorturl_list}), 200
    else:
        abort(400, "Invalid endpoint.")


@api.route('/<int:id>/delete', methods=['DELETE'])
@auth.login_required
def delete_urls(id):
    """Set short_url delete column to True."""
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
