from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    isadmin = Column(Boolean, default=False, nullable=False)
    isActive = Column(Boolean, default=True, nullable=False)
    deleteTime = Column(DateTime, nullable=True)
    
    
class loginlog(Base):
    __tablename__ = "loginlogs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String , nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    


