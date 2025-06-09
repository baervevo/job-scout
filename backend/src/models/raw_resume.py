from typing import Optional, List

from pydantic import BaseModel


class RawResume(BaseModel):
    internal_id: Optional[str]
    content: str
