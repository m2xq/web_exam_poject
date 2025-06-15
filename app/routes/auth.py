from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm
from app.models import User
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('books.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data == 'yes')
            flash("Вы успешно вошли в систему.", "success")
            return redirect(url_for('books.index'))
        else:
            flash("Невозможно аутентифицироваться с указанными логином и паролем", "danger")

    return render_template("auth/login.html", form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for('books.index'))
