from sqlmodel import SQLModel, Field 
from typing import Optional, List
# from models.user import User


# class Event():
#     def __init__(self, id: int, title: str,
#                  description: str, creator: User,
#                  image: Optional[str] = None) -> None:
#         self.id = id
#         self.title = title
#         self.image = image
#         self.description = description
#         self.creator = creator

#     def __str__(self) -> str:
#         result = (f"id: {self.id} \n"
#                   f"title: {self.title} \n"
#                   f"creator: {self.creator.email}")

#         return result

class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str 
    image: str 
    description: str 
    creator: Optional[str]
    
class EventUpdate(SQLModel): 
    title: Optional[str] 
    image: Optional[str] 
    description: Optional[str] 
    tags: Optional[List[str]] 
    location: Optional[str]