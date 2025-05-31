from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    name: str
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class PredictInputData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class PredictionData(BaseModel):
    id: int
    input_data: List[PredictInputData]
    result: List[str]
    credits_deducted: int
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
