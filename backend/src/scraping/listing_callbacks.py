from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import async_session_maker
from src.db.schemas.company import Company as CompanySchema
from src.db.schemas.listing import Listing as ListingSchema

from src.models.listing.listing_keyword_data import ListingKeywordData

async def process_and_commit_listing(listings: List[ListingKeywordData]) -> None:
    async def _row_from_listing_keyword_data(
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
    
    with async_session_maker() as db_session:
        for listing_data in listings:
            db_session.add(
                await _row_from_listing_keyword_data(listing_data, db_session)
            )
        await db_session.commit()
