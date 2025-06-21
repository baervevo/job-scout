from typing import List

import torch

from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.match import Match
from src.processing.processor import Processor
from src.prompts.llama3.matching_keywords import PROMPT as KEYWORD_MATCHING_PROMPT
from src.prompts.llama3.matching_summary import PROMPT as SUMMARY_MATCHING_PROMPT
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call, format_keywords, kw_text_to_list


class MatchingProcessor(Processor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def match(self, resume: ResumeKeywordData, listing: ListingKeywordData) -> Match:
        missing_keywords = self._find_missing_keywords(resume.keywords, listing.keywords)
        similarity = self._calculate_cosine_similarity(resume.keywords, listing.embedding)
        summary = self._generate_summary(resume.keywords, listing.keywords)

        return Match(
            resume_id=resume.internal_id,
            listing_id=listing.internal_id,
            missing_keywords=missing_keywords,
            cosine_similarity=similarity,
            summary=summary
        )

    def _calculate_cosine_similarity(self, resume_embedding: List[float], listing_embedding: List[float]) -> float:
        vec1 = torch.tensor(resume_embedding)
        vec2 = torch.tensor(listing_embedding)
        cos_sim = torch.nn.functional.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
        return cos_sim.item()

    def _find_missing_keywords(self, resume_keywords: List[str], listing_keywords: List[str]) -> List[str]:
        resumes_kw_joined = ", ".join(resume_keywords)
        listings_kw_joined = ", ".join(listing_keywords)
        prompt = KEYWORD_MATCHING_PROMPT.format(resumes_kw_joined, listings_kw_joined)
        missing_kw = ollama_api_call(prompt, model=self.llm_model_name).lower().strip()
        logger.debug(f"Keywords matched using llm: {missing_kw}.")

        missing_kw_clean = format_keywords(missing_kw)
        # logger.debug(f"Keywords cleaned with regex: {missing_kw_clean}.")

        missing_kw_list = kw_text_to_list(missing_kw_clean)
        # logger.debug(f"Missing keywords as python list: {missing_kw_list}.")

        return missing_kw_list

    def _generate_summary(self, resume_keywords: List[str], listing_keywords: List[str]) -> str:
        resumes_kw_joined = ", ".join(resume_keywords)
        listings_kw_joined = ", ".join(listing_keywords)
        prompt = SUMMARY_MATCHING_PROMPT.format(resumes_kw_joined, listings_kw_joined)
        summary = ollama_api_call(prompt, model=self.llm_model_name).lower().strip()
        logger.debug(f"Summary generated using llm: {summary}.")
        return summary
