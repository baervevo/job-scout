from abc import ABC, abstractmethod
from typing import List

from src.models.listing import Listing
from src.models.query import Query

class ListingScraper(ABC):
    @abstractmethod
    async def execute_query(self, query: Query) -> List[Listing]:
        raise NotImplementedError
