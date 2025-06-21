import queue
import threading
import asyncio
import time
from typing import List, Callable

from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.processing.resume_processor import ResumeProcessor

class ResumeProcessingQueue:
    _resume_queue: queue.Queue[Resume]
    _resume_processor: ResumeProcessor
    _on_processed_callbacks: List[Callable[[ResumeKeywordData], None]]

    _thread: threading.Thread
    _stop_event: threading.Event
    _mutex: threading.Lock

    def __init__(self, resume_processor: ResumeProcessor):
        self._resume_queue = queue.Queue()
        self._resume_processor = resume_processor
        self._on_processed_callbacks = []

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._thread_func)
        self._mutex = threading.Lock()
        self._thread.start()

    def _thread_func(self) -> None:
        asyncio.run(self._process_resumes())

    def enqueue(self, resume: Resume) -> None:
        with self._mutex:
            self._resume_queue.put(resume)

    def register_on_processed_callback(self, callback: Callable[[ResumeKeywordData], None]) -> None:
        with self._mutex:
            self._on_processed_callbacks.append(callback)

    async def _process_resumes(self) -> None:
        while not self._stop_event.is_set():
            while self._resume_queue.empty():
                time.sleep(60) # TODO(@mariusz): make this configurable
            try:
                resume = self._resume_queue.get(timeout=1)
                processed = await self._resume_processor.process_resume(resume)
                await self._notify_on_processed(processed)
            except queue.Empty:
                continue

    async def _notify_on_processed(self, processed_resume: ResumeKeywordData) -> None:
        with self._mutex:
            for callback in self._on_processed_callbacks:
                await callback(processed_resume)

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join()

_resume_processing_queue = None
_mutex = threading.Lock()

def get_resume_processing_queue() -> ResumeProcessingQueue:
    global _resume_processing_queue
    with _mutex:
        if _resume_processing_queue is None:
            processor = ResumeProcessor()
            _resume_processing_queue = ResumeProcessingQueue(processor)
        return _resume_processing_queue
