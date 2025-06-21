from typing import Optional, List

from pydantic import BaseModel


class KeywordData(BaseModel):
    id: Optional[int]
    keywords: List[str]
    embedding: List[float]
