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

async def process_and_commit_listing(listing: ListingKeywordData) -> ListingKeywordData:
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
            listing_schema = await _row_from_listing_keyword_data(listing, db_session)
            db_session.add(listing_schema)
            await db_session.commit()
            await db_session.refresh(listing_schema)
            updated_listing = ListingKeywordData(
                id=listing_schema.id,
                keywords=listing.keywords,
                embedding=listing.embedding,
                title=listing.title,
                company=listing.company,
                description=listing.description,
                remote=listing.remote,
                created_at=listing.created_at,
                updated_at=listing.updated_at,
                salary_min=listing.salary_min,
                salary_max=listing.salary_max,
                currency=listing.currency,
                location=listing.location,
                link=listing.link
            )
            logger.info(f"Listing saved to database with ID: {updated_listing.id}")
            return updated_listing
        except IntegrityError as e:
            await db_session.rollback()
            logger.error(f"Failed to save listing: {str(e)}")
            return listing

async def enqueue_matches(listing: ListingKeywordData) -> ListingKeywordData:
    from src.matching.matching_queue import get_matching_queue
    from src.models.resume.resume_keyword_data import ResumeKeywordData
    from src.db.schemas.resume import Resume as ResumeSchema
    from src.db.session import async_session_maker
    
    if listing.id is None:
        logger.warning(f"Skipping match enqueuing for listing with None ID: {listing.title}")
        return listing
    if not listing.keywords or not listing.embedding:
        logger.warning(f"Skipping match enqueuing for listing {listing.id} - missing keywords or embedding")
        return listing
    try:
        resumes = []
        async with async_session_maker() as db_session:
            result = await db_session.execute(
                select(ResumeSchema).filter(
                    ResumeSchema.keywords.isnot(None),
                    ResumeSchema.embedding.isnot(None)
                )
            )
            resumes = result.scalars().all()
        if not resumes:
            logger.debug(f"No resumes with keywords/embeddings found for matching with listing {listing.id}")
            return listing
        logger.info(f"Enqueuing matches for listing {listing.id} with {len(resumes)} resumes")
        for resume in resumes:
            try:
                kw_data = ResumeKeywordData(
                    id=resume.id,
                    user_id=resume.user_id,
                    file_name=resume.file_name,
                    file_path=resume.file_path,
                    content=extract_text_from_pdf(resume.file_path) if resume.file_path else "",
                    keywords=resume.keywords.split(",") if resume.keywords else [],
                    embedding=list(map(float, resume.embedding.split(","))) if resume.embedding else []
                )
                if kw_data.keywords and kw_data.embedding:
                    get_matching_queue().enqueue(kw_data, listing)
                else:
                    logger.debug(f"Skipping resume {resume.id} - missing keywords or embedding")
            except Exception as resume_error:
                logger.error(f"Error processing resume {resume.id} for matching: {str(resume_error)}")
                continue
    except Exception as e:
        logger.error(f"Error enqueuing matches for listing {listing.id}: {str(e)}")
    return listing