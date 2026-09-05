import httpx
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class TheMuseAdapter(BaseSourceAdapter):
    source_name = "The Muse Jobs API"
    adapter_key = "themuse_api"
    source_type = "api"
    base_url = "https://www.themuse.com/api/public/jobs"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            headers = {"User-Agent": "JobFusion/1.0 (Job Aggregator; info@jobfusion.local)"}
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                # Fetch page 1
                resp = await client.get(f"{self.base_url}?page=1")
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get("results", [])
                    for j in jobs[:limit]:
                        company_info = j.get("company", {}) or {}
                        locations = j.get("locations", []) or []
                        loc_str = locations[0].get("name", "Remote") if locations else "Remote"
                        levels = j.get("levels", []) or []
                        level_str = levels[0].get("name", "Not specified") if levels else "Not specified"
                        categories = j.get("categories", []) or []
                        tags = [c.get("name") for c in categories if c.get("name")]
                        refs = j.get("refs", {}) or {}
                        apply_url = refs.get("landing_page", "")

                        raw_jobs.append({
                            "title": j.get("name", ""),
                            "company": company_info.get("name", "Leading Tech Company"),
                            "location": loc_str,
                            "employment_type": "full_time",
                            "experience_required": level_str,
                            "salary": "Not specified",
                            "description": (j.get("contents") or "")[:4000],
                            "skills": tags,
                            "source": self.source_name,
                            "source_url": apply_url,
                            "application_url": apply_url,
                            "posted_at": j.get("publication_date")
                        })
                else:
                    logger.warning(f"The Muse API returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch from The Muse API: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}?page=1")
                return resp.status_code == 200
        except Exception:
            return False
