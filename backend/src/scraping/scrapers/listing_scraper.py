from abc import ABC, abstractmethod
from typing import List

from backend.src.models.listing.listing import Listing
from backend.src.models.query import Query

class ListingScraper(ABC):
    @abstractmethod
    async def execute_query(self, query: Query) -> List[Listing]:
        raise NotImplementedError
