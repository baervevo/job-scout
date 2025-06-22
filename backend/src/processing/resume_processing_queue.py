import threading
import asyncio
from typing import List, Callable

from backend.src.models.resume.resume import Resume
from backend.src.models.resume.resume_keyword_data import ResumeKeywordData
from src.processing.resume_processor import ResumeProcessor

class ResumeProcessingQueue:
    _resume_queue: asyncio.Queue[Resume]
    _resume_processor: ResumeProcessor
    _on_processed_callbacks: List[Callable[[ResumeKeywordData], None]]

    _processing_task: asyncio.Task | None
    _stop_event: asyncio.Event

    def __init__(self, resume_processor: ResumeProcessor):
        self._resume_queue = asyncio.Queue()
        self._resume_processor = resume_processor
        self._on_processed_callbacks = []
        self._processing_task = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self._stop_event.clear()
        self._processing_task = asyncio.create_task(self._process_resumes())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._processing_task:
            await self._processing_task
            self._processing_task = None

    def enqueue(self, resume: Resume) -> None:
        self._resume_queue.put_nowait(resume)

    def register_on_processed_callback(self, callback: Callable[[ResumeKeywordData], None]) -> None:
        self._on_processed_callbacks.append(callback)

    async def _process_resumes(self) -> None:
        while not self._stop_event.is_set():
            try:
                resume = await asyncio.wait_for(self._resume_queue.get(), timeout=60)
            except asyncio.TimeoutError:
                continue

            processed = await self._resume_processor.process_resume(resume)
            await self._notify_on_processed(processed)

    async def _notify_on_processed(self, processed_resume: ResumeKeywordData) -> None:
        for callback in self._on_processed_callbacks:
            await callback(processed_resume)

_resume_processing_queue = None
_mutex = threading.Lock()

def get_resume_processing_queue() -> ResumeProcessingQueue:
    global _resume_processing_queue
    with _mutex:
        if _resume_processing_queue is None:
            processor = ResumeProcessor()
            _resume_processing_queue = ResumeProcessingQueue(processor)
        return _resume_processing_queue
