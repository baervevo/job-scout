from typing import Generator, Set

from src.models.query import Query
from src.scraping.query_managers.query_manager import QueryManager

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

    def __init__(self):
        self._queries = set()

    def add_query(self, query: Query) -> None:
        for q in self._queries:
            is_similar = _check_similarity(existing_query=q, query=query)
            if is_similar:
                existing_keywords_set = set(q.keywords)
                new_keywords_set = set(query.keywords)
                q.keywords = list(existing_keywords_set.union(new_keywords_set))
                return
        self._queries.add(query)

    def remove_query(self, query: Query) -> None:
        if query in self._queries:
            self._queries.remove(query)

    def get_queries(self) -> Generator[Query, None, None]:
        for query in self._queries:
            yield query
