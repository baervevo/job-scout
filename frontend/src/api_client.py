"""API client for communicating with the backend"""
import logging
from typing import List, Optional
import httpx
from src.models import Match, ListingKeywordData, Resume
from config import settings


class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.API_URL
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create a persistent HTTP client with session support"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                follow_redirects=True
            )
        return self._client

    async def _handle_auth_error(self, response: httpx.Response):
        """Handle authentication errors by redirecting to login"""
        if response.status_code == 401:
            logging.warning("Authentication failed - redirecting to login")
            from nicegui import ui
            ui.navigate.to('/login?msg=Session%20expired.%20Please%20log%20in%20again.')
            return True
        return False

    async def _make_request(self, method: str, url: str, **kwargs):
        """Make HTTP request with automatic auth error handling"""
        client = await self._get_client()
        response = await client.request(method, url, **kwargs)
        if await self._handle_auth_error(response):
            return type('MockResponse', (), {
                'json': lambda: {'error': 'Authentication required'},
                'content': b'',
                'status_code': 401
            })()
        response.raise_for_status()
        return response

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
        response = await self._make_request('POST', '/auth/logout')
        if response.status_code == 401:
            return {'success': True}
        result = response.json()
        if self._client:
            await self._client.aclose()
            self._client = None
        return result

    async def upload_resume(self, file_name: str, file_content: bytes, file_type: str, location: str = None, radius: int = None) -> dict:
        """Upload a resume file with optional location and radius"""
        files = {'file': (file_name, file_content, file_type)}
        data = {}
        if location:
            data['location'] = location
        if radius:
            data['radius'] = radius
        
        response = await self._make_request('POST', '/resumes/upload', files=files, data=data)
        if response.status_code == 401:
            raise httpx.HTTPStatusError("Authentication required", request=None, response=response)
        return response.json()

    async def get_resumes(self) -> List[Resume]:
        """Get user's resumes"""
        response = await self._make_request('GET', '/resumes/')
        if response.status_code == 401:
            raise httpx.HTTPStatusError("Authentication required", request=None, response=response)
        data = response.json()
        return [
            Resume(
                id=item['id'],
                user_id=item['user_id'],
                file_name=item['file_name'],
                uploaded_at=item.get('uploaded_at'),
                keywords=item.get('keywords', []),
                location=item.get('location'),
                radius=item.get('radius')
            )
            for item in data
        ]

    async def delete_resume(self, resume_id: int) -> dict:
        """Delete a resume"""
        response = await self._make_request('DELETE', f'/resumes/{resume_id}')
        if response.status_code == 401:
            raise httpx.HTTPStatusError("Authentication required", request=None, response=response)
        return response.json()

    async def download_resume(self, resume_id: int) -> bytes:
        """Download a resume file"""
        response = await self._make_request('GET', f'/resumes/{resume_id}/file')
        if response.status_code == 401:
            raise httpx.HTTPStatusError("Authentication required", request=None, response=response)
        return response.content

    async def get_matches(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get user's job matches"""
        response = await self._make_request('GET', '/matches/', params={'limit': limit, 'offset': offset})
        if response.status_code == 401:
            raise httpx.HTTPStatusError("Authentication required", request=None, response=response)
        return response.json()

    async def get_match_details(self, match_id: int) -> dict:
        """Get detailed information about a specific match"""
        response = await self._make_request('GET', f'/matches/{match_id}')
        if response.status_code == 401:
            raise httpx.HTTPStatusError("Authentication required", request=None, response=response)
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


api_client = APIClient()