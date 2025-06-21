from src.db.session import async_session_maker
from src.db.schemas.resume import Resume as ResumeSchema

from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.query import Query
from src.scraping.scraper_registry import get_query_manager

from src.utils.logger import logger

from sqlalchemy import select

async def update_resume_keywords(resume: ResumeKeywordData) -> None:
    async with async_session_maker() as db_session:
        result = await db_session.execute(
            select(ResumeSchema).filter(ResumeSchema.id == resume.id)
        )
        existing_resume = result.scalars().first()
        if existing_resume:
            existing_resume.keywords = resume.keywords
            existing_resume.embedding = ",".join(resume.embedding) if resume.embedding else None
            
            await db_session.commit()
            await db_session.refresh(existing_resume)
            logger.info(f"Updated keywords for resume ID {resume.id}.")
            return
        logger.error(f"Resume with ID {resume.id} not found in the database.")

        
async def generate_query(
    resume: ResumeKeywordData,
) -> list[str]:
    query = Query(
        keywords=resume.keywords,
    )
    get_query_manager().add_query(query)

async def enqueue_matches(
    resume: ResumeKeywordData,
) -> None:
    from src.matching.matching_queue import get_matching_queue
    from src.models.listing.listing_keyword_data import ListingKeywordData
    from src.db.schemas.listing import Listing as ListingSchema
    from src.db.session import async_session_maker

    listings = []
    async with async_session_maker() as db_session:
        result = db_session.query(ListingSchema).all()
        try:
            listings = [
                ListingKeywordData(
                    id=listing.id,
                    title=listing.title,
                    company=listing.company.name if listing.company else None,
                    keywords=listing.keywords,
                    embedding=[float(x) for x in listing.embedding.split(",")] if listing.embedding else None,
                ) for listing in result
            ]
        except Exception as e:
            logger.error(f"Error processing listings: {e}")
            return
    for listing in listings:
        get_matching_queue().enqueue(resume, listing)