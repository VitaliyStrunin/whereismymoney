from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateDTO(BaseModel):
    email: EmailStr
    plain_password: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(from_attributes=True)


class UserResponseDTO(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLoginDTO(BaseModel):
    email: EmailStr
    plain_password: str


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
