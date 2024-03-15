"""Created by Saeeda Doolan"""
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from my_app.models import Profile
from my_app import photos


class ProfileForm(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired(message='Username required')])
    bio = TextAreaField(label='Bio', validators=[Optional(strip_whitespace=True)],
                        description='Tell us about yourself')
    photo = FileField(label='Profile Picture',
                      validators=[Optional(strip_whitespace=True), FileAllowed(photos, 'Images only')])

    def validate_username(self, username):
        """
        If username is not in database and do not belong to current user,
        raise error
        """
        find_profile = Profile.query.filter_by(username=username.data).first()
        if find_profile is not None and find_profile != Profile.get_profile(current_user.id):
            raise ValidationError('An account is already registered for with that username.')

