from pydantic import BaseModel, ConfigDict, Field, field_validator


class TagListQueryDTO(BaseModel):
    limit: int = Field(default=100, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class TagCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_required(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("name is required")

        return value


class TagUpdateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_required(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("name is required")

        return value


class TagResponseDTO(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
