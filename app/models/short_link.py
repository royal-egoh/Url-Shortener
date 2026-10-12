from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

class Links(Base):
    __tablename__ = "Links"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shortcode = Column(String, unique = True)
    url = Column(String)
    accessCount = Column(Integer, default = 0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users", back_populates="my_links", cascade="all, delete") 