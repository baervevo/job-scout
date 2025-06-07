from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProcessedListing(BaseModel):
    internal_id: Optional[str]
    title: str
    company: str
    description: str
    required_qualifications: List[str]
    preferred_qualifications: List[str]
    experience: List[str]
    education: List[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    currency: Optional[str]
    location: Optional[str]
    remote: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    link: Optional[str]
