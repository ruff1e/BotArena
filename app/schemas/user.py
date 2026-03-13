from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=15)
    email: str = Field(min_length=5, max_length=30)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    elo_rating: int
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

