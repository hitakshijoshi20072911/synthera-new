from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from datetime import datetime
from typing import List
import uuid
class User(SQLModel, table=True):
    email : str = Field(primary_key=True)
    created_at : datetime = Field(default_factory=datetime.utcnow)
    chat_history : List["ChatHistory"] = Relationship(back_populates="user")     

class ChatHistory(SQLModel, table=True):
    id : str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_email = Field(foreign_key = "user.email")
    user : List["User"] = Relationship(back_populates="chat_history")
    file_key : str
    data : dict =Field(sa_column= Column(JSON))
    timestamp: datetime = Field(default_factory= datetime.utcnow)
    sources_links:List[str] = Field(default_factory=list, sa_column= Column(JSON))
    

