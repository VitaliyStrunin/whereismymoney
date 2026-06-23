from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateExpenseDTO(BaseModel):
    amount: Decimal = Field(gt=0)
    description: str = Field(default="", max_length=255)
    expense_date: date
    category_id: int = Field(gt=0)
    tags: list[int] = Field(default_factory=list)


class UpdateExpenseDTO(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=255)
    expense_date: date | None
    category_id: int | None = Field(default=None, gt=0)
    tags: list[int] | None = Field(default=None)
