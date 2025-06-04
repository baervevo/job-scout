from src.utils.logger import logger

from src.scraping.query_managers.query_manager import QueryManager
from src.scraping.scrapers.listing_scraper import ListingScraper

from src.models.listing import Listing
from src.db.schemas.listing import Listing as ListingSchema

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

class ScrapingManager:
    _db_session: AsyncSession
    _scraper: ListingScraper
    _query_manager: QueryManager

    def __init__(
        self,
        scraper: ListingScraper,
        db_session: AsyncSession,
        query_manager: QueryManager
    ):
        self._db_session = db_session
        self._scraper = scraper
        self._query_manager = query_manager

    async def run_scraper(self) -> None:
        for query in self._query_manager.get_queries():
            listings = await self._scraper.execute_query(query)
            if listings:
                await self._save_listings(listings)

    async def _save_listings(self, listings: List[Listing]) -> None:
        if not listings:
            return
        for listing in listings:
            data = listing.model_dump(exclude_unset=True)
            row: ListingSchema = ListingSchema(**data)
            self._db_session.add(row)
        logger.info(f"Saved {len(listings)} listings to the database.")
        await self._db_session.commit()
