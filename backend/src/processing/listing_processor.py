from typing import List

from src.models.listing.listing import Listing
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.processing.processor import Processor
from src.prompts.llama3.listing_keywords import PROMPT as PROMPT_LISTING_KEYWORDS
from src.utils.processing_utils import ollama_api_call_async, kw_text_to_list
from src.utils.logger import logger


class ListingProcessor(Processor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_listings(self, listings: List[Listing]) -> List[ListingKeywordData]:
        processed_listings = []
        for listing in listings:
            processed_listing = self._process_single_listing(listing)
            processed_listings.append(processed_listing)

        return processed_listings

    async def _process_single_listing_async(self, listing: Listing) -> ListingKeywordData:
        prompt = PROMPT_LISTING_KEYWORDS.format(listing.description)
        listing_kw = await ollama_api_call_async(
            prompt,
            model=self.llm_model_name
        )
        if listing_kw is None:
            logger.warning(f"LLM processing failed for listing {listing.id}, using fallback keyword extraction")
            fallback_keywords = self.extract_keywords(listing.description, top_n=8)
            kw_list = fallback_keywords
            listing_vec_text = ", ".join(fallback_keywords)
        else:
            listing_kw = listing_kw.lower().strip()
            kw_list = kw_text_to_list(listing_kw)
            listing_vec_text = listing_kw
        listing_vec = self.embed_text(listing_vec_text)
        listing_vec_converted = listing_vec.tolist()
        return ListingKeywordData(id=listing.id,
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

    def _process_single_listing(self, listing: Listing) -> ListingKeywordData:
        fallback_keywords = self.extract_keywords(listing.description, top_n=8)
        listing_vec_text = ", ".join(fallback_keywords)
        listing_vec = self.embed_text(listing_vec_text)
        listing_vec_converted = listing_vec.tolist()
        return ListingKeywordData(id=listing.id,
                                  keywords=fallback_keywords,
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
