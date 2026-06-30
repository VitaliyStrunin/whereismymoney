from flask import Blueprint, jsonify, request

from backend.api.dependencies import get_db_session
from backend.core.exceptions import (
    CategoryNotFoundError,
    ExpenseNotFoundError,
    TagNotFoundError,
)
from backend.schemas.expense import (
    ExpenseCreateDTO,
    ExpenseListQueryDTO,
    ExpenseResponseDTO,
    ExpenseUpdateDTO,
)
from backend.services.expense_service import ExpenseService

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@expenses_bp.get("")
def get_expenses():
    query_params = ExpenseListQueryDTO.model_validate(request.args.to_dict())

    with get_db_session() as session:
        service = ExpenseService(session)
        expenses = service.get_list(limit=query_params.limit, offset=query_params.offset)

        return jsonify([
             ExpenseResponseDTO.model_validate(expense).model_dump(mode="json")
             for expense in expenses
        ]), 200


@expenses_bp.post("")
def create_expense():
    create_dto = ExpenseCreateDTO.model_validate(request.get_json(silent=True) or {})

    with get_db_session() as session:
        service = ExpenseService(session)
        try:
            expense = service.create_expense(create_dto.amount,
                                            create_dto.description,
                                            create_dto.expense_date,
                                            create_dto.category_id,
                                            create_dto.tag_ids,
                                            )
            response_dto = ExpenseResponseDTO.model_validate(expense)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

        return jsonify(response_dto.model_dump(mode='json')), 201


@expenses_bp.get("/<int:expense_id>")
def get_expense(expense_id: int):
    with get_db_session() as session:
        service = ExpenseService(session)
        try:
            expense = service.get_by_id(expense_id)
            response_dto = ExpenseResponseDTO.model_validate(expense)
        except ExpenseNotFoundError:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(response_dto.model_dump(mode='json')), 200


@expenses_bp.patch("/<int:expense_id>")
def update_expense(expense_id: int):
    update_dto = ExpenseUpdateDTO.model_validate(request.get_json(silent=True) or {})
    update_data = update_dto.model_dump(exclude_unset=True)

    with get_db_session() as session:
        service = ExpenseService(session)
        try:
            updated_expense = service.update_expense(expense_id, update_data)
            response_dto = ExpenseResponseDTO.model_validate(updated_expense)
        except CategoryNotFoundError:
            return jsonify({"error": "Category not found"}), 404
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404
        except ExpenseNotFoundError:
            return jsonify({"error": "Expense not found"}), 404
        except Exception:
            return jsonify({"error": "Bad request"}), 400

        return jsonify(response_dto.model_dump(mode='json')), 200


@expenses_bp.delete("/<int:expense_id>")
def delete_expense(expense_id: int):
    with get_db_session() as session:
        service = ExpenseService(session)
        try:
            service.delete_expense(expense_id)
        except ExpenseNotFoundError:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify({"success": "Expense deleted successfully"}), 200
