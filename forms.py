from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email

class UserRegisterForm(FlaskForm):
    """Form for registering/login a user."""

    first_name = StringField("First name", validators=[InputRequired()])

    last_name = StringField("Last name", validators=[InputRequired()])

    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid email")])

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])