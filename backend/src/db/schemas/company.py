from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    listings = relationship("Listing", back_populates="company")