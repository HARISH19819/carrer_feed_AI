import httpx
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class RemoteOKAdapter(BaseSourceAdapter):
    source_name = "RemoteOK Live API"
    adapter_key = "remoteok_api"
    source_type = "api"
    base_url = "https://remoteok.com/api"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            headers = {"User-Agent": "JobFusion-App/1.0 (Public Aggregator; info@jobfusion.io)"}
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.base_url)
                if resp.status_code == 200:
                    items = resp.json()
                    # First item is legal note/metadata, skip items without 'position'
                    count = 0
                    for item in items:
                        if not isinstance(item, dict) or "position" not in item:
                            continue
                        tags = item.get("tags", []) or []
                        url = item.get("url", "")
                        if url and not url.startswith("http"):
                            url = f"https://remoteok.com{url}"

                        salary_min = item.get("salary_min")
                        salary_max = item.get("salary_max")
                        salary_str = "Competitive"
                        if salary_min and salary_max:
                            salary_str = f"${int(salary_min):,} - ${int(salary_max):,}/yr"

                        raw_jobs.append({
                            "title": item.get("position", ""),
                            "company": item.get("company", "Tech Co"),
                            "location": item.get("location", "Remote") or "Remote",
                            "employment_type": "full_time",
                            "experience_required": "Not specified",
                            "salary": salary_str,
                            "description": (item.get("description") or "")[:4000],
                            "skills": tags,
                            "source": self.source_name,
                            "source_url": url,
                            "application_url": item.get("apply_url") or url,
                            "posted_at": item.get("date")
                        })
                        count += 1
                        if count >= limit:
                            break
                else:
                    logger.warning(f"RemoteOK API returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch from RemoteOK API: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            headers = {"User-Agent": "JobFusion-App/1.0"}
            async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
                resp = await client.get(self.base_url)
                return resp.status_code == 200
        except Exception:
            return False
