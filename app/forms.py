from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, SubmitField, IntegerField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = SelectField("Запомнить", choices=[('yes', 'Да'), ('no', 'Нет')])
    submit = SubmitField("Войти")

class BookForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    year = IntegerField("Год", validators=[DataRequired()])
    publisher = StringField("Издательство", validators=[DataRequired()])
    author = StringField("Автор", validators=[DataRequired()])
    pages = IntegerField("Объем (стр)", validators=[DataRequired()])
    genres = SelectMultipleField("Жанры", coerce=int)
    cover = FileField("Обложка")
    submit = SubmitField("Сохранить")
