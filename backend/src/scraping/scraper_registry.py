from typing import Dict

from src.scraping.scrapers.jooble_scraper import JoobleScraper
from src.scraping.query_managers.simple_query_manager import SimpleQueryManager
from src.scraping.scraping_manager import ScrapingManager

from config import settings

_scraper_registry: Dict[str, ScrapingManager] = {}

def init_scraper_registry():
    global _scraper_registry
    jooble = JoobleScraper(
        settings.JOOBLE_API_KEY,
        settings.JOOBLE_HOST
    )
    _scraper_registry["jooble"] = ScrapingManager(
        scraper=jooble,
        query_manager=SimpleQueryManager()
    )

def get_scraper_registry() -> Dict[str, ScrapingManager]:
    return _scraper_registry
