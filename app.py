from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User
from forms import RegisterForm
from helpers import create_new_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "milaisthebestdogintheworld"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def home_page():
    """Shows home page"""
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def show_register_form():
    """Show and process a form to register a new user"""
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = create_new_user(form)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash(
                f"Welcome {new_user.first_name.title()}! We've created an account for you!", "success")
            return redirect('/')
        except IntegrityError as e:
            for arg in e.args:
                if 'username' in arg:
                    form.username.errors.append("Username is already taken!")
                if 'email' in arg:
                    form.email.errors.append("Email is already taken!")
    return render_template('register.html', form=form)
