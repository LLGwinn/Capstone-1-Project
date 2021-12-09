from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserAddForm(FlaskForm):
    """ Form for adding users """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    curr_city = StringField('What is your current city?', validators=[DataRequired()])
    curr_state = StringField('State', validators=[DataRequired()])


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class UserEditForm(FlaskForm):
    """ Form for editing user profile information """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    password = PasswordField('Enter Current Password', validators=[DataRequired(), Length(min=6)])
