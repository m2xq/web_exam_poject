from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'))
)

book_collection = db.Table('book_collection',
    db.Column('collection_id', db.Integer, db.ForeignKey('collection.id', ondelete='CASCADE')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete")
    collections = db.relationship('Collection', backref='user', lazy=True, cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()

    def __repr__(self):
        return f'<User {self.login}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Genre {self.name}>'


class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(255), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)

    book = db.relationship('Book', backref='cover', uselist=False)

    def __repr__(self):
        return f'<Cover {self.filename}>'


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)

    cover_id = db.Column(db.Integer, db.ForeignKey('cover.id'), nullable=True)

    genres = db.relationship('Genre', secondary=book_genre, backref=db.backref('books', lazy='dynamic'))
    reviews = db.relationship('Review', backref='book', lazy=True, cascade="all, delete-orphan")

    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum([r.rating for r in self.reviews]) / len(self.reviews), 1)

    def review_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f'<Book {self.title}>'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Review BookID={self.book_id} UserID={self.user_id}>'


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    books = db.relationship('Book', secondary=book_collection, backref=db.backref('collections', lazy='dynamic'))

    def __repr__(self):
        return f'<Collection {self.name}>'
