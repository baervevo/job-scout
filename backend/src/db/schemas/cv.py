from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship

from src.db.base import Base

class CV(Base):
    __tablename__ = 'cvs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(String, server_default=func.now())

    user = relationship("User", back_populates="cv")
