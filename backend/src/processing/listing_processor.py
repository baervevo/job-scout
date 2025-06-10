from typing import List

import spacy

from src.constants.processing_constants import DEFAULT_LISTING_KW_TOP_N, DEFAULT_LISTING_KW_NUM_CANDIDATES
from src.models.listing.listing import Listing
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.processing.processor import Processor
from src.prompts.listing_keywords import PROMPT as PROMPT_LISTING_KEYWORDS
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call

nlp = spacy.load("en_core_web_sm")


class ListingProcessor(Processor):

    def __init__(self):
        super().__init__()

    async def process_listings(self, listings: List[Listing]) -> List[ListingKeywordData]:
        processed_listings = []

        for listing in listings:
            processed_listing = await self._process_single_listing(listing)
            processed_listings.append(processed_listing)

        return processed_listings

    async def _process_single_listing(self, listing: Listing) -> ListingKeywordData:
        logger.debug(f"Raw listing {listing.internal_id}: {listing.description}.")

        prompt = PROMPT_LISTING_KEYWORDS.format(listing.description)
        listing_description_clean = ollama_api_call('llama2', prompt).lower().strip()
        logger.debug(f"Listing {listing.internal_id} cleaned with ollama: {listing_description_clean}.")

        listing_keywords = self.extract_keywords(listing_description_clean, top_n=DEFAULT_LISTING_KW_TOP_N,
                                                 nr_candidates=DEFAULT_LISTING_KW_NUM_CANDIDATES)
        listing_vec = self.embed_text(listing_description_clean)
        logger.info(
            f"Processed listing {listing.internal_id} with {len(listing_keywords)} keywords: {listing_keywords}")

        listing_vec_converted = listing_vec.tolist()
        return ListingKeywordData(internal_id=listing.internal_id,
                                  keywords=listing_keywords,
                                  embedding=listing_vec_converted,
                                  title=listing.title,
                                  company=listing.company,
                                  description=listing.description,
                                  remote=listing.remote,
                                  created_at=listing.created_at,
                                  updated_at=listing.updated_at,
                                  salary_min=listing.salary_min,
                                  salary_max=listing.salary_max,
                                  currency=listing.currency,
                                  location=listing.location,
                                  link=listing.link)
