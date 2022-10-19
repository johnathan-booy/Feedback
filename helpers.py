from flask import session
from models import User


def create_new_user(form):
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    return User.register(username=username, password=password,
                         email=email, first_name=first_name, last_name=last_name)


def authenticate_user(username):
    if username == session.get('username'):
        return True
