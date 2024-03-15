""" Created by Beatrix Popa, Isaiah John """
# based on the lecture notes provided for COMP0034


from datetime import timedelta
from sqlite3 import IntegrityError
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from urllib.parse import urlparse, urljoin
from flask_login import login_user, login_required, logout_user
from my_app import db, login_manager
from my_app.auth.forms import SignupForm, LoginForm
from my_app.models import User


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Sign up a new user"""
    form = SignupForm(request.form)
    if form.validate_on_submit():
        user = User(firstname=form.first_name.data, lastname=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f"Hello, {user.firstname} {user.lastname}. You are signed up.")
        except IntegrityError:
            db.session.rollback()
            flash(f'Error, unable to register {form.email.data}. ', 'error')
            return redirect(url_for('auth.signup'))
        login_user(user)
        return redirect(url_for('home.index'))
    return render_template('signup.html', title='Sign Up', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ log in an existing user """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, remember=form.remember.data, duration=timedelta(minutes=1))
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('home.index'))
    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.index'))


@login_manager.user_loader
def load_user(user_id):
    """ Takes a user ID and returns a user object or None if the user does not exist"""
    if user_id is not None:
        return User.query.get(user_id)
    return None


def is_safe_url(target):
    # check if the url is safe
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc


def get_safe_redirect():
    # redirect to a safe url
    url = request.args.get('next')
    if url and is_safe_url(url):
        return url
    url = request.referrer
    if url and is_safe_url(url):
        return url
    return '/'


@login_manager.unauthorized_handler
def unauthorized():
    """ Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))
