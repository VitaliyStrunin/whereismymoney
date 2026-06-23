from flask import Blueprint, jsonify, request

from backend.core.exceptions import CategoryNotFoundError
from backend.database.session import session_maker
from backend.models.category import Category
from backend.services.category_service import CategoryService

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


def category_to_dict(category: Category) -> dict:
    return {"id": category.id, "name": category.name}


@categories_bp.get("")
def get_categories():
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    with session_maker() as session:
        service = CategoryService(session)
        categories = service.get_list(limit=limit, offset=offset)

    return jsonify([
        category_to_dict(category) for category in categories
    ])


@categories_bp.post("")
def create_category():
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    with session_maker() as session:
        service = CategoryService(session)
        category = service.create_category(name)

    return jsonify(category_to_dict(category)), 201


@categories_bp.get("/<int:category_id>")
def get_category(category_id: int):
    with session_maker() as session:
        service = CategoryService(session)
        try:
            category = service.get_by_id(category_id)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404

    return jsonify(category_to_dict(category)), 200


@categories_bp.patch("/<int:category_id>")
def update_category(category_id: int):
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    with session_maker() as session:
        service = CategoryService(session)

        try:
            category = service.update_category(category_id, name)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404

    return jsonify(category_to_dict(category)), 200


@categories_bp.delete("/<int:category_id>")
def delete_category(category_id: int):
    with session_maker() as session:
        service = CategoryService(session)
        try:
            service.delete_category(category_id)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404

    return jsonify({"success": "Category deleted successfully"}), 200
