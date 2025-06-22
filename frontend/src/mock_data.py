# SAMPLE
from datetime import datetime

from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.match import Match
from src.models.resume.resume import Resume

path_pdf = r"resources/Berlin-Simple-Resume-Template.pdf"

sample_kw_list = ['Python', 'JavaScript', 'SQL', 'HTML', 'CSS', 'Django', 'Flask', 'React', 'Node.js']
resumes = [
    Resume(
        id="12345",
        user_id=1,
        file_name="example_resume",
        file_path=path_pdf,
        content="This is a sample resume content."
    ),
    Resume(
        id="67890",
        user_id=1,
        file_name="another_resume",
        file_path=path_pdf,
        content="This is another sample resume content."
    ),
    Resume(
        id="11223",
        user_id=1,
        file_name="cpp_resume",
        file_path=path_pdf,
        content="This is a C++ developer resume content."
    )
]

matches = [
    Match(
        resume_id="resume_001",
        listing_id="listing_001",  # ID now matches listing
        missing_keywords=["AWS", "Microservices"],  # missing keywords from listing
        cosine_similarity=0.92,
        summary="Strong match, but lacking some cloud infrastructure experience."
    ),
    Match(
        resume_id="resume_002",
        listing_id="listing_002",
        missing_keywords=["TensorFlow"],
        cosine_similarity=0.78,
        summary="Good ML background, but missing TensorFlow experience."
    ),
    Match(
        resume_id="resume_003",
        listing_id="listing_003",
        missing_keywords=["Leadership"],
        cosine_similarity=0.65,
        summary="Solid project management skills, but missing leadership experience."
    ),
    Match(
        resume_id="resume_004",
        listing_id="listing_004",
        missing_keywords=[],
        cosine_similarity=0.95,
        summary="Perfect match with all design skills covered."
    ),
    Match(
        resume_id="resume_005",
        listing_id="listing_005",
        missing_keywords=["Azure", "GCP"],
        cosine_similarity=0.80,
        summary="Good AWS experience, but missing multi-cloud expertise."
    ),
    Match(
        resume_id="resume_006",
        listing_id="listing_006",
        missing_keywords=["Analytics"],
        cosine_similarity=0.70,
        summary="Strong marketing skills, but lacking analytics experience."
    )
]

listings = [
    ListingKeywordData(
        title="Senior Software Engineer",
        company="TechCorp",
        description="Seeking experienced software engineer with Python and cloud experience.",
        remote=True,
        created_at=datetime(2025, 6, 10, 10, 30),
        updated_at=datetime(2025, 6, 15, 12, 0),
        salary_min=90000,
        salary_max=120000,
        currency="USD",
        location="Remote",
        link="https://techcorp.com/jobs/123",
        id="listing_001",
        keywords=["Python", "AWS", "Microservices", "Docker"],
        embedding=[0.12, 0.45, 0.87, 0.23, 0.56]
    ),
    ListingKeywordData(
        title="Data Scientist",
        company="DataX",
        description="Data scientist with strong ML and statistical skills.",
        remote=False,
        created_at=datetime(2025, 5, 20, 9, 0),
        updated_at=datetime(2025, 6, 18, 14, 30),
        salary_min=None,
        salary_max=None,
        currency="USD",
        location="New York, NY",
        link="https://datax.com/careers/456",
        id="listing_002",
        keywords=["Machine Learning", "Statistics", "Python", "TensorFlow"],
        embedding=[0.32, 0.15, 0.67, 0.78, 0.91]
    ),
    ListingKeywordData(
        title="Project Manager",
        company="BuildIt",
        description="Project manager with experience in Agile and cross-functional teams.",
        remote=True,
        created_at=datetime(2025, 4, 5, 11, 15),
        updated_at=datetime(2025, 6, 17, 16, 0),
        salary_min=70000,
        salary_max=95000,
        currency="USD",
        location="Remote",
        link="https://buildit.io/jobs/789",
        id="listing_003",
        keywords=["Agile", "Scrum", "Leadership", "Communication"],
        embedding=[0.21, 0.55, 0.77, 0.34, 0.68]
    ),
    ListingKeywordData(
        title="UX Designer",
        company="DesignPro",
        description="UX Designer with a strong portfolio and Figma expertise.",
        remote=False,
        created_at=datetime(2025, 6, 1, 8, 45),
        updated_at=datetime(2025, 6, 19, 10, 0),
        salary_min=60000,
        salary_max=85000,
        currency="USD",
        location="San Francisco, CA",
        link="https://designpro.com/careers/321",
        id="listing_004",
        keywords=["UX", "UI", "Figma", "Prototyping", "User Research"],
        embedding=[0.65, 0.32, 0.48, 0.91, 0.22]
    ),
    ListingKeywordData(
        title="Cloud Architect",
        company="SkyNet",
        description="Architect cloud solutions on AWS, Azure, and GCP platforms.",
        remote=True,
        created_at=datetime(2025, 3, 12, 14, 0),
        updated_at=datetime(2025, 6, 20, 9, 30),
        salary_min=110000,
        salary_max=150000,
        currency="USD",
        location="Remote",
        link="https://skynet.cloud/jobs/654",
        id="listing_005",
        keywords=["AWS", "Azure", "GCP", "Cloud Architecture", "DevOps"],
        embedding=[0.42, 0.56, 0.91, 0.13, 0.77]
    ),
    ListingKeywordData(
        title="Marketing Specialist",
        company="MarketGenius",
        description="Creative marketer with SEO, SEM, and social media experience.",
        remote=False,
        created_at=datetime(2025, 2, 8, 10, 0),
        updated_at=datetime(2025, 6, 19, 15, 0),
        salary_min=None,
        salary_max=None,
        currency=None,
        location="Austin, TX",
        link="https://marketgenius.com/jobs/987",
        id="listing_006",
        keywords=["SEO", "SEM", "Social Media", "Analytics"],
        embedding=[0.18, 0.44, 0.59, 0.72, 0.36]
    )
]