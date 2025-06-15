from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .routes import auth, books, reviews, collections
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(collections.bp)

    login_manager.login_view = 'auth.login'

    # 👉 Добавим начальные данные
    with app.app_context():
        create_initial_data()

    return app

# 📌 Функция добавления ролей и тестовых пользователей
def create_initial_data():
    from app.models import db, Role, User

    if not Role.query.first():
        admin_role = Role(name='администратор', description='полный доступ')
        mod_role = Role(name='модератор', description='редактирование и модерация')
        user_role = Role(name='пользователь', description='оставление рецензий')
        db.session.add_all([admin_role, mod_role, user_role])
        db.session.commit()

    if not User.query.filter_by(login='admin').first():
        admin = User(
            login='admin',
            password_hash=generate_password_hash('admin123'),
            last_name='Иванов',
            first_name='Админ',
            middle_name='',
            role_id=Role.query.filter_by(name='администратор').first().id
        )
        db.session.add(admin)

    if not User.query.filter_by(login='user').first():
        user = User(
            login='user',
            password_hash=generate_password_hash('user123'),
            last_name='Петров',
            first_name='Пользователь',
            middle_name='',
            role_id=Role.query.filter_by(name='пользователь').first().id
        )
        db.session.add(user)

    db.session.commit()
