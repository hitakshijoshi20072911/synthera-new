from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
engine=create_engine(DATABASE_URL)
sessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()
class Users(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, nullable=False)
    username=Column(String, unique=True)
    password=Column(String)
    isactive=Column(Boolean, default=False, nullable=False)

class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"
    id=Column(Integer, primary_key=True, index=True)
    user_username= Column(ForeignKey("users.username", ondelete="CASCADE"))
    token_hash= Column(String, unique=True)
    expires_at=Column(DateTime)
    revoked=Column(Boolean, default=False, nullable=False)


Base.metadata.create_all(bind=engine)
SQLAlchemyInstrumentor().instrument(engine=engine)
