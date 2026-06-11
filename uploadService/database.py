from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
engine=create_engine(DATABASE_URL)
sessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()
class Files(Base):
    __tablename__ = "files"
    id=Column(Integer, primary_key=True, index=True)
    user=Column(String)
    file_key=Column(String, unique=True, nullable=False)
    timestamp=Column(DateTime, server_default=func.now(), onupdate=func.now())

Base.metadata.create_all(bind=engine)
SQLAlchemyInstrumentor().instrument(engine=engine)
    
