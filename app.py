from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserRegisterForm, UserLoginForm, FeedbackForm
from models import db, connect_db, User, Feedback
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

def check_login():
    if "username" not in session:
        flash("Please login/register to unlock.", "warning")
        return redirect("/")

@app.route("/")
def homepage():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

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
    check_login()
    if session["username"] != username:
        return redirect(f"/users/{session['username']}")

    user = User.query.get_or_404(username)

    feedbacks = Feedback.query.all()

    return render_template("user_info.html", user=user, feedbacks=feedbacks)

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    check_login()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        flash("Feedback submitted", "success")

        return redirect("/users/{{user.username}}")

    return render_template("feedback_form.html", form=form)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """
    Right now each user can delete themself, which is good for now.
    Further update will only allow admin user to delete individual user.
    """
    check_login()

    # The method does not offer in-Python cascading of relationships - 
    # it is assumed that ON DELETE CASCADE/SET NULL/etc. 
    # is configured for any foreign key references which require it, 
    # otherwise the database may emit an integrity violation 
    # if foreign key references are being enforced. 
    user = db.session.query(User).filter(User.username==username).first()
    db.session.delete(user)
    db.session.commit()

    session.pop("username")

    flash("User deleted successfully", "success")

    return redirect("/")

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    check_login()

    existing_feedback = Feedback.query.get_or_404(feedback_id)

    form = FeedbackForm(obj=existing_feedback)

    if form.validate_on_submit():
        existing_feedback.title = form.title.data
        existing_feedback.content = form.content.data

        db.session.add(existing_feedback)
        db.session.commit()

        return redirect(f"/users/{existing_feedback.user.username}")

    return render_template("update_feedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    check_login()

    feedback = Feedback.query.get_or_404(feedback_id)

    Feedback.query.filter_by(id=feedback_id).delete()

    db.session.commit()

    flash("Feedback deleted successfully", "success")

    return redirect(f"/users/{feedback.username}")