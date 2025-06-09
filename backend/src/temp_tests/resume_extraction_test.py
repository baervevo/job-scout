import asyncio

import torch

from src.listing_processing.listing_nlp_processor import NLPListingProcessor
from src.models.listing import Listing
from src.models.raw_resume import RawResume
from src.prompts.job_matching import PROMPT as JOB_MATCHING_PROMPT
from src.resume_processing.nlp_resume_processor import NLPResumeProcessor
from src.utils.processing import ollama_api_call
from src.utils.resume_extraction import extract_text_from_pdf


async def main():
    resume_path = r"C:\Users\mateu\PycharmProjects\JSProject\job-scout\resources\Berlin-Simple-Resume-Template.pdf"
    resume_text = extract_text_from_pdf(resume_path)
    resume = RawResume(content=resume_text, internal_id="47")

    listing = Listing(internal_id="123", title="Software Engineer", company="Tech Company", remote=False,
                      description=r"Strong Java, Spring and TypeScript skills Performing code review for peers Experience in Unit Testing,"
                                  r" familiar with at least one testing and mocking framework"
                                  r"Ability to design an architecture of a feature or application from scratch"
                                  r"Strong Knowledge of data structures and algorithms"
                                  r"Deep Knowledge of OOP and design patternsGood English communication skills & experience in client-facing communications"
                                  r"Solid SDLC understanding and experience working in agile environment"
                                  r"Self-management and strong prioritization skills"
                                  r"Capability to work in agile environment without direct supervision")

    listing_processor = NLPListingProcessor()
    resume_processor = NLPResumeProcessor()

    processed_listings = await listing_processor.process_listings([listing])

    processed_resumes = await resume_processor.process_resumes([resume])

    processed_resumes_text = ", ".join(processed_resumes[0].keywords)
    processed_listings_text = ", ".join(processed_listings[0].keywords)
    print("Processed Resumes Keywords:{}".format(processed_resumes_text))
    print("Processed Listings Keywords:{}".format(processed_listings_text))

    prompt = JOB_MATCHING_PROMPT.format(processed_resumes_text, processed_listings_text)
    result = ollama_api_call('llama2', prompt).lower().strip()
    print(result)

    vec1 = torch.tensor(processed_listings[0].embedding)
    vec2 = torch.tensor(processed_resumes[0].embedding)
    cos_sim = torch.nn.functional.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
    print(f"Cosine Similarity: {cos_sim.item()}")


if __name__ == "__main__":
    asyncio.run(main())
