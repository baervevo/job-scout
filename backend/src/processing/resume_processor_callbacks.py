from src.db.session import async_session_maker
from src.db.schemas.resume import Resume as ResumeSchema

from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.query import Query
from src.scraping.scraper_registry import get_query_manager

from src.utils.logger import logger

from sqlalchemy import select

async def update_resume_keywords(resume: ResumeKeywordData) -> None:
    try:
        async with async_session_maker() as db_session:
            async with db_session.begin():
                result = await db_session.execute(
                    select(ResumeSchema).filter(ResumeSchema.id == resume.id)
                )
                existing_resume = result.scalars().first()
                if existing_resume is not None:
                    existing_resume.keywords = ",".join(resume.keywords) if resume.keywords else ""
                    existing_resume.embedding = ",".join(map(str, resume.embedding)) if resume.embedding else ""
                    await db_session.commit()
                    await db_session.refresh(existing_resume)
                    logger.info(f"Updated keywords for resume ID {resume.id}: {len(resume.keywords)} keywords")
                    return
                logger.error(f"Resume with ID {resume.id} not found in the database.")
    except Exception as e:
        logger.error(f"Error updating resume keywords for {resume.id}: {str(e)}")

        
async def generate_query(resume: ResumeKeywordData) -> None:
    try:
        if not resume.keywords:
            logger.warning(f"No keywords available for resume {resume.id}, skipping query generation")
            return
        top_keywords = resume.keywords
        query = Query(
            keywords=tuple(top_keywords),
            location=None,
        )
        logger.info(f"Generated query for resume {resume.id}: {query}")
        query_manager = get_query_manager()
        query_manager.add_query(query)
        active_queries = list(query_manager.get_queries())
        logger.info(f"Total active queries after adding: {len(active_queries)}")
        for i, q in enumerate(active_queries):
            logger.info(f"Query {i+1}: keywords={q.keywords}, location={q.location}")
            
    except Exception as e:
        logger.error(f"Error generating query for resume {resume.id}: {str(e)}")

async def enqueue_matches(resume: ResumeKeywordData) -> None:
    try:
        if not resume.keywords or not resume.embedding:
            logger.warning(f"Resume {resume.id} missing keywords or embedding, skipping match enqueuing")
            return
        from src.matching.matching_queue import get_matching_queue
        from src.models.listing.listing_keyword_data import ListingKeywordData
        from src.db.schemas.listing import Listing as ListingSchema
        from src.db.schemas.company import Company as CompanySchema
        from src.db.session import async_session_maker
        processed_count = 0
        error_count = 0
        async with async_session_maker() as db_session:
            result = await db_session.execute(
                select(ListingSchema, CompanySchema)
                .join(CompanySchema, ListingSchema.company_id == CompanySchema.id)
                .filter(
                    ListingSchema.keywords.isnot(None),
                    ListingSchema.embedding.isnot(None)
                )
            )
            listing_data = result.all()
            for listing_row, company_row in listing_data:
                try:
                    if not listing_row or not company_row:
                        logger.warning(f"Invalid listing or company data, skipping")
                        error_count += 1
                        continue
                    if not listing_row.keywords or not listing_row.embedding:
                        logger.warning(f"Listing {listing_row.id} missing keywords or embedding")
                        error_count += 1
                        continue
                    listing_kw_data = ListingKeywordData(
                        id=listing_row.id,
                        title=listing_row.title,
                        company=company_row.name,
                        description=listing_row.description,
                        remote=listing_row.remote,
                        created_at=listing_row.created_at,
                        updated_at=listing_row.updated_at,
                        salary_min=listing_row.salary_min,
                        salary_max=listing_row.salary_max,
                        currency=listing_row.currency,
                        location=listing_row.location,
                        link=listing_row.link,
                        keywords=listing_row.keywords.split(",") if listing_row.keywords else [],
                        embedding=[float(x) for x in listing_row.embedding.split(",")] if listing_row.embedding else []
                    )
                    if not listing_kw_data or not listing_kw_data.keywords or not listing_kw_data.embedding:
                        logger.warning(f"Created listing object {listing_row.id} is invalid, skipping")
                        error_count += 1
                        continue
                    get_matching_queue().enqueue(resume, listing_kw_data)
                    processed_count += 1
                except Exception as listing_error:
                    logger.error(f"Error processing listing {listing_row.id if listing_row else 'Unknown'}: {str(listing_error)}")
                    error_count += 1
                    continue
            logger.info(f"Enqueued matches for resume {resume.id}: {processed_count} successful, {error_count} errors")
    except Exception as e:
        logger.error(f"Error enqueuing matches for resume {resume.id}: {str(e)}")