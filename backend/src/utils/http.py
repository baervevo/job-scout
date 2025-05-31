from httpx import Client, Response
from typing import Callable, Optional, Any

class HTTPClient:
    def __init__(self, base_url: str):
        self.client = Client(base_url=base_url)
        self.callbacks: dict[int, Callable[[Response], Any]] = {}

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        response = self.client.request(method, endpoint, **kwargs)
        handler = self.callbacks.get(response.status_code)
        if handler:
            return handler(response)
        return self.default_handler(response)

    def get(self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
        return self._request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint: str, json: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
        return self._request("POST", endpoint, json=json, headers=headers)

    def put(self, endpoint: str, json: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
        return self._request("PUT", endpoint, json=json, headers=headers)

    def delete(self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
        return self._request("DELETE", endpoint, params=params, headers=headers)

    def on_status(self, status_code: int):
        def decorator(func: Callable[[Response], Any]) -> Callable[[Response], Any]:
            self.callbacks[status_code] = func
            return func
        return decorator

    def default_handler(self, response: Response) -> Any:
        response.raise_for_status()
