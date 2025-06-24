"""
Unit tests for job scraping functionality
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
import httpx

from src.scraping.scrapers.jooble_scraper import JoobleScraper
from src.models.listing.listing import Listing
from src.models.query import Query

class TestJoobleScraper:
    """Test Jooble scraper functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create Jooble scraper instance."""
        with patch('config.settings') as mock_settings:
            mock_settings.JOOBLE_API_KEY = "test_api_key"
            return JoobleScraper("test_api_key", "https://jooble.org")
    
    @pytest.fixture
    def sample_query(self):
        """Sample query for testing."""
        return Query(
            keywords=("python", "django"),
            location="New York",
            radius="50"
        )
    
    @pytest.fixture
    def sample_jooble_response(self):
        """Sample Jooble API response."""
        return {
            "totalCount": 100,
            "jobs": [
                {
                    "id": "12345",
                    "title": "Senior Python Developer",
                    "company": "Tech Corp",
                    "location": "New York, NY",
                    "snippet": "Looking for experienced Python developer with Django knowledge",
                    "salary": "$80,000 - $120,000",
                    "updated": "2024-01-15T10:00:00Z",
                    "link": "https://example.com/job/12345"
                },
                {
                    "id": "67890",
                    "title": "Full Stack Developer",
                    "company": "StartupXYZ",
                    "location": "Remote",
                    "snippet": "Full stack position using Python and React",
                    "salary": "",
                    "updated": "2024-01-14T15:30:00Z",
                    "link": "https://example.com/job/67890"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_execute_query_success(self, scraper, sample_query, sample_jooble_response):
        """Test successful job scraping."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_jooble_response
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            listings = await scraper.execute_query(sample_query)
            
            assert len(listings) == 2
            assert listings[0].title == "Senior Python Developer"
            assert listings[0].company == "Tech Corp"
            assert listings[0].location == "New York, NY"
            assert listings[1].remote is True  # Remote location
    
    @pytest.mark.asyncio
    async def test_execute_query_api_error(self, scraper, sample_query):
        """Test scraping with API error."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.HTTPStatusError(
                "API Error", request=MagicMock(), response=MagicMock()
            )
            
            listings = await scraper.execute_query(sample_query)
            
            assert listings == []
    
    @pytest.mark.asyncio
    async def test_execute_query_network_error(self, scraper, sample_query):
        """Test scraping with network error."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")
            
            listings = await scraper.execute_query(sample_query)
            
            assert listings == []
    
    @pytest.mark.asyncio
    async def test_execute_query_invalid_json(self, scraper, sample_query):
        """Test scraping with invalid JSON response."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            listings = await scraper.execute_query(sample_query)
            
            assert listings == []
    
    def test_parse_response_empty(self, scraper):
        """Test parsing empty response."""
        empty_response = {"jobs": []}
        listings = scraper._parse_response(empty_response)
        
        assert listings == []
    
    def test_parse_response_missing_fields(self, scraper):
        """Test parsing response with missing fields."""
        response_with_missing = {
            "jobs": [
                {
                    "id": "123",
                    "title": "Developer",
                    # Missing company, location, etc.
                }
            ]
        }
        listings = scraper._parse_response(response_with_missing)
        
        assert len(listings) == 1
        assert listings[0].title == "Developer"
        assert listings[0].company == ""  # Default value
        assert listings[0].location == ""  # Default value

class TestSalaryParsing:
    """Test salary parsing utilities."""
    
    def test_parse_salary_range_usd(self):
        """Test parsing USD salary range."""
        from src.utils.salary import parse_salary_range
        
        min_sal, max_sal, currency = parse_salary_range("80,000 USD - 120,000 USD")
        
        assert min_sal == 80000
        assert max_sal == 120000
        assert currency == "USD"
    
    def test_parse_salary_range_single_value(self):
        """Test parsing single salary value."""
        from src.utils.salary import parse_salary_range
        
        min_sal, max_sal, currency = parse_salary_range("100,000 USD")
        
        assert min_sal == 100000
        assert max_sal == 100000
        assert currency == "USD"
    
    def test_parse_salary_range_empty(self):
        """Test parsing empty salary."""
        from src.utils.salary import parse_salary_range
        
        min_sal, max_sal, currency = parse_salary_range("")
        
        assert min_sal is None
        assert max_sal is None
        assert currency is None
    
    def test_parse_salary_range_invalid_format(self):
        """Test parsing invalid salary format."""
        from src.utils.salary import parse_salary_range
        
        min_sal, max_sal, currency = parse_salary_range("Competitive salary")
        
        assert min_sal is None
        assert max_sal is None
        assert currency is None

class TestProcessingUtils:
    """Test processing utilities."""
    
    def test_clean_html_text(self):
        """Test HTML text cleaning."""
        from src.utils.processing_utils import clean_html_text
        
        html_text = "<p>This is a <strong>job description</strong> with <a href='#'>links</a>.</p>"
        cleaned = clean_html_text(html_text)
        
        assert "<p>" not in cleaned
        assert "<strong>" not in cleaned
        assert "<a" not in cleaned
        assert "This is a job description with links." in cleaned
    
    def test_format_keywords(self):
        """Test keyword formatting."""
        from src.utils.processing_utils import format_keywords
        
        raw_keywords = "1. Python\n2. Django\n3. FastAPI\n4. REST API"
        formatted = format_keywords(raw_keywords)
        
        # The function adds commas and removes numbering
        assert "Python," in formatted
        assert "Django," in formatted
        assert "FastAPI," in formatted
        assert "REST API," in formatted
    
    def test_kw_text_to_list(self):
        """Test converting keyword text to list."""
        from src.utils.processing_utils import kw_text_to_list
        
        # The function processes each line separately
        kw_text = "python\ndjango\nfastapi\nrest api"
        kw_list = kw_text_to_list(kw_text)
        
        assert "python" in kw_list
        assert "django" in kw_list
        assert "fastapi" in kw_list
        assert "rest api" in kw_list
    
    def test_kw_text_to_list_empty(self):
        """Test converting empty keyword text."""
        from src.utils.processing_utils import kw_text_to_list
        
        kw_list = kw_text_to_list("")
        
        assert kw_list == []
    
    @pytest.mark.asyncio
    async def test_ollama_api_call_async_success(self):
        """Test successful Ollama API call."""
        with patch('src.utils.processing_utils.ollama') as mock_ollama:
            from src.utils.processing_utils import ollama_api_call_async
            
            mock_response = {"message": {"content": "python, django, fastapi"}}
            mock_ollama.chat.return_value = mock_response
            
            result = await ollama_api_call_async("Test prompt", "llama3")
            
            assert result == "python, django, fastapi"
    
    @pytest.mark.asyncio
    async def test_ollama_api_call_async_disabled(self):
        """Test Ollama API call when disabled."""
        # Import inside the test with proper mocking
        with patch('src.utils.processing_utils.settings') as mock_settings:
            mock_settings.OLLAMA_ENABLED = False
            
            from src.utils.processing_utils import ollama_api_call_async
            
            result = await ollama_api_call_async("Test prompt", "llama3")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_ollama_api_call_async_error(self):
        """Test Ollama API call with error."""
        with patch('config.settings') as mock_settings:
            mock_settings.OLLAMA_ENABLED = True
            
            with patch('src.utils.processing_utils.ollama') as mock_ollama:
                from src.utils.processing_utils import ollama_api_call_async
                
                mock_ollama.chat.side_effect = Exception("API Error")
                
                # The function should handle the exception and re-raise it
                with pytest.raises(Exception, match="API Error"):
                    await ollama_api_call_async("Test prompt", "llama3")