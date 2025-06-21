

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.routes import auth

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
    map(queue.register_on_match_callback, on_match_callbacks)

def setup_scrapers() -> None:
    from src.scraping.scraper_registry import get_scraper_registry
    from src.scraping.listing_callbacks import process_and_commit_listing

    listing_callbacks = [
        process_and_commit_listing
    ]
    for name, manager in get_scraper_registry().items():
        map(manager.register_listing_callback, listing_callbacks)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.scraping.scheduler import start_scraping_scheduler, shutdown_scraping_scheduler

    setup_scrapers()
    setup_matching_queue()

    start_scraping_scheduler()
    yield
    shutdown_scraping_scheduler()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])