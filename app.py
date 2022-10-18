from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User
from forms import LoginForm, RegisterForm
from helpers import create_new_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "milaisthebestdogintheworld"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

KEY_USER_ID = 'user_id'


@app.route('/')
def home_page():
    """Shows home page"""
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show and process the sign up form for new users"""
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

        session[KEY_USER_ID] = new_user.id

        flash(
            f"Welcome {new_user.first_name.title()}! We've created an account for you!", "success")
        return redirect('/')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Show and process the login form for existing users"""

    if KEY_USER_ID in session:
        flash("You are already logged in!", "warning")
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            session[KEY_USER_ID] = user.id
            flash(f"Welcome back {user.first_name}!", "success")
            return redirect('/')

        flash("Incorrect username or password!", "danger")

    return render_template("login.html", form=form)
