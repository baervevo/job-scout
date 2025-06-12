from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from src.db.base import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    internal_id = Column(String)
    title = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    description = Column(String, nullable=False)
    remote = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    salary_min = Column(Float)
    salary_max = Column(Float)
    currency = Column(String)
    location = Column(String)
    link = Column(String)
    keywords = Column(String)
    embedding = Column(Vector(1536))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="listings")
