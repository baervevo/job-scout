from itertools import chain
from typing import List, Callable

from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.query import Query
from src.scraping.query_managers.query_manager import QueryManager
from src.scraping.scrapers.listing_scraper import ListingScraper

from src.processing.listing_processor import ListingProcessor

class ScrapingManager:
    _scraper: ListingScraper
    _query_manager: QueryManager
    _listing_processor: ListingProcessor
    _listing_callbacks: List[Callable[[ListingKeywordData], None]]

    def __init__(
        self,
        scraper: ListingScraper,
        query_manager: QueryManager,
        listing_processor: ListingProcessor
    ):
        self._scraper = scraper
        self._query_manager = query_manager
        self._listing_processor = listing_processor
        self._listing_callbacks = []

    async def run_scraper(self) -> None:    
        async def process_query(query: Query) -> List[ListingKeywordData]:
            listings = await self._scraper.execute_query(query)
            if not listings:
                return []
            return self._listing_processor.process_listings(listings)

        results = [await process_query(query) for query in self._query_manager.get_queries()]
        flattened_results = list(chain.from_iterable(results))
        if not flattened_results:
            return
        for callback in self._listing_callbacks:
            map(callback, flattened_results)

    def register_listing_callback(self, callback: Callable[[ListingKeywordData], None]) -> None:
        self._listing_callbacks.append(callback)
    