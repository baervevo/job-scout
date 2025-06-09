import json
import subprocess
from typing import List

from src.listing_processing.abstract_listing_processor import AbstractListingProcessor
from src.models.listing import Listing
from src.models.processed_listing import ProcessedListing
from src.prompts.job_details import PROMPT as LISTING_PROCESSING_PROMPT
from src.utils.processing import clean_html_text
from src.utils.logger import logger


class OllamaListingProcessor(AbstractListingProcessor):
    """
    Concrete implementation of AbstractListingProcessor using the Ollama LLM.
    """

    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name

    async def process_listings(self, listings: List[Listing]) -> List[ProcessedListing]:
        """
        Processes a list of raw listings into structured processed listings.
        """
        processed_listings = []

        for listing in listings:
            processed_listing = await self._process_single_listing(listing)
            processed_listings.append(processed_listing)

        return processed_listings

    async def _process_single_listing(self, listing: Listing) -> ProcessedListing:
        """
        Processes a single listing using the Ollama LLM to extract structured information.
        """
        job_description = clean_html_text(listing.description)
        prompt = LISTING_PROCESSING_PROMPT.format(job_description)

        logger.debug(f"Processing listing {listing.internal_id} with description: {job_description}...")
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Unexpected error with subprocess for listing {listing.internal_id}: {e}")
            result = None

        required_qualifications = []
        preferred_qualifications = []
        experience = []
        education = None

        if result and result.stdout:
            logger.debug(f"Raw JSON output from LLM (ID: {listing.internal_id}): {result.stdout.strip()}")
            try:
                data = json.loads(result.stdout)
                required_qualifications = data.get("required_qualifications", []) or []
                preferred_qualifications = data.get("preferred_qualifications", []) or []
                experience = data.get("experience", []) or []
                education = data.get("education")
                if education == "null":
                    education = None
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error decoding JSON for listing {listing.internal_id}: {e}")
        else:
            logger.warning(f"No output received from LLM for listing {listing.internal_id}.")

        return ProcessedListing(
            internal_id=listing.internal_id,
            title=listing.title,
            company=listing.company,
            description=listing.description,
            required_qualifications=required_qualifications,
            preferred_qualifications=preferred_qualifications,
            experience=experience,
            education=education,
            salary_min=listing.salary_min,
            salary_max=listing.salary_max,
            currency=listing.currency,
            location=listing.location,
            remote=listing.remote,
            created_at=listing.created_at,
            updated_at=listing.updated_at,
            link=listing.link
        )
