"""Frontend data models - independent of backend"""
from typing import List, Optional
from datetime import datetime


class Match:
    def __init__(self, id: int, resume_id: int, listing_id: int, missing_keywords: List[str], 
                 cosine_similarity: float, summary: Optional[str] = None, matched_at: Optional[str] = None):
        self.id = id
        self.resume_id = resume_id
        self.listing_id = listing_id
        self.missing_keywords = missing_keywords
        self.cosine_similarity = cosine_similarity
        self.summary = summary
        self.matched_at = matched_at


class ListingKeywordData:
    def __init__(self, id: int, title: str, company: str, description: str = "",
                 remote: bool = False, location: str = "", salary_min: Optional[float] = None,
                 salary_max: Optional[float] = None, currency: Optional[str] = None,
                 link: str = "", keywords: Optional[List[str]] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.id = id
        self.title = title
        self.company = company
        self.description = description
        self.remote = remote
        self.location = location
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.currency = currency
        self.link = link
        self.keywords = keywords or []
        self.created_at = created_at
        self.updated_at = updated_at


class Resume:
    def __init__(self, id: int, user_id: int, file_name: str, uploaded_at: Optional[str] = None,
                 keywords: Optional[List[str]] = None, location: Optional[str] = None, 
                 radius: Optional[int] = None):
        self.id = id
        self.user_id = user_id
        self.file_name = file_name
        self.uploaded_at = uploaded_at
        self.keywords = keywords or []
        self.location = location
        self.radius = radius