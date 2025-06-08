from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.company import Company as CompanySchema
from src.db.schemas.listing import Listing as ListingSchema
from src.db.session import async_session_maker
from src.listing_processing.ollama_listing_processor import OllamaListingProcessor
from src.models.listing import Listing
from src.scraping.query_managers.query_manager import QueryManager
from src.scraping.scrapers.listing_scraper import ListingScraper


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

                processor = OllamaListingProcessor()
                processed_listings = await processor.process_listings(listings)
                # TODO: save processed listings

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
