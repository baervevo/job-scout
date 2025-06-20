from itertools import chain
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.company import Company as CompanySchema
from src.db.schemas.listing import Listing as ListingSchema
from src.db.session import async_session_maker
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.query import Query
from src.processing.listing_processor import ListingProcessor
from src.scraping.query_managers.query_manager import QueryManager
from src.scraping.scrapers.listing_scraper import ListingScraper


class ScrapingManager:
    _scraper: ListingScraper
    _query_manager: QueryManager
    _listing_processor: ListingProcessor

    def __init__(
        self,
        scraper: ListingScraper,
        query_manager: QueryManager,
        listing_processor: ListingProcessor
    ):
        self._scraper = scraper
        self._query_manager = query_manager
        self._listing_processor = listing_processor

    async def run_scraper(self) -> None:    
        async def process_query(query: Query) -> List[ListingKeywordData]:
            listings = await self._scraper.execute_query(query)
            if not listings:
                return []
            processed_listings = self._listing_processor.process_listings(listings)
            return processed_listings

        results = [await process_query(query) for query in self._query_manager.get_queries()]
        flattened_results = list(chain.from_iterable(results))
        if not flattened_results:
            return
        async with async_session_maker() as db_session:
            await self._save_listings_keyword_data(
                flattened_results, db_session
            )

    async def _save_listings_keyword_data(
        self,
        data: List[ListingKeywordData],
        db_session: AsyncSession
    ) -> None:
        if not data:
            return
        for listing_data in data:
            db_session.add(
                await self._row_from_listing_keyword_data(listing_data, db_session)
            )
        await db_session.commit()

    async def _row_from_listing_keyword_data(
        self,
        data: ListingKeywordData, 
        db_session: AsyncSession
    ) -> ListingSchema:
        result = await db_session.execute(
            select(CompanySchema).filter_by(name=data.company)
        )
        company = result.scalars().first()
        if not company:
            company = CompanySchema(name=data.company)
            db_session.add(company)
            await db_session.commit()
            await db_session.refresh(company)
        data = data.model_dump(exclude={"company"}, exclude_unset=True)
        data["company_id"] = company.id
        return ListingSchema(**data)
    