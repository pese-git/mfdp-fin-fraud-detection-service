from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr
from sqlmodel import Field


# -------- USERS -----------

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# -------- TOKENS -----------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None


# --- Финансовый Transaction, Prediction ---

class PredictionBase(BaseModel):
    TransactionID: int
    TransactionDT: int
    TransactionAmt: float
    ProductCD: str
    card1: Optional[int] = None
    card2: Optional[int] = None
    card3: Optional[float] = None
    card4: Optional[str] = None
    card5: Optional[float] = None
    card6: Optional[str] = None
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    dist1: Optional[float] = None
    dist2: Optional[float] = None
    P_emaildomain: Optional[str] = None
    R_emaildomain: Optional[str] = None
    isFraud: Optional[bool] = None

    C: List[Optional[float]] = Field(..., min_items=14, max_items=14)
    D: List[Optional[Union[float, str]]] = Field(..., min_items=15, max_items=15)
    M: List[Optional[str]] = Field(..., min_items=9, max_items=9)
    V: List[Optional[float]] = Field(..., min_items=339, max_items=339)
    id: List[Optional[Union[str, float]]] = Field(..., min_items=27, max_items=27)


class PredictionCreate(PredictionBase):
    class Config:
        schema_extra = {
            "example": {
                "isFraud": None,
                "TransactionID": 2987000,
                "TransactionDT": 86400,
                "TransactionAmt": 68.5,
                "ProductCD": "W",
                "card1": 13926,
                "card2": None,
                "card3": 150.0,
                "card4": "discover",
                "card5": 142.0,
                "card6": "credit",
                "addr1": 315.0,
                "addr2": 87.0,
                "dist1": 19.0,
                "dist2": None,
                "P_emaildomain": None,
                "R_emaildomain": None,
                "C": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 1.0],
                "D": [14.0, None, 13.0, None, None, None, None, None, 13.0, 13.0, None, None, 0.0, 0.0, 0.0],
                "M": ["T", "M2", "F", "T", None, None, None, None, None],
                "V": [1.0 for _ in range(339)],
                "id": [None for _ in range(27)]
            }
        }


class PredictionResponse(PredictionBase):
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "isFraud": 1,
                "TransactionID": 2987000,
                "TransactionDT": 86400,
                "TransactionAmt": 68.5,
                "ProductCD": "W",
                "card1": 13926,
                "card2": None,
                "card3": 150.0,
                "card4": "discover",
                "card5": 142.0,
                "card6": "credit",
                "addr1": 315.0,
                "addr2": 87.0,
                "dist1": 19.0,
                "dist2": None,
                "P_emaildomain": None,
                "R_emaildomain": None,
                "C": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 1.0],
                "D": [14.0, None, 13.0, None, None, None, None, None, 13.0, 13.0, None, None, 0.0, 0.0, 0.0],
                "M": ["T", "M2", "F", "T", None, None, None, None, None],
                "V": [1.0 for _ in range(339)],
                "id": [None for _ in range(27)],
                'created_at': "2025-06-07 06:51:17.248"
            }
        }


class TaskResponse(BaseModel):
    task_id: str
    # status: str
    result: Optional[PredictionResponse] = None
