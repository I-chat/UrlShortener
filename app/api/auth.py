"""Manage user authentication and registration endpoints."""
from . import api
from flask import request, abort, jsonify, g
from flask_login import AnonymousUserMixin
from ..models import User
from voluptuous import MultipleInvalid
from flask_httpauth import HTTPBasicAuth
from .validators import register
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """Manage the authentication of either email and password or token."""
    if not email_or_token:
        g.current_user = AnonymousUserMixin()
        return True
    if not password:
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/token', strict_slashes=False)
@auth.login_required
def get_token():
    """Return a valid token for registered users."""
    if g.current_user.is_anonymous or g.token_used:
        return abort(403)
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600).decode('ascii'), 'expiration': '3600secs'}), 201


@api.route('/register', methods=['POST'], strict_slashes=False)
def new_user():
    """Register a user and save the details."""
    try:
        register(request.json)
    except MultipleInvalid:
        abort(400, "Incomplete number of required keys provided.")

    first_name = request.json.get('firstname')
    last_name = request.json.get('lastname')
    email = request.json.get('email')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')

    if not password == confirm_password:
        abort(400, "password and confirm_password do not match.")

    if User.query.filter_by(email=email).first() is not None:
        abort(400, "User already registered.Try login.")  # existing user

    user = User(email=email, first_name=first_name,
                last_name=last_name)
    user.password = password
    user.save()
    return jsonify({
        "email": user.email,
        "message": "Registration Successful."
        }), 201
