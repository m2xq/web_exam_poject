from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Book, Genre, Cover
from app.forms import BookForm
import os, hashlib

bp = Blueprint('books', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=10)
    return render_template('books/index.html', books=books)

@bp.route('/book/<int:id>')
def view(id):
    book = Book.query.get_or_404(id)
    return render_template('books/view.html', book=book)

@bp.route('/book/add', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.role.name != 'администратор':
        flash("У вас недостаточно прав для выполнения данного действия.", 'danger')
        return redirect(url_for('books.index'))

    form = BookForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.all()]

    if form.validate_on_submit():
        try:
            book = Book(
                title=form.title.data,
                description=form.description.data,
                year=form.year.data,
                publisher=form.publisher.data,
                author=form.author.data,
                pages=form.pages.data,
                genres=[Genre.query.get(id) for id in form.genres.data]
            )
            db.session.add(book)
            db.session.flush()  # получаем id книги

            # загрузка обложки
            file = form.cover.data
            if file:
                content = file.read()
                md5 = hashlib.md5(content).hexdigest()
                existing = Cover.query.filter_by(md5_hash=md5).first()
                if existing:
                    book.cover = existing
                else:
                    filename = secure_filename(file.filename)
                    new_cover = Cover(
                        filename=filename,
                        mimetype=file.mimetype,
                        md5_hash=md5
                    )
                    db.session.add(new_cover)
                    db.session.flush()
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"cover_{new_cover.id}")
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    book.cover = new_cover

            db.session.commit()
            flash("Книга успешно добавлена.", "success")
            return redirect(url_for('books.index'))
        except Exception as e:
            db.session.rollback()
            flash("Ошибка при сохранении книги.", "danger")

    return render_template('books/add_edit.html', form=form)

@bp.route('/book/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    book = Book.query.get_or_404(id)
    if current_user.role.name not in ['администратор', 'модератор']:
        flash("У вас недостаточно прав для выполнения данного действия.", 'danger')
        return redirect(url_for('books.index'))

    form = BookForm(obj=book)
    form.genres.choices = [(g.id, g.name) for g in Genre.query.all()]
    if request.method == 'GET':
        form.genres.data = [g.id for g in book.genres]

    if form.validate_on_submit():
        try:
            book.title = form.title.data
            book.description = form.description.data
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.author = form.author.data
            book.pages = form.pages.data
            book.genres = [Genre.query.get(id) for id in form.genres.data]

            db.session.commit()
            flash("Книга успешно обновлена.", "success")
            return redirect(url_for('books.view', id=book.id))
        except Exception:
            db.session.rollback()
            flash("Ошибка при обновлении книги.", "danger")

    return render_template('books/add_edit.html', form=form, editing=True)

@bp.route('/book/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if current_user.role.name != 'администратор':
        flash("У вас недостаточно прав для выполнения данного действия.", 'danger')
        return redirect(url_for('books.index'))

    book = Book.query.get_or_404(id)
    try:
        cover = book.cover
        db.session.delete(book)
        db.session.commit()

        # если обложка больше не используется — удалить файл и запись
        if cover and not Book.query.filter_by(cover_id=cover.id).first():
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"cover_{cover.id}")
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(cover)
            db.session.commit()

        flash("Книга успешно удалена.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при удалении книги.", "danger")

    return redirect(url_for('books.index'))