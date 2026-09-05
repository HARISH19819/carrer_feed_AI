import re
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse, urlunparse
from app.utils.skills import normalize_skill_list, normalize_skill
from app.utils.text import clean_text, extract_years_of_experience

class JobNormalizer:
    @staticmethod
    def clean_company_name(name: str) -> str:
        if not name:
            return "Company Not Specified"
        name = clean_text(name)
        # Remove common corporate suffixes for uniform matching
        patterns = [
            r'\b(inc\.?|incorporated)\b',
            r'\b(llc\.?)\b',
            r'\b(ltd\.?|limited)\b',
            r'\b(pvt\.?\s*ltd\.?|private\s+limited)\b',
            r'\b(corp\.?|corporation)\b',
            r'\b(technologies|tech)\b',
            r'\b(solutions)\b',
            r'\b(software)\b'
        ]
        # Keep clean title-cased company
        cleaned = name
        for p in patterns:
            cleaned = re.sub(p, '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'[,.\-_]+$', '', cleaned).strip()
        return cleaned if len(cleaned) >= 2 else name.strip()

    @staticmethod
    def normalize_title(title: str) -> str:
        if not title:
            return "Job Opportunity"
        title = clean_text(title)
        # Standardize common abbreviations
        title = re.sub(r'\b(jr\.?|jr)\b', 'Junior', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(sr\.?|sr)\b', 'Senior', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(sde\s*1|sde\s*i)\b', 'Software Development Engineer I', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(sde\s*2|sde\s*ii)\b', 'Software Development Engineer II', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(ml)\b', 'Machine Learning', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(ai)\b', 'AI', title, flags=re.IGNORECASE)
        # Strip trailing location annotations like "(Remote)", "- New York"
        title = re.sub(r'\s*\([^)]*\)$', '', title).strip()
        return title

    @staticmethod
    def normalize_location(location: Any) -> Tuple[str, str]:
        """Returns (normalized_location_name, location_type) where location_type is remote/hybrid/onsite."""
        if isinstance(location, list):
            location = ", ".join(str(x) for x in location if x)
        elif not isinstance(location, str):
            location = str(location or "Remote")
            
        loc_lower = location.lower()
        
        if "remote" in loc_lower or "anywhere" in loc_lower or "work from home" in loc_lower:
            loc_type = "remote"
            norm_loc = "Remote"
        elif "hybrid" in loc_lower:
            loc_type = "hybrid"
            norm_loc = clean_text(location)
        else:
            loc_type = "onsite"
            norm_loc = clean_text(location)
            
        return (norm_loc, loc_type)

    @staticmethod
    def normalize_experience(exp_text: Any, title: str = "", desc: str = "") -> Tuple[str, float, float]:
        """
        Returns (experience_level, min_years, max_years).
        Levels: fresher, entry_level, junior, mid_level, senior
        """
        if isinstance(exp_text, list):
            exp_text = " ".join(str(x) for x in exp_text)
        elif not isinstance(exp_text, str):
            exp_text = str(exp_text or "")

        combined = f"{exp_text} {title} {desc}".lower()
        
        # Check for fresher / intern explicitly
        if any(w in combined for w in ["fresher", "intern", "internship", "college graduate", "0 years", "0-1 years", "0 to 1"]):
            if "intern" in combined:
                return ("fresher", 0.0, 1.0)
            return ("fresher", 0.0, 1.0)
            
        min_y, max_y = extract_years_of_experience(combined)
        
        if min_y is not None:
            if min_y <= 1.0 and (max_y is None or max_y <= 2.0):
                return ("entry_level", min_y, max_y if max_y else 2.0)
            elif min_y < 3.0:
                return ("junior", min_y, max_y if max_y else 3.0)
            elif min_y < 5.0:
                return ("mid_level", min_y, max_y if max_y else 5.0)
            else:
                return ("senior", min_y, max_y if max_y else 10.0)
                
        # Heuristic fallback based on title keywords
        if any(w in title.lower() for w in ["lead", "principal", "senior", "architect"]):
            return ("senior", 5.0, 10.0)
        if any(w in title.lower() for w in ["junior", "associate"]):
            return ("junior", 1.0, 3.0)
            
        return ("entry_level", 0.0, 2.0)

    @staticmethod
    def normalize_employment_type(emp_type: Any, title: str = "") -> str:
        if isinstance(emp_type, list):
            emp_type = " ".join(str(x) for x in emp_type)
        elif not isinstance(emp_type, str):
            emp_type = str(emp_type or "full_time")
            
        combined = f"{emp_type} {title}".lower()
        if "intern" in combined:
            return "internship"
        if "part" in combined:
            return "part_time"
        if "contract" in combined or "freelance" in combined:
            return "contract"
        return "full_time"

    @staticmethod
    def standardize_url(url: str) -> str:
        if not url:
            return ""
        try:
            parsed = urlparse(url.strip())
            # Clean common tracking parameters
            clean_query = ""
            if parsed.query:
                params = parsed.query.split("&")
                clean_params = [
                    p for p in params 
                    if not any(p.lower().startswith(x) for x in ["utm_", "ref=", "source=", "track"])
                ]
                clean_query = "&".join(clean_params)
            
            clean_path = parsed.path.rstrip("/")
            return urlunparse((parsed.scheme or "https", parsed.netloc, clean_path, parsed.params, clean_query, ""))
        except Exception:
            return url.strip()

    @classmethod
    def normalize_job_dict(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all fields of a job record into the canonical schema."""
        title = cls.normalize_title(raw.get("title", ""))
        company = clean_text(raw.get("company", ""))
        desc = clean_text(raw.get("description", ""))
        
        loc_str = raw.get("location", "Remote")
        norm_location, loc_type = cls.normalize_location(loc_str)
        
        emp_raw = raw.get("employment_type", "full_time")
        emp_type = cls.normalize_employment_type(emp_raw, title)
        
        exp_raw = raw.get("experience_required", "")
        exp_level, min_y, max_y = cls.normalize_experience(exp_raw, title, desc)
        
        skills = normalize_skill_list(raw.get("skills", []))
        
        source_url = cls.standardize_url(raw.get("source_url", ""))
        app_url = cls.standardize_url(raw.get("application_url", source_url))
        
        return {
            "title": title,
            "company": company,
            "location": norm_location,
            "location_type": loc_type,
            "employment_type": emp_type,
            "experience_level": exp_level,
            "experience_required": f"{int(min_y)}-{int(max_y)} years" if max_y > 0 else "Fresher / 0 years",
            "min_experience_years": min_y,
            "max_experience_years": max_y,
            "salary": raw.get("salary", "Not specified"),
            "description": desc,
            "skills": skills,
            "domain": raw.get("domain", "Software Development"),
            "secondary_domains": raw.get("secondary_domains", []),
            "source": raw.get("source", "Direct"),
            "source_url": source_url,
            "application_url": app_url,
            "status": "active"
        }

job_normalizer = JobNormalizer()
