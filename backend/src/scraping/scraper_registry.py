from typing import Dict

from config import settings
from src.models.query import Query
from src.processing.listing_processor import ListingProcessor
from src.scraping.query_managers.simple_query_manager import SimpleQueryManager
from src.scraping.scrapers.jooble_scraper import JoobleScraper
from src.scraping.scraping_manager import ScrapingManager
from src.utils.logger import logger

_scraper_registry: Dict[str, ScrapingManager] = {}


def init_scraper_registry():
    global _scraper_registry
    jooble = JoobleScraper(
        settings.JOOBLE_API_KEY,
        settings.JOOBLE_HOST
    )
    manager = SimpleQueryManager()
    listing_processor = ListingProcessor()
    manager.add_query(Query(keywords=["java", "developer"], location="remote"))

    _scraper_registry["jooble"] = ScrapingManager(
        scraper=jooble,
        query_manager=manager,
        listing_processor=listing_processor
    )


def get_scraper_registry() -> Dict[str, ScrapingManager]:
    return _scraper_registry


async def run_all_scrapers():
    logger.info(f"Executing all scrapers...")
    for name, manager in _scraper_registry.items():
        try:
            await manager.run_scraper()
            logger.info(f"Ran scraper: {name}")
        except Exception as e:
            logger.error(f"Error in {name}: {str(e)}")
    logger.info(f"Scrapers execution completed.")
