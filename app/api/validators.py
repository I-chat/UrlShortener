"""Validates all json schemas and data."""
from flask import abort
from voluptuous import Schema, Required
from validators import url, email, validator


@validator
def valid_name(value):
    """Check that all names are valid strings and alphabets."""
    return (isinstance(value, str) and value.isalpha() and len(value) > 0)


@validator
def valid_password(value):
    """Check that all Passwords are strings and non empty."""
    return(isinstance(value, str) and len(value) > 0)


def string_with_email(value):
    """Check that value has a valid email pattern."""
    if email(value):
        return value
    abort(400, "Not a valid email format.")


def url_string(value):
    """Check that value has a valid url pattern."""
    if url(value):
        return value
    abort(400, "Invalid URL format, Possibly missing 'http://'")


def name_string(value):
    """Check that all names are valid strings and alphabets."""
    if valid_name(value):
        return value
    abort(400, "Invalid name format. Name should include only one or"
          " more alphabets.")


def password_string(value):
    """Check that all Passwords are strings and non empty."""
    if valid_password(value):
        return value
    abort(400, "Invalid password format. Passwords can only be strings.")


def check_vanity_str(value):
    """Check that all vanity strings are strings and non empty."""
    if type(value) is str and len(value) > 0 and " " not in value:
        return value
    abort(400, "Invalid input. Vanity string can only be a non empty string.")


register = Schema({
    Required('firstname'): name_string,
    Required('lastname'): name_string,
    Required('email'): string_with_email,
    Required('password'): password_string,
    Required('confirm_password'): password_string
}, extra=True)

valid_url = Schema({
    Required('url'): url_string,
    'vanity_string': check_vanity_str,
})
