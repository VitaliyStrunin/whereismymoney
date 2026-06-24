
from sqlalchemy.orm import Session

from backend.core.exceptions import (
    CategoryNotFoundError,
    ExpenseNotFoundError,
    TagNotFoundError,
)
from backend.models.expense import Expense
from backend.repositories.category_repository import CategoryRepository
from backend.repositories.expense_repository import ExpenseRepository
from backend.repositories.tag_repository import TagRepository
from backend.schemas.expense import UpdateExpenseDTO


class ExpenseService:
    def __init__(self, session: Session):
        self.session = session
        self.expense_repo = ExpenseRepository(session)
        self.category_repo = CategoryRepository(session)
        self.tag_repo = TagRepository(session)

    def create_expense(self,
                       create_data: dict
                       ) -> Expense:
        try:
            category = self.category_repo.get_by_id(create_data.get("category_id"), -1)
            if category is None:
                raise CategoryNotFoundError
        except CategoryNotFoundError:
            raise

        try:
            tag_ids = create_data.get("tag_ids", [])
            tags = self.tag_repo.get_by_ids(tag_ids)
            if len(tags) != len(set(tag_ids)):
                raise TagNotFoundError
        except TagNotFoundError:
            raise

        expense = self.expense_repo.create(
            amount=create_data.amount,
            description=create_data.description,
            expense_date=create_data.expense_date,
            category=category,
            tags=tags,
        )
        self.session.commit()

        return expense

    def get_by_id(self, expense_id: int) -> Expense:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(f"Expense with id {expense_id} not found")
        return expense

    def get_list(self, limit: int = 100, offset: int = 0) -> list[Expense]:
        expenses = self.expense_repo.get_list(limit, offset)
        return expenses

    def update_expense(self, expense_id: int, update_data: dict):
        try:
            expense = self.get_by_id(expense_id)
        except ExpenseNotFoundError:
            raise
        update_data = UpdateExpenseDTO.model_validate(update_data)
        updated_expense = self.expense_repo.update(expense, update_data)
        self.session.commit()
        return updated_expense

    def delete_expense(self, expense_id: int) -> None:
        try:
            expense = self.get_by_id(expense_id)
            self.expense_repo.delete(expense)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
