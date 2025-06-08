from typing import List

from src.models.processed_resume import ProcessedResume
from src.resume_processing.abstract_resume_processor import AbstractResumeProcessor


class OllamaResumeProcessor(AbstractResumeProcessor):
    """
    Resume processor that uses the Ollama to process resumes.
    """
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name

    async def process_resumes(self, raw_resumes: List[str]) -> List[ProcessedResume]:
        """
        Process a list of extracted raw strings and return a list of processed resumes.
        """
        processed_resumes = []

        for resume in raw_resumes:
            processed_resume = await self._process_single_resume(resume)
            processed_resumes.append(processed_resume)

        return processed_resumes

    async def _process_single_resume(self, resume: str) -> ProcessedResume:
        raise NotImplementedError("OllamaResumeProcessor._process_single_resume is not implemented yet.")
