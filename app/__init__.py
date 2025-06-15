from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect  # ✅ Добавлено
from config import Config
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()  # ✅ Добавлено

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # ✅ CSRF защита активирована

    from .routes import auth, books, reviews, collections
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(collections.bp)

    login_manager.login_view = 'auth.login'

    with app.app_context():
        create_initial_data()

    return app

def create_initial_data():
    from app.models import db, Role, User, Genre
    from werkzeug.security import generate_password_hash

    if not Role.query.first():
        db.session.add_all([
            Role(name='администратор', description='полный доступ'),
            Role(name='модератор', description='редактирование и модерация'),
            Role(name='пользователь', description='оставление рецензий')
        ])
        db.session.commit()

    if not User.query.filter_by(login='admin').first():
        db.session.add(User(
            login='admin',
            password_hash=generate_password_hash('admin123'),
            last_name='Иванов',
            first_name='Админ',
            middle_name='',
            role_id=Role.query.filter_by(name='администратор').first().id
        ))

    if not User.query.filter_by(login='user').first():
        db.session.add(User(
            login='user',
            password_hash=generate_password_hash('user123'),
            last_name='Петров',
            first_name='Пользователь',
            middle_name='',
            role_id=Role.query.filter_by(name='пользователь').first().id
        ))

    if not Genre.query.first():
        default_genres = [
            'Фантастика',
            'Детектив',
            'Роман',
            'Приключения',
            'Научная литература',
            'Поэзия',
            'История',
            'Биография'
        ]
        db.session.add_all([Genre(name=name) for name in default_genres])

    db.session.commit()
