from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.category import CategoryResponseDTO
from backend.schemas.tags import TagResponseDTO


class ExpenseListQueryDTO(BaseModel):
    limit: int = Field(default=100, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ExpenseCreateDTO(BaseModel):
    amount: Decimal = Field(gt=0)
    description: str = Field(default="", max_length=255)
    expense_date: date
    category_id: int = Field(gt=0)
    tag_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdateDTO(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=255)
    expense_date: date | None = None
    category_id: int | None = Field(default=None, gt=0)
    tag_ids: list[int] | None = Field(default=None)


class ExpenseResponseDTO(BaseModel):
    id: int
    amount: Decimal
    description: str
    expense_date: date
    category_id: int
    category: CategoryResponseDTO
    tags: list[TagResponseDTO]

    model_config = ConfigDict(from_attributes=True)
