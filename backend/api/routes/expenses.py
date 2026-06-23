from flask import Blueprint, jsonify, request

from backend.api.routes.categories import category_to_dict
from backend.api.routes.tags import tag_to_dict
from backend.core.exceptions import ExpenseNotFoundError
from backend.database.session import session_maker
from backend.models.expense import Expense
from backend.services.expense_service import ExpenseService

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


def expense_to_dict(expense: Expense) -> dict:
    expense_dict = {
        "id": expense.id,
        "amount": expense.amount,
        "description": expense.description,
        "expense_date": expense.description,
        "category_id": expense.description,
        "category": category_to_dict(expense.category),
        "tags": [
            tag_to_dict(tag) for tag in expense.tags
        ]
    }
    return expense_dict


@expenses_bp.get("")
def get_expenses():
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    with session_maker() as session:
        service = ExpenseService(session)
        expenses = service.get_list(limit=limit, offset=offset)

    return jsonify([
        expense_to_dict(expense) for expense in expenses
    ]), 200


@expenses_bp.post("")
def create_expense():
    create_data = request.get_json(silent=True) or {}

    with session_maker() as session:
        service = ExpenseService(session)
        expense = service.create_expense(create_data)

    return jsonify(category_to_dict(expense)), 201


@expenses_bp.get("/<int:expense_id>")
def get_expense(expense_id: int):
    with session_maker() as session:
        service = ExpenseService(session)
        try:
            expense = service.get_by_id(expense_id)
        except ExpenseNotFoundError:
            return jsonify({"error": "Expense not found"}), 404
    return jsonify(expense_to_dict(expense)), 200


@expenses_bp.patch("/<int:expense_id>")
def update_expense(expense_id: int):
    update_data = request.get_json(silent=True) or {}

    with session_maker() as session:
        service = ExpenseService(session)
        try:
            updated_expense = service.update_expense(expense_id, update_data)
        except ExpenseNotFoundError:
            return jsonify({"error": "Expense not found"}), 404
        except Exception:
            return jsonify({"error": "Bad request"}), 400

    return jsonify(expense_to_dict(updated_expense)), 200


@expenses_bp.delete("/<int:expense_id>")
def delete_expense(expense_id: int):
    with session_maker() as session:
        service = ExpenseService(session)
        try:
            service.delete_expense(expense_id)
        except ExpenseNotFoundError:
            return jsonify({"error": "Expense not found"}), 404
    return jsonify({"success": "Expense deleted successfully"}), 200
