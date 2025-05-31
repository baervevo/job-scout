from typing import Generator

from src.scraper.listing_scraper import RestAPIListingScraper
from src.models.listing import Listing
from src.models.query import Query
from src.utils.logger import logger
from src.utils.salary import parse_salary_range
import src.config as cfg

REQUEST_HEADERS = {"Content-Type": "application/json"}

class JoobleScraper(RestAPIListingScraper):
    def __init__(self, api_key: str):
        super().__init__(api_key, cfg.settings.JOOBLE_HOST)
        self._http_client.on_status(200)(self._handle_success)
        self._http_client.on_status(403)(self._handle_no_listings)
        self._http_client.on_status(404)(self._handle_not_found)
        
    def _handle_success(self, response):
        for job in response.json().get("jobs", []):
            salary_range = parse_salary_range(job.get("salary"))
            yield Listing(
                id=str(job.get("id")),
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                description=job.get("snippet", ""),
                salary_min=salary_range[0],
                salary_max=salary_range[1],
                currency=salary_range[2],
                remote="remote" in job.get("location", "").lower(),
                created_at=job.get("updated", ""),
                updated_at=job.get("updated", ""),
                url=job.get("link", "")
            )
    
    def _handle_no_listings(self, response):
        logger.info("No listings found for the given query.")
        return []
    
    def _handle_not_found(self, response):
        logger.error("Jooble API endpoint not found.")
        return []
    
    def fetch_listings(self, query: Query) -> Generator[Listing, None, None]:
        body = {
            "keywords": ", ".join(query.keywords),
            "location": query.location
        }
        return self._http_client.post(
            f"/api/{self._api_key}",
            json=body, 
            headers=REQUEST_HEADERS
        )
    