import asyncio

from src.models.listing.listing import Listing
from src.models.resume.resume import Resume
from src.processing.listing_processor import ListingProcessor
from src.processing.matching_processor import MatchingProcessor
from src.processing.resume_processor import ResumeProcessor
from src.utils.pdf import extract_text_from_pdf


async def main():
    resume_path = r"C:\Users\mateu\PycharmProjects\JSProject\job-scout\resources\Berlin-Simple-Resume-Template.pdf"
    resume_text = extract_text_from_pdf(resume_path)
    resume = Resume(content=resume_text, internal_id="47", file_path=resume_path,
                    file_name="Berlin-Simple-Resume-Template.pdf")

    job_offer = (
        "Looking for an experienced IT Consultant with strong knowledge in hardware maintenance, software installation, "
        "and network security. The candidate should be familiar with database management, ethical hacking principles, "
        "and modern IT project management practices. Experience with process improvement, ticket management systems, "
        "and reducing wait times is a plus. Strong communication skills and ability to interface directly with clients "
        "is essential. Certification in CompTIA A+, CCNA, or Microsoft Solutions Expert preferred. "
        "We value experience in coaching, business administration, and strategic IT operations. "
        "Familiarity with agile methodologies and ability to work independently in a fast-paced environment required."
    )
    listing = Listing(internal_id="123", title="Software Engineer", company="Tech Company", remote=False,
                      description=job_offer)

    listing_processor = ListingProcessor()
    resume_processor = ResumeProcessor()

    processed_listings = listing_processor.process_listings([listing])
    processed_resumes = await resume_processor.process_resumes([resume])

    matching_processor = MatchingProcessor(processed_resumes[0])

    matching_result = await matching_processor.match_single_listing(processed_listings[0])
    print(matching_result)


if __name__ == "__main__":
    asyncio.run(main())
