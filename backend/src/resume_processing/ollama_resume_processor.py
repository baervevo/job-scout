import json
import subprocess
from typing import List

from src.models.processed_resume import ProcessedResume
from src.prompts.resume_details import PROMPT as RESUME_PROCESSING_PROMPT
from src.resume_processing.abstract_resume_processor import AbstractResumeProcessor
from src.utils.logger import logger
from src.utils.processing import ollama_api_call


class OllamaResumeProcessor(AbstractResumeProcessor):
    """
    Resume processor that uses the Ollama to process resumes.
    """

    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name

    async def process_resumes(self, resumes: List[str]) -> List[ProcessedResume]:
        """
        Process a list of extracted raw strings and return a list of processed resumes.
        """
        processed_resumes = []

        for resume in resumes:
            processed_resume = await self._process_single_resume(resume)
            processed_resumes.append(processed_resume)

        return processed_resumes

    async def _process_single_resume(self, resume: str) -> ProcessedResume:
        prompt = RESUME_PROCESSING_PROMPT.format(resume)

        result = ollama_api_call('llama2', prompt).lower().strip()

        skills = []
        experience = []
        education = []
        certifications = []
        years_of_experience = None

        if result:
            logger.debug(f"Raw JSON output from LLM: {result}")
            try:
                data = json.loads(result)
                skills = data.get("required_qualifications", []) or []
                experience = data.get("experience", []) or []
                education = data.get("education", []) or []
                certifications = data.get("certifications", []) or []
                years_of_experience = data.get("years_of_experience", None)
                if years_of_experience is None:
                    years_of_experience = 0
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error decoding JSON for listing: {e}")
        else:
            logger.warning(f"No output received from LLM for listing.")

        return ProcessedResume(
            skills=skills,
            experience=experience,
            education=education,
            certifications=certifications
        )
