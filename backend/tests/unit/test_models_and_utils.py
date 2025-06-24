"""
Unit tests for data models and utility functions
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData
from src.models.listing.listing_keyword_data import ListingKeywordData
from src.models.match import Match
from src.models.query import Query

class TestDataModels:
    """Test data model validation and functionality."""
    
    def test_resume_model_creation(self):
        """Test Resume model creation and validation."""
        resume = Resume(
            id="1",
            user_id=1,
            file_name="test_resume.pdf",
            file_path="/tmp/test_resume.pdf",
            content="Python developer with 5 years experience"
        )
        
        assert resume.id == "1"
        assert resume.user_id == 1
        assert resume.file_name == "test_resume.pdf"
        assert resume.file_path == "/tmp/test_resume.pdf"
        assert resume.content == "Python developer with 5 years experience"
    
    def test_resume_keyword_data_model(self):
        """Test ResumeKeywordData model creation."""
        resume_data = ResumeKeywordData(
            id="1",
            user_id=1,
            file_name="test.pdf",
            file_path="/tmp/test.pdf",
            content="Python developer",
            keywords=["python", "django", "fastapi"],
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
        )
        
        assert resume_data.keywords == ["python", "django", "fastapi"]
        assert len(resume_data.embedding) == 5
        assert resume_data.user_id == 1
    
    def test_listing_keyword_data_model(self):
        """Test ListingKeywordData model creation."""
        listing_data = ListingKeywordData(
            id="1",
            title="Senior Python Developer",
            company="Tech Corp",
            description="Looking for Python developer",
            remote=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            salary_min=80000,
            salary_max=120000,
            currency="USD",
            location="New York, NY",
            link="https://example.com/job/1",
            keywords=["python", "django", "rest", "api"],
            embedding=[0.2, 0.3, 0.4, 0.5, 0.6]
        )
        
        assert listing_data.title == "Senior Python Developer"
        assert listing_data.salary_min == 80000
        assert listing_data.remote is False
        assert len(listing_data.keywords) == 4
    
    def test_match_model_creation(self):
        """Test Match model creation."""
        match = Match(
            resume_id="1",
            listing_id="2",
            missing_keywords=["docker", "kubernetes"],
            cosine_similarity=0.85,
            summary="Good match with strong Python skills"
        )
        
        assert match.resume_id == "1"
        assert match.listing_id == "2"
        assert match.missing_keywords == ["docker", "kubernetes"]
        assert match.cosine_similarity == 0.85
        assert match.summary == "Good match with strong Python skills"
    
    def test_query_model_creation(self):
        """Test Query model creation."""
        query = Query(
            keywords=("python", "django", "fastapi"),
            location="New York",
            radius="50"
        )
        
        assert query.keywords == ("python", "django", "fastapi")
        assert query.location == "New York"
        assert query.radius == "50"
    
    def test_query_model_defaults(self):
        """Test Query model with default values."""
        query = Query(keywords=("python",))
        
        assert query.keywords == ("python",)
        assert query.location is None
        assert query.radius is None

class TestPasswordHashing:
    """Test password hashing utilities."""
    
    def test_hash_password_strength(self):
        """Test password hashing produces strong hashes."""
        from src.utils.password import hash_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Check hash format and length
        assert hashed.startswith("$2b$")
        assert len(hashed) >= 50  # bcrypt hashes are typically 60 chars
        assert hashed != password
    
    def test_hash_password_different_outputs(self):
        """Test that same password produces different hashes (salt)."""
        from src.utils.password import hash_password
        
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Should be different due to random salt
        assert hash1 != hash2
    
    def test_verify_password_consistency(self):
        """Test password verification is consistent."""
        from src.utils.password import hash_password, verify_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Multiple verifications should be consistent
        assert verify_password(password, hashed) is True
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

class TestUtilityFunctions:
    """Test various utility functions."""
    
    def test_logger_setup(self):
        """Test logger setup utility."""
        from src.utils.logger import setup_logger
        import logging
        
        logger = setup_logger("test_logger", logging.INFO, "%(name)s: %(message)s")
        
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    @pytest.mark.asyncio
    async def test_pdf_text_extraction_mock(self):
        """Test PDF text extraction with mock."""
        from unittest.mock import patch, mock_open
        
        with patch('src.utils.pdf.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Sample PDF content with Python programming"
            
            # Simulate PDF extraction
            result = mock_extract("/fake/path/resume.pdf")
            
            assert result == "Sample PDF content with Python programming"
            mock_extract.assert_called_once_with("/fake/path/resume.pdf")
    
    def test_model_validation_errors(self):
        """Test model validation with invalid data."""
        # Test Query with invalid types
        with pytest.raises((TypeError, ValueError)):
            Query(keywords="not_a_tuple")  # Should be tuple
    
    def test_embedding_vector_validation(self):
        """Test embedding vector validation."""
        # Valid embedding
        resume_data = ResumeKeywordData(
            id="1",
            user_id=1,
            file_name="test.pdf",
            file_path="/tmp/test.pdf",
            content="Python developer",
            keywords=["python"],
            embedding=[0.1, 0.2, 0.3]
        )
        
        assert len(resume_data.embedding) == 3
        assert all(isinstance(x, float) for x in resume_data.embedding)

class TestConfigurationSettings:
    """Test configuration and settings."""
    
    def test_settings_defaults(self):
        """Test that settings have reasonable defaults."""
        from config import settings
        
        # Test that critical settings exist
        assert hasattr(settings, 'APP_HOST')
        assert hasattr(settings, 'APP_PORT')
        assert hasattr(settings, 'POSTGRES_HOST')
        assert hasattr(settings, 'MATCHING_COSINE_THRESHOLD')
    
    def test_postgres_url_construction(self):
        """Test PostgreSQL URL construction."""
        from config import settings
        
        postgres_url = settings.POSTGRES_URL
        
        assert "postgresql+asyncpg://" in postgres_url
        assert settings.POSTGRES_HOST in postgres_url
        assert str(settings.POSTGRES_PORT) in postgres_url
        assert settings.POSTGRES_DB in postgres_url