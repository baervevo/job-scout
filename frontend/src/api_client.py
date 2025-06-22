"""API client for communicating with the backend"""
import logging
from typing import List, Optional
import httpx
from src.models import Match, ListingKeywordData, Resume
from config import settings


class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.API_URL
        self._client = None  # Persistent client for session management

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create a persistent HTTP client with session support"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                follow_redirects=True
            )
        return self._client

    async def login(self, username: str, password: str) -> dict:
        """Login user"""
        client = await self._get_client()
        response = await client.post(
            '/auth/login',
            data={'login': username, 'password': password}
        )
        response.raise_for_status()
        return response.json()

    async def register(self, username: str, password: str) -> dict:
        """Register new user"""
        client = await self._get_client()
        response = await client.post(
            '/auth/register',
            data={'login': username, 'password': password}
        )
        response.raise_for_status()
        return response.json()

    async def logout(self) -> dict:
        """Logout user"""
        client = await self._get_client()
        response = await client.post('/auth/logout')
        response.raise_for_status()
        result = response.json()
        # Close the client to clear session
        if self._client:
            await self._client.aclose()
            self._client = None
        return result

    async def upload_resume(self, file_name: str, file_content: bytes, file_type: str) -> dict:
        """Upload a resume file"""
        client = await self._get_client()
        files = {'file': (file_name, file_content, file_type)}
        response = await client.post('/resumes/upload', files=files)
        response.raise_for_status()
        return response.json()

    async def get_resumes(self) -> List[Resume]:
        """Get user's resumes"""
        client = await self._get_client()
        response = await client.get('/resumes/')
        response.raise_for_status()
        data = response.json()
        return [
            Resume(
                id=item['id'],
                user_id=item['user_id'],
                file_name=item['file_name'],
                uploaded_at=item.get('uploaded_at'),
                keywords=item.get('keywords', [])
            )
            for item in data
        ]

    async def delete_resume(self, resume_id: int) -> dict:
        """Delete a resume"""
        client = await self._get_client()
        response = await client.delete(f'/resumes/{resume_id}')
        response.raise_for_status()
        return response.json()

    async def download_resume(self, resume_id: int) -> bytes:
        """Download a resume file"""
        client = await self._get_client()
        response = await client.get(f'/resumes/{resume_id}/file')
        response.raise_for_status()
        return response.content

    async def get_matches(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get user's job matches"""
        client = await self._get_client()
        response = await client.get(
            '/matches/',
            params={'limit': limit, 'offset': offset}
        )
        response.raise_for_status()
        return response.json()

    async def get_match_details(self, match_id: int) -> dict:
        """Get detailed information about a specific match"""
        client = await self._get_client()
        response = await client.get(f'/matches/{match_id}')
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# Global API client instance
api_client = APIClient()