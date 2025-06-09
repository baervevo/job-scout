from typing import Optional, List

from pydantic import BaseModel
from torch import Tensor


class ListingKeywords(BaseModel):
    internal_id: Optional[str]
    keywords: List[str]
    embedding: List[float]
