from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, PasswordField, BooleanField, 
    SelectField, SubmitField, IntegerField, FileField, 
    SelectMultipleField
)
from wtforms.validators import DataRequired, Length, NumberRange


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[
        DataRequired(), Length(min=3, max=64)
    ])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class BookForm(FlaskForm):
    title = StringField("Название", validators=[
        DataRequired(), Length(min=1, max=128)
    ])
    description = TextAreaField("Описание", validators=[
        DataRequired(), Length(min=10)
    ])
    year = IntegerField("Год издания", validators=[
        DataRequired(), NumberRange(min=0, max=2100)
    ])
    publisher = StringField("Издательство", validators=[
        DataRequired(), Length(min=2, max=128)
    ])
    author = StringField("Автор", validators=[
        DataRequired(), Length(min=2, max=128)
    ])
    pages = IntegerField("Количество страниц", validators=[
        DataRequired(), NumberRange(min=1, max=10000)
    ])
    genres = SelectMultipleField("Жанры", coerce=int, validators=[
        DataRequired()
    ])
    cover = FileField("Обложка (необязательно)")  # Только для добавления
    submit = SubmitField("Добавить книгу")


class ReviewForm(FlaskForm):
    rating = SelectField("Оценка", choices=[
        (5, 'Отлично'),
        (4, 'Хорошо'),
        (3, 'Удовлетворительно'),
        (2, 'Плохо'),
        (1, 'Очень плохо'),
        (0, 'Ужасно')
    ], coerce=int, validators=[DataRequired()])
    text = TextAreaField("Текст рецензии", validators=[
        DataRequired(), Length(min=10)
    ])
    submit = SubmitField("Сохранить")

