from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.scraping.scheduler import start_scheduler, shutdown_scheduler
    from src.scraping.scraper_registry import init_scraper_registry

    init_scraper_registry()
    start_scheduler()
    yield
    shutdown_scheduler()

app = FastAPI(lifespan=lifespan)