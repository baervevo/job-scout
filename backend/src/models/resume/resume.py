from typing import Optional, List

from pydantic import BaseModel


class Resume(BaseModel):
    internal_id: Optional[str] = None
    user_id: Optional[str] = None
    file_name: str
    file_path: str
    content: str
