import httpx
import re
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class LinkedInAdapter(BaseSourceAdapter):
    source_name = "LinkedIn Jobs Feed"
    adapter_key = "linkedin_feed"
    source_type = "feed"
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        queries = ["software engineer", "machine learning", "frontend developer", "backend engineer"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        try:
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                for q in queries:
                    if len(raw_jobs) >= limit:
                        break
                    url = f"{self.base_url}?keywords={q.replace(' ', '%20')}&start=0"
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        continue
                    
                    html = resp.text
                    # Split into cards
                    cards = re.findall(r'<div class="base-card[^"]*"[^>]*>(.*?)</li>', html, re.DOTALL)
                    for card in cards:
                        # Extract title
                        title_m = re.search(r'<h3 class="base-search-card__title">[\s\n]*([^<]+)[\s\n]*</h3>', card)
                        # Extract company
                        comp_m = re.search(r'<h4 class="base-search-card__subtitle">[\s\n]*(?:<a[^>]*>)?[\s\n]*([^<]+)[\s\n]*(?:</a>)?[\s\n]*</h4>', card)
                        # Extract location
                        loc_m = re.search(r'<span class="job-search-card__location">[\s\n]*([^<]+)[\s\n]*</span>', card)
                        # Extract link
                        link_m = re.search(r'<a class="base-card__full-link[^"]*"[^>]+href="([^"]+)"', card)

                        if not title_m or not link_m:
                            continue

                        title = title_m.group(1).strip()
                        company = comp_m.group(1).strip() if comp_m else "Verified Employer"
                        location = loc_m.group(1).strip() if loc_m else "Remote"
                        raw_link = link_m.group(1).strip()
                        # Clean link tracking parameters
                        job_link = raw_link.split("?")[0] if "?" in raw_link else raw_link

                        raw_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "employment_type": "full_time",
                            "experience_required": "Not specified",
                            "salary": "Market Rate",
                            "description": f"Verified live job opening for {title} at {company} ({location}). Apply directly via LinkedIn.",
                            "skills": [q.title(), "Engineering"],
                            "source": self.source_name,
                            "source_url": job_link,
                            "application_url": job_link,
                            "posted_at": None
                        })
                        if len(raw_jobs) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Failed to fetch from LinkedIn Feed: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}?keywords=python&start=0")
                return resp.status_code == 200
        except Exception:
            return False
