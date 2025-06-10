from typing import Optional

from src.models.keyword_data import KeywordData


class ResumeKeywordData(KeywordData):
    user_id: Optional[str]
    file_name: str
    file_path: str
    content: str
