from abc import ABC, abstractmethod
from typing import List

from src.models.processed_resume import ProcessedResume


class AbstractResumeProcessor(ABC):
    """
    Abstract base class defining the interface for resume processors.
    """

    @abstractmethod
    async def process_resumes(self, resumes: List[str]) -> List[ProcessedResume]:
        """
        Process a list of extracted raw strings and return a list of processed resumes.
        """
        pass

