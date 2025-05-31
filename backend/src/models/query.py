from pydantic import BaseModel
from typing import List, Optional

class Query(BaseModel):
	keywords: List[str]
	location: Optional[str]