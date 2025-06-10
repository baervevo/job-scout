from typing import List

from src.constants.processing_constants import DEFAULT_RESUME_KW_TOP_N, DEFAULT_RESUME_KW_NUM_CANDIDATES
from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.processing.processor import Processor
from src.prompts.resume_keywords import PROMPT as PROMPT_RESUME_KEYWORDS
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call, format_lines


class ResumeProcessor(Processor):
    def __init__(self):
        super().__init__()

    async def process_resumes(self, resumes: List[Resume]) -> List[ResumeKeywordData]:
        processed_resumes = []

        for resume in resumes:
            processed_resume = await self._process_single_resume(resume)
            processed_resumes.append(processed_resume)

        return processed_resumes

    async def _process_single_resume(self, resume: Resume) -> ResumeKeywordData:
        logger.debug(f"Raw resume {resume.internal_id}: {resume.content}.")

        prompt = PROMPT_RESUME_KEYWORDS.format(resume.content)
        resume_content_llm_processed = ollama_api_call('llama2', prompt).lower().strip()
        logger.debug(f"Resume{resume.internal_id} processed with llm: {resume_content_llm_processed}.")

        resume_content_clean = format_lines(resume_content_llm_processed)
        logger.debug(f"Resume {resume.internal_id} cleaned with regex: {resume_content_clean}.")

        resume_keywords = self.extract_keywords(resume_content_clean, top_n=DEFAULT_RESUME_KW_TOP_N,
                                                nr_candidates=DEFAULT_RESUME_KW_NUM_CANDIDATES)
        resume_vec = self.embed_text(resume_content_clean)

        logger.info(
            f"Processed resume {resume.internal_id} with {len(resume_keywords)} keywords.")

        resume_vec_converted = resume_vec.tolist()
        return ResumeKeywordData(internal_id=resume.internal_id,
                                 user_id=resume.user_id,
                                 file_name=resume.file_name,
                                 file_path=resume.file_path,
                                 content=resume_content_clean,
                                 keywords=resume_keywords,
                                 embedding=resume_vec_converted)
