from . import api
from .auth import auth
from flask import request, render_template, jsonify


@api.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@api.app_errorhandler(400)
def bad_request(e):
    response = jsonify({
        'error': '400 Bad Request',
        'message': "The request is invalid or inconsistent. {e}"
        .format(e=e.description)})
    response.status_code = 400
    return response


@api.errorhandler(403)
def bad_request(e):
    response = jsonify({
        'error': '403 Forbidden',
        'message': "Authentication required! "
                   "Anonymous users are not allowed access to this resource."
        })
    response.status_code = 403
    return response


@auth.error_handler
def unauthorized():
    response = jsonify({
        'error': '401 Unauthenticated',
        'message': 'The authentication credentials sent with the request are '
                   'invalid or insufficient for the request.'
        })
    response.status_code = 401
    return response
