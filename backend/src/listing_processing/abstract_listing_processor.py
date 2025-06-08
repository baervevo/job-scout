from abc import ABC, abstractmethod
from typing import List

from src.models.listing import Listing
from src.models.processed_listing import ProcessedListing


class AbstractListingProcessor(ABC):
    """
    Abstract base class defining the interface for listing processors.
    """

    @abstractmethod
    async def process_listings(self, listings: List[Listing]) -> List[ProcessedListing]:
        """
        Process a list of listings and return a list of processed listings.
        """
        pass
