import dotenv
from flask import flash, redirect, render_template, request
from flask_login import login_required, current_user
from . import main
from ..auth.forms import RegistrationForm, LoginForm
from ..helper import UrlSaver
from ..models import User
from .forms import ShortForm


dotenv.load()
site_url = dotenv.get('SITE_URL')


@main.route('/')
@main.route('/index')
@main.route('/shorten', methods=['POST'])
def index():
    if current_user.is_authenticated:
        return redirect()
    register_form = RegistrationForm()
    login_form = LoginForm()
    short_form = ShortForm()
    short_url = ""

    if short_form.validate_on_submit():
        user = User.query.filter_by(email='AnonymousUser').first()
        if not user:
            user = User(first_name='AnonymousUser', last_name='AnonymousUser',
                        email='AnonymousUser')
            user.save()
        short_url = UrlSaver.generate_and_save_urls(
                            short_form.short_url.data, user).short_url
    if short_form.errors:
        flash([value for value in short_form.errors.values()][0][0],
              'shorten')
    try:
        if request.headers['Ajax-Test']:
            return site_url + short_url
    except KeyError:
        return render_template('index.html', register_form=register_form,
                               login_form=login_form, short_form=short_form,
                               short_url=site_url + short_url)
