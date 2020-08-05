from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserRegisterForm
from models import User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///authentication_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = "abc123"

toolbar = DebugToolbarExtension(app)

@app.route("/")
def homepage():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = UserRegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        new_user = User.register(username=username, password=password)

    return render_template("register.html", form=form)

