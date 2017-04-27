"""URL shortening module.

The module is for all endpoints that manages all services related
to url shortening.
"""

import dotenv
from flask import request, abort, jsonify, g, redirect
from werkzeug.exceptions import BadRequest
from . import api
from app import db
from ..models import LongUrl, ShortUrl, User
from .auth import auth
from ..helper import UrlSaver
from .validators import valid_url
from voluptuous import MultipleInvalid


dotenv.load()
site_url = dotenv.get('SITE_URL')


def check_authentication_with_token():
    """Check that a user is authenticated and used token for authentication."""
    if g.current_user.is_anonymous or not g.token_used:
        abort(403)


@api.route('/shorten', methods=['POST'], strict_slashes=False)
@auth.login_required
def shorten_url():
    """An endpoint which shortens a long url.

    It makes use of a vanity string if supplied by a registered user.
    """
    check_authentication_with_token()

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


@api.route('/<shorturl>', strict_slashes=False)
def get_url(shorturl):
    """Redirect short_urls to their long_url version.

    Given a short url, the code looks up the short url in database
    and if found redirects to the long url path. if not found sends a 404
    status_code.
    """
    short_url = ShortUrl.findurl(shorturl, request)
    if short_url and short_url.deleted:
        abort(404, "This URL has been deleted.")
    elif short_url and not short_url.is_active:
        abort(400, "URL is inactive.")
    elif short_url and short_url.is_active:
        return redirect(short_url.long_url.long_url, code=302)
    else:
        abort(404)


@api.route('/short_url/<int:id>/change_longurl', methods=['PUT'],
           strict_slashes=False)
@auth.login_required
def change_long_url(id):
    """Update target url of a given short_url."""
    check_authentication_with_token()

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
        abort(404, "You do not have any such URL.")

    long_url = request.json.get('url')
    result = short_url.change_long_url(long_url, g.current_user)
    if result is True:
        return jsonify({'message': "Target url successfully changed to %s."
                        % long_url}), 200
    short_url = site_url + result.short_url
    return jsonify({'message': "You have previously shortened this URL"
                    " to %s." % short_url}), 400


@api.route('/user/short_urls', strict_slashes=False)
@auth.login_required
def get_user_short_urls():
    """Return a list of a users service shortened URLs."""
    check_authentication_with_token()

    short_url = [short_url for short_url in g.current_user.short_urls]
    if not short_url:
        abort(404, "You are yet to shorten any URL.")
    return jsonify({'short_url list':
                    [{'Date_added': x.when, 'Times_visted': x.no_of_visits,
                      'Active status': x.is_active,
                      'short_url': site_url + x.short_url}
                        for x in short_url]}), 200


@api.route('/shorturl/<int:id>/logs', strict_slashes=False)
@auth.login_required
def get_short_url_visit_log(id):
    """Get log details of visits to a particular short_url."""
    check_authentication_with_token()

    try:
        logs = [short_url for short_url in g.current_user.short_urls
                if short_url.id == id][0].logs
    except IndexError:
        abort(404, "You do not have any such URL.")
    if logs:
        return jsonify({'short_url logs':
                        [{'I.P Address': x.ip, 'User agent': x.browser,
                          'System platform': x.platform} for x in logs]}), 200
    else:
        return jsonify({'message': 'This URL has never been visited or unable'
                        ' to record any details.'}), 404


@api.route('/shorturl/<int:id>', strict_slashes=False)
@auth.login_required
def get_short_url(id):
    """Get the details of a short_url."""
    check_authentication_with_token()

    try:
        short_url = [short_url for short_url in g.current_user.short_urls
                     if short_url.id == id][0]
    except IndexError:
        abort(404, "You do not have any such URL.")

    return jsonify({'short_url': site_url + short_url.short_url,
                    'Times_visted': short_url.no_of_visits,
                    'long_url': short_url.long_url.long_url,
                    'Date added': short_url.when,
                    'Active status': short_url.is_active}), 200


@api.route('/short_url/<int:id>/deactivate', methods=['PUT'],
           strict_slashes=False)
@api.route('/short_url/<int:id>/activate', methods=['PUT'],
           strict_slashes=False)
@auth.login_required
def toogle_is_active(id):
    """Deactivate or activate a users short_url."""
    check_authentication_with_token()

    try:
        short_url = [short_url for short_url in g.current_user.short_urls
                     if short_url.id == id][0]
    except IndexError:
        abort(404, "You do not have any such URL.")

    if short_url.is_active and request.url.endswith('deactivate'):
        short_url.is_active = False
        output = "Deactivation Successful."
    elif not short_url.is_active and request.url.endswith('activate') and not\
            request.url.endswith('deactivate'):
        short_url.is_active = True
        output = "Activation Successful."
    else:
        abort(400, "You are trying to either activate a URL that is already"
              " activated or deactivate a URL that is already deactivated.")

    db.session.commit()
    return jsonify({'message': output}), 200


@api.route('/users/influential', strict_slashes=False)
@auth.login_required
def get_influential_users():
    """Get a list of influential users and the number of URLs shortened."""
    check_authentication_with_token()
    users = User.query.all()
    sorted_users = sorted(users, key=lambda user: len(user.short_urls),
                          reverse=True)
    return jsonify({'users_list': [{'Name': x.first_name + " " + x.last_name,
                                    'No of URLs shortened': len(list(
                                     x.short_urls))} for x in sorted_users]})


@api.route('/user', strict_slashes=False)
@auth.login_required
def get_user_details():
    """Get a details of the current user."""
    check_authentication_with_token()

    return jsonify({'firstname': g.current_user.first_name,
                    'lastname': g.current_user.last_name,
                    'email': g.current_user.email,
                    'no of URL shortened': len(list(
                                g.current_user.short_urls))}), 200


@api.route('/<string:url_type>/<string:sort_type>', strict_slashes=False)
@auth.login_required
def sort_urls(url_type, sort_type):
    """Return short_urls based popularity and recently added."""
    check_authentication_with_token()

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


@api.route('/short_url/<int:id>/delete', methods=['DELETE'],
           strict_slashes=False)
@auth.login_required
def delete_urls(id):
    """Set short_url delete column to True."""
    check_authentication_with_token()

    try:
        short_url = [short_url for short_url in g.current_user.short_urls
                     if short_url.id == id][0]
    except IndexError:
        abort(404, "You do not have any such URL.")
    if short_url.deleted:
        abort(404, "This URL has been deleted.")
    short_url.deleted = True
    db.session.commit()
    return jsonify({'message': 'Deletion successful.'})
