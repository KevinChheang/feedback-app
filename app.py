from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserRegisterForm, UserLoginForm
from models import db, connect_db, User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = "abc123"

toolbar = DebugToolbarExtension(app)

connect_db(app) # connect to db
db.create_all() # create tables

@app.route("/")
def homepage():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = UserRegisterForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data

        new_user = User.register(first_name, last_name, email, username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
            session["username"] = new_user.username
            return redirect("/secret")
        except IntegrityError:
            form.username.errors.append("Username already taken. Please choose another.")
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.authenticate(username, password)

        if existing_user:
            session["username"] = existing_user.username

            flash(f"Welcome {existing_user.username}", "success")

            return redirect("/secret")
        else:
            form.password.errors = ["Incorrect username/password"]
    
    return render_template("login.html", form=form)

@app.route("/secret")
def show_secret():
    return "<h1>You made it!</h1>"