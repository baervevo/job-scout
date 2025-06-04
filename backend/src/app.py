from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.scraping.scheduler import start_scheduler, shutdown_scheduler
    from src.scraping.scraper_registry import init_scraper_registry
    from src.db.session import get_db

    async with get_db() as db_session:
        app.state.db_session = db_session
        init_scraper_registry(db_session)
        start_scheduler()
        yield
        shutdown_scheduler()

app = FastAPI(lifespan=lifespan)