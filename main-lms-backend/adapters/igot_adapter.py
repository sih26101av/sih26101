from abc import ABC, abstractmethod
import httpx
from typing import List, Dict, Any

class ILearningPlatformAdapter(ABC):
    """
    Interface for external learning platform integration
    """
    @abstractmethod
    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        pass

class MockIgotAdapter(ILearningPlatformAdapter):
    """
    Concrete adapter for the Mock iGOT server running on port 8001
    """
    def __init__(self):
        self.base_url = "http://localhost:8001/api/external/igot"
        self.headers = {
            "Authorization": "Bearer mock_igot_secret_2026"
        }
        
    async def fetch_catalog(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/catalog", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
            
    async def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users/{user_id}/history", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
