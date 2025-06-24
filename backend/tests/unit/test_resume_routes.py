"""
Unit tests for resume API routes
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile, Request
from pathlib import Path
import tempfile
import io

from src.app import app
from src.db.schemas.resume import Resume as ResumeSchema
from src.db.schemas.user import User as UserSchema
from src.db.session import get_db
from src.processing.resume_processing_queue import get_resume_processing_queue

class TestResumeRoutes:
    """Test resume API routes functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_authenticated_request(self):
        """Mock an authenticated request."""
        mock_request = MagicMock(spec=Request)
        mock_request.session = {"user_id": 1}
        return mock_request
    
    @pytest.fixture
    def mock_unauthenticated_request(self):
        """Mock an unauthenticated request."""
        mock_request = MagicMock(spec=Request)
        mock_request.session = {}
        return mock_request
    
    @pytest.mark.asyncio
    async def test_upload_resume_success(self, client, temp_resume_dir, mock_authenticated_request):
        """Test successful resume upload."""
        # Mock database
        mock_session = AsyncMock()
        user = UserSchema(id=1, login="testuser", password="hash")
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = user
        mock_session.execute.return_value = mock_result
        
        # Mock resume creation
        resume_db = ResumeSchema(id=1, user_id=1, file_name="test.pdf", file_path="/tmp/test.pdf")
        mock_session.refresh.side_effect = lambda r: setattr(r, 'id', 1)
        
        # Mock processing queue
        mock_queue = MagicMock()
        
        async def mock_get_db():
            return mock_session
        
        def mock_get_queue():
            return mock_queue
        
        # Override dependencies
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[get_resume_processing_queue] = mock_get_queue
        
        # Mock file operations and request
        with patch('src.routes.resumes.UPLOAD_DIR', temp_resume_dir):
            with patch('src.routes.resumes.save_file_async') as mock_save:
                with patch('src.routes.resumes.process_resume_content') as mock_process:
                    with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
                        mock_save.return_value = None
                        mock_process.return_value = "extracted text"
                        
                        # Create test file
                        file_content = b"dummy pdf content"
                        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
                        data = {"location": "New York", "radius": "50"}
                        
                        response = client.post("/resumes/upload", files=files, data=data)
                        
                        assert response.status_code == 200
                        result = response.json()
                        assert result["success"] is True
                        assert "resume_id" in result
        
        # Clean up
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_upload_resume_unauthenticated(self, client, mock_unauthenticated_request):
        """Test resume upload without authentication."""
        with patch('src.routes.resumes.Request', return_value=mock_unauthenticated_request):
            file_content = b"dummy pdf content"
            files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
            
            response = client.post("/resumes/upload", files=files)
            
            assert response.status_code == 401
            assert "User not authenticated" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_resume_invalid_file_type(self, client, mock_authenticated_request):
        """Test resume upload with invalid file type."""
        with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
            file_content = b"dummy content"
            files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
            
            response = client.post("/resumes/upload", files=files)
            
            assert response.status_code == 400
            assert "not allowed" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_user_resumes_success(self, client, mock_authenticated_request):
        """Test getting user resumes."""
        mock_session = AsyncMock()
        
        # Mock resumes
        resume1 = ResumeSchema(
            id=1, user_id=1, file_name="resume1.pdf",
            keywords="python,django", location="New York", radius=50
        )
        resume2 = ResumeSchema(
            id=2, user_id=1, file_name="resume2.pdf",
            keywords="java,spring", location="Boston", radius=25
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [resume1, resume2]
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
                response = client.get("/resumes/")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["file_name"] == "resume1.pdf"
                assert data[0]["keywords"] == ["python", "django"]
                assert data[0]["location"] == "New York"
                assert data[0]["radius"] == 50
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_user_resumes_unauthenticated(self, client, mock_unauthenticated_request):
        """Test getting resumes without authentication."""
        with patch('src.routes.resumes.Request', return_value=mock_unauthenticated_request):
            response = client.get("/resumes/")
            
            assert response.status_code == 401
            assert "User not authenticated" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_download_resume_success(self, client, temp_resume_dir, mock_authenticated_request):
        """Test resume file download."""
        mock_session = AsyncMock()
        
        # Create test file
        test_file = temp_resume_dir / "test_resume.pdf"
        test_file.write_bytes(b"test pdf content")
        
        # Mock resume exists
        resume = ResumeSchema(
            id=1, user_id=1, file_name="test_resume.pdf",
            file_path=str(test_file)
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = resume
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
                response = client.get("/resumes/1/file")
                
                assert response.status_code == 200
                assert response.content == b"test pdf content"
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_download_resume_not_found(self, client, mock_authenticated_request):
        """Test downloading non-existent resume."""
        mock_session = AsyncMock()
        
        # Mock resume not found
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
                response = client.get("/resumes/999/file")
                
                assert response.status_code == 404
                assert "Resume not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_delete_resume_success(self, client, temp_resume_dir, mock_authenticated_request):
        """Test successful resume deletion."""
        mock_session = AsyncMock()
        
        # Create test file
        test_file = temp_resume_dir / "test_resume.pdf"
        test_file.write_bytes(b"test content")
        
        # Mock resume exists
        resume = ResumeSchema(
            id=1, user_id=1, file_name="test_resume.pdf",
            file_path=str(test_file)
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = resume
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
                response = client.delete("/resumes/1")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "deleted successfully" in data["message"]
                
                # Verify file deletion called
                mock_session.delete.assert_called_once_with(resume)
                mock_session.commit.assert_called_once()
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_delete_resume_not_found(self, client, mock_authenticated_request):
        """Test deleting non-existent resume."""
        mock_session = AsyncMock()
        
        # Mock resume not found
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            with patch('src.routes.resumes.Request', return_value=mock_authenticated_request):
                response = client.delete("/resumes/999")
                
                assert response.status_code == 404
                assert "Resume not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_delete_resume_unauthenticated(self, client, mock_unauthenticated_request):
        """Test deleting resume without authentication."""
        with patch('src.routes.resumes.Request', return_value=mock_unauthenticated_request):
            response = client.delete("/resumes/1")
            
            assert response.status_code == 401
            assert "User not authenticated" in response.json()["detail"]