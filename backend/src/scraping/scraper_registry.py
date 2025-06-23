from typing import Dict

from config import settings
from src.models.query import Query
from src.processing.listing_processor import ListingProcessor
from src.scraping.query_managers.query_manager import QueryManager
from src.scraping.query_managers.simple_query_manager import SimpleQueryManager
from src.scraping.scrapers.jooble_scraper import JoobleScraper
from src.scraping.scraping_manager import ScrapingManager
from src.utils.logger import logger

_scraper_registry: Dict[str, ScrapingManager] = None
_query_manager: QueryManager = None

def init_scraper_registry(query_manager: QueryManager = None):
    if query_manager is None:
        query_manager = SimpleQueryManager()

    global _scraper_registry
    jooble = JoobleScraper(
        settings.JOOBLE_API_KEY,
        settings.JOOBLE_HOST
    )
    listing_processor = ListingProcessor()

    _scraper_registry = {}
    _scraper_registry["jooble"] = ScrapingManager(
        scraper=jooble,
        query_manager=query_manager,
        listing_processor=listing_processor
    )


def set_query_manager(query_manager: QueryManager):
    global _query_manager
    _query_manager = query_manager
    init_scraper_registry(_query_manager)


def get_query_manager() -> QueryManager:
    global _query_manager
    if _query_manager is None:
        _query_manager = SimpleQueryManager()
    return _query_manager


def get_scraper_registry() -> Dict[str, ScrapingManager]:
    global _scraper_registry
    global _query_manager
    if not _scraper_registry:
        if _query_manager is None:
            _query_manager = SimpleQueryManager()
        init_scraper_registry(_query_manager)
    return _scraper_registry


async def run_all_scrapers():
    if not _scraper_registry:
        return
    for name, manager in _scraper_registry.items():
        try:
            await manager.run_scraper()
        except Exception as e:
            logger.error(f"Error in {name}: {str(e)}")


async def initialize_query_manager():
    global _query_manager
    if _query_manager and hasattr(_query_manager, 'initialize'):
        try:
            await _query_manager.initialize()
            logger.info("Query manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize query manager: {str(e)}")


async def shutdown_query_manager():
    global _query_manager
    if _query_manager and hasattr(_query_manager, 'shutdown'):
        try:
            await _query_manager.shutdown()
            logger.info("Query manager shutdown successfully")
        except Exception as e:
            logger.error(f"Failed to shutdown query manager: {str(e)}")
