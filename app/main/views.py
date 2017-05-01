import dotenv
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.auth.forms import RegistrationForm, LoginForm
from app.helper import UrlSaver
from app.main import main
from app.models import AnonymousUser, User
from app.main.forms import ShortForm


dotenv.load()
site_url = dotenv.get('SITE_URL')


@main.route('/')
@main.route('/shorten', methods=['POST'])
@main.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_dashboard'))
    register_form = RegistrationForm()
    login_form = LoginForm()
    short_form = ShortForm()
    short_url = ""

    if short_form.validate_on_submit():
        user = User.query.filter_by(email='AnonymousUser').first()
        if not user:
            user = AnonymousUser.create_anonymous_user()

        short_url = UrlSaver.generate_and_save_urls(
                            short_form.url.data, user).short_url

        try:
            if request.headers['Ajax-Test']:
                return site_url + short_url
        except KeyError:
            return render_template('index.html', register_form=register_form,
                                   login_form=login_form,
                                   short_form=short_form,
                                   short_url=site_url + short_url)

    if short_form.errors:
        flash([value for value in short_form.errors.values()][0][0],
              'shorten')
    try:
        request.headers['Ajax-Test']
    except KeyError:
        return render_template('index.html', register_form=register_form,
                               login_form=login_form, short_form=short_form,
                               short_url=site_url + short_url)


@main.route('/dashboard')
@login_required
def user_dashboard():
    return render_template('dashboard.html', register_form="",
                           login_form="", short_form="",)
