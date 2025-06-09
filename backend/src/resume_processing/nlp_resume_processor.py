from typing import List

import spacy
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from torch import Tensor

from src.models.raw_resume import RawResume
from src.models.resume_keywords import ResumeKeywords
from src.prompts.resume_keywords import PROMPT as PROMPT_RESUME_KEYWORDS
from src.utils.logger import logger
from src.utils.processing import ollama_api_call

nlp = spacy.load("en_core_web_sm")


class NLPResumeProcessor:
    """
    Resume processor that uses nlp to process resumes.
    """

    def __init__(self):
        self.nlp_spacy = spacy.load("en_core_web_sm")
        self.kw_model = KeyBERT(model='all-MiniLM-L6-v2')
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def process_resumes(self, resumes: List[RawResume]) -> List[ResumeKeywords]:
        """
        Process a list of extracted raw strings and return a list of processed resumes.
        """
        processed_resumes = []

        for resume in resumes:
            processed_resume = await self._process_single_resume(resume)
            processed_resumes.append(processed_resume)

        return processed_resumes

    async def _process_single_resume(self, resume: RawResume) -> ResumeKeywords:
        logger.debug(f"Cleaning resume with ollama: {resume.content}...")
        prompt = PROMPT_RESUME_KEYWORDS.format(resume.content)
        resume_content_clean = ollama_api_call('llama2', prompt).lower().strip()
        # logger.debug(f"Processing resume with nlp: {resume_content_clean}...")
        # resume_proc = self.preprocess(resume_content_clean)
        logger.debug(f"Extracting keywords from processed resume: {resume_content_clean}...")
        resume_keywords = self.extract_keywords(resume_content_clean, top_n=20)
        resume_vec = self.embed_text(resume_content_clean)

        logger.info(
            f"Processed resume with {len(resume_keywords)} keywords: {resume_keywords} and vector of shape {resume_vec.shape}")

        resume_vec_converted = resume_vec.tolist()
        return ResumeKeywords(internal_id=resume.internal_id,
                              keywords=resume_keywords,
                              embedding=resume_vec_converted)

    def preprocess(self, text: str) -> str:
        doc = self.nlp_spacy(text)
        tokens = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct and not token.is_space
        ]
        return " ".join(tokens)

    def extract_keywords(self, text: str, top_n: int = 6) -> list[str]:
        keyword_tuples = self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            use_maxsum=False,
            nr_candidates=35,
            top_n=top_n
        )
        keywords = [kw for kw, score in keyword_tuples]
        return keywords

    def embed_text(self, text: str) -> Tensor:
        return self.embed_model.encode(text)
