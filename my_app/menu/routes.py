""" Created based on the lecture notes for COMP0034 """

from flask import Blueprint, render_template
from flask_login import login_required, current_user

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


@menu_bp.route('/')
@login_required
def index():
    return render_template('menu.html', username=current_user.firstname)
