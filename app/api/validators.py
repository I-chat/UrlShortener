"""Validates all json schemas and data."""
from voluptuous import (Email, All, Length, Match, REMOVE_EXTRA, Required,
                        Schema, Url)

register = Schema({
    'firstname': Match('^[A-Za-z][A-Za-z]*$', msg="Invalid name format. Name"
                       " should include only one or more alphabets."),
    'lastname': Match('^[A-Za-z][A-Za-z]*$', msg="Invalid name format. Name"
                      " should include only one or more alphabets."),
    'email': Email(msg="Not a valid email format."),
    'password': All(str, Length(min=1), msg="Invalid password format."
                    " Passwords can only be strings."),
    'confirm_password': All(str, Length(min=1), msg="Invalid password format."
                            " Passwords can only be strings.")
}, required=True, extra=REMOVE_EXTRA)

valid_url = Schema({
    Required('url'): Url(msg="Invalid URL format, Possibly missing 'http://'"),
    'vanity_string': Match(r'^\S+$', msg="Invalid input. Vanity string can"
                           " only be a non empty string."),
})
