from typing import List

from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.processing.processor import Processor
from src.prompts.llama2.resume_keywords import PROMPT as PROMPT_RESUME_KEYWORDS
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call, format_keywords, kw_text_to_list


class ResumeProcessor(Processor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def process_resumes(self, resumes: List[Resume]) -> List[ResumeKeywordData]:
        processed_resumes = []

        for resume in resumes:
            processed_resume = await self._process_single_resume(resume)
            processed_resumes.append(processed_resume)

        return processed_resumes

    async def _process_single_resume(self, resume: Resume) -> ResumeKeywordData:
        # logger.debug(f"Raw resume {resume.internal_id}: {resume.content}.")

        prompt = PROMPT_RESUME_KEYWORDS.format(resume.content)
        resume_content_llm_processed = ollama_api_call(prompt, model=self.llm_model_name).lower().strip()
        logger.debug(f"Resume{resume.internal_id} processed with llm: {resume_content_llm_processed}.")

        resume_kw = format_keywords(resume_content_llm_processed)
        # logger.debug(f"Resume {resume.internal_id} cleaned with regex: {resume_kw}.")

        kw_nlp_list = self.extract_keywords(resume_kw, top_n=30, nr_candidates=60, ngram_max=1)
        kw_normal_list = kw_text_to_list(resume_kw)
        kw_list = kw_nlp_list + kw_normal_list
        logger.debug(f"Resume {resume.internal_id} as a keyword list: {kw_list}.")

        resume_vec = self.embed_text(resume_kw)
        resume_vec_converted = resume_vec.tolist()

        return ResumeKeywordData(internal_id=resume.internal_id,
                                 user_id=resume.user_id,
                                 file_name=resume.file_name,
                                 file_path=resume.file_path,
                                 content=resume.content,
                                 keywords=kw_list,
                                 embedding=resume_vec_converted)
