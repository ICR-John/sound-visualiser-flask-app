""" Created based on the lecture notes for COMP0034 """
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('menu.index'))
    return render_template('index.html', title='Home page', name='Anonymous')

