import threading
import asyncio
from typing import Tuple, List, Callable

from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.match import Match
from src.processing.matching_processor import MatchingProcessor

from src.utils.logger import logger

class MatchingQueue:
    _matching_queue: asyncio.Queue[Tuple[ResumeKeywordData, ListingKeywordData]]
    _matching_processor: MatchingProcessor
    _on_match_callbacks: List[Callable[[Match], None]]

    _processing_task: asyncio.Task | None
    _stop_event: asyncio.Event

    def __init__(self, matching_processor: MatchingProcessor):
        self._matching_queue = asyncio.Queue()
        self._matching_processor = matching_processor
        self._on_match_callbacks = []
        self._processing_task = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self._stop_event.clear()
        self._processing_task = asyncio.create_task(self._process_matches())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._processing_task:
            await self._processing_task
            self._processing_task = None

    def enqueue(self, resume: ResumeKeywordData, listing: ListingKeywordData) -> None:
        self._matching_queue.put_nowait((resume, listing))

    def register_on_match_callback(self, callback: Callable[[Match], None]) -> None:
        self._on_match_callbacks.append(callback)

    async def _process_matches(self) -> None:
        while not self._stop_event.is_set():
            try:
                resume, listing = await asyncio.wait_for(self._matching_queue.get(), timeout=60)
                match = await self._matching_processor.match(resume, listing)
                if match is not None:
                    await self._notify_on_match(match)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing match: {str(e)}")
                continue

    async def _notify_on_match(self, match: Match) -> None:
        for callback in self._on_match_callbacks:
            try:
                await callback(match)
            except Exception as e:
                logger.error(f"Error in match callback {callback.__name__}: {str(e)}")

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
