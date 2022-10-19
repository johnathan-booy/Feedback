from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Feedback
from forms import LoginForm, RegisterForm, FeedbackForm
from helpers import create_new_user, authenticate_user
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "hellosecret123")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def home_page():
    """Shows all feedback"""
    feedback = Feedback.query.all()
    return render_template('home.html', feedback=feedback)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show and process the sign up form for new users"""

    if 'username' in session:
        flash("You are already logged in!", "warning")
        return redirect('/')

    form = RegisterForm()
    if form.validate_on_submit():
        new_user = create_new_user(form)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError as e:
            for arg in e.args:
                if 'username' in arg:
                    form.username.errors.append("Username is already taken!")
                if 'email' in arg:
                    form.email.errors.append("Email is already taken!")
            return render_template('register.html', form=form)

        session['username'] = new_user.username

        flash(
            f"Welcome {new_user.first_name.title()}! We've created an account for you!", "success")
        return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Show and process the login form for existing users"""

    if 'username' in session:
        flash("You are already logged in!", "warning")
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            flash(f"Welcome back {user.first_name}!", "success")
            return redirect(f'/users/{user.username}')

        flash("Incorrect username or password!", "danger")

    return render_template("login.html", form=form)


@app.route('/logout', methods=['GET'])
def logout_user():
    """Logout user, removing id from the session"""
    session.pop('username')
    flash(f"Goodbye!", "success")
    return redirect('/')


@app.route('/users/<username>')
def show_user_details(username):
    """Show details about the current user. You must be logged in as the specified user to see this page"""

    if authenticate_user(username):
        user = User.query.filter_by(username=username).first()

        if user:
            feedback = Feedback.query.filter_by(username=username).all()
            return render_template("user.html", user=user, feedback=feedback)
    else:
        flash("You don't have permision to view that page!", "warning")
        return redirect('/')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user if they are signed in"""

    if authenticate_user(username):
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("User has been deleted", 'success')
    else:
        flash("You don't have permission to delete this user!", 'warning')

    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Show and process the add feedback form"""

    if authenticate_user(username):
        form = FeedbackForm()
        if form.validate_on_submit():
            feedback = Feedback(username=username)
            form.populate_obj(feedback)
            db.session.add(feedback)
            db.session.commit()
            flash("Feedback added!", "success")
            return redirect(f'/users/{username}')

        return render_template("add-feedback.html", form=form)
    else:
        flash("You don't have permision to view that page!", "warning")
        return redirect("/")


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Update feedback if the correct user is signed in"""

    feedback = Feedback.query.get(feedback_id)

    if authenticate_user(feedback.username):
        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash("Feedback updated!", "success")
            return redirect(f'/users/{feedback.username}')

        return render_template('update-feedback.html', form=form)
    else:
        flash("You don't have permission to edit that feedback!", "warning")
        return redirect('/')


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Delete feedback if the correct user is signed in"""

    feedback = Feedback.query.get(feedback_id)

    if authenticate_user(feedback.username):
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback has been deleted", 'success')
        return redirect(f'/users/{feedback.username}')
    else:
        flash("You don't have permission to delete that feedback!", "warning")
        return redirect('/')
