from typing import Optional, List

from pydantic import BaseModel


class ProcessedResume(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    summary: Optional[str]
    skills: List[str]
    experience: List[str]
    education: List[str]
    certifications: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    years_of_experience: Optional[float] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
