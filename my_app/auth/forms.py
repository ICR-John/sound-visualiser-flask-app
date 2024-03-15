""" Created by Beatrix Popa """
# based on the lecture notes provided for COMP0034


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_app.models import User


class SignupForm(FlaskForm):
    """ Create the sign up form """
    first_name = StringField(label='First name', validators=[DataRequired(message='First name required')])
    last_name = StringField(label='Last name', validators=[DataRequired(message='Last name required')])
    email = EmailField(label='Email address', validators=[DataRequired(message='Email address required')])
    password = PasswordField(label='Password', validators=[DataRequired(message='Password required')])
    password_repeat = PasswordField(label='Repeat Password',
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    def validate_email(self, email):
        # check if the email already has an account registered
        users = User.query.filter_by(email=email.data).first()
        if users is not None:
            raise ValidationError('An account is already registered for that email address')


class LoginForm(FlaskForm):
    """ Create the login form """
    email = EmailField(label='Email address', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField(label='Remember me')

    def validate_email(self, email):
        # check if the email has an acount registered
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email address.')

    def validate_password(self, password):
        # check if password matches the account
        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            raise ValidationError('No account found with that email address.')
        if not user.check_password(password.data):
            raise ValidationError('Incorrect password.')
