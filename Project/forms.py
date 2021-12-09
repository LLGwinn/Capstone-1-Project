from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional



class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class UserEditForm(FlaskForm):
    """ Form for editing user profile information """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    password = PasswordField('Enter Current Password', validators=[DataRequired(), Length(min=6)])
