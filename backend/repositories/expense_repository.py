from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

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
        query = (select(Expense)
                 .where(Expense.id == expense_id)
                 .options(
                     joinedload(Expense.category),
                     selectinload(Expense.tags)
                    )
                )

        return self.session.scalar(query)

    def get_list(self, limit: int = 100, offset: int = 0) -> list[Expense]:
        query = select(Expense).order_by(Expense.id).limit(limit).offset(offset)
        return list(self.session.scalars(query))

    def update(
        self,
        expense: Expense,
        update_data: UpdateExpenseDTO,
        category: Category | None = None,
        tags: list[Tag] | None = None,
    ) -> Expense:
        update_fields = update_data.model_dump(exclude_unset=True)

        simple_fields = {"amount", "description", "expense_date"}

        for field, value in update_fields.items():
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
