from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSourceAdapter(ABC):
    source_name: str
    adapter_key: str
    source_type: str  # api, rss, dataset
    base_url: str

    @abstractmethod
    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch raw job records from permitted source."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test whether source endpoint is accessible."""
        pass
