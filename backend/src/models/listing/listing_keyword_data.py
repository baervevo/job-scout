from datetime import datetime
from typing import Optional

from src.models.keyword_data import KeywordData


class ListingKeywordData(KeywordData):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    remote: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    link: Optional[str] = None
