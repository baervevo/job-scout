from typing import Optional, List

from pydantic import BaseModel


class Match(BaseModel):
    resume_id: Optional[str] = None
    listing_id: Optional[str] = None
    missing_keywords: List[str]
    cosine_similarity: Optional[float] = None
    summary: Optional[str] = None
