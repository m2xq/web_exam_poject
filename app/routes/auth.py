from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm, RegisterForm
from app.models import User, Role, db
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
            login_user(user, remember=form.remember.data)
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


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('books.index'))

    form = RegisterForm()

    # Все доступные роли
    form.role.choices = [(r.id, r.name.capitalize()) for r in Role.query.order_by(Role.name).all()]

    if form.validate_on_submit():
        if User.query.filter_by(login=form.login.data).first():
            flash("Пользователь с таким логином уже существует.", "danger")
            return render_template("auth/register.html", form=form)

        selected_role = Role.query.get(form.role.data)
        if not selected_role:
            flash("Выбранная роль недействительна.", "danger")
            return redirect(url_for('auth.register'))

        user = User(
            login=form.login.data,
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data or "",
            role=selected_role
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Регистрация прошла успешно!", "success")
        return redirect(url_for('books.index'))

    return render_template("auth/register.html", form=form)
