"""
Unit tests for resume processing functionality
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import tempfile

from src.processing.resume_processor import ResumeProcessor
from src.models.resume.resume import Resume
from src.models.resume.resume_keyword_data import ResumeKeywordData

class TestResumeProcessor:
    """Test resume processing functionality."""
    
    @pytest.fixture
    def processor(self, mock_embedding_model):
        """Create resume processor with mocked embedding model."""
        with patch('src.processing.resume_processor.Processor.__init__'):
            processor = ResumeProcessor()
            processor.embed_text = mock_embedding_model.embed_text
            processor.extract_keywords = MagicMock(return_value=["python", "django", "fastapi"])
            processor.llm_model_name = "test_model"
            return processor
    
    @pytest.mark.asyncio
    async def test_process_resume_with_ollama_success(self, processor, sample_resume, mock_ollama_api):
        """Test successful resume processing with Ollama."""
        with patch('src.processing.resume_processor.ollama_api_call_async', mock_ollama_api):
            with patch('src.processing.resume_processor.format_keywords') as mock_format:
                with patch('src.processing.resume_processor.kw_text_to_list') as mock_to_list:
                    mock_format.return_value = "python, django, fastapi"
                    mock_to_list.return_value = ["python", "django", "fastapi"]
                    
                    result = await processor.process_resume(sample_resume)
                    
                    assert isinstance(result, ResumeKeywordData)
                    assert result.id == sample_resume.id  # Both should be strings
                    assert result.user_id == sample_resume.user_id  # Both should be integers
                    assert result.keywords == ["python", "django", "fastapi"]
                    assert len(result.embedding) == 5
    
    @pytest.mark.asyncio
    async def test_process_resume_ollama_fallback(self, processor, sample_resume):
        """Test resume processing with Ollama failure, falling back to keyword extraction."""
        with patch('src.processing.resume_processor.ollama_api_call_async') as mock_ollama:
            mock_ollama.side_effect = Exception("Ollama failed")
            
            result = await processor.process_resume(sample_resume)
            
            assert isinstance(result, ResumeKeywordData)
            assert result.keywords == ["python", "django", "fastapi"]  # From fallback
            processor.extract_keywords.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_resume_none_response(self, processor, sample_resume):
        """Test resume processing when Ollama returns None."""
        with patch('src.processing.resume_processor.ollama_api_call_async') as mock_ollama:
            mock_ollama.return_value = None
            
            result = await processor.process_resume(sample_resume)
            
            assert isinstance(result, ResumeKeywordData)
            assert result.keywords == ["python", "django", "fastapi"]  # From fallback
    
    @pytest.mark.asyncio
    async def test_process_resumes_multiple(self, processor):
        """Test processing multiple resumes."""
        resumes = [
            Resume(id="1", user_id=1, file_name="resume1.pdf", file_path="/tmp/1.pdf", content="Python developer"),
            Resume(id="2", user_id=1, file_name="resume2.pdf", file_path="/tmp/2.pdf", content="Java developer")
        ]
        
        with patch.object(processor, 'process_resume') as mock_process:
            mock_process.side_effect = [
                ResumeKeywordData(id="1", user_id=1, file_name="resume1.pdf", file_path="/tmp/1.pdf", 
                                content="Python developer", keywords=["python"], embedding=[0.1]),
                ResumeKeywordData(id="2", user_id=1, file_name="resume2.pdf", file_path="/tmp/2.pdf",
                                content="Java developer", keywords=["java"], embedding=[0.2])
            ]
            
            results = await processor.process_resumes(resumes)
            
            assert len(results) == 2
            assert results[0].keywords == ["python"]
            assert results[1].keywords == ["java"]
            assert mock_process.call_count == 2

class TestResumeFileHandling:
    """Test resume file handling utilities."""
    
    def test_validate_file_valid_pdf(self):
        """Test file validation with valid PDF."""
        from src.routes.resumes import validate_file
        from fastapi import UploadFile
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_resume.pdf"
        
        # Should not raise exception
        validate_file(mock_file)
    
    def test_validate_file_invalid_extension(self):
        """Test file validation with invalid extension."""
        from src.routes.resumes import validate_file
        from fastapi import UploadFile, HTTPException
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_resume.txt"
        
        with pytest.raises(HTTPException) as exc_info:
            validate_file(mock_file)
        
        assert exc_info.value.status_code == 400
        assert "not allowed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_save_file_async(self, temp_resume_dir):
        """Test async file saving."""
        from src.routes.resumes import save_file_async
        from fastapi import UploadFile
        
        # Create mock file
        mock_file = MagicMock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=b"test content")
        
        file_path = temp_resume_dir / "test_file.pdf"
        
        await save_file_async(mock_file, file_path)
        
        assert file_path.exists()
        assert file_path.read_bytes() == b"test content"
    
    @pytest.mark.asyncio
    async def test_process_resume_content(self, temp_resume_dir):
        """Test PDF content extraction."""
        from src.routes.resumes import process_resume_content
        
        # Create a test file
        test_file = temp_resume_dir / "test.pdf"
        test_file.write_bytes(b"dummy pdf content")
        
        with patch('src.routes.resumes.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Extracted text content"
            
            content = await process_resume_content(test_file)
            
            assert content == "Extracted text content"
            # Fix: convert Path to string for comparison
            mock_extract.assert_called_once_with(str(test_file))