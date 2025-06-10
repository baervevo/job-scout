from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")