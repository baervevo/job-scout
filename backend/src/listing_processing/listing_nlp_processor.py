from typing import List

import spacy
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from torch import Tensor

from src.models.listing import Listing
from src.models.listing_keywords import ListingKeywords
from src.prompts.listing_keywords import PROMPT as PROMPT_LISTING_KEYWORDS
from src.utils.logger import logger
from src.utils.processing import ollama_api_call

nlp = spacy.load("en_core_web_sm")


class NLPListingProcessor:

    def __init__(self):
        self.nlp_spacy = spacy.load("en_core_web_sm")
        self.kw_model = KeyBERT(model='all-MiniLM-L6-v2')
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def process_listings(self, listings: List[Listing]) -> List[ListingKeywords]:
        processed_listings = []

        for listing in listings:
            processed_listing = await self._process_single_listing(listing)
            processed_listings.append(processed_listing)

        return processed_listings

    async def _process_single_listing(self, listing: Listing) -> ListingKeywords:
        logger.debug(f"Cleaning listing with ollama: {listing.description}...")
        prompt = PROMPT_LISTING_KEYWORDS.format(listing.description)
        listing_description_clean = ollama_api_call('llama2', prompt).lower().strip()
        # logger.debug(f"Processing listing with nlp: {listing_description_clean}...")
        # listing_proc = self.preprocess(listing_description_clean)
        logger.debug(f"Extracting keywords from processed listing: {listing_description_clean}...")
        listing_keywords = self.extract_keywords(listing_description_clean, top_n=8)
        listing_vec = self.embed_text(listing_description_clean)

        logger.info(
            f"Processed listing with {len(listing_keywords)} keywords: {listing_keywords} and vector of shape {listing_vec.shape}")

        listing_vec_converted = listing_vec.tolist()
        return ListingKeywords(internal_id=listing.internal_id,
                               keywords=listing_keywords,
                               embedding=listing_vec_converted)

    def extract_keywords(self, text: str, top_n: int = 6) -> list[str]:
        keyword_tuples = self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            use_maxsum=False,
            nr_candidates=20,
            top_n=top_n
        )
        keywords = [kw for kw, score in keyword_tuples]
        return keywords

    def embed_text(self, text: str) -> Tensor:
        return self.embed_model.encode(text)
