from src.scraping.query_managers.query_manager import QueryManager

from typing import Generator, Set

from src.models.query import Query

class SimpleQueryManager(QueryManager):
    _queries: Set[Query]

    def __init__(self):
        self._queries = set()

    def add_query(self, query: Query) -> None:
        self._queries.add(query)

    def remove_query(self, query: Query) -> None:
        if query in self._queries:
            self._queries.remove(query)

    def get_queries(self) -> Generator[Query, None, None]:
        for query in self._queries:
            yield query
