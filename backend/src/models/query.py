from pydantic import BaseModel
from typing import Tuple, Optional

class Query(BaseModel):
    keywords: Tuple[str, ...]
    location: Optional[str]
    radius: Optional[str] = None
    salary: Optional[int] = None

    class Config:
        frozen = True