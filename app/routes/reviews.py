from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms import ReviewForm
from app.models import db, Review, Book
from bleach import clean

bp = Blueprint('reviews', __name__)

@bp.route('/book/<int:book_id>/review/add', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    existing = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing:
        flash("Вы уже оставляли рецензию на эту книгу.", "info")
        return redirect(url_for('books.view', id=book_id))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            book_id=book_id,
            user_id=current_user.id,
            rating=form.rating.data,
            text=clean(form.text.data)
        )
        db.session.add(review)
        db.session.commit()
        flash("Рецензия добавлена.", "success")
        return redirect(url_for('books.view', id=book_id))

    return render_template('reviews/add.html', form=form, book=book)