from sqlmodel import SQLModel, Field, Relationship, Column, JSON, create_engine, Session
from datetime import datetime
from typing import List, Annotated, Optional
import uuid
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()
class User(SQLModel, table=True):
    email : str = Field(primary_key=True)
    created_at : datetime = Field(default_factory=datetime.utcnow)
    chat_history : List["ChatHistory"] = Relationship(back_populates="user")     

class ChatHistory(SQLModel, table=True):
    id : str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_email:str = Field(foreign_key = "user.email")
    user : Optional["User"] = Relationship(back_populates="chat_history")
    file_key : str
    data : dict =Field(sa_column= Column(JSON))
    timestamp: datetime = Field(default_factory= datetime.utcnow)
    sources_links:List[str] = Field(default_factory=list, sa_column= Column(JSON))

NEON_URL = os.getenv("NEON_URL")
engine = create_engine(NEON_URL, echo=True)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
    

