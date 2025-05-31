from abc import ABC, abstractmethod
from typing import List

from src.models.listing import Listing
from src.models.query import Query
from src.utils.http import HTTPClient

class ListingScraper(ABC):
    @abstractmethod
    def fetch_listings(self, query: Query) -> List[Listing]:
        """
        Scrape job listings matching the query.

        Args:
            query (str): The query to match.

        Returns:
            List[Listing]: A list of job listings.
        """
        raise NotImplementedError
    
class RestAPIListingScraper(ListingScraper):
    _api_key: str
    _http_client: HTTPClient

    def __init__(self, api_key: str, host: str):
        self._api_key = api_key
        self._http_client = HTTPClient(host)

    @abstractmethod
    def fetch_listings(self, query: Query) -> List[Listing]:
        raise NotImplementedError
