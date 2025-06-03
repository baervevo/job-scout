import threading
import time

from typing import List, Optional

from src.scraping.query_managers.simple_query_manager import SimpleQueryManager
from src.scraping.scrapers.listing_scraper import RestAPIListingScraper
from src.models.listing import Listing
from src.models.query import Query
from src.utils.logger import logger
from src.utils.salary import parse_salary_range

REQUEST_HEADERS = {"Content-Type": "application/json"}

class JoobleScraper(RestAPIListingScraper):
    _api_key: str
    _query_manager: SimpleQueryManager
    _newest_results: List[Listing]
    
    _interval: float
    _stop_event: threading.Event
    _thread: Optional[threading.Thread]
    _results_lock: threading.Lock
    
    def __init__(
        self, 
        api_key: str,
        target_host: str,
        interval: float
    ):
        super().__init__(target_host)
        self._api_key = api_key
        self._query_manager = SimpleQueryManager()
        self._newest_results = []

        self._interval = interval
        self._stop_event = threading.Event()
        self._thread = None
        self._results_lock = threading.Lock()
        
        self._http_client.on_status(200)(self._handle_success)
        self._http_client.on_status(403)(self._handle_no_listings)
        self._http_client.on_status(404)(self._handle_not_found)

    def add_query(self, query: Query) -> None:
        self._query_manager.add_query(query)

    def remove_query(self, query: Query) -> None:
        self._query_manager.remove_query(query)

    def get_newest_results(self) -> List[Listing]:
        with self._results_lock:
            results = self._newest_results
            self._newest_results = []
            return results
    
    def start(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._thread_func, daemon=True)
            self._thread.start()
            logger.info("Jooble scraper started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            logger.info("Jooble scraper stopped.")
    
    def _thread_func(self) -> None:
        while not self._stop_event.is_set():
            for query in self._query_manager.get_queries():
                try:
                    self._execute_query(query)
                except Exception as e:
                    logger.error(f"Error executing query {query}: {e}")
            time.sleep(self._interval)

    def _handle_success(self, response) -> None:
        with self._results_lock:
            for job in response.json().get("jobs", []):
                salary_range = parse_salary_range(job.get("salary"))
                self._newest_results.append(Listing(
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
                ))
    
    def _handle_no_listings(self, response) -> None:
        logger.info("No listings found for the given query.")
    
    def _handle_not_found(self, response) -> None:
        logger.error("Jooble API endpoint not found.")
    
    def _execute_query(self, query: Query) -> None:
        body = {
            "keywords": ", ".join(query.keywords),
            "location": query.location
        }
        self._http_client.post(
            f"/api/{self._api_key}",
            json=body, 
            headers=REQUEST_HEADERS
        )
    