import httpx
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class ArbeitnowAdapter(BaseSourceAdapter):
    source_name = "Arbeitnow Tech API"
    adapter_key = "arbeitnow_api"
    source_type = "api"
    base_url = "https://www.arbeitnow.com/api/job-board-api"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            headers = {"User-Agent": "JobFusion/1.0 (Career Intelligence Platform; info@jobfusion.local)"}
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.base_url)
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get("data", [])
                    for j in jobs[:limit]:
                        tags = j.get("tags", []) or []
                        job_types = j.get("job_types", []) or []
                        emp_type = "full_time"
                        if any("part" in str(t).lower() for t in job_types):
                            emp_type = "part_time"
                        elif any("contract" in str(t).lower() for t in job_types):
                            emp_type = "contract"
                        elif any("intern" in str(t).lower() for t in job_types):
                            emp_type = "internship"

                        raw_jobs.append({
                            "title": j.get("title", ""),
                            "company": j.get("company_name", ""),
                            "location": j.get("location", "Remote") or "Remote",
                            "employment_type": emp_type,
                            "experience_required": "Not specified",
                            "salary": "Competitive",
                            "description": (j.get("description") or "")[:4000],
                            "skills": tags,
                            "source": self.source_name,
                            "source_url": j.get("url", ""),
                            "application_url": j.get("url", ""),
                            "posted_at": j.get("created_at")
                        })
                else:
                    logger.warning(f"Arbeitnow API returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch from Arbeitnow API: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.base_url)
                return resp.status_code == 200
        except Exception:
            return False
