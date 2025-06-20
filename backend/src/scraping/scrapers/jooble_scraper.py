import httpx
from typing import List

from src.scraping.scrapers.listing_scraper import ListingScraper
from src.models.listing.listing import Listing
from src.models.query import Query
from src.utils.logger import logger
from src.utils.salary import parse_salary_range
from dateutil import parser

class JoobleScraper(ListingScraper):
    _api_key: str
    _target_host: str

    def __init__(self, api_key: str, target_host: str):
        self._api_key = api_key
        self._target_host = target_host

    async def execute_query(self, query: Query) -> List[Listing]:
        logger.info(f"Executing query: {query}")
        url = f"{self._target_host}/api/{self._api_key}"

        payload = {}
        if query.keywords:
            payload["keywords"] = ", ".join(query.keywords)
        if query.location:
            payload["location"] = query.location
        if query.radius is not None:
            payload["radius"] = query.radius
        if query.salary is not None:
            payload["salary"] = query.salary

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return self._parse_response(response.json())
            except httpx.HTTPError as e:
                logger.warning(f"Request failed for query {query}: {str(e)}")
                return []

    def _parse_response(self, data: dict) -> List[Listing]:
        listings = []
        for job in data.get("jobs", []):
            salary_min, salary_max, currency = parse_salary_range(job.get("salary"))
            listings.append(Listing(
                internal_id=str(job.get("id")),
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                description=job.get("snippet", ""),
                salary_min=salary_min,
                salary_max=salary_max,
                currency=currency,
                remote="remote" in job.get("location", "").lower(),
                created_at=parser.isoparse(job.get("updated", "")),
                updated_at=parser.isoparse(job.get("updated", "")),
                link=job.get("link", "")
            ))
        return listings
