from fastapi import FastAPI
from contextlib import asynccontextmanager

from starlette.middleware.sessions import SessionMiddleware

from src.routes import auth, resumes, matches

from src.utils.logger import logger

async def setup_matching_queue() -> None:
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
    await queue.start()
    logger.info("Matching queue setup complete with callbacks registered and started.")

async def setup_resume_processing_queue() -> None:
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
    await queue.start()
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
    from backend.src.models.query import Query
    get_query_manager()
    listing_callbacks = [
        process_and_commit_listing,
        enqueue_matches
    ]
    for name, manager in get_scraper_registry().items():
        for callback in listing_callbacks:
            logger.info(f"Registering callback {callback.__name__} for scraper {name}")
            manager.register_listing_callback(callback)
    logger.info("Scrapers setup complete with listing callbacks registered.")

async def stop() -> None:
    from src.processing.resume_processing_queue import get_resume_processing_queue
    from src.matching.matching_queue import get_matching_queue

    await get_resume_processing_queue().stop()
    await get_matching_queue().stop()
    logger.info("All queues stopped successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.scraping.scheduler import start_scraping_scheduler, shutdown_scraping_scheduler
    from src.scraping.scraper_registry import initialize_query_manager, shutdown_query_manager

    setup_scrapers()
    await initialize_query_manager()
    await setup_resume_processing_queue()
    await setup_matching_queue()

    start_scraping_scheduler()
    yield
    shutdown_scraping_scheduler()
    await shutdown_query_manager()
    await stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="your-super-secret-key")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(matches.router, prefix="/matches", tags=["matches"])