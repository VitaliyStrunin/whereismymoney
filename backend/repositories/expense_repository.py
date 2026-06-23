from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.models.expense import Expense
from backend.models.tag import Tag
from backend.schemas.expense import UpdateExpenseDTO

_NOT_SET = object()


class ExpenseRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self,
               amount: Decimal,
               description: str,
               expense_date: date,
               category: Category,
               tags: list[Tag],
               ) -> Expense:
        expense = Expense(
            amount=amount,
            description=description,
            expense_date=expense_date,
            category=category,
            tags=tags,
        )
        self.session.add(expense)
        self.session.flush()
        return expense

    def get_by_id(self, expense_id: int) -> Expense | None:
        expense = self.session.get(Expense, expense_id)
        return expense

    def get_list(self, limit: int = 100, offset: int = 0) -> list[Expense]:
        query = select(Expense).order_by(Expense.id).limit(limit).offset(offset)
        return list(self.session.scalars(query))

    def update(self, expense: Expense, update_data: UpdateExpenseDTO) -> Expense:
        update_fields = update_data.model_dump(mode="json", exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(expense, field):
                setattr(expense, field, value)
            else:
                raise ValueError(f"Invalid field: {field}")

        self.session.flush()
        return expense

    def delete(self, expense: Expense) -> None:
        self.session.delete(expense)
        self.session.flush()
