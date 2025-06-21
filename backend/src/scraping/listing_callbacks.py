from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.db.session import async_session_maker
from src.db.schemas.company import Company as CompanySchema
from src.db.schemas.listing import Listing as ListingSchema

from src.models.listing.listing_keyword_data import ListingKeywordData

from src.utils.logger import logger
from src.utils.pdf import extract_text_from_pdf

async def log_listing_keywords(
    listing: ListingKeywordData,
) -> None:
    from src.utils.logger import logger
    logger.info(f"Listing keywords: {listing.keywords}")

async def process_and_commit_listing(listing: ListingKeywordData) -> None:
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
        dumped = data.model_dump(exclude={"company", "keywords", "embedding"}, exclude_unset=True)
        dumped["company_id"] = company.id
        dumped["keywords"] = ",".join(data.keywords) if data.keywords else None
        dumped["embedding"] = ",".join(map(str, data.embedding)) if data.embedding else None
        return ListingSchema(**dumped)
    
    async with async_session_maker() as db_session:
        try:
            db_session.add(
                await _row_from_listing_keyword_data(listing, db_session)
            )
            await db_session.commit()
        except IntegrityError as e:
            await db_session.rollback()

async def enqueue_matches(listing: ListingKeywordData) -> None:
    from src.matching.matching_queue import get_matching_queue
    from src.models.resume.resume_keyword_data import ResumeKeywordData
    from src.db.schemas.resume import Resume as ResumeSchema
    from src.db.session import async_session_maker

    resumes = []
    async with async_session_maker() as db_session:
        result = await db_session.execute(
            select(ResumeSchema)
        )
        resumes = result.scalars().all()
    for resume in resumes:
        kw_data = ResumeKeywordData(
            id=resume.id,
            user_id=resume.user_id,
            file_name=resume.file_name,
            file_path=resume.file_path,
            content=extract_text_from_pdf(resume.file_path) if resume.file_path else "",
            keywords=resume.keywords.split(",") if resume.keywords else [],
            embedding=list(map(float, resume.embedding.split(","))) if resume.embedding else []
        )
        get_matching_queue().enqueue(kw_data, listing)
