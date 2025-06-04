from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.utils.logger import logger

from src.scraping.scraper_registry import get_scraper_registry

_scraping_scheduler = None

def start_scheduler():
    global _scraping_scheduler
    if _scraping_scheduler is not None:
        logger.warning("Scheduler already started.")
        return
    logger.info("Starting APScheduler...")
    _scraping_scheduler = AsyncIOScheduler()
    for name, manager in get_scraper_registry().items():
        _scraping_scheduler.add_job(
            manager.run_scraper,
            trigger=IntervalTrigger(seconds=5),
            id=f"{name}_scraper_job",
            name=f"Run {name} scraper",
            replace_existing=True,
        )
    _scraping_scheduler.start()

def shutdown_scheduler():
    global _scraping_scheduler
    if _scraping_scheduler:
        logger.info("Shutting down scheduler...")
        _scraping_scheduler.shutdown(wait=False)
        _scraping_scheduler = None
