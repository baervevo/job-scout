from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship

from src.db.base import Base

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False)
    missing_keywords = Column(String, nullable=False)
    cosine_similarity = Column(Float, nullable=False)
    summary = Column(String, nullable=True)

    resume = relationship("User", back_populates="matches")
    listing = relationship("Listing", back_populates="matches")