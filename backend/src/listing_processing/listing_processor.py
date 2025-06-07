import spacy

from src.models.listing import Listing
from src.models.processed_listing import *


class ListingProcessor:
    def __init__(self):
        self._skill_keywords = {
            "required": ["requirements", "must have", "required"],
            "preferred": ["preferred", "nice to have", "bonus"]
        }

    async def process_listing(self, listing: Listing) -> ProcessedListing:
        """Process a raw listing into structured keywords"""
        title_keywords = self._extract_keywords(listing.title, "title", SkillType.TITLE)
        company_keywords = self._extract_keywords(listing.company, "company", SkillType.COMPANY)
        desc_keywords = self._extract_keywords(listing.description, "description", SkillType.DESCRIPTION)

        all_keywords = title_keywords + company_keywords + desc_keywords

        metadata = {
            "salary_min": listing.salary_min,
            "salary_max": listing.salary_max,
            "currency": listing.currency,
            "location": listing.location,
            "remote": listing.remote,
            "link": listing.link,
            "created_at": listing.created_at,
            "updated_at": listing.updated_at
        }

        return ProcessedListing(
            internal_id=listing.internal_id,
            keywords=self._deduplicate_keywords(all_keywords),
            metadata=metadata,
            processed_at=datetime.now()
        )

    def _extract_keywords(self, text: str, field_name: str, skill_type: SkillType) -> List[ExtractedKeyword]:
        """Extract and normalize keywords from text"""
        if not text:
            return []

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text.lower())
        keywords = {}

        # Extract noun phrases and important tokens
        for chunk in doc.noun_chunks:
            clean_text = " ".join([token.lemma_ for token in chunk
                                   if not token.is_stop and not token.is_punct])
            if clean_text and len(clean_text) > 2:
                keywords[clean_text] = keywords.get(clean_text, 0) + 1

        # Add individual important tokens
        for token in doc:
            if (not token.is_stop and not token.is_punct and
                    token.pos_ in ["NOUN", "PROPN", "VERB"] and
                    len(token.lemma_) > 2):
                keywords[token.lemma_] = keywords.get(token.lemma_, 0) + 1

        return [
            ExtractedKeyword(
                text=kw,
                type=skill_type,
                source_field=field_name,
                importance=self._calculate_importance(skill_type),
                frequency=count
            )
            for kw, count in keywords.items()
        ]

    def _calculate_importance(self, skill_type: SkillType) -> float:
        """Calculate importance weight based on keyword type and content"""
        base_weights = {
            SkillType.TITLE: 1.2,
            SkillType.DESCRIPTION: 1.0,
            SkillType.COMPANY: 0.8
        }
        return base_weights.get(skill_type, 1.0)

    def _deduplicate_keywords(self, keywords: List[ExtractedKeyword]) -> List[ExtractedKeyword]:
        """Merge duplicate keywords while preserving the highest importance"""
        merged = {}
        for kw in keywords:
            if kw.text not in merged:
                merged[kw.text] = kw
            else:
                # Keep the version with highest importance
                if kw.importance > merged[kw.text].importance:
                    merged[kw.text] = kw
                # Sum frequencies
                merged[kw.text].frequency += kw.frequency
        return list(merged.values())
