from pydantic import BaseModel
from typing import Tuple, Optional

class Query(BaseModel):
    keywords: Tuple[str]
    location: Optional[str]

    class Config:
        frozen = True