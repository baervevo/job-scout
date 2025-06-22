from typing import Generator, Set
import asyncio

from src.models.query import Query
from src.scraping.query_managers.query_manager import QueryManager
from src.utils.logger import logger

SIMILARITY_THRESHOLD = 0.5


def _check_similarity(existing_query: Query, query: Query) -> bool:
    def jaccard_similarity(list1, list2):
        set1, set2 = set(list1), set(list2)
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union)

    if existing_query.location != query.location:
        return False
    if existing_query.radius != query.radius:
        return False
    if existing_query.salary != query.salary:
        return False
    return jaccard_similarity(existing_query.keywords, query.keywords) > SIMILARITY_THRESHOLD


class AggregatingQueryManager(QueryManager):
    _queries: Set[Query]
    _loaded: bool

    def __init__(self):
        self._queries = set()
        self._loaded = False

    async def _load_queries_from_db(self) -> None:
        """Load stored queries from the database"""
        try:
            from src.db.session import async_session_maker
            from src.db.schemas.stored_query import StoredQuery
            from sqlalchemy import select

            async with async_session_maker() as db_session:
                result = await db_session.execute(select(StoredQuery))
                stored_queries = result.scalars().all()
                
                for stored_query in stored_queries:
                    keywords = tuple(stored_query.keywords.split(",")) if stored_query.keywords else tuple()
                    query = Query(
                        keywords=keywords,
                        location=stored_query.location,
                        radius=stored_query.radius,
                        salary=stored_query.salary
                    )
                    self._queries.add(query)
                
                logger.info(f"Loaded {len(stored_queries)} queries from database")
                self._loaded = True
                
        except Exception as e:
            logger.error(f"Failed to load queries from database: {str(e)}")
            self._loaded = True  # Mark as loaded even on error to prevent repeated attempts

    async def _save_queries_to_db(self) -> None:
        """Save current queries to the database"""
        try:
            from src.db.session import async_session_maker
            from src.db.schemas.stored_query import StoredQuery
            from sqlalchemy import select, delete

            async with async_session_maker() as db_session:
                # Clear existing stored queries
                await db_session.execute(delete(StoredQuery))
                
                # Save current queries
                for query in self._queries:
                    keywords_str = ",".join(query.keywords) if query.keywords else ""
                    stored_query = StoredQuery(
                        keywords=keywords_str,
                        location=query.location,
                        radius=query.radius,
                        salary=query.salary
                    )
                    db_session.add(stored_query)
                
                await db_session.commit()
                logger.info(f"Saved {len(self._queries)} queries to database")
                
        except Exception as e:
            logger.error(f"Failed to save queries to database: {str(e)}")

    async def _ensure_loaded(self) -> None:
        """Ensure queries are loaded from database"""
        if not self._loaded:
            await self._load_queries_from_db()

    def add_query(self, query: Query) -> None:
        # Load queries if not already loaded (sync version for compatibility)
        if not self._loaded:
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self._load_queries_from_db())
            except RuntimeError:
                # If no event loop is running, we'll load on first get_queries call
                pass

        for q in self._queries:
            is_similar = _check_similarity(existing_query=q, query=query)
            if is_similar:
                existing_keywords_set = set(q.keywords)
                new_keywords_set = set(query.keywords)
                # Create a new query with merged keywords to maintain immutability
                merged_keywords = tuple(existing_keywords_set.union(new_keywords_set))
                new_query = Query(
                    keywords=merged_keywords,
                    location=q.location,
                    radius=q.radius,
                    salary=q.salary
                )
                self._queries.remove(q)
                self._queries.add(new_query)
                return
        self._queries.add(query)

    def remove_query(self, query: Query) -> None:
        if query in self._queries:
            self._queries.remove(query)

    def get_queries(self) -> Generator[Query, None, None]:
        # Load queries if not already loaded
        if not self._loaded:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, we can't await here
                    # The loading will happen asynchronously
                    pass
                else:
                    loop.run_until_complete(self._load_queries_from_db())
            except RuntimeError:
                # No event loop, will be loaded later
                pass
        
        for query in self._queries:
            yield query

    async def shutdown(self) -> None:
        """Save queries to database on shutdown"""
        await self._save_queries_to_db()

    async def initialize(self) -> None:
        """Initialize by loading queries from database"""
        await self._load_queries_from_db()
