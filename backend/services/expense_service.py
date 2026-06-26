
from datetime import date
from decimal import Decimal

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


class ExpenseService:
    def __init__(self, session: Session):
        self.session = session
        self.expense_repo = ExpenseRepository(session)
        self.category_repo = CategoryRepository(session)
        self.tag_repo = TagRepository(session)

    def create_expense(self,
                       amount: Decimal,
                       description: str,
                       expense_date: date,
                       category_id: int,
                       tag_ids: list
                       ) -> Expense:
        try:
            category = self.category_repo.get_by_id(category_id)
            if category is None:
                raise CategoryNotFoundError
        except CategoryNotFoundError:
            raise

        try:
            tags = self.tag_repo.get_by_ids(tag_ids)
            if len(tags) != len(set(tag_ids)):
                raise TagNotFoundError
        except TagNotFoundError:
            raise
        try:
            expense = self.expense_repo.create(
                amount=amount,
                description=description,
                expense_date=expense_date,
                category=category,
                tags=tags,
            )
            self.session.commit()
            return expense
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, expense_id: int) -> Expense:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(f"Expense with id {expense_id} not found")
        return expense

    def get_list(self, limit: int = 100, offset: int = 0) -> list[Expense]:
        expenses = self.expense_repo.get_list(limit, offset)
        return expenses

    def update_expense(self, expense_id: int, update_data: dict) -> Expense:
        try:
            expense = self.get_by_id(expense_id)

            category = None
            if "category_id" in update_data:
                category = self.category_repo.get_by_id(update_data['category_id'])

                if category is None:
                    raise CategoryNotFoundError(
                        f"Category with id {update_data['category_id']} not found"
                    )

            tags = None
            if "tag_ids" in update_data:
                tag_ids = update_data['tag_ids'] or []
                tags = self.tag_repo.get_by_ids(tag_ids)

                if len(tags) != len(set(tag_ids)):
                    raise TagNotFoundError("One or more tags not found")

            updated_expense = self.expense_repo.update(
                expense=expense,
                update_data=update_data,
                category=category,
                tags=tags,
            )

            self.session.commit()
            return updated_expense

        except Exception:
            self.session.rollback()
            raise

    def delete_expense(self, expense_id: int) -> None:
        try:
            expense = self.get_by_id(expense_id)
            self.expense_repo.delete(expense)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
