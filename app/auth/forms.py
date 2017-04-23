from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, Length, Required, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class RegistrationForm(FlaskForm):
    first_name = StringField(validators=[Required(), Length(1, 64),
                                         Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                         'Names must have only letters.')])
    last_name = StringField(validators=[Required(), Length(1, 64),
                                        Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                        'Names must have only letters.')])
    email = StringField(validators=[Required(), Length(1, 64),
                        Email()])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Password mismatch.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Sign up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Length(1, 64),
                        Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Login')
