import httpx
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class RemotiveAdapter(BaseSourceAdapter):
    source_name = "Remotive Public API"
    adapter_key = "remotive_api"
    source_type = "api"
    base_url = "https://remotive.com/api/remote-jobs"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.base_url}?limit={limit}")
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get("jobs", [])
                    for j in jobs[:limit]:
                        raw_jobs.append({
                            "title": j.get("title", ""),
                            "company": j.get("company_name", ""),
                            "location": j.get("candidate_required_location", "Remote"),
                            "employment_type": j.get("job_type", "full_time"),
                            "experience_required": "Not specified",
                            "salary": j.get("salary", "Not specified"),
                            "description": j.get("description", "")[:4000],
                            "skills": j.get("tags", []),
                            "source": self.source_name,
                            "source_url": j.get("url", ""),
                            "application_url": j.get("url", ""),
                            "posted_at": j.get("publication_date")
                        })
                else:
                    logger.warning(f"Remotive API returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch from Remotive API: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}?limit=1")
                return resp.status_code == 200
        except Exception:
            return False
