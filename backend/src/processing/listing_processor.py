from typing import List

import spacy

from src.models.listing.listing import Listing
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.processing.processor import Processor
from src.prompts.llama2.listing_keywords import PROMPT as PROMPT_LISTING_KEYWORDS
from src.utils.logger import logger
from src.utils.processing_utils import ollama_api_call, kw_text_to_list

class ListingProcessor(Processor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def process_listings(self, listings: List[Listing]) -> List[ListingKeywordData]:
        processed_listings = []

        for listing in listings:
            processed_listing = await self._process_single_listing(listing)
            processed_listings.append(processed_listing)

        return processed_listings

    async def _process_single_listing(self, listing: Listing) -> ListingKeywordData:
        # logger.debug(f"Raw listing {listing.internal_id}: {listing.description}.")

        prompt = PROMPT_LISTING_KEYWORDS.format(listing.description)
        listing_kw = ollama_api_call(prompt, model=self.llm_model_name).lower().strip()
        logger.debug(f"Listing {listing.internal_id} processed with ollama: {listing_kw}.")

        kw_list = kw_text_to_list(listing_kw)
        logger.debug(f"Listing {listing.internal_id} as a keyword list: {kw_list}.")

        listing_vec = self.embed_text(listing_kw)
        listing_vec_converted = listing_vec.tolist()

        return ListingKeywordData(internal_id=listing.internal_id,
                                  keywords=kw_list,
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
