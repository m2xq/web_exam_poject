from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models import db, Collection, Book

bp = Blueprint('collections', __name__)

# 📚 Список подборок пользователя
@bp.route('/collections')
@login_required
def list_collections():
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    return render_template('collections/index.html', collections=collections)

# 👁 Просмотр конкретной подборки
@bp.route('/collection/<int:id>')
@login_required
def view_collection(id):
    collection = Collection.query.get_or_404(id)
    if collection.user_id != current_user.id:
        flash("У вас нет доступа к этой подборке", "danger")
        return redirect(url_for('collections.list_collections'))
    return render_template('collections/view.html', collection=collection)

# ➕ Добавление новой подборки (через JavaScript)
@bp.route('/collection/add', methods=['POST'])
@login_required
def add_collection():
    name = request.form.get('name', '').strip()
    current_app.logger.info(f"📥 Запрос на создание подборки: {name}")

    if not name:
        current_app.logger.warning("❌ Пустое название подборки.")
        return jsonify({"error": "Название не может быть пустым"}), 400

    try:
        new_collection = Collection(name=name, user_id=current_user.id)
        db.session.add(new_collection)
        db.session.commit()
        current_app.logger.info(f"✅ Подборка '{name}' добавлена.")
        return jsonify({"message": "Подборка добавлена"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Ошибка при создании подборки: {str(e)}")
        return jsonify({"error": "Ошибка при сохранении"}), 500

# 📚 Добавление книги в подборку (через JavaScript)
@bp.route('/collection/<int:id>/add_book', methods=['POST'])
@login_required
def add_book_to_collection(id):
    collection = Collection.query.get_or_404(id)
    if collection.user_id != current_user.id:
        return jsonify({"error": "Нет доступа"}), 403

    book_id = request.form.get('book_id', '').strip()
    if not book_id.isdigit():
        return jsonify({"error": "Некорректный ID книги"}), 400

    book = Book.query.get_or_404(int(book_id))

    if book in collection.books:
        return jsonify({"message": "Книга уже есть в подборке"}), 200

    try:
        collection.books.append(book)
        db.session.commit()
        current_app.logger.info(f"✅ Книга '{book.title}' добавлена в подборку '{collection.name}'")
        return jsonify({"message": "Книга добавлена в подборку"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Ошибка при добавлении книги: {str(e)}")
        return jsonify({"error": "Ошибка при добавлении книги"}), 500
