from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import URL, Required
from wtforms.widgets import HTMLString
from wtforms.widgets.core import html_params


class InlineButtonWidget(object):
    """Render a basic ``<button>`` field."""

    input_type = 'submit'
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', "shorten")
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('value', field.label.text)
        return HTMLString('<button %s>SHORTEN!' % self.html_params(
                            name=field.name, **kwargs))


class InlineSubmitField(BooleanField):
    """
    Represents an ``<button type="submit">``.  This allows checking if a given
    submit button has been pressed.
    """
    widget = InlineButtonWidget()


class ShortForm(FlaskForm):
    url = StringField(validators=[Required(), URL()])
    vanity_string = StringField()
    submit = InlineSubmitField()
