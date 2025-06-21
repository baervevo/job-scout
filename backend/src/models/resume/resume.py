from typing import Optional, List

from pydantic import BaseModel


class Resume(BaseModel):
    id: Optional[str] = None
    user_id: int
    file_name: str
    file_path: str
    content: Optional[str]
