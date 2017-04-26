"""Customize http errors to return specific messages."""
from . import api
from .auth import auth
from flask import request, render_template, jsonify


@api.app_errorhandler(404)
def page_not_found(e):
    """Customize the defualt http 404 status_code message."""
    if request.accept_mimetypes.accept_json:
        response = jsonify({'error': 'Resource not found. {e}'
                            .format(e=e.description)})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@api.app_errorhandler(400)
def bad_request(e):
    """Customize the defualt http 400 status_code message."""
    response = jsonify({
        'error': '400 Bad Request',
        'message': "The request is invalid or inconsistent. {e}"
        .format(e=e.description)})
    response.status_code = 400
    return response


@api.errorhandler(403)
def forbidden(e):
    """Customize the defualt http 403 status_code message."""
    response = jsonify({
        'error': '403 Forbidden',
        'message': "Permission required! "
                   "You are not allowed access to this resource."
        })
    response.status_code = 403
    return response


@auth.error_handler
def unauthorized():
    """Customize the defualt http 401 status_code message."""
    response = jsonify({
        'error': '401 Unauthenticated',
        'message': 'The authentication credentials sent with the request are '
                   'invalid or insufficient for the request.'
        })
    response.status_code = 401
    return response
