from flask import flash, redirect, render_template, request, url_for
from flask_login import (login_required, login_user, logout_user,
                         current_user)
from app.auth import auth
from app.main.forms import ShortForm
from app.models import User
from app.auth.forms import RegistrationForm, LoginForm


@auth.route('/signup', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_dashboard'))
    register_form = RegistrationForm()
    login_form = LoginForm()
    short_form = ShortForm()
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data,
                    first_name=register_form.first_name.data,
                    last_name=register_form.last_name.data,
                    password=register_form.password.data)
        user.save()
        flash('You can now login.', 'login')
        return redirect(url_for('auth.login'))
    if register_form.errors:
        flash([value for value in register_form.errors.values()][0][0],
              'register')
    return render_template('index.html', register_form=register_form,
                           short_form=short_form, login_form=login_form,
                           register_flag=True)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_dashboard'))
    login_form = LoginForm()
    register_form = RegistrationForm()
    short_form = ShortForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, False)
            flash('Logged in successfully.', 'login')
            return redirect(request.args.get('next') or url_for(
                'main.user_dashboard'))
        flash('Invalid username or password.', 'login')
    if login_form.errors:
        flash([value for value in login_form.errors.values()][0][0], 'login')
    return render_template('index.html', register_form=register_form,
                           short_form=short_form, login_form=login_form,
                           login_flag=True)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
