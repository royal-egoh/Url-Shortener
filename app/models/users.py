from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_key  =Column(String, unique=True)
    created_at = Column(DateTime, server_default=func.now()) 
    
    my_links = relationship("Links", back_populates="owner") 
    