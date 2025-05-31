from pydantic import BaseModel
from sqlmodel import SQLModel, Field 
from typing import Optional, List
# from models.event import Event

# class User:
#     def __init__(self, id: int, email: str) -> None:
#         self.id = id
#         self.email = email

#     def __str__(self) -> str:
#         return f"id: {self.id}, email: {self.email}"

class User(SQLModel, table=True): 
    id: int = Field(default=None, primary_key=True)
    email: str 
    password: str
    events: Optional[str]
    
class TokenResponse(BaseModel): 
    access_token: str 
    token_type: str
    
class UserSignIn(SQLModel): 
    email: str 
    password: str