

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.routes import auth, resumes

from src.utils.logger import logger

def setup_matching_queue() -> None:
    from src.matching.matching_queue import get_matching_queue
    from src.matching.matching_callbacks import log_match, commit_match_to_db
    from src.processing.matching_processor import MatchingProcessor
    
    on_match_callbacks = [
        log_match,
        commit_match_to_db
    ]
    matching_processor = MatchingProcessor()
    queue = get_matching_queue(matching_processor)
    for callback in on_match_callbacks:
        logger.info(f"Registering callback {callback.__name__} for matching queue")
        queue.register_on_match_callback(callback)
    logger.info("Matching queue setup complete with callbacks registered.")

def setup_resume_processing_queue() -> None:
    from src.processing.resume_processing_queue import get_resume_processing_queue
    from src.processing.resume_processor_callbacks import (
        update_resume_keywords,
        generate_query,
        enqueue_matches
    )

    resume_callbacks = [
        update_resume_keywords,
        generate_query,
        enqueue_matches
    ]
    queue = get_resume_processing_queue()
    for callback in resume_callbacks:
        logger.info(f"Registering callback {callback.__name__} for resume processing queue")
        queue.register_on_processed_callback(callback)
    logger.info("Resume processing queue setup complete with callbacks registered.")

def setup_scrapers() -> None:
    from src.scraping.scraper_registry import get_scraper_registry, set_query_manager, get_query_manager
    from src.scraping.listing_callbacks import (
        log_listing_keywords,
        process_and_commit_listing,
        enqueue_matches
    )
    from src.scraping.query_managers.aggregating_query_manager import AggregatingQueryManager

    set_query_manager(
        AggregatingQueryManager()
    )
    from src.models.query import Query
    get_query_manager().add_query(
        Query(
            keywords=("python", "fastapi", "asyncio"),
            location="remote",
        )
    )
    listing_callbacks = [
        process_and_commit_listing,
        enqueue_matches
    ]
    for name, manager in get_scraper_registry().items():
        for callback in listing_callbacks:
            logger.info(f"Registering callback {callback.__name__} for scraper {name}")
            manager.register_listing_callback(callback)
    logger.info("Scrapers setup complete with listing callbacks registered.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.scraping.scheduler import start_scraping_scheduler, shutdown_scraping_scheduler

    setup_scrapers()
    setup_resume_processing_queue()
    setup_matching_queue()

    start_scraping_scheduler()
    yield
    shutdown_scraping_scheduler()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])