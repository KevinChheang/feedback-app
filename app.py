from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserRegisterForm, UserLoginForm
from models import db, connect_db, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import DataError

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
            flash("Account created", "success")

            return redirect(f"/users/{new_user.username}")
        except IntegrityError:
            form.username.errors.append("Username already taken. Please choose another.")
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" not in session:
        flash("Please create an account first.", "info")
        return redirect("/register")
    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.authenticate(username, password)

        if existing_user:
            session["username"] = existing_user.username

            flash(f"Welcome {existing_user.first_name}", "success")

            return redirect(f"/users/{existing_user.username}")
        else:
            form.password.errors = ["Incorrect username/password"]
    
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.pop("username")
    flash("Logout successful", "success")

    return redirect("/")

@app.route("/users/<username>")
def show_secret(username):
    if "username" not in session:
        flash("Please login/register to unlock.", "warning")
        return redirect("/")
    elif session["username"] != username:
        flash("Invalid URL address", "danger")
        return redirect(f"/users/{session['username']}")

    user = User.query.get_or_404(username)

    return render_template("user_info.html", user=user)
