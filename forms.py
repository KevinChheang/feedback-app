from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class UserRegisterForm(FlaskForm):
    """Form for registering a user."""

    first_name = StringField("First name", validators=[InputRequired(), Length(max=30, message="Maximum 30 characters")])

    last_name = StringField("Last name", validators=[InputRequired(), Length(max=30, message="Maximum 30 characters")])

    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid email"), Length(max=50, message="Maximum 50 characters")])

    username = StringField("Username", validators=[InputRequired(), Length(max=20, message="Maximum 20 characters")])

    password = PasswordField("Password", validators=[InputRequired()])

class UserLoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    """Form for getting user feedback."""

    title = StringField("TItle", validators=[InputRequired(), Length(max=100, message="Maximum 100 characters")])

    content = TextAreaField("Content", validators=[InputRequired()])