from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.company import Company as CompanySchema
from src.db.schemas.listing import Listing as ListingSchema
from src.db.session import async_session_maker
from src.listing_processing.listing_processor import ListingProcessor
from src.models.listing import Listing
from src.models.processed_listing import ProcessedListing
from src.scraping.query_managers.query_manager import QueryManager
from src.scraping.scrapers.listing_scraper import ListingScraper
from src.utils.logger import logger


class ScrapingManager:
    _scraper: ListingScraper
    _query_manager: QueryManager

    def __init__(
            self,
            scraper: ListingScraper,
            query_manager: QueryManager
    ):
        self._scraper = scraper
        self._query_manager = query_manager

    async def run_scraper(self) -> None:
        async with async_session_maker() as db_session:
            for query in self._query_manager.get_queries():
                listings = await self._scraper.execute_query(query)

                # TODO: save processed listings
                processed_listings = await self.transform_to_processed_listings(listings)

                if listings:
                    await self._save_listings(listings, db_session)

    async def _save_listings(self, listings: List[Listing], db_session: AsyncSession) -> None:
        if not listings:
            return
        for listing in listings:
            db_session.add(await self._row_from_listing(listing, db_session))
        await db_session.commit()

    async def _row_from_listing(self, listing: Listing, db_session: AsyncSession) -> ListingSchema:
        result = await db_session.execute(
            select(CompanySchema).filter_by(name=listing.company)
        )
        company = result.scalars().first()
        if not company:
            company = CompanySchema(name=listing.company)
            db_session.add(company)
            await db_session.commit()
            await db_session.refresh(company)
        data = listing.model_dump(exclude={"company"}, exclude_unset=True)
        data["company_id"] = company.id
        return ListingSchema(**data)

    async def transform_to_processed_listings(self, listings: List[Listing]) -> List[ProcessedListing]:
        """
        Transforms a list of Listing objects into a list of ProcessedListing objects.
        """
        processor = ListingProcessor()
        processed_listings = []
        for listing in listings:
            logger.info(f"Processing raw listing: {listing.internal_id}")
            logger.debug(listing)
            processed = await processor.process_listing(listing)
            logger.info(f"Finished processing listing: {processed.internal_id} with keywords: {processed.keywords}")
            processed_listings.append(processed)
        return processed_listings
