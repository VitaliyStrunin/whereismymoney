from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.schemas.category import CategoryResponseDTO
from backend.schemas.tags import TagResponseDTO

PositiveId = Annotated[int, Field(gt=0)]


class ExpenseListQueryDTO(BaseModel):
    limit: int = Field(default=100, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ExpenseCreateDTO(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    description: str = Field(default="", max_length=255)
    expense_date: date
    category_id: PositiveId = Field(gt=0)
    tag_ids: list[PositiveId] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdateDTO(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    description: str | None = Field(default=None, max_length=255)
    expense_date: date | None = None
    category_id: PositiveId | None = Field(default=None, gt=0)
    tag_ids: list[PositiveId] | None = Field(default=None)

    @field_validator("category_id", "tag_ids")
    @classmethod
    def explicit_null_not_allowed(cls, value):
        if value is None:
            raise ValueError("field may not be null")
        return value

class ExpenseResponseDTO(BaseModel):
    id: int
    amount: Decimal
    description: str
    expense_date: date
    category_id: int
    category: CategoryResponseDTO
    tags: list[TagResponseDTO]

    model_config = ConfigDict(from_attributes=True)
