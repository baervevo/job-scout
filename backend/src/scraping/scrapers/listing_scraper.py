from abc import ABC, abstractmethod
from typing import List

from src.models.listing import Listing
from src.models.query import Query
from src.utils.http import HTTPClient

class ListingScraper(ABC):
    @abstractmethod
    def add_query(self, query: Query) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def remove_query(self, query: Query) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def get_newest_results(self) -> List[Listing]:
        raise NotImplementedError
    
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError 

    
class RestAPIListingScraper(ListingScraper):
    _http_client: HTTPClient

    def __init__(self, host: str):
        self._http_client = HTTPClient(host)
