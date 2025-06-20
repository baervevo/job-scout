from sqlalchemy import Column, Integer, String, ForeignKey, func, DateTime
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from src.db.base import Base

class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    keywords = Column(String)
    embedding = Column(Vector(384))
    last_evaluated_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="resumes")
