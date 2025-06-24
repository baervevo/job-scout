# JobScout Backend Testing Guide

This directory contains comprehensive unit and integration tests for the JobScout backend application.

## 🧪 Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_auth.py         # Authentication routes and password utilities
│   ├── test_resume_processing.py # Resume processing and file handling
│   ├── test_matching_processor.py # Job-resume matching algorithms
│   ├── test_resume_routes.py # Resume API endpoints
│   ├── test_scraping.py     # Job scraping functionality
│   └── test_models_and_utils.py # Data models and utility functions
├── integration/             # Integration tests
│   └── test_integration.py  # End-to-end workflow tests
└── README.md               # This file
```

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests with our custom runner
./run_tests.py

# Or use poetry directly
poetry run pytest
```

### Specific Test Categories

#### Unit Tests Only
```bash
poetry run pytest tests/unit/ -v
```

#### Integration Tests Only
```bash
poetry run pytest tests/integration/ -v
```

#### Specific Test Files
```bash
# Authentication tests
poetry run pytest tests/unit/test_auth.py -v

# Resume processing tests
poetry run pytest tests/unit/test_resume_processing.py -v

# Matching algorithm tests
poetry run pytest tests/unit/test_matching_processor.py -v
```

#### With Coverage
```bash
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Test Markers
```bash
# Run only fast tests
poetry run pytest -m "not slow"

# Run only integration tests
poetry run pytest -m integration

# Run only unit tests
poetry run pytest -m unit
```

## 📊 Test Coverage

The test suite covers:

### 🔐 Authentication (`test_auth.py`)
- User registration and login
- Password hashing and verification
- Session management
- Error handling for invalid credentials

### 📄 Resume Processing (`test_resume_processing.py`)
- PDF file upload and validation
- Text extraction from resumes
- AI-powered keyword extraction
- Fallback mechanisms when AI services fail

### 🎯 Matching Algorithm (`test_matching_processor.py`)
- Cosine similarity calculations
- Missing keyword identification
- AI-generated match summaries
- Threshold-based filtering
- Error handling and edge cases

### 🛣️ API Routes (`test_resume_routes.py`)
- Resume upload, download, listing, deletion
- Authentication and authorization
- File handling and validation
- Error responses and status codes

### 🕷️ Scraping (`test_scraping.py`)
- Jooble API integration
- Job data parsing and validation
- Salary range extraction
- HTML content cleaning
- Network error handling

### 📊 Data Models & Utils (`test_models_and_utils.py`)
- Pydantic model validation
- Password hashing utilities
- Configuration settings
- Utility function testing

### 🔄 Integration Tests (`test_integration.py`)
- Complete user workflows
- Component integration
- End-to-end data flow

## 🛠️ Test Configuration

### Pytest Configuration
The tests use the following configuration (in `pyproject.toml`):
- Coverage reporting with 80% minimum threshold
- HTML coverage reports in `htmlcov/`
- Async test support
- Custom markers for test categorization

### Test Database
Integration tests use a temporary SQLite database that's automatically created and cleaned up.

### Mocking Strategy
- External APIs (Ollama, Jooble) are mocked
- Database operations use async mocks
- File operations use temporary directories

## 🎯 Key Testing Patterns

### Async Testing
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Database Testing
```python
async def test_database_operation(test_db):
    async with test_db() as session:
        # Database operations
        pass
```

### API Testing
```python
def test_api_endpoint(authenticated_session):
    response = authenticated_session.get("/api/endpoint")
    assert response.status_code == 200
```

### File Handling Testing
```python
def test_file_operation(temp_resume_dir):
    test_file = temp_resume_dir / "test.pdf"
    # File operations
```

## 📈 Coverage Goals

- **Overall Coverage**: 80%+ 
- **Critical Paths**: 95%+ (auth, processing, matching)
- **API Routes**: 90%+
- **Utility Functions**: 85%+

## 🐛 Debugging Failed Tests

### Common Issues
1. **Import Errors**: Check Python path and dependencies
2. **Async Issues**: Ensure proper `@pytest.mark.asyncio` decoration
3. **Mock Failures**: Verify mock patches target correct modules
4. **Database Issues**: Check test database setup in `conftest.py`

### Verbose Output
```bash
poetry run pytest -v -s --tb=long
```

### Debug Specific Test
```bash
poetry run pytest tests/unit/test_auth.py::TestAuthRoutes::test_login_success -v -s
```

## 🔧 Test Dependencies

The test suite requires:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support  
- `pytest-mock` - Mocking utilities
- `pytest-cov` - Coverage reporting
- `aiosqlite` - Async SQLite for testing
- `httpx` - HTTP client for API testing

## 📝 Writing New Tests

### Test File Structure
```python
"""
Unit tests for [component name]
"""
import pytest
from unittest.mock import patch, AsyncMock

class Test[ComponentName]:
    """Test [component] functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample test data."""
        return {"key": "value"}
    
    def test_basic_functionality(self, sample_data):
        """Test basic functionality."""
        # Test implementation
        pass
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        # Async test implementation
        pass
```

### Best Practices
1. Use descriptive test names
2. Test both success and failure cases
3. Mock external dependencies
4. Use fixtures for common test data
5. Keep tests focused and atomic
6. Add docstrings explaining test purpose

## 🚀 Continuous Integration

For CI/CD pipelines, use:
```bash
# Install dependencies
poetry install --with test

# Run tests with coverage
poetry run pytest --cov=src --cov-report=xml

# Check coverage threshold
poetry run coverage report --fail-under=80
```