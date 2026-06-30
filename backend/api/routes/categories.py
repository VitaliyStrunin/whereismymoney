from flask import Blueprint, jsonify, request

from backend.api.dependencies import get_db_session
from backend.core.exceptions import CategoryInUseError, CategoryNotFoundError
from backend.schemas.category import (
    CategoryCreateDTO,
    CategoryListQueryDTO,
    CategoryResponseDTO,
    CategoryUpdateDTO,
)
from backend.services.category_service import CategoryService

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.get("")
def get_categories():
    query_params = CategoryListQueryDTO.model_validate(request.args.to_dict())

    with get_db_session() as session:
        service = CategoryService(session)
        categories = service.get_list(limit=query_params.limit, offset=query_params.offset)

        return jsonify([
            CategoryResponseDTO.model_validate(category).model_dump(mode="json")
            for category in categories
        ])


@categories_bp.post("")
def create_category():
    category_dto = CategoryCreateDTO.model_validate(request.get_json(silent=True) or {})

    with get_db_session() as session:
        service = CategoryService(session)
        category = service.create_category(category_dto.name)
        response_dto = CategoryResponseDTO.model_validate(category)

        return jsonify(response_dto.model_dump(mode="json")), 201


@categories_bp.get("/<int:category_id>")
def get_category(category_id: int):
    with get_db_session() as session:
        service = CategoryService(session)
        try:
            category = service.get_by_id(category_id)
            response_dto = CategoryResponseDTO.model_validate(category)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404

        return jsonify(response_dto.model_dump(mode="json")), 200


@categories_bp.patch("/<int:category_id>")
def update_category(category_id: int):
    category_dto = CategoryUpdateDTO.model_validate(request.get_json(silent=True) or {})
    with get_db_session() as session:
        service = CategoryService(session)
        try:
            category = service.update_category(category_id, category_dto.name)
            response_dto = CategoryResponseDTO.model_validate(category)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404

        return jsonify(response_dto.model_dump(mode="json")), 200


@categories_bp.delete("/<int:category_id>")
def delete_category(category_id: int):
    with get_db_session() as session:
        service = CategoryService(session)
        try:
            service.delete_category(category_id)
        except CategoryInUseError:
            return jsonify({"error": "Category is used by expenses"}), 409
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404

        return jsonify({"success": "Category deleted successfully"}), 200
