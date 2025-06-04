from pydantic import BaseModel
from typing import Optional

class Listing(BaseModel):
    id: Optional[int]
    title: str
    company: str
    description: str
    remote: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    currency: Optional[str]
    location: Optional[str]
    link: Optional[str]
    