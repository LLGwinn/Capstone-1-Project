from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class UserEditForm(FlaskForm):
    """ Form for editing user profile information """

    email = StringField('Email', validators=[Optional(), Email()])
    city = StringField('Current City', validators=[Optional()])
    state = SelectField('Current State', validators=[Optional()])
    new_pw = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    old_pw = PasswordField('Current Password', validators=[Optional(), Length(min=6)])
