from abc import ABC, abstractmethod

from typing import Generator

from backend.src.models.query import Query

class QueryManager(ABC):
    """
    Abstract base class for managing queries in a scraping context.
    This class defines the interface for adding, removing, and retrieving queries.
    It is intended to be extended by concrete implementations that handle specific 
    query storage and/or "compression" mechanisms.
    """
    @abstractmethod
    def add_query(self, query: Query) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_query(self, query: Query) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_queries(self) -> Generator[Query, None, None]:
        raise NotImplementedError