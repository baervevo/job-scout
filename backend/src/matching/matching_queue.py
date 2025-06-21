import queue
import threading
import time
from typing import Tuple, List, Callable

from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.match import Match
from src.processing.matching_processor import MatchingProcessor

class MatchingQueue:
    _matching_queue: queue.Queue[Tuple[ResumeKeywordData, ListingKeywordData]]
    _matching_processor: MatchingProcessor
    _on_match_callbacks: List[Callable[[Match], None]]

    _thread: threading.Thread
    _stop_event: threading.Event
    _mutex: threading.Lock

    def __init__(self, matching_processor: MatchingProcessor):
        self._matching_queue = queue.Queue()
        self._matching_processor = matching_processor
        self._on_match_callbacks = []

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_matches)
        self._mutex = threading.Lock()
        self._thread.start()

    def enqueue(self, resume: ResumeKeywordData, listing: ListingKeywordData) -> None:
        with self._mutex:
            self._matching_queue.put((resume, listing))

    def register_on_match_callback(self, callback: Callable[[Match], None]) -> None:
        with self._mutex:
            self._on_match_callbacks.append(callback)

    def _process_matches(self) -> None:
        while not self._stop_event.is_set():
            while self._matching_queue.empty():
                time.sleep(60) # TODO(@mariusz): make this configurable
            try:
                resume, listing = self._matching_queue.get(timeout=1)
                match = self._matching_processor.match(resume, listing)
                self._notify_on_match(match)
            except queue.Empty:
                continue

    def _notify_on_match(self, match: Match) -> None:
        with self._mutex:
            for callback in self._on_match_callbacks:
                callback(match)

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join()

_matching_queue = None
_mutex = threading.Lock()

def get_matching_queue(processor: MatchingProcessor = None) -> MatchingQueue:
    global _matching_queue
    with _mutex:
        if _matching_queue is None:
            if processor is None:
                processor = MatchingProcessor()
            _matching_queue = MatchingQueue(processor)
        return _matching_queue
