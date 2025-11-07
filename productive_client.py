import httpx
from typing import Dict, Any, Optional
from config import config

class ProductiveAPIError(Exception):
    """Custom exception for Productive API errors"""
    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ProductiveClient:
    """Async HTTP client for Productive API"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers=config.headers
        )

    async def _request(self, method: str, endpoint: str, params: Optional[dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Productive API"""
        url = f"{config.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise ProductiveAPIError("Unauthorized: Invalid API token", 401, "UNAUTHORIZED")
            elif response.status_code == 404:
                raise ProductiveAPIError("Resource not found", 404, "NOT_FOUND")
            elif response.status_code == 429:
                raise ProductiveAPIError("Rate limit exceeded", 429, "RATE_LIMIT")
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "Unknown error")
                    error_code = error_data.get("errorCode", "UNKNOWN")
                    raise ProductiveAPIError(error_message, response.status_code, error_code)
                except Exception:
                    raise ProductiveAPIError(
                        f"HTTP {response.status_code}: {response.text}",
                        response.status_code
                    )
                    
        except httpx.RequestError as e:
            raise ProductiveAPIError(f"Request failed: {str(e)}")

    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects"""
        return await self._request("GET", "/projects")

    async def get_tasks(self, params: Optional[dict] = None) -> Dict[str, Any]:
        """Get all tasks
        """
        return await self._request("GET", "/tasks", params=params)

    async def get_task(self, task_id: int) -> Dict[str, Any]:
        """Get task by ID"""
        return await self._request("GET", f"/tasks/{str(task_id)}")

    async def get_comments(self, params: Optional[dict] = None) -> Dict[str, Any]:
        """Get all comments
        """
        return await self._request("GET", "/comments", params=params)

    async def get_comment(self, comment_id: int) -> Dict[str, Any]:
        """Get comment by ID"""
        return await self._request("GET", f"/comments/{str(comment_id)}")

    async def get_todos(self, params: Optional[dict] = None) -> Dict[str, Any]:
        """Get all todos
        """
        return await self._request("GET", "/todos", params=params)

    async def get_todo(self, todo_id: int) -> Dict[str, Any]:
        """Get todo by ID"""
        return await self._request("GET", f"/todos/{str(todo_id)}")

    async def get_activities(self, params: Optional[dict] = None) -> Dict[str, Any]:
        """Get activities with optional filtering"""
        return await self._request("GET", "/activities", params=params)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global client instance
client = ProductiveClient()