from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.base import Base

class StoredQuery(Base):
    __tablename__ = 'stored_queries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    keywords = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    radius = Column(String, nullable=True)
    salary = Column(Integer, nullable=True)