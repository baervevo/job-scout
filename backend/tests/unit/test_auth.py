"""
Unit tests for authentication routes and password utilities
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.db.schemas.user import User as UserSchema
from src.db.session import get_db
from src.utils.password import hash_password, verify_password

class TestAuthRoutes:
    """Test authentication routes functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "login": "testuser",
            "password": "testpassword123"
        }
    
    @pytest.mark.asyncio
    async def test_register_success(self, client, sample_user_data):
        """Test successful user registration."""
        # Mock the database dependency
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock no existing user found
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Mock user creation
        new_user = UserSchema(id=1, login="testuser", password="hashed_password")
        mock_session.refresh = AsyncMock()
        mock_session.refresh.side_effect = lambda user: setattr(user, 'id', 1)
        
        # Override the dependency
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            response = client.post("/auth/register", data=sample_user_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "user_id" in data
            
            # Verify database operations
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_register_existing_user(self, client, sample_user_data):
        """Test registration with existing user."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock existing user found
        existing_user = UserSchema(login="testuser", password="hashed_password")
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = existing_user
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            response = client.post("/auth/register", data=sample_user_data)
            
            assert response.status_code == 400
            assert "User already exists" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_register_missing_credentials(self, client):
        """Test registration with missing credentials."""
        response = client.post("/auth/register", data={"login": "testuser"})
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock user exists with correct password
        hashed_password = hash_password(sample_user_data["password"])
        user = UserSchema(
            id=1, 
            login=sample_user_data["login"], 
            password=hashed_password
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = user
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            response = client.post("/auth/login", data=sample_user_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["user_id"] == 1
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, client, sample_user_data):
        """Test login with non-existent user."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock user not found
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            response = client.post("/auth/login", data=sample_user_data)
            
            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, sample_user_data):
        """Test login with invalid password."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock user exists with different password
        user = UserSchema(
            id=1,
            login=sample_user_data["login"],
            password=hash_password("different_password")
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = user
        mock_session.execute.return_value = mock_result
        
        async def mock_get_db():
            return mock_session
        
        app.dependency_overrides[get_db] = mock_get_db
        
        try:
            response = client.post("/auth/login", data=sample_user_data)
            
            assert response.status_code == 401
            assert "Invalid credentials" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()

class TestPasswordUtils:
    """Test password utility functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False