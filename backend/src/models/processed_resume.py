from typing import Optional, List

from pydantic import BaseModel


class ProcessedResume(BaseModel):
    skills: List[str]
    experience: List[str]
    education: List[str]
    certifications: List[str]
