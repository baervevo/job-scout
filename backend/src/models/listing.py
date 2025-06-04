from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Listing(BaseModel):
    internal_id: Optional[str]
    title: str
    company: str
    description: str
    remote: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    salary_min: Optional[float]
    salary_max: Optional[float]
    currency: Optional[str]
    location: Optional[str]
    link: Optional[str]
    