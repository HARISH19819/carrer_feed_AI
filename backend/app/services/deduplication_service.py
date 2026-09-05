import hashlib
import re
from typing import Dict, Any, Optional, Tuple, List
from app.core.logging import logger

class DeduplicationService:
    @staticmethod
    def generate_deterministic_fingerprint(company: str, title: str, location: str) -> str:
        """
        Stage 1: Deterministic hash computed from alphanumeric lowercased company + title + location.
        """
        from app.services.normalization_service import job_normalizer
        clean_company = job_normalizer.clean_company_name(company)
        clean_title = job_normalizer.normalize_title(title)
        
        clean_c = re.sub(r'[^a-z0-9]', '', clean_company.lower())
        clean_t = re.sub(r'[^a-z0-9]', '', clean_title.lower())
        clean_l = re.sub(r'[^a-z0-9]', '', (location or "").lower())
        
        raw_key = f"{clean_c}:{clean_t}:{clean_l}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def is_url_match(url1: str, url2: str) -> bool:
        """
        Stage 2: Check URL canonical match.
        """
        if not url1 or not url2:
            return False
        return url1.lower().rstrip("/") == url2.lower().rstrip("/")

    @staticmethod
    def compute_jaccard_similarity(text1: str, text2: str) -> float:
        """
        Stage 3: Token-based similarity for descriptions/titles.
        """
        if not text1 or not text2:
            return 0.0
        tokens1 = set(re.findall(r'\w+', text1.lower()))
        tokens2 = set(re.findall(r'\w+', text2.lower()))
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union)

    def check_is_duplicate(
        self,
        new_job: Dict[str, Any],
        existing_jobs: List[Dict[str, Any]],
        threshold: float = 0.85
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if new_job matches any existing job.
        Returns (is_duplicate, matched_job_id).
        """
        fp = new_job.get("fingerprint") or self.generate_deterministic_fingerprint(
            new_job.get("company", ""),
            new_job.get("title", ""),
            new_job.get("location", "")
        )
        
        new_app_url = new_job.get("application_url", "")
        new_title = new_job.get("title", "")
        new_company = new_job.get("company", "").lower()
        
        for ex in existing_jobs:
            # Stage 1: Exact fingerprint
            if ex.get("fingerprint") == fp:
                return (True, str(ex.get("_id", ex.get("id"))))
                
            # Stage 2: URL match
            if self.is_url_match(new_app_url, ex.get("application_url", "")):
                return (True, str(ex.get("_id", ex.get("id"))))
                
            # Stage 3: Same company + high title Jaccard
            ex_company = ex.get("company", "").lower()
            if ex_company and new_company and ex_company == new_company:
                sim = self.compute_jaccard_similarity(new_title, ex.get("title", ""))
                if sim >= threshold:
                    return (True, str(ex.get("_id", ex.get("id"))))
                    
        return (False, None)

deduplication_service = DeduplicationService()
