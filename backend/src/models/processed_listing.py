from datetime import datetime
from enum import Enum
from typing import List, Dict

from pydantic import BaseModel


class SkillType(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    DESCRIPTION = "description"
    TITLE = "title"
    COMPANY = "company"
    EXPERIENCE = "experience"


class ExtractedKeyword(BaseModel):
    text: str
    type: SkillType
    source_field: str
    importance: float = 1.0
    frequency: int = 1


class ProcessedListing(BaseModel):
    internal_id: str
    keywords: List[ExtractedKeyword]
    metadata: Dict
    processed_at: datetime
