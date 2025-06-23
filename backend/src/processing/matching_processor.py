from typing import List, Optional
from datetime import datetime

import torch

from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.match import Match
from src.processing.processor import Processor
from src.prompts.llama3.matching_keywords import PROMPT as KEYWORD_MATCHING_PROMPT
from src.prompts.llama3.matching_summary import PROMPT as SUMMARY_MATCHING_PROMPT
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call_async, format_keywords, kw_text_to_list

from config import settings

class MatchingProcessor(Processor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def match(self, resume: ResumeKeywordData, listing: ListingKeywordData) -> Optional[Match]:
        """Process a match between resume and listing"""
        try:
            if not resume:
                logger.warning("Resume object is None, skipping match")
                return None
            if not listing:
                logger.warning(f"Listing object is None for resume {resume.id if resume else 'Unknown'}, skipping match")
                return None
            if not resume.keywords:
                logger.warning(f"Resume {resume.id} has no keywords, skipping match")
                return None
            if not listing.keywords:
                logger.warning(f"Listing {listing.id} has no keywords, skipping match")
                return None
            if not resume.embedding or not listing.embedding:
                logger.warning(f"Missing embeddings for resume {resume.id} or listing {listing.id}")
                return None
            similarity = self._calculate_cosine_similarity(resume.embedding, listing.embedding)
            if similarity < settings.MATCHING_COSINE_THRESHOLD:
                logger.debug(f"Match between resume {resume.id} and listing {listing.id} below threshold: {similarity}")
                return None
            missing_keywords = await self._find_missing_keywords_async(resume.keywords, listing.keywords)
            summary = await self._generate_summary_async(resume.keywords, listing.keywords)
            match = Match(
                resume_id=str(resume.id),
                listing_id=str(listing.id),
                missing_keywords=missing_keywords,
                cosine_similarity=similarity,
                summary=summary
            )
            logger.info(f"Generated match: resume {resume.id} <-> listing {listing.id}, similarity: {similarity:.3f}")
            return match
            
        except Exception as e:
            logger.error(f"Error matching resume {resume.id} with listing {listing.id}: {str(e)}")
            return None

    def _calculate_cosine_similarity(self, resume_embedding: List[float], listing_embedding: List[float]) -> float:
        try:
            if not resume_embedding or not listing_embedding:
                return 0.0
            vec1 = torch.tensor(resume_embedding, dtype=torch.float32)
            vec2 = torch.tensor(listing_embedding, dtype=torch.float32)
            if vec1.shape != vec2.shape:
                logger.warning(f"Embedding dimension mismatch: {vec1.shape} vs {vec2.shape}")
                return 0.0
            cos_sim = torch.nn.functional.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
            return float(cos_sim.item())
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0

    async def _find_missing_keywords_async(self, resume_keywords: List[str], listing_keywords: List[str]) -> List[str]:
        """Async version with LLM fallback"""
        try:
            if not resume_keywords or not listing_keywords:
                return listing_keywords if listing_keywords else []
            
            resume_set = set(kw.lower().strip() for kw in resume_keywords)
            listing_set = set(kw.lower().strip() for kw in listing_keywords)
            missing_simple = list(listing_set - resume_set)
            
            try:
                resumes_kw_joined = ", ".join(resume_keywords)
                listings_kw_joined = ", ".join(listing_keywords)
                prompt = KEYWORD_MATCHING_PROMPT.format(resumes_kw_joined, listings_kw_joined)
                
                missing_kw = await ollama_api_call_async(
                    prompt, 
                    model=self.llm_model_name, 
                    temperature=0.1
                )
                
                if missing_kw is None:
                    logger.debug("Ollama disabled, using simple set-based keyword matching")
                    return missing_simple
                    
                missing_kw_clean = format_keywords(missing_kw.lower().strip())
                missing_kw_list = kw_text_to_list(missing_kw_clean)
                if missing_kw_list:
                    return missing_kw_list
                else:
                    logger.debug("LLM returned empty keywords, using simple set-based approach")
                    return missing_simple
                
            except Exception as llm_error:
                logger.debug(f"LLM keyword matching failed: {str(llm_error)}, using simple approach")
                return missing_simple
                
        except Exception as e:
            logger.error(f"Error finding missing keywords: {str(e)}")
            return []

    async def _generate_summary_async(self, resume_keywords: List[str], listing_keywords: List[str]) -> str:
        """Async summary generation with fallback"""
        try:
            if not resume_keywords or not listing_keywords:
                return "Unable to generate summary due to missing keywords"
            
            try:
                resumes_kw_joined = ", ".join(resume_keywords)
                listings_kw_joined = ", ".join(listing_keywords)
                prompt = SUMMARY_MATCHING_PROMPT.format(resumes_kw_joined, listings_kw_joined)
                
                summary = await ollama_api_call_async(
                    prompt, 
                    model=self.llm_model_name, 
                    temperature=0.3
                )
                
                if summary is None:
                    logger.debug("Ollama disabled, using fallback summary")
                elif summary and len(summary.strip()) > 10:
                    return summary.strip()
                    
            except Exception as llm_error:
                logger.debug(f"LLM summary generation failed: {str(llm_error)}, using fallback")
            
            overlap = set(kw.lower() for kw in resume_keywords) & set(kw.lower() for kw in listing_keywords)
            return f"The candidate's resume shows {len(overlap)} matching skills out of {len(listing_keywords)} required. Key overlapping areas include: {', '.join(list(overlap)[:5])}."
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed"

    def _find_missing_keywords(self, resume_keywords: List[str], listing_keywords: List[str]) -> List[str]:
        try:
            if not resume_keywords or not listing_keywords:
                return listing_keywords if listing_keywords else []
            resume_set = set(kw.lower().strip() for kw in resume_keywords)
            listing_set = set(kw.lower().strip() for kw in listing_keywords)
            return list(listing_set - resume_set)
        except Exception as e:
            logger.error(f"Error finding missing keywords: {str(e)}")
            return []

    def _generate_summary(self, resume_keywords: List[str], listing_keywords: List[str]) -> str:
        try:
            if not resume_keywords or not listing_keywords:
                return "Unable to generate summary due to missing keywords"
            overlap = set(kw.lower() for kw in resume_keywords) & set(kw.lower() for kw in listing_keywords)
            return f"Match found with {len(overlap)} overlapping skills out of {len(listing_keywords)} required."
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed"
