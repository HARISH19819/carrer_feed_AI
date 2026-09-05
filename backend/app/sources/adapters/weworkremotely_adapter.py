import httpx
import re
from typing import List, Dict, Any
from xml.etree import ElementTree as ET
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class WeWorkRemotelyAdapter(BaseSourceAdapter):
    source_name = "WeWorkRemotely Live RSS"
    adapter_key = "wwr_rss"
    source_type = "feed"
    base_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            headers = {"User-Agent": "JobFusion/1.0 (Public RSS Reader; info@jobfusion.local)"}
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.base_url)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    items = root.findall(".//item")
                    for it in items[:limit]:
                        title_full = it.findtext("title", "")
                        # Often formatted as "Company Name: Job Title"
                        if ":" in title_full:
                            parts = title_full.split(":", 1)
                            company = parts[0].strip()
                            title = parts[1].strip()
                        else:
                            company = "Leading Tech Company"
                            title = title_full.strip()

                        link = it.findtext("link", "")
                        desc = it.findtext("description", "")
                        # Clean basic html tags from description snippet
                        clean_desc = re.sub(r"<[^>]+>", " ", desc)[:4000]
                        pub_date = it.findtext("pubDate", "")

                        raw_jobs.append({
                            "title": title,
                            "company": company,
                            "location": "Remote",
                            "employment_type": "full_time",
                            "experience_required": "Not specified",
                            "salary": "Competitive",
                            "description": clean_desc,
                            "skills": ["Software Engineering", "Remote"],
                            "source": self.source_name,
                            "source_url": link,
                            "application_url": link,
                            "posted_at": pub_date
                        })
                else:
                    logger.warning(f"WeWorkRemotely RSS returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch from WeWorkRemotely RSS: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            headers = {"User-Agent": "JobFusion/1.0"}
            async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
                resp = await client.get(self.base_url)
                return resp.status_code == 200
        except Exception:
            return False
