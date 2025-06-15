from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Collection, Book

bp = Blueprint('collections', __name__)

@bp.route('/collections')
@login_required
def list_collections():
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    return render_template('collections/index.html', collections=collections)

@bp.route('/collection/<int:id>')
@login_required
def view_collection(id):
    collection = Collection.query.get_or_404(id)
    if collection.user_id != current_user.id:
        flash("У вас нет доступа к этой подборке", "danger")
        return redirect(url_for('collections.list_collections'))
    return render_template('collections/view.html', collection=collection)

@bp.route('/collection/add', methods=['POST'])
@login_required
def add_collection():
    name = request.form.get('name')
    if not name:
        return jsonify({"error": "Название не может быть пустым"}), 400

    new_collection = Collection(name=name, user_id=current_user.id)
    db.session.add(new_collection)
    db.session.commit()
    return jsonify({"message": "Подборка добавлена"})

@bp.route('/collection/<int:id>/add_book', methods=['POST'])
@login_required
def add_book_to_collection(id):
    collection = Collection.query.get_or_404(id)
    if collection.user_id != current_user.id:
        return jsonify({"error": "Нет доступа"}), 403

    book_id = request.form.get('book_id')
    book = Book.query.get_or_404(book_id)

    if book not in collection.books:
        collection.books.append(book)
        db.session.commit()

    return jsonify({"message": "Книга добавлена в подборку"})