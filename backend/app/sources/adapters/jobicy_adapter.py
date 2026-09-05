import httpx
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class JobicyAdapter(BaseSourceAdapter):
    source_name = "Jobicy Remote API"
    adapter_key = "jobicy_api"
    source_type = "api"
    base_url = "https://jobicy.com/api/v2/remote-jobs"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.base_url}?count={limit}")
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get("jobs", [])
                    for j in jobs[:limit]:
                        raw_jobs.append({
                            "title": j.get("jobTitle", ""),
                            "company": j.get("companyName", ""),
                            "location": j.get("jobGeo", "Remote"),
                            "employment_type": j.get("jobType", "full_time"),
                            "experience_required": j.get("jobLevel", "Not specified"),
                            "salary": j.get("annualSalaryMin", "Not specified"),
                            "description": j.get("jobDescription", "")[:4000],
                            "skills": [j.get("jobIndustry", "")] if j.get("jobIndustry") else [],
                            "source": self.source_name,
                            "source_url": j.get("url", ""),
                            "application_url": j.get("url", ""),
                            "posted_at": j.get("pubDate")
                        })
                else:
                    logger.warning(f"Jobicy API returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch from Jobicy API: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}?count=1")
                return resp.status_code == 200
        except Exception:
            return False
