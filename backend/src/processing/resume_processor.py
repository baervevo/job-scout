from typing import List

from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.processing.processor import Processor
from src.prompts.llama3.resume_keywords import PROMPT as PROMPT_RESUME_KEYWORDS
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

        kw_list = kw_text_to_list(resume_kw)
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

    async def _process_single_resume_with_chunking(self, resume: Resume) -> ResumeKeywordData:
        chunks = self.chunk_into_n(self.tokenize_sentences(resume.content), n_chunks=5)
        all_processed_chunks = set()

        for i, chunk_text in enumerate(chunks):
            prompt = PROMPT_RESUME_KEYWORDS.format(chunk_text)
            chunk_processed = ollama_api_call(prompt, model=self.llm_model_name).lower().strip()
            logger.debug(f"Resume {resume.internal_id} - chunk {i + 1} processed with LLM: {chunk_processed}.")

            chunk_kw_formatted = format_keywords(chunk_processed)
            logger.debug(f"Resume {resume.internal_id} - chunk {i + 1} cleaned with regex: {chunk_kw_formatted}.")

            chunk_kw_list = kw_text_to_list(chunk_kw_formatted)
            logger.debug(f"Resume {resume.internal_id} - chunk {i + 1} as a keyword list: {chunk_kw_list}.")
            chunk_kw_set = set(chunk_kw_list)
            all_processed_chunks.update(chunk_kw_set)

        resume_full = ", ".join(all_processed_chunks)
        resume_vec = self.embed_text(resume_full)
        resume_vec_converted = resume_vec.tolist()

        logger.debug(f"Final keywords for resume {resume.internal_id}: {all_processed_chunks}.")
        return ResumeKeywordData(internal_id=resume.internal_id,
                                 user_id=resume.user_id,
                                 file_name=resume.file_name,
                                 file_path=resume.file_path,
                                 content=resume.content,
                                 keywords=list(all_processed_chunks),
                                 embedding=resume_vec_converted)
