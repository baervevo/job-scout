"""
Test configuration and fixtures for JobScout backend tests
"""
import asyncio
import pytest
import tempfile
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.db.base import Base
from src.db.session import get_db
from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.match import Match
from src.app import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_jobscout.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create a test database and clean up after tests."""
    # Create test database
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create async session
    TestingSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal
    
    # Cleanup
    await engine.dispose()
    app.dependency_overrides.clear()
    
    # Remove test database file
    if Path("./test_jobscout.db").exists():
        Path("./test_jobscout.db").unlink()

@pytest.fixture
def temp_resume_dir():
    """Create a temporary directory for resume files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def sample_resume():
    """Sample resume data for testing."""
    return Resume(
        id="1",
        user_id=1,
        file_name="test_resume.pdf",
        file_path="/tmp/test_resume.pdf",
        content="Python developer with 5 years experience in Django, FastAPI, PostgreSQL"
    )

@pytest.fixture
def sample_resume_keyword_data():
    """Sample resume keyword data for testing."""
    return ResumeKeywordData(
        id="1",
        user_id=1,
        file_name="test_resume.pdf",
        file_path="/tmp/test_resume.pdf",
        content="Python developer with 5 years experience",
        keywords=["python", "django", "fastapi", "postgresql"],
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
    )

@pytest.fixture
def sample_listing_keyword_data():
    """Sample listing keyword data for testing."""
    return ListingKeywordData(
        id="1",
        title="Senior Python Developer",
        company="Tech Corp",
        description="Looking for Python developer with Django experience",
        remote=False,
        created_at=None,
        updated_at=None,
        salary_min=80000,
        salary_max=120000,
        currency="USD",
        location="New York, NY",
        link="https://example.com/job/1",
        keywords=["python", "django", "rest", "api"],
        embedding=[0.2, 0.3, 0.4, 0.5, 0.6]
    )

@pytest.fixture
def sample_match():
    """Sample match data for testing."""
    return Match(
        resume_id="1",
        listing_id="1",
        missing_keywords=["rest", "api"],
        cosine_similarity=0.85,
        summary="Good match with strong Python skills"
    )

@pytest.fixture
def mock_ollama_api():
    """Mock Ollama API calls."""
    return AsyncMock(return_value="python, django, fastapi, postgresql")

@pytest.fixture
def mock_embedding_model():
    """Mock embedding model for testing."""
    import numpy as np
    mock = MagicMock()
    # Return numpy array so .tolist() works
    mock.embed_text.return_value = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    return mock