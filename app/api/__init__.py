"""Initializes the api Blueprint."""
from flask import Blueprint

api = Blueprint('api', __name__)

from app.api import auth, errors, shorten
