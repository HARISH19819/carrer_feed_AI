import httpx
import re
from typing import List, Dict, Any
from app.sources.base_source import BaseSourceAdapter
from app.core.logging import logger

class InternshalaAdapter(BaseSourceAdapter):
    source_name = "Internshala Live Feed"
    adapter_key = "internshala_feed"
    source_type = "scraper"
    base_url = "https://internshala.com/fresher-jobs/computer-science-jobs"

    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        raw_jobs = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            # Try computer-science first, fallback to fresher-jobs
            urls = [
                "https://internshala.com/fresher-jobs/computer-science-jobs",
                "https://internshala.com/fresher-jobs"
            ]
            async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
                html = ""
                for u in urls:
                    resp = await client.get(u)
                    if resp.status_code == 200 and len(resp.text) > 5000:
                        html = resp.text
                        break

                if html:
                    # Pattern for job blocks starting at job-title-href
                    sections = re.findall(r'(<a[^>]+class="job-title-href"[^>]*>.*?)(?=<a[^>]+class="job-title-href"|\Z)', html, re.DOTALL)
                    count = 0
                    for sec in sections:
                        # Extract title and relative link
                        title_match = re.search(r'<a[^>]+class="job-title-href"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', sec)
                        if not title_match:
                            continue
                        rel_link = title_match.group(1).strip()
                        title = title_match.group(2).strip()

                        # Extract company name
                        comp_match = re.search(r'class="company-name"[^>]*>[\s\n]*([^<]+)[\s\n]*</p>', sec)
                        if not comp_match:
                            comp_match = re.search(r'class="link_display_like_text"[^>]*>[\s\n]*([^<]+)[\s\n]*<', sec)
                        company = comp_match.group(1).strip() if comp_match else "Hiring Tech Startup"

                        # Extract location
                        loc_match = re.search(r'class="row-1-item\s+locations"[^>]*>.*?<span>[\s\n]*(?:<a[^>]*>)?([^<]+)<', sec, re.DOTALL)
                        location = loc_match.group(1).strip() if loc_match else "India / Remote"

                        # Extract salary/stipend
                        sal_match = re.search(r'<i class="ic-16-money"></i>\s*<span>\s*<span class="desktop">([^<]+)</span>', sec)
                        salary = sal_match.group(1).strip() if sal_match else "Competitive / Stipend"

                        full_url = f"https://internshala.com{rel_link}" if rel_link.startswith("/") else rel_link

                        raw_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "employment_type": "full_time" if "fresher" in rel_link else "internship",
                            "experience_required": "Fresher / Entry Level",
                            "salary": salary,
                            "description": f"Fresher software and tech opportunity at {company}. Apply directly on Internshala.",
                            "skills": ["Software Engineering", "Computer Science", "Fresher"],
                            "source": self.source_name,
                            "source_url": full_url,
                            "application_url": full_url,
                            "posted_at": None
                        })
                        count += 1
                        if count >= limit:
                            break
                else:
                    logger.warning("Could not fetch Internshala content.")
        except Exception as e:
            logger.warning(f"Failed to fetch from Internshala: {e}")
        return raw_jobs

    async def test_connection(self) -> bool:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
                resp = await client.get(self.base_url)
                return resp.status_code == 200
        except Exception:
            return False
