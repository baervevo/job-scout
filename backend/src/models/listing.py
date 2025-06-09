from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Listing(BaseModel):
    internal_id: Optional[str] = None
    title: str
    company: str
    description: str
    remote: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    link: Optional[str] = None
