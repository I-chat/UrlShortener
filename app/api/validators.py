from flask import abort
from voluptuous import Schema, Required
from validators import url, email, validator


@validator
def valid_name(value):
    return (isinstance(value, str) and value.isalpha() and len(value) > 0)


@validator
def valid_password(value):
    return(isinstance(value, str) and len(value) > 0)


def string_with_email(value):
    if email(value):
        return value
    abort(400, "Not a valid email format.")


def url_string(value):
    if url(value):
        return value
    abort(400, "Invalid URL format, Possibly missing 'http://'")


def name_string(value):
    if valid_name(value):
        return value
    abort(400, "Invalid name format. Name should include only one or"
          " more alphabets.")


def password_string(value):
    if valid_password(value):
        return value
    abort(400, "Invalid password format. Passwords can only be strings.")


register = Schema({
    Required('firstname'): name_string,
    Required('lastname'): name_string,
    Required('email'): string_with_email,
    Required('password'): password_string,
    Required('confirm_password'): password_string
}, extra=True)

valid_url = Schema({
    Required('url'): url_string
})
