from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from backend.models.category import Category
from backend.models.expense import Expense
from backend.models.tag import Tag


class ExpenseRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self,
               amount: Decimal,
               description: str,
               expense_date: date,
               category: Category,
               tags: list[Tag],
               user_id: int
               ) -> Expense:
        expense = Expense(
            amount=amount,
            description=description,
            expense_date=expense_date,
            category=category,
            tags=tags,
            user_id=user_id
        )
        self.session.add(expense)
        self.session.flush()
        return expense

    def get_by_id(self, expense_id: int, user_id: int) -> Expense | None:
        query = (select(Expense)
                 .where(Expense.id == expense_id, Expense.user_id == user_id)
                 .options(
                        joinedload(Expense.category),
                        selectinload(Expense.tags),
                    )
                )

        return self.session.scalar(query)

    def get_list(self, limit: int, offset: int, user_id: int) -> list[Expense]:
        query = (select(Expense)
                 .options(
                        joinedload(Expense.category),
                        selectinload(Expense.tags),
                 )
                 .where(Expense.user_id == user_id)
                 .order_by(Expense.id)
                 .limit(limit)
                 .offset(offset)
                 )
        return list(self.session.scalars(query))

    def update(
        self,
        expense: Expense,
        update_data: dict,
        category: Category | None = None,
        tags: list[Tag] | None = None,
    ) -> Expense:
        simple_fields = {"amount", "description", "expense_date"}

        for field, value in update_data.items():
            if field in simple_fields:
                setattr(expense, field, value)

        if category is not None:
            expense.category = category

        if tags is not None:
            expense.tags = tags

        self.session.flush()
        return expense

    def delete(self, expense: Expense) -> None:
        self.session.delete(expense)
        self.session.flush()
