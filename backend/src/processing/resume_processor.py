from typing import List, Optional

from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.processing.processor import Processor
from src.prompts.llama3.resume_keywords import PROMPT as PROMPT_RESUME_KEYWORDS
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call_async, format_keywords, kw_text_to_list


class ResumeProcessor(Processor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def process_resumes(self, resumes: List[Resume]) -> List[ResumeKeywordData]:
        processed_resumes = []
        for resume in resumes:
            processed_resume = await self.process_resume(resume)
            processed_resumes.append(processed_resume)
        return processed_resumes

    async def process_resume(self, resume: Resume) -> ResumeKeywordData:
        prompt = PROMPT_RESUME_KEYWORDS.format(resume.content)
        
        try:
            # Use non-blocking async Ollama call
            resume_content_llm_processed = await ollama_api_call_async(
                prompt, 
                model=self.llm_model_name
            )
            
            if resume_content_llm_processed is None:
                # Only happens if Ollama is disabled
                logger.info(f"Ollama is disabled, using fallback keyword extraction for resume {resume.id}")
                fallback_keywords = self.extract_keywords(resume.content, top_n=10)
                resume_kw = ", ".join(fallback_keywords)
                kw_list = fallback_keywords
            else:
                # Normal LLM processing
                resume_content_llm_processed = resume_content_llm_processed.lower().strip()
                resume_kw = format_keywords(resume_content_llm_processed)
                kw_list = kw_text_to_list(resume_kw)
                
        except Exception as e:
            # Only fall back on actual errors (connection issues, model problems, etc.)
            logger.warning(f"Ollama failed for resume {resume.id} ({str(e)}), using fallback keyword extraction")
            fallback_keywords = self.extract_keywords(resume.content, top_n=10)
            resume_kw = ", ".join(fallback_keywords)
            kw_list = fallback_keywords

        resume_vec = self.embed_text(resume_kw if isinstance(resume_kw, str) else ", ".join(kw_list))
        resume_vec_converted = resume_vec.tolist()

        return ResumeKeywordData(id=resume.id,
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
            chunk_processed = await ollama_api_call_async(prompt, model=self.llm_model_name).lower().strip()
            logger.debug(f"Resume {resume.id} - chunk {i + 1} processed with LLM: {chunk_processed}.")
            chunk_kw_formatted = format_keywords(chunk_processed)
            logger.debug(f"Resume {resume.id} - chunk {i + 1} cleaned with regex: {chunk_kw_formatted}.")
            chunk_kw_list = kw_text_to_list(chunk_kw_formatted)
            logger.debug(f"Resume {resume.id} - chunk {i + 1} as a keyword list: {chunk_kw_list}.")
            chunk_kw_set = set(chunk_kw_list)
            all_processed_chunks.update(chunk_kw_set)
        resume_full = ", ".join(all_processed_chunks)
        resume_vec = self.embed_text(resume_full)
        resume_vec_converted = resume_vec.tolist()
        logger.debug(f"Final keywords for resume {resume.id}: {all_processed_chunks}.")
        return ResumeKeywordData(id=resume.id,
                                 user_id=resume.user_id,
                                 file_name=resume.file_name,
                                 file_path=resume.file_path,
                                 content=resume.content,
                                 keywords=list(all_processed_chunks),
                                 embedding=resume_vec_converted)
