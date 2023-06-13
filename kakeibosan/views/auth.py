from flask_login import login_user, logout_user
from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from kakeibosan.views.forms import LoginForm
from kakeibosan.models import User


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(user_name=form.username.data).first()
        password_hash = User.calculate_password_hash(form.password.data)

        if user and user.password == password_hash:
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get('next')
            # return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form, this_year=_year())


@bp.route('/logout')
def logout():
    logout_user()
    form = LoginForm()
    flash('Log out', 'info')
    return render_template('login.html', form=form, this_year=_year())


def _year():
    return datetime.today().year
