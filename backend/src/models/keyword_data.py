from typing import Optional, List

from pydantic import BaseModel


class KeywordData(BaseModel):
    internal_id: Optional[str]
    keywords: List[str]
    embedding: List[float]
